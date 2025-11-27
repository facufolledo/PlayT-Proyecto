"""
Script para verificar los nombres de las tablas en la base de datos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from src.database.config import engine

def verificar_tablas():
    """Verificar nombres de tablas"""
    
    with engine.connect() as conn:
        try:
            print("\n=== TABLAS EN LA BASE DE DATOS ===\n")
            
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tablas = result.fetchall()
            
            for tabla in tablas:
                print(f"  • {tabla[0]}")
            
            print("\n")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    verificar_tablas()
