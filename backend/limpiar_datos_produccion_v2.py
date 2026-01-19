"""
Script mejorado para limpiar datos de producción
Usa CASCADE para manejar foreign keys automáticamente
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: No se encontró DATABASE_URL en .env")
    sys.exit(1)

def confirmar_accion():
    """Pedir confirmación"""
    print("\n" + "="*80)
    print("⚠️  LIMPIEZA COMPLETA DE BASE DE DATOS")
    print("="*80)
    print("\n⚠️  Este script borrará TODOS los datos de usuarios, salas, torneos y partidos")
    print("✅ Se mantendrán las categorías del sistema\n")
    
    respuesta = input("¿Continuar? (escribe 'SI'): ")
    return respuesta == "SI"

def limpiar_base_datos():
    """Limpiar todos los datos"""
    
    if not confirmar_accion():
        print("❌ Operación cancelada")
        return
    
    print("\n🔄 Conectando a la base de datos...")
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            print("\n🧹 Limpiando datos...")
            
            # Usar TRUNCATE con CASCADE para borrar todo de una vez
            # TRUNCATE es más rápido que DELETE y resetea los IDs automáticamente
            
            comandos = [
                # Primero las tablas sin dependencias o con CASCADE
                ("TRUNCATE TABLE salas CASCADE", "Salas"),
                ("DELETE FROM usuarios CASCADE", "Usuarios"),  # Usar DELETE porque puede tener FK complejas
                ("TRUNCATE TABLE torneos CASCADE", "Torneos"),
                ("TRUNCATE TABLE partidos CASCADE", "Partidos"),
                ("DELETE FROM historial_enfrentamientos", "Historial enfrentamientos"),
            ]
            
            for comando, descripcion in comandos:
                try:
                    print(f"\n🗑️  Limpiando {descripcion}...")
                    conn.execute(text(comando))
                    conn.commit()
                    print(f"   ✅ {descripcion} limpiado")
                except Exception as e:
                    error_msg = str(e)
                    if "does not exist" in error_msg:
                        print(f"   ⚠️  Tabla no existe (normal)")
                    else:
                        print(f"   ⚠️  Error: {error_msg[:100]}")
                    # Hacer rollback y continuar
                    conn.rollback()
            
            # Verificar categorías
            print("\n✅ Verificando categorías del sistema...")
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM categorias"))
                count = result.scalar()
                print(f"   ✅ {count} categorías mantienen intactas")
            except:
                print(f"   ⚠️  No se pudo verificar")
            
            print("\n" + "="*80)
            print("✅ LIMPIEZA COMPLETADA")
            print("="*80)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        engine.dispose()

def verificar_estado():
    """Verificar estado final"""
    print("\n🔍 Verificando estado...")
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            tablas = ["usuarios", "torneos", "salas", "partidos"]
            
            print("\n📊 Conteo de registros:")
            for tabla in tablas:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                    count = result.scalar()
                    emoji = "✅" if count == 0 else "⚠️"
                    print(f"  {emoji} {tabla.capitalize()}: {count}")
                except:
                    print(f"  ❌ {tabla.capitalize()}: Error")
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("\n🚀 LIMPIEZA DE BASE DE DATOS")
    limpiar_base_datos()
    verificar_estado()
    print("\n✅ Proceso completado\n")
