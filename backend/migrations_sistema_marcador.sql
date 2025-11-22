-- ============================================
-- MIGRACIÓN: Sistema de Marcador de Pádel
-- Versión: 1.0
-- Fecha: 2024-11-21
-- ============================================

-- ============================================
-- 1. ACTUALIZAR TABLA PARTIDOS
-- ============================================

ALTER TABLE partidos 
ADD COLUMN IF NOT EXISTS tipo VARCHAR(20) DEFAULT 'amistoso',
ADD COLUMN IF NOT EXISTS id_torneo BIGINT,
ADD COLUMN IF NOT EXISTS id_sala BIGINT,
ADD COLUMN IF NOT EXISTS resultado_padel JSON,
ADD COLUMN IF NOT EXISTS estado_confirmacion VARCHAR(30) DEFAULT 'sin_resultado',
ADD COLUMN IF NOT EXISTS ganador_equipo INTEGER,
ADD COLUMN IF NOT EXISTS elo_aplicado BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS creado_por BIGINT;

-- Agregar constraints
ALTER TABLE partidos 
ADD CONSTRAINT fk_partido_torneo FOREIGN KEY (id_torneo) REFERENCES torneos(id_torneo) ON DELETE SET NULL,
ADD CONSTRAINT fk_partido_sala FOREIGN KEY (id_sala) REFERENCES salas(id_sala) ON DELETE SET NULL,
ADD CONSTRAINT fk_partido_creador FOREIGN KEY (creado_por) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
ADD CONSTRAINT chk_tipo_partido CHECK (tipo IN ('amistoso', 'torneo', 'ranking')),
ADD CONSTRAINT chk_estado_confirmacion CHECK (estado_confirmacion IN ('sin_resultado', 'pendiente_confirmacion', 'confirmado', 'disputado', 'auto_confirmado')),
ADD CONSTRAINT chk_ganador_equipo CHECK (ganador_equipo IN (1, 2));

-- Índices
CREATE INDEX IF NOT EXISTS idx_partidos_tipo ON partidos(tipo);
CREATE INDEX IF NOT EXISTS idx_partidos_estado_confirmacion ON partidos(estado_confirmacion);
CREATE INDEX IF NOT EXISTS idx_partidos_elo_aplicado ON partidos(elo_aplicado);
CREATE INDEX IF NOT EXISTS idx_partidos_fecha ON partidos(fecha);

-- Comentarios
COMMENT ON COLUMN partidos.tipo IS 'Tipo de partido: amistoso, torneo, ranking';
COMMENT ON COLUMN partidos.resultado_padel IS 'JSON con resultado completo (sets, games, supertiebreak)';
COMMENT ON COLUMN partidos.estado_confirmacion IS 'Estado: sin_resultado, pendiente_confirmacion, confirmado, disputado, auto_confirmado';
COMMENT ON COLUMN partidos.ganador_equipo IS 'Equipo ganador: 1 o 2';
COMMENT ON COLUMN partidos.elo_aplicado IS 'Indica si ya se aplicó el cálculo de Elo';

-- ============================================
-- 2. ACTUALIZAR TABLA PARTIDO_JUGADORES
-- ============================================

ALTER TABLE partido_jugadores
ADD COLUMN IF NOT EXISTS rating_antes INTEGER,
ADD COLUMN IF NOT EXISTS rating_despues INTEGER,
ADD COLUMN IF NOT EXISTS cambio_elo INTEGER;

-- Índices
CREATE INDEX IF NOT EXISTS idx_partido_jugadores_usuario ON partido_jugadores(id_usuario);
CREATE INDEX IF NOT EXISTS idx_partido_jugadores_equipo ON partido_jugadores(equipo);

-- Comentarios
COMMENT ON COLUMN partido_jugadores.rating_antes IS 'Rating del jugador antes del partido';
COMMENT ON COLUMN partido_jugadores.rating_despues IS 'Rating del jugador después del partido';
COMMENT ON COLUMN partido_jugadores.cambio_elo IS 'Cambio de Elo (+/-)';

-- ============================================
-- 3. CREAR TABLA CONFIRMACIONES
-- ============================================

CREATE TABLE IF NOT EXISTS confirmaciones (
    id_confirmacion BIGSERIAL PRIMARY KEY,
    id_partido BIGINT NOT NULL REFERENCES partidos(id_partido) ON DELETE CASCADE,
    id_usuario BIGINT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('confirmacion', 'reporte')),
    motivo TEXT,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_confirmacion_por_usuario UNIQUE(id_partido, id_usuario)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_confirmaciones_partido ON confirmaciones(id_partido);
CREATE INDEX IF NOT EXISTS idx_confirmaciones_usuario ON confirmaciones(id_usuario);
CREATE INDEX IF NOT EXISTS idx_confirmaciones_tipo ON confirmaciones(tipo);
CREATE INDEX IF NOT EXISTS idx_confirmaciones_fecha ON confirmaciones(fecha);

-- Comentarios
COMMENT ON TABLE confirmaciones IS 'Registro de confirmaciones y reportes de resultados de partidos amistosos';
COMMENT ON COLUMN confirmaciones.tipo IS 'Tipo de acción: confirmacion o reporte';
COMMENT ON COLUMN confirmaciones.motivo IS 'Motivo del reporte (solo para tipo=reporte)';

-- ============================================
-- 4. CREAR TABLA HISTORIAL_ENFRENTAMIENTOS
-- Sistema Anti-Trampa
-- ============================================

