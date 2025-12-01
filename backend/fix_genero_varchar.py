"""
Script para cambiar la columna genero a VARCHAR
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text

def fix_genero_varchar():
    """Cambia la columna genero a VARCHAR"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL no configurada")
        return False
    
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Eliminar la columna existente
            print("Eliminando columna genero existente...")
            conn.execute(text("ALTER TABLE torneos DROP COLUMN IF EXISTS genero"))
            conn.commit()
            
            # Agregar la columna como VARCHAR
            print("Agregando columna genero como VARCHAR...")
            conn.execute(text("""
                ALTER TABLE torneos 
                ADD COLUMN genero VARCHAR(20) DEFAULT 'masculino'
            """))
            conn.commit()
            
            # Eliminar el tipo enum si existe
            print("Eliminando tipo enum...")
            conn.execute(text("DROP TYPE IF EXISTS generotorneo"))
            conn.commit()
            
            print("✓ Columna genero cambiada a VARCHAR exitosamente")
            
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
    print("FIX: Cambiar genero a VARCHAR")
    print("=" * 60)
    fix_genero_varchar()
