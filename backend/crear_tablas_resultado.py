from src.database.config import engine
from sqlalchemy import text

# SQL para crear las tablas
sql = """
-- Tabla de resultados de pádel
CREATE TABLE IF NOT EXISTS resultados_padel (
    id_resultado BIGSERIAL PRIMARY KEY,
    id_sala VARCHAR(50) NOT NULL,
    id_creador BIGINT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    sets TEXT NOT NULL,
    ganador_equipo VARCHAR(10) NOT NULL CHECK (ganador_equipo IN ('equipo1', 'equipo2')),
    estado VARCHAR(30) NOT NULL DEFAULT 'pendiente_confirmacion' CHECK (estado IN ('pendiente_confirmacion', 'confirmado', 'rechazado')),
    confirmaciones BIGINT DEFAULT 1,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT idx_resultados_sala UNIQUE (id_sala)
);

CREATE INDEX IF NOT EXISTS idx_resultados_padel_sala ON resultados_padel(id_sala);
CREATE INDEX IF NOT EXISTS idx_resultados_padel_creador ON resultados_padel(id_creador);
CREATE INDEX IF NOT EXISTS idx_resultados_padel_estado ON resultados_padel(estado);

-- Tabla de confirmaciones de usuarios
CREATE TABLE IF NOT EXISTS confirmaciones_usuarios (
    id_confirmacion BIGSERIAL PRIMARY KEY,
    id_resultado BIGINT NOT NULL REFERENCES resultados_padel(id_resultado) ON DELETE CASCADE,
    id_usuario BIGINT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_confirmacion_usuario UNIQUE (id_resultado, id_usuario)
);

CREATE INDEX IF NOT EXISTS idx_confirmaciones_usuarios_resultado ON confirmaciones_usuarios(id_resultado);
CREATE INDEX IF NOT EXISTS idx_confirmaciones_usuarios_usuario ON confirmaciones_usuarios(id_usuario);
"""

print("🔄 Creando tablas de resultados...")
conn = engine.connect()
trans = conn.begin()

try:
    # Ejecutar cada statement
    for statement in sql.split(';'):
        statement = statement.strip()
        if statement:
            conn.execute(text(statement))
    
    trans.commit()
    print("✅ Tablas creadas exitosamente")
    
    # Verificar
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' 
        AND table_name IN ('resultados_padel', 'confirmaciones_usuarios')
    """)).fetchall()
    
    print(f"✅ Tablas verificadas: {[r[0] for r in result]}")
    
except Exception as e:
    trans.rollback()
    print(f"❌ Error: {e}")
finally:
    conn.close()
