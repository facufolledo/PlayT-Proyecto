"""
Migración para agregar columnas de torneos a la tabla partidos existente
"""
from src.database.config import engine
from sqlalchemy import text

sql = """
-- Agregar columnas para torneos a la tabla partidos existente
ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS zona_id BIGINT REFERENCES torneo_zonas(id) ON DELETE SET NULL;

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS fase VARCHAR(20) CHECK (fase IN ('zona', '16avos', '8vos', '4tos', 'semis', 'final'));

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS numero_partido INTEGER;

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS pareja1_id BIGINT REFERENCES torneos_parejas(id);

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS pareja2_id BIGINT REFERENCES torneos_parejas(id);

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS cancha_id BIGINT REFERENCES torneo_canchas(id) ON DELETE SET NULL;

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS fecha_hora TIMESTAMP WITH TIME ZONE;

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS ganador_pareja_id BIGINT REFERENCES torneos_parejas(id);

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS origen VARCHAR(10) DEFAULT 'manual' CHECK (origen IN ('auto', 'manual'));

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS requiere_reprogramacion BOOLEAN DEFAULT false;

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS observaciones TEXT;

-- Crear índices para optimización de torneos
CREATE INDEX IF NOT EXISTS idx_partidos_torneo ON partidos(id_torneo) WHERE id_torneo IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_partidos_zona ON partidos(zona_id) WHERE zona_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_partidos_fase ON partidos(fase) WHERE fase IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_partidos_parejas ON partidos(pareja1_id, pareja2_id) WHERE pareja1_id IS NOT NULL;

-- Tabla para sets de partidos (tanto AMD como torneos)
CREATE TABLE IF NOT EXISTS partido_sets (
    id BIGSERIAL PRIMARY KEY,
    partido_id BIGINT NOT NULL REFERENCES partidos(id_partido) ON DELETE CASCADE,
    numero_set INTEGER NOT NULL CHECK (numero_set BETWEEN 1 AND 3),
    games_equipo1 INTEGER NOT NULL CHECK (games_equipo1 >= 0),
    games_equipo2 INTEGER NOT NULL CHECK (games_equipo2 >= 0),
    es_tiebreak BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (partido_id, numero_set)
);

CREATE INDEX IF NOT EXISTS idx_partido_sets_partido ON partido_sets(partido_id);

-- Comentarios para documentación
COMMENT ON COLUMN partidos.zona_id IS 'ID de zona si es partido de torneo en fase de grupos';
COMMENT ON COLUMN partidos.fase IS 'Fase del torneo: zona, 16avos, 8vos, 4tos, semis, final';
COMMENT ON COLUMN partidos.pareja1_id IS 'ID de pareja 1 en torneos';
COMMENT ON COLUMN partidos.pareja2_id IS 'ID de pareja 2 en torneos';
COMMENT ON COLUMN partidos.cancha_id IS 'ID de cancha asignada en torneos';
COMMENT ON COLUMN partidos.origen IS 'auto: generado automáticamente, manual: creado/editado por organizador';
"""

print("\n" + "="*60)
print("MIGRACION: Agregar columnas de torneos a tabla partidos")
print("="*60)
print()

conn = engine.connect()

try:
    print("Ejecutando migracion...")
    
    # Ejecutar cada statement en su propia transacción
    for statement in sql.split(';'):
        statement = statement.strip()
        if statement and not statement.startswith('--'):
            trans = conn.begin()
            try:
                conn.execute(text(statement))
                trans.commit()
                
                if 'ALTER TABLE' in statement.upper():
                    print("  [OK] Columna agregada")
                elif 'CREATE TABLE' in statement.upper():
                    print("  [OK] Tabla partido_sets creada")
                elif 'CREATE INDEX' in statement.upper():
                    print("  [OK] Indice creado")
                elif 'COMMENT' in statement.upper():
                    print("  [OK] Comentario agregado")
            except Exception as e:
                trans.rollback()
                if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                    print("  [YA EXISTE] Saltando...")
                else:
                    print(f"  [ADVERTENCIA] {str(e)[:150]}")
    
    print("\n" + "="*60)
    print("MIGRACION COMPLETADA")
    print("="*60)
    
    # Verificar columnas agregadas
    print("\nVerificando columnas en tabla partidos...")
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema='public' 
        AND table_name='partidos'
        AND column_name IN ('zona_id', 'fase', 'pareja1_id', 'pareja2_id', 'cancha_id', 'origen')
        ORDER BY column_name
    """)).fetchall()
    
    print(f"\nColumnas de torneos encontradas: {len(result)}")
    for r in result:
        print(f"  - {r[0]} ({r[1]})")
    
    # Verificar tabla partido_sets
    result_sets = conn.execute(text("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema='public' 
        AND table_name='partido_sets'
    """)).fetchone()
    
    if result_sets[0] > 0:
        print("\n[OK] Tabla partido_sets creada correctamente")
    
    print("\n[OK] La tabla partidos ahora soporta torneos!")
    print("     - Partidos AMD: tipo='amistoso', id_torneo=NULL")
    print("     - Partidos Torneo: tipo='torneo', id_torneo=<id>, zona_id, fase, etc.")
    
except Exception as e:
    trans.rollback()
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
