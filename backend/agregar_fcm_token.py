"""
Script para agregar columna fcm_token a la tabla usuarios
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from src.database.config import engine

def agregar_fcm_token():
    """Agregar columna fcm_token a usuarios"""
    
    with engine.connect() as conn:
        try:
            # Verificar si la columna ya existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='usuarios' AND column_name='fcm_token'
            """))
            
            if result.fetchone():
                print("✓ La columna fcm_token ya existe")
                return
            
            # Agregar columna
            conn.execute(text("""
                ALTER TABLE usuarios 
                ADD COLUMN fcm_token VARCHAR(255)
            """))
            conn.commit()
            
            print("✓ Columna fcm_token agregada exitosamente")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            conn.rollback()

if __name__ == "__main__":
    print("Agregando columna fcm_token a usuarios...")
    agregar_fcm_token()
    print("Migración completada")
