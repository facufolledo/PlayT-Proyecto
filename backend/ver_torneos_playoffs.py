"""
Script para ver qué torneos tienen playoffs
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Ver partidos de playoffs (fase != zona y fase != null)
    result = conn.execute(text("""
        SELECT DISTINCT id_torneo, fase, COUNT(*) as total,
               SUM(CASE WHEN ganador_pareja_id IS NOT NULL THEN 1 ELSE 0 END) as con_ganador
        FROM partidos 
        WHERE fase IS NOT NULL AND fase != 'zona'
        GROUP BY id_torneo, fase
        ORDER BY id_torneo, fase
    """))
    
    print("=== Partidos de playoffs por torneo ===")
    for row in result:
        print(f"  Torneo {row[0]}: {row[1]} - {row[2]} partidos ({row[3]} con ganador)")
    
    # Ver detalle de partidos de playoffs
    result = conn.execute(text("""
        SELECT id_partido, id_torneo, fase, numero_partido, 
               pareja1_id, pareja2_id, ganador_pareja_id, estado
        FROM partidos 
        WHERE fase IS NOT NULL AND fase != 'zona'
        ORDER BY id_torneo, fase, numero_partido
    """))
    
    print("\n=== Detalle de partidos de playoffs ===")
    for row in result:
        print(f"  ID:{row[0]} T:{row[1]} {row[2]}#{row[3]} - P1:{row[4]} vs P2:{row[5]} -> Ganador:{row[6]} ({row[7]})")
