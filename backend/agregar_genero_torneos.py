"""
Script para agregar la columna 'genero' a la tabla torneos
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text

def agregar_columna_genero():
    """Agrega la columna genero a la tabla torneos"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL no configurada")
        return False
    
    # Convertir URL de postgres:// a postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Verificar si la columna ya existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'torneos' AND column_name = 'genero'
            """))
            
            if result.fetchone():
                print("✓ La columna 'genero' ya existe en la tabla torneos")
            else:
                # Crear el tipo ENUM si no existe
                conn.execute(text("""
                    DO $$ BEGIN
                        CREATE TYPE generotorneo AS ENUM ('masculino', 'femenino', 'mixto');
                    EXCEPTION
                        WHEN duplicate_object THEN null;
                    END $$;
                """))
                conn.commit()
                
                # Agregar la columna
                conn.execute(text("""
                    ALTER TABLE torneos 
                    ADD COLUMN genero generotorneo DEFAULT 'masculino'
                """))
                conn.commit()
                
                print("✓ Columna 'genero' agregada exitosamente a la tabla torneos")
            
            # Verificar la estructura actual
            result = conn.execute(text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns 
                WHERE table_name = 'torneos'
                ORDER BY ordinal_position
            """))
            
            print("\nEstructura actual de la tabla torneos:")
            print("-" * 60)
            for row in result.fetchall():
                print(f"  {row[0]}: {row[1]} (default: {row[2]})")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN: Agregar columna 'genero' a torneos")
    print("=" * 60)
    agregar_columna_genero()
