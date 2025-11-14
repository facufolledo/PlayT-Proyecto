-- Migraciones para el algoritmo Elo avanzado
-- Ejecutar estas migraciones para habilitar todas las nuevas funcionalidades

-- === NUEVOS CAMPOS PARA USUARIOS ===

-- Agregar campo de volatilidad (confianza del rating)
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS volatilidad REAL DEFAULT 1.0;

-- Agregar campo de último partido para calcular inactividad
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS ultimo_partido_at TIMESTAMPTZ;

-- Agregar campo de categoría sugerida basada en rating
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS categoria_sugerida VARCHAR(10);

-- === NUEVOS CAMPOS PARA PARTIDOS ===

-- Agregar tipo de partido (amistoso, torneo, final)
ALTER TABLE partidos ADD COLUMN IF NOT EXISTS tipo VARCHAR(20) DEFAULT 'torneo';

-- Agregar campo para detalles de sets (JSON)
ALTER TABLE partidos ADD COLUMN IF NOT EXISTS detalle_sets JSONB;

-- Agregar campo para desenlace específico
ALTER TABLE partidos ADD COLUMN IF NOT EXISTS desenlace VARCHAR(20) DEFAULT 'normal';

-- Agregar campo para flag de abuso
ALTER TABLE partidos ADD COLUMN IF NOT EXISTS flag_abuso BOOLEAN DEFAULT FALSE;

-- === NUEVOS CAMPOS PARA ELO_HISTORY ===

-- Agregar campo de volatilidad en el historial
ALTER TABLE elo_history ADD COLUMN IF NOT EXISTS volatilidad_anterior REAL DEFAULT 1.0;
ALTER TABLE elo_history ADD COLUMN IF NOT EXISTS volatilidad_nueva REAL DEFAULT 1.0;

-- Agregar campo de factor K aplicado
ALTER TABLE elo_history ADD COLUMN IF NOT EXISTS factor_k_aplicado REAL;

-- Agregar campo de multiplicadores aplicados
ALTER TABLE elo_history ADD COLUMN IF NOT EXISTS multiplicador_sets REAL DEFAULT 1.0;
ALTER TABLE elo_history ADD COLUMN IF NOT EXISTS bonus_dominante REAL DEFAULT 0.0;
ALTER TABLE elo_history ADD COLUMN IF NOT EXISTS reduccion_tiebreak REAL DEFAULT 1.0;

-- Agregar campo de suavizador aplicado
ALTER TABLE elo_history ADD COLUMN IF NOT EXISTS suavizador_aplicado REAL DEFAULT 1.0;

-- Agregar campo de caps aplicados
ALTER TABLE elo_history ADD COLUMN IF NOT EXISTS cap_win REAL;
ALTER TABLE elo_history ADD COLUMN IF NOT EXISTS cap_loss REAL;

-- Agregar campo de tipo de partido
ALTER TABLE elo_history ADD COLUMN IF NOT EXISTS tipo_partido VARCHAR(20) DEFAULT 'torneo';

-- Agregar campo de desenlace
ALTER TABLE elo_history ADD COLUMN IF NOT EXISTS desenlace VARCHAR(20) DEFAULT 'normal';

-- Agregar campo de flag de abuso
ALTER TABLE elo_history ADD COLUMN IF NOT EXISTS flag_abuso BOOLEAN DEFAULT FALSE;

-- === ÍNDICES PARA OPTIMIZACIÓN ===

-- Índice para búsqueda por fecha de último partido
CREATE INDEX IF NOT EXISTS idx_usuarios_ultimo_partido ON usuarios(ultimo_partido_at);

-- Índice para búsqueda por tipo de partido
CREATE INDEX IF NOT EXISTS idx_partidos_tipo ON partidos(tipo);

-- Índice para búsqueda por desenlace
CREATE INDEX IF NOT EXISTS idx_partidos_desenlace ON partidos(desenlace);

-- Índice para búsqueda por fecha y jugadores (anti-abuso)
CREATE INDEX IF NOT EXISTS idx_partidos_fecha_jugadores ON partidos(fecha, jugador1_id, jugador2_id, jugador3_id, jugador4_id);

-- === FUNCIONES UTILITARIAS ===

-- Función para actualizar categoría sugerida basada en rating
CREATE OR REPLACE FUNCTION actualizar_categoria_sugerida()
RETURNS TRIGGER AS $$
BEGIN
    -- Actualizar categoría sugerida basada en el nuevo rating
    NEW.categoria_sugerida = CASE
        WHEN NEW.rating >= 1600 THEN 'Libre'
        WHEN NEW.rating >= 1400 THEN '4ta'
        WHEN NEW.rating >= 1200 THEN '5ta'
        WHEN NEW.rating >= 1050 THEN '6ta'
        WHEN NEW.rating >= 900 THEN '7ma'
        WHEN NEW.rating >= 700 THEN '8va'
        ELSE '9na'
    END;
    
    -- Actualizar fecha de último partido
    NEW.ultimo_partido_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar categoría automáticamente
