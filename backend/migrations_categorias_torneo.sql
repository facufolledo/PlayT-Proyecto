-- Migracion: Sistema de Categorias en Torneos
-- Permite que un torneo tenga multiples categorias

CREATE TABLE IF NOT EXISTS torneo_categorias (
    id BIGSERIAL PRIMARY KEY,
    torneo_id BIGINT NOT NULL REFERENCES torneos(id) ON DELETE CASCADE,
    nombre VARCHAR(50) NOT NULL,
    genero VARCHAR(20) DEFAULT 'masculino',
    max_parejas INTEGER DEFAULT 16,
    estado VARCHAR(30) DEFAULT 'inscripcion',
    orden INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_torneo_categorias_torneo ON torneo_categorias(torneo_id);
CREATE INDEX IF NOT EXISTS idx_torneo_categorias_estado ON torneo_categorias(estado);

ALTER TABLE torneos_parejas ADD COLUMN IF NOT EXISTS categoria_id BIGINT REFERENCES torneo_categorias(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_torneos_parejas_categoria ON torneos_parejas(categoria_id);

ALTER TABLE torneo_zonas ADD COLUMN IF NOT EXISTS categoria_id BIGINT REFERENCES torneo_categorias(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_torneo_zonas_categoria ON torneo_zonas(categoria_id);

ALTER TABLE partidos ADD COLUMN IF NOT EXISTS categoria_id BIGINT;
CREATE INDEX IF NOT EXISTS idx_partidos_categoria ON partidos(categoria_id);

SELECT 'Tabla torneo_categorias creada' as info;