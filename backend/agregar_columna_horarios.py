import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from src.database.config import get_db

db = next(get_db())

try:
    print("Agregando columna horarios_disponibles...")
    
    db.execute(text("""
        ALTER TABLE torneos 
        ADD COLUMN horarios_disponibles JSON
    """))
    
    db.commit()
    print("✅ Columna agregada exitosamente!")
    
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
