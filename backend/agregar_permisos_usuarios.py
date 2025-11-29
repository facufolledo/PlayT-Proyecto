"""
Script para agregar columnas de permisos a la tabla usuarios
Ejecutar con: python agregar_permisos_usuarios.py
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# Obtener URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL no está configurada en .env")
    exit(1)

print("🔧 Conectando a la base de datos...")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("✅ Conexión exitosa")
        
        # Agregar columna puede_crear_torneos
        print("\n📝 Agregando columna 'puede_crear_torneos'...")
        conn.execute(text("""
            ALTER TABLE usuarios 
            ADD COLUMN IF NOT EXISTS puede_crear_torneos BOOLEAN NOT NULL DEFAULT FALSE
        """))
        conn.commit()
        print("✅ Columna 'puede_crear_torneos' agregada")
        
        # Agregar columna es_administrador
        print("\n📝 Agregando columna 'es_administrador'...")
        conn.execute(text("""
            ALTER TABLE usuarios 
            ADD COLUMN IF NOT EXISTS es_administrador BOOLEAN NOT NULL DEFAULT FALSE
        """))
        conn.commit()
        print("✅ Columna 'es_administrador' agregada")
        
        # Verificar que las columnas existen
        print("\n🔍 Verificando columnas...")
        result = conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'usuarios' 
            AND column_name IN ('puede_crear_torneos', 'es_administrador')
        """))
        
        columns = result.fetchall()
        if len(columns) == 2:
            print("✅ Ambas columnas verificadas correctamente:")
            for col in columns:
                print(f"   - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        else:
            print(f"⚠️  Solo se encontraron {len(columns)} columnas")
        
        print("\n✅ ¡Migración completada exitosamente!")
        print("\n💡 Ahora reinicia el servidor backend para que los cambios surtan efecto:")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        
except Exception as e:
    print(f"\n❌ Error durante la migración: {e}")
    print("\n💡 Sugerencias:")
    print("   1. Verifica que DATABASE_URL esté correctamente configurada")
    print("   2. Verifica que tengas permisos para modificar la tabla")
    print("   3. Verifica que la tabla 'usuarios' exista")
    exit(1)
