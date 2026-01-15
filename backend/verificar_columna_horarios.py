import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from src.database.config import get_db

db = next(get_db())
result = db.execute(text("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'torneos' 
    AND column_name = 'horarios_disponibles'
"""))

columna = result.fetchone()
if columna:
    print(f"✅ Columna existe: {columna[0]} ({columna[1]})")
else:
    print("❌ Columna no existe")

db.close()
