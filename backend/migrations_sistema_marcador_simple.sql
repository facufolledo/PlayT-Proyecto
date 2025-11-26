-- ============================================
-- MIGRACIÓN SIMPLIFICADA: Sistema de Marcador de Pádel
-- ============================================

-- 1. ACTUALIZAR TABLA PARTIDOS
ALTER TABLE partidos ADD COLUMN IF NOT EXISTS tipo VARCHAR(20) DEFAULT 'amistoso';
ALTER TABLE partidos ADD COLUMN IF NOT EXISTS id_torneo BIGINT;
ALTER TABLE partidos ADD COLUMN IF NOT EXISTS id_sala BIGINT;
ALTER TABLE partidos ADD COLUMN IF NOT EXISTS resultado_padel JSON;
ALTER TABLE partidos ADD COLUMN IF NOT EXISTS estado_confirmacion VARCHAR(30) DEFAULT 'sin_resultado';
ALTER TABLE partidos ADD COLUMN IF NOT EXISTS ganador_equipo INTEGER;
ALTER TABLE partidos ADD COLUMN IF NOT EXISTS elo_aplicado BOOLEAN DEFAULT false;
ALTER TABLE partidos ADD COLUMN IF NOT EXISTS creado_por BIGINT;

-- 2. ACTUALIZAR TABLA PARTIDO_JUGADORES
ALTER TABLE partido_jugadores ADD COLUMN IF NOT EXISTS rating_antes INTEGER;
ALTER TABLE partido_jugadores ADD COLUMN IF NOT EXISTS rating_despues INTEGER;
ALTER TABLE partido_jugadores ADD COLUMN IF NOT EXISTS cambio_elo INTEGER;

-- 3. CREAR TABLA CONFIRMACIONES
CREATE TABLE IF NOT EXISTS confirmaciones (
    id_confirmacion BIGSERIAL PRIMARY KEY,
    id_partido BIGINT NOT NULL REFERENCES partidos(id_partido) ON DELETE CASCADE,
    id_usuario BIGINT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('confirmacion', 'reporte')),
    motivo TEXT,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_confirmacion_por_usuario UNIQUE(id_partido, id_usuario)
);

-- 4. CREAR TABLA HISTORIAL_ENFRENTAMIENTOS
CREATE TABLE IF NOT EXISTS historial_enfrentamientos (
    id_historial BIGSERIAL PRIMARY KEY,
    id_partido BIGINT NOT NULL REFERENCES partidos(id_partido) ON DELETE CASCADE,
    fecha TIMESTAMP WITH TIME ZONE NOT NULL,
    jugador1_id BIGINT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    jugador2_id BIGINT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    jugador3_id BIGINT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    jugador4_id BIGINT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    hash_trio_1 VARCHAR(64) NOT NULL,
    hash_trio_2 VARCHAR(64) NOT NULL,
    hash_trio_3 VARCHAR(64) NOT NULL,
    hash_trio_4 VARCHAR(64) NOT NULL,
    tipo_partido VARCHAR(20) NOT NULL,
    elo_aplicado BOOLEAN DEFAULT false
);

-- 5. CREAR ÍNDICES
CREATE INDEX IF NOT EXISTS idx_partidos_tipo ON partidos(tipo);
CREATE INDEX IF NOT EXISTS idx_partidos_estado_confirmacion ON partidos(estado_confirmacion);
CREATE INDEX IF NOT EXISTS idx_partidos_elo_aplicado ON partidos(elo_aplicado);
CREATE INDEX IF NOT EXISTS idx_confirmaciones_partido ON confirmaciones(id_partido);
CREATE INDEX IF NOT EXISTS idx_confirmaciones_usuario ON confirmaciones(id_usuario);
CREATE INDEX IF NOT EXISTS idx_hist_hash_trio_1_fecha ON historial_enfrentamientos(hash_trio_1, fecha);
CREATE INDEX IF NOT EXISTS idx_hist_hash_trio_2_fecha ON historial_enfrentamientos(hash_trio_2, fecha);
CREATE INDEX IF NOT EXISTS idx_hist_hash_trio_3_fecha ON historial_enfrentamientos(hash_trio_3, fecha);
CREATE INDEX IF NOT EXISTS idx_hist_hash_trio_4_fecha ON historial_enfrentamientos(hash_trio_4, fecha);
CREATE INDEX IF NOT EXISTS idx_hist_fecha ON historial_enfrentamientos(fecha);
