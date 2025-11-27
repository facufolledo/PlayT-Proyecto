"""
Script de migración para unificar resultados
Migra todos los resultados de resultado_padel (JSON) a la tabla resultados_partidos
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import json

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 100)
print("MIGRACIÓN: UNIFICAR RESULTADOS")
print("=" * 100)

# 1. Buscar partidos con resultado_padel pero sin entrada en resultados_partidos
query_partidos = text("""
    SELECT 
        p.id_partido,
        p.resultado_padel,
        p.ganador_equipo,
        p.creado_por,
        p.creado_en
    FROM partidos p
    LEFT JOIN resultados_partidos r ON p.id_partido = r.id_partido
    WHERE p.resultado_padel IS NOT NULL
    AND r.id_partido IS NULL
    ORDER BY p.id_partido
""")

result = db.execute(query_partidos)
partidos_migrar = result.fetchall()

print(f"\n📊 Partidos a migrar: {len(partidos_migrar)}\n")

if len(partidos_migrar) == 0:
    print("✅ No hay partidos para migrar")
    db.close()
    exit(0)

migrados = 0
errores = 0

for partido in partidos_migrar:
    try:
        print(f"\n--- Migrando Partido {partido.id_partido} ---")
        
        resultado_padel = partido.resultado_padel
        
        # Extraer información del JSON
        sets_data = resultado_padel.get('sets', [])
        ganador = resultado_padel.get('ganador', '')
        
        # Contar sets ganados por cada equipo
        sets_eq1 = 0
        sets_eq2 = 0
        detalle_sets = []
        
        for idx, set_info in enumerate(sets_data, 1):
            games_eq1 = set_info.get('gamesEquipoA', 0)
            games_eq2 = set_info.get('gamesEquipoB', 0)
            
            # Contar sets ganados
            if games_eq1 > games_eq2:
                sets_eq1 += 1
            elif games_eq2 > games_eq1:
                sets_eq2 += 1
            
            # Formato unificado
            detalle_set = {
                "set": idx,
                "juegos_eq1": games_eq1,
                "juegos_eq2": games_eq2
            }
            
            # Agregar tiebreak si existe
            if 'tiebreakEquipoA' in set_info and set_info['tiebreakEquipoA'] is not None:
                detalle_set["tiebreak_eq1"] = set_info['tiebreakEquipoA']
                detalle_set["tiebreak_eq2"] = set_info.get('tiebreakEquipoB')
            
            detalle_sets.append(detalle_set)
        
        print(f"  Sets: {sets_eq1}-{sets_eq2}")
        print(f"  Detalle: {json.dumps(detalle_sets, indent=2)}")
        
        # Insertar en resultados_partidos
        query_insert = text("""
            INSERT INTO resultados_partidos 
            (id_partido, id_reportador, sets_eq1, sets_eq2, detalle_sets, confirmado, desenlace, creado_en)
            VALUES 
            (:id_partido, :id_reportador, :sets_eq1, :sets_eq2, CAST(:detalle_sets AS jsonb), :confirmado, :desenlace, :creado_en)
        """)
        
        db.execute(query_insert, {
            'id_partido': partido.id_partido,
            'id_reportador': partido.creado_por,
            'sets_eq1': sets_eq1,
            'sets_eq2': sets_eq2,
            'detalle_sets': json.dumps(detalle_sets),
            'confirmado': True,  # Ya están confirmados si tienen elo_aplicado
            'desenlace': 'normal',
            'creado_en': partido.creado_en
        })
        
        print(f"  ✅ Migrado exitosamente")
        migrados += 1
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        errores += 1
        db.rollback()
        continue

db.commit()

print("\n" + "=" * 100)
print("RESUMEN DE MIGRACIÓN")
print("=" * 100)
print(f"✅ Migrados exitosamente: {migrados}")
print(f"❌ Errores: {errores}")

# 2. Verificar migración
print("\n" + "=" * 100)
print("VERIFICACIÓN POST-MIGRACIÓN")
print("=" * 100)

query_verificar = text("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN r.id_partido IS NOT NULL THEN 1 END) as con_resultado_tabla,
        COUNT(CASE WHEN p.resultado_padel IS NOT NULL THEN 1 END) as con_resultado_json
    FROM partidos p
    LEFT JOIN resultados_partidos r ON p.id_partido = r.id_partido
    WHERE p.estado IN ('confirmado', 'finalizado')
""")

result = db.execute(query_verificar)
stats = result.fetchone()

print(f"\nPartidos confirmados/finalizados: {stats.total}")
print(f"Con entrada en resultados_partidos: {stats.con_resultado_tabla}")
print(f"Con resultado_padel (JSON): {stats.con_resultado_json}")

if stats.con_resultado_tabla == stats.total:
    print("\n✅ MIGRACIÓN COMPLETA - Todos los partidos tienen entrada en resultados_partidos")
else:
    print(f"\n⚠️  Faltan {stats.total - stats.con_resultado_tabla} partidos por migrar")

db.close()
