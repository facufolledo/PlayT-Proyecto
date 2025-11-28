from src.database.config import engine
from sqlalchemy import text

conn = engine.connect()
trans = conn.begin()

try:
    print("Agregando columna zona_id a tabla partidos...")
    conn.execute(text("""
        ALTER TABLE partidos 
        ADD COLUMN zona_id BIGINT REFERENCES torneo_zonas(id) ON DELETE SET NULL
    """))
    trans.commit()
    print("[OK] Columna zona_id agregada")
    
    # Crear índice
    trans = conn.begin()
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_partidos_zona 
        ON partidos(zona_id) 
        WHERE zona_id IS NOT NULL
    """))
    trans.commit()
    print("[OK] Indice idx_partidos_zona creado")
    
    # Crear tabla partido_sets si no existe
    trans = conn.begin()
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS partido_sets (
            id BIGSERIAL PRIMARY KEY,
            partido_id BIGINT NOT NULL REFERENCES partidos(id_partido) ON DELETE CASCADE,
            numero_set INTEGER NOT NULL CHECK (numero_set BETWEEN 1 AND 3),
            games_equipo1 INTEGER NOT NULL CHECK (games_equipo1 >= 0),
            games_equipo2 INTEGER NOT NULL CHECK (games_equipo2 >= 0),
            es_tiebreak BOOLEAN DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (partido_id, numero_set)
        )
    """))
    trans.commit()
    print("[OK] Tabla partido_sets creada")
    
    trans = conn.begin()
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_partido_sets_partido 
        ON partido_sets(partido_id)
    """))
    trans.commit()
    print("[OK] Indice idx_partido_sets_partido creado")
    
except Exception as e:
    trans.rollback()
    if 'already exists' in str(e).lower():
        print("[YA EXISTE]")
    else:
        print(f"[ERROR] {e}")
finally:
    conn.close()

print("\n[OK] Migracion completada!")