DROP TRIGGER IF EXISTS trigger_actualizar_categoria ON usuarios;
CREATE TRIGGER trigger_actualizar_categoria
    BEFORE UPDATE ON usuarios
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_categoria_sugerida();

-- Función para calcular decay por inactividad
CREATE OR REPLACE FUNCTION calcular_decay_inactividad(p_ultimo_partido TIMESTAMPTZ)
RETURNS REAL AS $$
DECLARE
    meses_inactivo REAL;
    decay_factor REAL;
BEGIN
    -- Calcular meses de inactividad
    meses_inactivo = EXTRACT(EPOCH FROM (NOW() - p_ultimo_partido)) / (30 * 24 * 3600);
    
    -- Aplicar decay (0.5% por mes, máximo 5%)
    decay_factor = LEAST(meses_inactivo * 0.005, 0.05);
    
    RETURN 1.0 - decay_factor;
END;
$$ LANGUAGE plpgsql;

-- Función para verificar abuso de partidos repetidos
CREATE OR REPLACE FUNCTION verificar_abuso_partidos(
    p_jugador1_id INTEGER,
    p_jugador2_id INTEGER,
    p_jugador3_id INTEGER,
    p_jugador4_id INTEGER,
    p_fecha TIMESTAMPTZ
)
RETURNS BOOLEAN AS $$
DECLARE
    partidos_repetidos INTEGER;
    ventana_inicio TIMESTAMPTZ;
BEGIN
    -- Ventana de 48 horas hacia atrás
    ventana_inicio := p_fecha - INTERVAL '48 hours';
    
    -- Contar partidos con los mismos 4 jugadores en la ventana
    SELECT COUNT(*)
    INTO partidos_repetidos
    FROM partidos
    WHERE fecha >= ventana_inicio
      AND fecha < p_fecha
      AND (
          (jugador1_id = p_jugador1_id AND jugador2_id = p_jugador2_id AND 
           jugador3_id = p_jugador3_id AND jugador4_id = p_jugador4_id)
        OR
          (jugador1_id = p_jugador3_id AND jugador2_id = p_jugador4_id AND 
           jugador3_id = p_jugador1_id AND jugador4_id = p_jugador2_id)
      );
    
    -- Retornar true si hay 3 o más partidos repetidos
    RETURN partidos_repetidos >= 3;
END;
$$ LANGUAGE plpgsql;

-- === VISTAS ÚTILES ===

-- Vista para rankings con decay por inactividad
CREATE OR REPLACE VIEW ranking_con_decay AS
SELECT 
    u.id,
    u.nombre,
    u.apellido,
    u.rating,
    u.volatilidad,
    u.categoria_sugerida,
    u.ultimo_partido_at,
    calcular_decay_inactividad(u.ultimo_partido_at) as factor_decay,
    ROUND(u.rating * calcular_decay_inactividad(u.ultimo_partido_at)) as rating_ajustado
FROM usuarios u
WHERE u.rating IS NOT NULL
ORDER BY rating_ajustado DESC;

-- Vista para partidos sospechosos de abuso
CREATE OR REPLACE VIEW partidos_sospechosos AS
SELECT 
    p.id,
    p.fecha,
    p.jugador1_id,
    p.jugador2_id,
    p.jugador3_id,
    p.jugador4_id,
    p.tipo,
    p.desenlace,
    verificar_abuso_partidos(p.jugador1_id, p.jugador2_id, p.jugador3_id, p.jugador4_id, p.fecha) as es_sospechoso
FROM partidos p
WHERE verificar_abuso_partidos(p.jugador1_id, p.jugador2_id, p.jugador3_id, p.jugador4_id, p.fecha) = true;

-- === DATOS INICIALES ===

-- Actualizar categorías sugeridas para usuarios existentes
UPDATE usuarios 
SET categoria_sugerida = CASE
    WHEN rating >= 1600 THEN 'Libre'
    WHEN rating >= 1400 THEN '4ta'
    WHEN rating >= 1200 THEN '5ta'
    WHEN rating >= 1050 THEN '6ta'
    WHEN rating >= 900 THEN '7ma'
    WHEN rating >= 700 THEN '8va'
    ELSE '9na'
END
WHERE rating IS NOT NULL;

-- === COMENTARIOS ===

COMMENT ON COLUMN usuarios.volatilidad IS 'Factor de volatilidad del rating (0.7-1.3). Valores bajos = más estable, valores altos = más volátil';
COMMENT ON COLUMN usuarios.ultimo_partido_at IS 'Fecha del último partido jugado para calcular inactividad';
COMMENT ON COLUMN usuarios.categoria_sugerida IS 'Categoría sugerida basada en el rating actual';
COMMENT ON COLUMN partidos.tipo IS 'Tipo de partido: amistoso, torneo, final';
COMMENT ON COLUMN partidos.detalle_sets IS 'Detalles de cada set en formato JSON: [{"games_a": 6, "games_b": 4}, ...]';
COMMENT ON COLUMN partidos.desenlace IS 'Desenlace del partido: normal, wo_eq1, wo_eq2, ret_eq1, ret_eq2';
COMMENT ON COLUMN partidos.flag_abuso IS 'Flag que indica si se detectó patrón de abuso en este partido';

