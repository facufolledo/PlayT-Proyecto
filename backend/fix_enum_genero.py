"""
Script para arreglar el enum de género en la tabla torneos
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text

def fix_enum_genero():
    """Arregla el enum de género para usar minúsculas"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL no configurada")
        return False
    
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Eliminar la columna y el tipo enum existente
            print("Eliminando columna genero existente...")
            conn.execute(text("ALTER TABLE torneos DROP COLUMN IF EXISTS genero"))
            conn.commit()
            
            print("Eliminando tipo enum existente...")
            conn.execute(text("DROP TYPE IF EXISTS generotorneo"))
            conn.commit()
            
            # Crear el tipo enum con valores en minúsculas
            print("Creando nuevo tipo enum con valores en minúsculas...")
            conn.execute(text("""
                CREATE TYPE generotorneo AS ENUM ('masculino', 'femenino', 'mixto')
            """))
            conn.commit()
            
            # Agregar la columna con el nuevo tipo
            print("Agregando columna genero...")
            conn.execute(text("""
                ALTER TABLE torneos 
                ADD COLUMN genero generotorneo DEFAULT 'masculino'
            """))
            conn.commit()
            
            print("✓ Enum de género arreglado exitosamente")
            
            # Verificar
            result = conn.execute(text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns 
                WHERE table_name = 'torneos' AND column_name = 'genero'
            """))
            row = result.fetchone()
            if row:
                print(f"  Columna: {row[0]}, Tipo: {row[1]}, Default: {row[2]}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("FIX: Arreglar enum de género en torneos")
    print("=" * 60)
    fix_enum_genero()
