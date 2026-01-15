"""
Script para verificar parejas pendientes
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT id, torneo_id, jugador1_id, jugador2_id, estado, 
               codigo_confirmacion, confirmado_jugador2 
        FROM torneos_parejas 
        WHERE confirmado_jugador2 = false 
        LIMIT 10
    """))
    
    rows = result.fetchall()
    
    if not rows:
        print("No hay parejas pendientes de confirmación")
    else:
        print(f"\n{'='*80}")
        print(f"Parejas pendientes de confirmación ({len(rows)}):")
        print(f"{'='*80}\n")
        
        for r in rows:
            print(f"ID: {r[0]}")
            print(f"  Torneo ID: {r[1]}")
            print(f"  Jugador 1: {r[2]}")
            print(f"  Jugador 2: {r[3]}")
            print(f"  Estado: '{r[4]}'")
            print(f"  Código: {r[5]}")
            print(f"  Confirmado J2: {r[6]}")
            print()
