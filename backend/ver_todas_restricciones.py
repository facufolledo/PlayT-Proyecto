"""
Ver todas las restricciones del torneo 25
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from src.database.config import get_db
import json

def ver_restricciones():
    db = next(get_db())
    
    try:
        result = db.execute(text("""
            SELECT id, disponibilidad_horaria
            FROM torneos_parejas
            WHERE torneo_id = 25
            ORDER BY id
        """))
        
        rows = result.fetchall()
        
        print(f"Total parejas: {len(rows)}\n")
        
        restricciones_unicas = {}
        
        for row in rows:
            pareja_id = row[0]
            restricciones = row[1]
            
            if restricciones:
                restricciones_str = json.dumps(restricciones, ensure_ascii=False, sort_keys=True)
                
                if restricciones_str not in restricciones_unicas:
                    restricciones_unicas[restricciones_str] = []
                
                restricciones_unicas[restricciones_str].append(pareja_id)
                
                print(f"ID {pareja_id:3}: {restricciones_str}")
        
        print(f"\n{'='*80}")
        print("RESUMEN DE RESTRICCIONES UNICAS:")
        print(f"{'='*80}\n")
        
        for i, (restriccion, parejas) in enumerate(restricciones_unicas.items(), 1):
            print(f"{i}. {restriccion}")
            print(f"   Parejas ({len(parejas)}): {parejas}\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    ver_restricciones()
