"""
Agrega el campo nombre_pareja a la tabla torneos_parejas
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.config import engine
from sqlalchemy import text

def agregar_campo_nombre_pareja():
    """Agrega el campo nombre_pareja si no existe"""
    try:
        with engine.connect() as conn:
            # Verificar si la columna ya existe
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'torneos_parejas' 
                AND COLUMN_NAME = 'nombre_pareja'
            """))
            
            exists = result.fetchone()[0] > 0
            
            if exists:
                print("✅ El campo 'nombre_pareja' ya existe")
                return
            
            # Agregar la columna
            conn.execute(text("""
                ALTER TABLE torneos_parejas 
                ADD COLUMN nombre_pareja VARCHAR(100) 
                COMMENT 'Nombre de la pareja'
            """))
            conn.commit()
            
            print("✅ Campo 'nombre_pareja' agregado exitosamente")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    agregar_campo_nombre_pareja()
