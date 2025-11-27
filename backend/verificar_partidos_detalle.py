"""
Script para verificar el detalle de partidos en la base de datos
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Crear engine
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 100)
print("VERIFICANDO PARTIDOS CON RESULTADOS")
print("=" * 100)

# Consulta para obtener partidos con resultados
query = text("""
    SELECT 
        p.id_partido,
        p.fecha,
        p.estado,
        p.tipo,
        r.sets_eq1,
        r.sets_eq2,
        r.detalle_sets,
        r.confirmado,
        r.desenlace,
        COUNT(pj.id_usuario) as num_jugadores
    FROM partidos p
    LEFT JOIN resultados_partidos r ON p.id_partido = r.id_partido
    LEFT JOIN partido_jugadores pj ON p.id_partido = pj.id_partido
    WHERE p.id_partido IN (
        SELECT DISTINCT id_partido 
        FROM partido_jugadores 
        WHERE id_usuario = 14
    )
    GROUP BY p.id_partido, p.fecha, p.estado, p.tipo, r.sets_eq1, r.sets_eq2, r.detalle_sets, r.confirmado, r.desenlace
    ORDER BY p.fecha DESC
    LIMIT 10
""")

result = db.execute(query)
partidos = result.fetchall()

print(f"\nTotal de partidos encontrados: {len(partidos)}\n")

for partido in partidos:
    print(f"--- Partido ID: {partido.id_partido} ---")
    print(f"Fecha: {partido.fecha}")
    print(f"Estado: {partido.estado}")
    print(f"Tipo: {partido.tipo}")
    print(f"Jugadores: {partido.num_jugadores}")
    
    if partido.sets_eq1 is not None:
        print(f"Resultado: {partido.sets_eq1}-{partido.sets_eq2}")
        print(f"Confirmado: {partido.confirmado}")
        print(f"Desenlace: {partido.desenlace}")
        print(f"Detalle sets (raw): {partido.detalle_sets}")
        print(f"Tipo de detalle_sets: {type(partido.detalle_sets)}")
        
        # Intentar parsear si es string
        if isinstance(partido.detalle_sets, str):
            try:
                detalle_parsed = json.loads(partido.detalle_sets)
                print(f"Detalle sets (parsed): {detalle_parsed}")
            except:
                print("No se pudo parsear el JSON")
    else:
        print("Sin resultado")
    
    print()

# Verificar estructura de la tabla resultados_partidos
print("\n" + "=" * 100)
print("ESTRUCTURA DE LA TABLA resultados_partidos")
print("=" * 100)

query_estructura = text("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'resultados_partidos'
    ORDER BY ordinal_position
""")

result = db.execute(query_estructura)
columnas = result.fetchall()

for col in columnas:
    print(f"{col.column_name}: {col.data_type}")

db.close()
