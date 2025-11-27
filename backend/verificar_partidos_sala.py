"""
Script para verificar partidos creados desde salas
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
print("VERIFICANDO SALAS Y SUS PARTIDOS")
print("=" * 100)

# Consulta para obtener salas con sus partidos
query = text("""
    SELECT 
        s.id_sala,
        s.nombre,
        s.codigo_invitacion,
        s.estado,
        s.id_partido,
        s.id_creador,
        p.id_partido as partido_id,
        p.estado as partido_estado,
        p.tipo as partido_tipo,
        COUNT(DISTINCT sj.id_usuario) as num_jugadores_sala,
        COUNT(DISTINCT pj.id_usuario) as num_jugadores_partido
    FROM salas s
    LEFT JOIN partidos p ON s.id_partido = p.id_partido
    LEFT JOIN sala_jugadores sj ON s.id_sala = sj.id_sala
    LEFT JOIN partido_jugadores pj ON p.id_partido = pj.id_partido
    GROUP BY s.id_sala, s.nombre, s.codigo_invitacion, s.estado, s.id_partido, s.id_creador, 
             p.id_partido, p.estado, p.tipo
    ORDER BY s.creado_en DESC
    LIMIT 10
""")

result = db.execute(query)
salas = result.fetchall()

print(f"\nTotal de salas encontradas: {len(salas)}\n")

for sala in salas:
    print(f"--- Sala ID: {sala.id_sala} ---")
    print(f"Nombre: {sala.nombre}")
    print(f"Código: {sala.codigo_invitacion}")
    print(f"Estado: {sala.estado}")
    print(f"Jugadores en sala: {sala.num_jugadores_sala}")
    print(f"ID Partido: {sala.id_partido}")
    
    if sala.partido_id:
        print(f"✅ Tiene partido asociado:")
        print(f"   - Partido ID: {sala.partido_id}")
        print(f"   - Estado: {sala.partido_estado}")
        print(f"   - Tipo: {sala.partido_tipo}")
        print(f"   - Jugadores en partido: {sala.num_jugadores_partido}")
    else:
        print(f"❌ No tiene partido asociado")
    
    print()

# Verificar partidos que tienen id_sala
print("\n" + "=" * 100)
print("PARTIDOS CON ID_SALA")
print("=" * 100)

query_partidos = text("""
    SELECT 
        p.id_partido,
        p.id_sala,
        p.estado,
        p.tipo,
        p.fecha,
        s.nombre as sala_nombre,
        s.codigo_invitacion,
        COUNT(pj.id_usuario) as num_jugadores
    FROM partidos p
    LEFT JOIN salas s ON p.id_sala = s.id_sala
    LEFT JOIN partido_jugadores pj ON p.id_partido = pj.id_partido
    WHERE p.id_sala IS NOT NULL
    GROUP BY p.id_partido, p.id_sala, p.estado, p.tipo, p.fecha, s.nombre, s.codigo_invitacion
    ORDER BY p.fecha DESC
    LIMIT 10
""")

result = db.execute(query_partidos)
partidos = result.fetchall()

print(f"\nPartidos con id_sala: {len(partidos)}\n")

for partido in partidos:
    print(f"Partido ID: {partido.id_partido}")
    print(f"  Sala: {partido.sala_nombre} ({partido.codigo_invitacion})")
    print(f"  Estado: {partido.estado}")
    print(f"  Tipo: {partido.tipo}")
    print(f"  Jugadores: {partido.num_jugadores}")
    print()

db.close()
