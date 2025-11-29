from src.database.config import engine
from sqlalchemy import text

conn = engine.connect()

print("\nColumnas actuales en tabla partidos:")
result = conn.execute(text("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name='partidos'
    ORDER BY ordinal_position
""")).fetchall()

for r in result:
    print(f"  - {r[0]:<30} ({r[1]})")

print("\n\nColumnas necesarias para torneos:")
columnas_necesarias = [
    'zona_id', 'fase', 'numero_partido', 'pareja1_id', 'pareja2_id',
    'cancha_id', 'fecha_hora', 'ganador_pareja_id', 'origen',
    'requiere_reprogramacion', 'observaciones'
]

result2 = conn.execute(text(f"""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name='partidos'
    AND column_name IN ('{"','".join(columnas_necesarias)}')
""")).fetchall()

existentes = [r[0] for r in result2]
faltantes = [c for c in columnas_necesarias if c not in existentes]

print(f"\nExistentes: {len(existentes)}/{len(columnas_necesarias)}")
for c in existentes:
    print(f"  [OK] {c}")

if faltantes:
    print(f"\nFaltantes: {len(faltantes)}")
    for c in faltantes:
        print(f"  [X] {c}")

conn.close()
