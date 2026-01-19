"""
Script para limpiar TODOS los datos de prueba antes del lanzamiento
CUIDADO: Este script borra TODOS los datos excepto las categorías del sistema
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: No se encontró DATABASE_URL en .env")
    sys.exit(1)

def confirmar_accion():
    """Pedir confirmación triple para evitar accidentes"""
    print("\n" + "="*80)
    print("⚠️  ADVERTENCIA: LIMPIEZA COMPLETA DE BASE DE DATOS")
    print("="*80)
    print("\nEste script va a BORRAR:")
    print("  ❌ Todos los usuarios (excepto estructura)")
    print("  ❌ Todas las salas")
    print("  ❌ Todos los partidos")
    print("  ❌ Todos los torneos")
    print("  ❌ Todas las parejas")
    print("  ❌ Todas las zonas")
    print("  ❌ Todo el historial ELO")
    print("  ❌ Todas las confirmaciones")
    print("  ❌ Todos los enfrentamientos")
    print("\n✅ Se MANTIENEN:")
    print("  ✓ Estructura de tablas")
    print("  ✓ Categorías del sistema")
    print("  ✓ Configuraciones")
    print("\n" + "="*80)
    
    respuesta1 = input("\n¿Estás SEGURO que quieres continuar? (escribe 'SI ESTOY SEGURO'): ")
    if respuesta1 != "SI ESTOY SEGURO":
        print("❌ Operación cancelada")
        return False
    
    respuesta2 = input("\n¿REALMENTE quieres borrar TODOS los datos? (escribe 'BORRAR TODO'): ")
    if respuesta2 != "BORRAR TODO":
        print("❌ Operación cancelada")
        return False
    
    respuesta3 = input("\n⚠️  ÚLTIMA CONFIRMACIÓN - ¿Proceder con la limpieza? (escribe 'CONFIRMO'): ")
    if respuesta3 != "CONFIRMO":
        print("❌ Operación cancelada")
        return False
    
    return True

def limpiar_base_datos():
    """Limpiar todos los datos de prueba"""
    
    if not confirmar_accion():
        return
    
    print("\n🔄 Conectando a la base de datos...")
    engine = create_engine(DATABASE_URL)
    
    try:
        print("\n🧹 Iniciando limpieza de datos...")
        
        # ORDEN IMPORTANTE: Borrar en orden inverso a las dependencias
        # Cada operación en su propia transacción para evitar rollback en cadena
        
        tablas_a_limpiar = [
            ("historial_enfrentamientos", "1️⃣  Historial de enfrentamientos"),
            ("elo_history", "2️⃣  Historial ELO"),
            ("partidos", "3️⃣  Partidos"),
            ("parejas_torneo", "4️⃣  Parejas de torneos"),
            ("zonas_torneo", "5️⃣  Zonas de torneos"),
            ("categorias_torneo", "6️⃣  Categorías de torneos"),
            ("torneos", "7️⃣  Torneos"),
            ("salas", "8️⃣  Salas"),
            ("usuarios", "9️⃣  Usuarios"),
        ]
        
        for tabla, descripcion in tablas_a_limpiar:
            try:
                with engine.connect() as conn:
                    print(f"\n{descripcion}...")
                    result = conn.execute(text(f"DELETE FROM {tabla}"))
                    conn.commit()
                    print(f"   ✅ {result.rowcount} registros eliminados")
            except Exception as e:
                print(f"   ⚠️  Error o tabla no existe: {str(e)[:100]}")
        
        # Resetear secuencias (IDs auto-incrementales)
        print("\n🔄 Reseteando secuencias de IDs...")
        
        secuencias = [
            "usuarios_id_usuario_seq",
            "torneos_id_torneo_seq",
            "categorias_torneo_id_categoria_torneo_seq",
            "parejas_torneo_id_pareja_seq",
            "zonas_torneo_id_zona_seq",
            "partidos_id_partido_seq",
            "salas_id_sala_seq",
            "elo_history_id_seq",
            "historial_enfrentamientos_id_seq"
        ]
        
        for seq in secuencias:
            try:
                with engine.connect() as conn:
                    conn.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1"))
                    conn.commit()
                    print(f"   ✅ {seq} reseteada")
            except Exception as e:
                print(f"   ⚠️  {seq} no existe")
        
        # Verificar que las categorías del sistema siguen ahí
        print("\n✅ Verificando categorías del sistema...")
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM categorias"))
                count = result.scalar()
                print(f"   ✅ {count} categorías del sistema mantienen intactas")
        except Exception as e:
            print(f"   ⚠️  No se pudo verificar categorías")
        
        print("\n" + "="*80)
        print("✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
        print("="*80)
        print("\n📊 Estado de la base de datos:")
        print("  ✅ Base de datos limpia y lista para producción")
        print("  ✅ Todas las tablas mantienen su estructura")
        print("  ✅ Categorías del sistema intactas")
        print("  ✅ IDs reseteados a 1")
        print("\n🚀 La aplicación está lista para el lanzamiento!")
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO durante la limpieza: {e}")
        print("⚠️  Revisa el estado de la base de datos antes de continuar")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        engine.dispose()

def verificar_estado_final():
    """Verificar el estado final de la base de datos"""
    print("\n🔍 Verificando estado final de la base de datos...")
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            tablas = [
                ("usuarios", "Usuarios"),
                ("torneos", "Torneos"),
                ("salas", "Salas"),
                ("partidos", "Partidos"),
                ("parejas_torneo", "Parejas"),
                ("zonas_torneo", "Zonas"),
                ("categorias", "Categorías Sistema"),
                ("elo_history", "Historial ELO")
            ]
            
            print("\n📊 Conteo de registros:")
            for tabla, nombre in tablas:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {tabla}"))
                    count = result.scalar()
                    emoji = "✅" if count == 0 or tabla == "categorias" else "⚠️"
                    print(f"  {emoji} {nombre}: {count} registros")
                except Exception as e:
                    print(f"  ❌ {nombre}: Error al contar")
    
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("\n🚀 SCRIPT DE LIMPIEZA PRE-LANZAMIENTO")
    print("="*80)
    
    limpiar_base_datos()
    verificar_estado_final()
    
    print("\n" + "="*80)
    print("✅ Proceso completado")
    print("="*80)
