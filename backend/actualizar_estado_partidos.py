"""
Script para actualizar el estado de partidos que tienen Elo aplicado
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
print("ACTUALIZANDO ESTADO DE PARTIDOS CON ELO APLICADO")
print("=" * 100)

# Actualizar partidos que tienen elo_aplicado = true pero estado != 'confirmado'
query_update = text("""
    UPDATE partidos
    SET estado = 'confirmado'
    WHERE elo_aplicado = true
    AND estado != 'confirmado'
    RETURNING id_partido, estado
""")

result = db.execute(query_update)
partidos_actualizados = result.fetchall()
db.commit()

print(f"\n✅ Partidos actualizados: {len(partidos_actualizados)}\n")

for partido in partidos_actualizados:
    print(f"Partido ID: {partido.id_partido} -> Estado: {partido.estado}")

# También actualizar partidos que tienen estado_confirmacion = 'confirmado' pero estado != 'confirmado'
print("\n" + "=" * 100)
print("ACTUALIZANDO PARTIDOS CON ESTADO_CONFIRMACION = 'confirmado'")
print("=" * 100)

query_update2 = text("""
    UPDATE partidos
    SET estado = 'confirmado'
    WHERE estado_confirmacion = 'confirmado'
    AND estado != 'confirmado'
    RETURNING id_partido, estado
""")

result2 = db.execute(query_update2)
partidos_actualizados2 = result2.fetchall()
db.commit()

print(f"\n✅ Partidos actualizados: {len(partidos_actualizados2)}\n")

for partido in partidos_actualizados2:
    print(f"Partido ID: {partido.id_partido} -> Estado: {partido.estado}")

# Verificar partidos confirmados
print("\n" + "=" * 100)
print("VERIFICANDO PARTIDOS CONFIRMADOS")
print("=" * 100)

query_verificar = text("""
    SELECT 
        p.id_partido,
        p.estado,
        p.estado_confirmacion,
        p.elo_aplicado,
        p.tipo,
        COUNT(pj.id_usuario) as num_jugadores
    FROM partidos p
    LEFT JOIN partido_jugadores pj ON p.id_partido = pj.id_partido
    WHERE p.estado = 'confirmado'
    GROUP BY p.id_partido, p.estado, p.estado_confirmacion, p.elo_aplicado, p.tipo
    ORDER BY p.fecha DESC
    LIMIT 10
""")

result3 = db.execute(query_verificar)
partidos_confirmados = result3.fetchall()

print(f"\nPartidos confirmados: {len(partidos_confirmados)}\n")

for partido in partidos_confirmados:
    print(f"Partido ID: {partido.id_partido}")
    print(f"  Estado: {partido.estado}")
    print(f"  Estado confirmación: {partido.estado_confirmacion}")
    print(f"  Elo aplicado: {partido.elo_aplicado}")
    print(f"  Tipo: {partido.tipo}")
    print(f"  Jugadores: {partido.num_jugadores}")
    print()

db.close()

print("\n✅ Actualización completada!")
