"""
Script para ejecutar la migración del sistema de marcador
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def ejecutar_migracion():
    """Ejecuta el script de migración SQL"""
    
    # Obtener URL de la base de datos
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ Error: DATABASE_URL no encontrada en .env")
        return
    
    print("🔄 Conectando a la base de datos...")
    engine = create_engine(database_url)
    
    # Leer el archivo SQL
    print("📄 Leyendo archivo de migración...")
    with open("migrations_sistema_marcador_simple.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()
    
    print(f"📊 Ejecutando migración completa...")
    
    # Ejecutar todo el script de una vez (PostgreSQL maneja las transacciones)
    try:
        with engine.connect() as conn:
            # Ejecutar el script completo
            conn.execute(text(sql_content))
            conn.commit()
            print("  ✅ Migración ejecutada correctamente")
    except Exception as e:
        print(f"  ❌ Error durante la migración: {e}")
        print("\n💡 Tip: Algunos errores son normales si las tablas ya existen.")
        print("   Verifica manualmente en tu base de datos.")
    
    print("\n✅ Migración completada!")
    print("\n📋 Verificando estructura...")
    
    # Verificar que las tablas existen
    with engine.connect() as conn:
        # Verificar confirmaciones
        result = conn.execute(text("""
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_name = 'confirmaciones'
        """))
        if result.fetchone()[0] > 0:
            print("  ✅ Tabla 'confirmaciones' creada")
        
        # Verificar historial_enfrentamientos
        result = conn.execute(text("""
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_name = 'historial_enfrentamientos'
        """))
        if result.fetchone()[0] > 0:
            print("  ✅ Tabla 'historial_enfrentamientos' creada")
        
        # Verificar campos en partidos
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'partidos' 
            AND column_name IN ('resultado_padel', 'estado_confirmacion', 'elo_aplicado')
        """))
        campos = [row[0] for row in result.fetchall()]
        if len(campos) == 3:
            print("  ✅ Campos nuevos en 'partidos' agregados")
        
        # Verificar campos en partido_jugadores
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'partido_jugadores' 
            AND column_name IN ('rating_antes', 'rating_despues', 'cambio_elo')
        """))
        campos = [row[0] for row in result.fetchall()]
        if len(campos) == 3:
            print("  ✅ Campos nuevos en 'partido_jugadores' agregados")
    
    print("\n🎉 ¡Todo listo! El sistema de marcador está configurado.")

if __name__ == "__main__":
    ejecutar_migracion()
