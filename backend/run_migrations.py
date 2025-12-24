"""
Script para ejecutar migraciones SQL
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# Obtener URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no está configurada en .env")
    exit(1)

# Crear engine
engine = create_engine(DATABASE_URL)

# Obtener nombre del archivo de migraciones desde argumentos
import sys
migration_file = sys.argv[1] if len(sys.argv) > 1 else 'migrations_salas.sql'

if not os.path.exists(migration_file):
    print(f"❌ Error: Archivo {migration_file} no encontrado")
    exit(1)

# Leer archivo de migraciones
with open(migration_file, 'r', encoding='utf-8') as f:
    sql_script = f.read()

# Ejecutar migraciones
try:
    with engine.begin() as conn:
        # Limpiar comentarios y dividir por líneas
        lines = []
        current_statement = []
        
        for line in sql_script.split('\n'):
            line = line.strip()
            # Ignorar comentarios y líneas vacías
            if not line or line.startswith('--'):
                continue
            
            current_statement.append(line)
            
            # Si la línea termina con ;, ejecutar el statement
            if line.endswith(';'):
                statement = ' '.join(current_statement).strip()
                if statement:
                    try:
                        conn.execute(text(statement))
                        print(f"✅ Ejecutado: {statement[:60]}...")
                    except Exception as e:
                        print(f"⚠️  Advertencia: {str(e)[:100]}")
                current_statement = []
        
        print(f"\n✅ Migraciones de {migration_file} completadas")
        
except Exception as e:
    print(f"❌ Error ejecutando migraciones: {e}")
    exit(1)
