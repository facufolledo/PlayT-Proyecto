"""
Script para verificar qué jugadores participaron en los partidos de sala
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
print("JUGADORES EN PARTIDOS DE SALA (19, 20)")
print("=" * 100)

query = text("""
    SELECT 
        p.id_partido,
        p.estado,
        p.elo_aplicado,
        s.nombre as sala_nombre,
        pj.id_usuario,
        u.nombre_usuario,
        pj.equipo
    FROM partidos p
    LEFT JOIN salas s ON p.id_sala = s.id_sala
    LEFT JOIN partido_jugadores pj ON p.id_partido = pj.id_partido
    LEFT JOIN usuarios u ON pj.id_usuario = u.id_usuario
    WHERE p.id_partido IN (19, 20)
    ORDER BY p.id_partido, pj.equipo, pj.id_usuario
""")

result = db.execute(query)
jugadores = result.fetchall()

partido_actual = None
for jugador in jugadores:
    if partido_actual != jugador.id_partido:
        partido_actual = jugador.id_partido
        print(f"\n--- Partido {jugador.id_partido} ---")
        print(f"Sala: {jugador.sala_nombre}")
        print(f"Estado: {jugador.estado}")
        print(f"Elo aplicado: {jugador.elo_aplicado}")
        print("Jugadores:")
    
    print(f"  - {jugador.nombre_usuario} (ID: {jugador.id_usuario}, Equipo: {jugador.equipo})")

db.close()
