"""
Script para crear entradas de historial_rating para partidos de sala
que tienen elo_aplicado pero no tienen historial
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
print("CREANDO HISTORIAL DE RATING PARA PARTIDOS DE SALA")
print("=" * 100)

# Buscar partidos con elo_aplicado pero sin historial_rating
query_partidos = text("""
    SELECT DISTINCT
        p.id_partido,
        p.ganador_equipo,
        pj.id_usuario,
        pj.equipo,
        pj.rating_antes,
        pj.rating_despues,
        pj.cambio_elo
    FROM partidos p
    INNER JOIN partido_jugadores pj ON p.id_partido = pj.id_partido
    LEFT JOIN historial_rating hr ON p.id_partido = hr.id_partido AND pj.id_usuario = hr.id_usuario
    WHERE p.elo_aplicado = true
    AND p.id_sala IS NOT NULL
    AND hr.id_historial IS NULL
    AND pj.rating_antes IS NOT NULL
    AND pj.rating_despues IS NOT NULL
    ORDER BY p.id_partido, pj.id_usuario
""")

result = db.execute(query_partidos)
jugadores_sin_historial = result.fetchall()

print(f"\nJugadores sin historial encontrados: {len(jugadores_sin_historial)}\n")

if len(jugadores_sin_historial) == 0:
    print("✅ Todos los partidos ya tienen historial de rating")
    db.close()
    exit(0)

# Crear entradas de historial_rating
for jugador in jugadores_sin_historial:
    print(f"Partido {jugador.id_partido} - Usuario {jugador.id_usuario}")
    print(f"  Rating antes: {jugador.rating_antes}")
    print(f"  Rating después: {jugador.rating_despues}")
    print(f"  Delta: {jugador.cambio_elo}")
    
    # Insertar en historial_rating
    query_insert = text("""
        INSERT INTO historial_rating (id_usuario, id_partido, rating_antes, delta, rating_despues, creado_en)
        VALUES (:id_usuario, :id_partido, :rating_antes, :delta, :rating_despues, NOW())
    """)
    
    db.execute(query_insert, {
        'id_usuario': jugador.id_usuario,
        'id_partido': jugador.id_partido,
        'rating_antes': jugador.rating_antes,
        'delta': jugador.cambio_elo,
        'rating_despues': jugador.rating_despues
    })
    
    print("  ✅ Historial creado")

db.commit()

print(f"\n✅ Se crearon {len(jugadores_sin_historial)} entradas de historial de rating")

# Verificar
print("\n" + "=" * 100)
print("VERIFICANDO HISTORIAL CREADO")
print("=" * 100)

query_verificar = text("""
    SELECT 
        hr.id_partido,
        hr.id_usuario,
        u.nombre_usuario,
        hr.rating_antes,
        hr.delta,
        hr.rating_despues
    FROM historial_rating hr
    LEFT JOIN usuarios u ON hr.id_usuario = u.id_usuario
    WHERE hr.id_partido IN (19, 20)
    ORDER BY hr.id_partido, hr.id_usuario
""")

result = db.execute(query_verificar)
historiales = result.fetchall()

print(f"\nHistoriales para partidos 19 y 20: {len(historiales)}\n")

partido_actual = None
for historial in historiales:
    if partido_actual != historial.id_partido:
        partido_actual = historial.id_partido
        print(f"\n--- Partido {historial.id_partido} ---")
    
    print(f"{historial.nombre_usuario} (ID: {historial.id_usuario})")
    print(f"  Rating antes: {historial.rating_antes}")
    print(f"  Delta: {historial.delta:+d}")
    print(f"  Rating después: {historial.rating_despues}")

db.close()
