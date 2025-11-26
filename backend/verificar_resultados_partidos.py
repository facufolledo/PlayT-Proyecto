"""
Script para verificar si los partidos 19 y 20 tienen resultado
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Crear engine
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 100)
print("VERIFICANDO RESULTADOS DE PARTIDOS 19 Y 20")
print("=" * 100)

query = text("""
    SELECT 
        p.id_partido,
        p.estado,
        p.elo_aplicado,
        p.resultado_padel,
        p.ganador_equipo,
        r.id_partido as resultado_existe,
        r.sets_eq1,
        r.sets_eq2
    FROM partidos p
    LEFT JOIN resultados_partidos r ON p.id_partido = r.id_partido
    WHERE p.id_partido IN (19, 20)
""")

result = db.execute(query)
partidos = result.fetchall()

for partido in partidos:
    print(f"\n--- Partido {partido.id_partido} ---")
    print(f"Estado: {partido.estado}")
    print(f"Elo aplicado: {partido.elo_aplicado}")
    print(f"Ganador equipo: {partido.ganador_equipo}")
    print(f"Resultado_padel (JSON): {partido.resultado_padel}")
    print(f"Tiene resultado en tabla resultados_partidos: {partido.resultado_existe is not None}")
    
    if partido.resultado_existe:
        print(f"Sets: {partido.sets_eq1}-{partido.sets_eq2}")

db.close()
