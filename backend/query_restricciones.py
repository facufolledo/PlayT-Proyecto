"""
Query directo para ver restricciones
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from src.database.config import get_db

def query():
    db = next(get_db())
    
    try:
        result = db.execute(text("""
            SELECT id, jugador1_id, jugador2_id, estado, 
                   CASE WHEN disponibilidad_horaria IS NULL THEN 'NULL' ELSE 'NOT NULL' END as tiene_restricciones
            FROM torneos_parejas
            WHERE torneo_id = 25
            ORDER BY id
        """))
        
        rows = result.fetchall()
        
        print(f"Total parejas: {len(rows)}\n")
        
        con_restricciones = 0
        sin_restricciones = 0
        
        for row in rows:
            tiene = row[4]
            if tiene == 'NOT NULL':
                con_restricciones += 1
                print(f"ID {row[0]:3} | SI  | {row[3]:12}")
            else:
                sin_restricciones += 1
                print(f"ID {row[0]:3} | NO  | {row[3]:12}")
        
        print(f"\nCon restricciones: {con_restricciones}")
        print(f"Sin restricciones: {sin_restricciones}")
        
    finally:
        db.close()

if __name__ == "__main__":
    query()