CREATE TABLE IF NOT EXISTS historial_enfrentamientos (
    id_historial BIGSERIAL PRIMARY KEY,
    id_partido BIGINT NOT NULL REFERENCES partidos(id_partido) ON DELETE CASCADE,
    fecha TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Los 4 jugadores (ordenados por ID)
    jugador1_id BIGINT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    jugador2_id BIGINT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    jugador3_id BIGINT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    jugador4_id BIGINT NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    
    -- Hashes de todas las combinaciones de 3 jugadores
    hash_trio_1 VARCHAR(64) NOT NULL, -- jugadores 1,2,3
    hash_trio_2 VARCHAR(64) NOT NULL, -- jugadores 1,2,4
    hash_trio_3 VARCHAR(64) NOT NULL, -- jugadores 1,3,4
    hash_trio_4 VARCHAR(64) NOT NULL, -- jugadores 2,3,4
    
    tipo_partido VARCHAR(20) NOT NULL,
    elo_aplicado BOOLEAN DEFAULT false,
    
    CONSTRAINT chk_jugadores_diferentes CHECK (
        jugador1_id != jugador2_id AND 
        jugador1_id != jugador3_id AND 
        jugador1_id != jugador4_id AND
        jugador2_id != jugador3_id AND 
        jugador2_id != jugador4_id AND 
        jugador3_id != jugador4_id
    )
);

-- Índices para búsquedas rápidas de anti-trampa
CREATE INDEX IF NOT EXISTS idx_hist_hash_trio_1_fecha ON historial_enfrentamientos(hash_trio_1, fecha);
CREATE INDEX IF NOT EXISTS idx_hist_hash_trio_2_fecha ON historial_enfrentamientos(hash_trio_2, fecha);
CREATE INDEX IF NOT EXISTS idx_hist_hash_trio_3_fecha ON historial_enfrentamientos(hash_trio_3, fecha);
CREATE INDEX IF NOT EXISTS idx_hist_hash_trio_4_fecha ON historial_enfrentamientos(hash_trio_4, fecha);
CREATE INDEX IF NOT EXISTS idx_hist_partido ON historial_enfrentamientos(id_partido);
CREATE INDEX IF NOT EXISTS idx_hist_fecha ON historial_enfrentamientos(fecha);

-- Comentarios
COMMENT ON TABLE historial_enfrentamientos IS 'Tracking de enfrentamientos para sistema anti-trampa (máx 2 partidos/semana por trío)';
COMMENT ON COLUMN historial_enfrentamientos.hash_trio_1 IS 'Hash MD5 de jugadores 1,2,3 ordenados';
COMMENT ON COLUMN historial_enfrentamientos.hash_trio_2 IS 'Hash MD5 de jugadores 1,2,4 ordenados';
COMMENT ON COLUMN historial_enfrentamientos.hash_trio_3 IS 'Hash MD5 de jugadores 1,3,4 ordenados';
COMMENT ON COLUMN historial_enfrentamientos.hash_trio_4 IS 'Hash MD5 de jugadores 2,3,4 ordenados';

-- ============================================
-- 5. FUNCIÓN AUXILIAR: Generar hash de trío
-- ============================================

CREATE OR REPLACE FUNCTION generar_hash_trio(j1 BIGINT, j2 BIGINT, j3 BIGINT)
RETURNS VARCHAR(64) AS $$
DECLARE
    jugadores_ordenados BIGINT[];
    hash_result VARCHAR(64);
BEGIN
    -- Ordenar los 3 jugadores
    jugadores_ordenados := ARRAY[j1, j2, j3];
    jugadores_ordenados := ARRAY(SELECT unnest(jugadores_ordenados) ORDER BY 1);
    
    -- Generar hash MD5
    hash_result := MD5(jugadores_ordenados::TEXT);
    
    RETURN hash_result;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================
-- 6. VERIFICACIÓN DE INSTALACIÓN
-- ============================================

-- Verificar campos en partidos
SELECT 
    'partidos' as tabla,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'partidos'
AND column_name IN ('tipo', 'resultado_padel', 'estado_confirmacion', 'ganador_equipo', 'elo_aplicado')
ORDER BY column_name;

-- Verificar campos en partido_jugadores
SELECT 
    'partido_jugadores' as tabla,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'partido_jugadores'
AND column_name IN ('rating_antes', 'rating_despues', 'cambio_elo')
ORDER BY column_name;

-- Verificar tabla confirmaciones
SELECT 
    'confirmaciones' as tabla,
    COUNT(*) as total_columnas
FROM information_schema.columns
WHERE table_name = 'confirmaciones';

-- Verificar tabla historial_enfrentamientos
SELECT 
    'historial_enfrentamientos' as tabla,
    COUNT(*) as total_columnas
FROM information_schema.columns
WHERE table_name = 'historial_enfrentamientos';

-- Verificar índices creados
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('partidos', 'partido_jugadores', 'confirmaciones', 'historial_enfrentamientos')
ORDER BY tablename, indexname;

-- ============================================
-- FIN DE MIGRACIÓN
-- ============================================

-- Resumen:
-- ✅ Tabla partidos actualizada (tipo, resultado, confirmación, Elo)
-- ✅ Tabla partido_jugadores actualizada (tracking de rating)
-- ✅ Tabla confirmaciones creada
-- ✅ Tabla historial_enfrentamientos creada (anti-trampa)
-- ✅ Función auxiliar generar_hash_trio creada
-- ✅ Índices optimizados
-- ✅ Constraints de validación


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

COMMENT ON TABLE resultados_padel IS 'Resultados de partidos de pádel con sistema de confirmación';

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

COMMENT ON TABLE confirmaciones_usuarios IS 'Confirmaciones de usuarios para resultados de pádel';
