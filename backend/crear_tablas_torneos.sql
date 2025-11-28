-- ============================================
-- SISTEMA DE TORNEOS CLÁSICO - PLAYT
-- PostgreSQL / Neon
-- ============================================

-- 1. Organizadores autorizados (pueden crear torneos)
CREATE TABLE IF NOT EXISTS organizadores_autorizados (
    user_id BIGINT PRIMARY KEY,
    autorizado_por BIGINT,
    fecha_autorizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT true,
    FOREIGN KEY (user_id) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (autorizado_por) REFERENCES usuarios(id_usuario)
);

-- 2. Torneos
CREATE TABLE IF NOT EXISTS torneos (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(20) DEFAULT 'clasico' CHECK (tipo IN ('clasico')),
    categoria VARCHAR(50) NOT NULL,
    estado VARCHAR(30) DEFAULT 'inscripcion' CHECK (estado IN ('inscripcion', 'armando_zonas', 'fase_grupos', 'fase_eliminacion', 'finalizado')),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    lugar VARCHAR(255),
    reglas_json JSONB,
    creado_por BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creado_por) REFERENCES usuarios(id_usuario)
);

-- 3. Organizadores del torneo (owner + colaboradores)
CREATE TABLE IF NOT EXISTS torneos_organizadores (
    id BIGSERIAL PRIMARY KEY,
    torneo_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    rol VARCHAR(20) DEFAULT 'colaborador' CHECK (rol IN ('owner', 'colaborador')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (torneo_id, user_id),
    FOREIGN KEY (torneo_id) REFERENCES torneos(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- 4. Parejas inscritas en el torneo
CREATE TABLE IF NOT EXISTS torneos_parejas (
    id BIGSERIAL PRIMARY KEY,
    torneo_id BIGINT NOT NULL,
    jugador1_id BIGINT NOT NULL,
    jugador2_id BIGINT NOT NULL,
    estado VARCHAR(20) DEFAULT 'inscripta' CHECK (estado IN ('inscripta', 'confirmada', 'baja')),
    categoria_asignada VARCHAR(50),
    observaciones TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (torneo_id) REFERENCES torneos(id) ON DELETE CASCADE,
    FOREIGN KEY (jugador1_id) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (jugador2_id) REFERENCES usuarios(id_usuario)
);

-- 5. Zonas del torneo
CREATE TABLE IF NOT EXISTS torneo_zonas (
    id BIGSERIAL PRIMARY KEY,
    torneo_id BIGINT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    numero_orden INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (torneo_id) REFERENCES torneos(id) ON DELETE CASCADE
);

-- 6. Parejas asignadas a cada zona
CREATE TABLE IF NOT EXISTS torneo_zona_parejas (
    id BIGSERIAL PRIMARY KEY,
    zona_id BIGINT NOT NULL,
    pareja_id BIGINT NOT NULL,
    posicion_final INTEGER,
    clasificado BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (zona_id, pareja_id),
    FOREIGN KEY (zona_id) REFERENCES torneo_zonas(id) ON DELETE CASCADE,
    FOREIGN KEY (pareja_id) REFERENCES torneos_parejas(id) ON DELETE CASCADE
);

-- 7. Canchas disponibles para el torneo
CREATE TABLE IF NOT EXISTS torneo_canchas (
    id BIGSERIAL PRIMARY KEY,
    torneo_id BIGINT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    activa BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (torneo_id) REFERENCES torneos(id) ON DELETE CASCADE
);

-- 8. Slots de horarios disponibles
CREATE TABLE IF NOT EXISTS torneo_slots (
    id BIGSERIAL PRIMARY KEY,
    torneo_id BIGINT NOT NULL,
    cancha_id BIGINT NOT NULL,
    fecha_hora_inicio TIMESTAMP WITH TIME ZONE NOT NULL,
    fecha_hora_fin TIMESTAMP WITH TIME ZONE NOT NULL,
    ocupado BOOLEAN DEFAULT false,
    partido_id BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (torneo_id) REFERENCES torneos(id) ON DELETE CASCADE,
    FOREIGN KEY (cancha_id) REFERENCES torneo_canchas(id) ON DELETE CASCADE
);

-- 9. Restricciones horarias de jugadores
CREATE TABLE IF NOT EXISTS torneo_bloqueos_jugador (
    id BIGSERIAL PRIMARY KEY,
    torneo_id BIGINT NOT NULL,
    jugador_id BIGINT NOT NULL,
    fecha DATE NOT NULL,
    hora_desde TIME NOT NULL,
    hora_hasta TIME NOT NULL,
    motivo VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (torneo_id) REFERENCES torneos(id) ON DELETE CASCADE,
    FOREIGN KEY (jugador_id) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- NOTA: Los partidos de torneo se guardan en la tabla 'partidos' existente
-- con tipo='torneo' y las columnas adicionales: zona_id, fase, pareja1_id, pareja2_id, etc.
-- Ver migración: migrar_partidos_torneos.py

-- 12. Tabla de posiciones por zona (se calcula dinámicamente pero se puede cachear)
CREATE TABLE IF NOT EXISTS torneo_tabla_posiciones (
    id BIGSERIAL PRIMARY KEY,
    zona_id BIGINT NOT NULL,
    pareja_id BIGINT NOT NULL,
    puntos INTEGER DEFAULT 0,
    partidos_jugados INTEGER DEFAULT 0,
    partidos_ganados INTEGER DEFAULT 0,
    partidos_perdidos INTEGER DEFAULT 0,
    sets_favor INTEGER DEFAULT 0,
    sets_contra INTEGER DEFAULT 0,
    games_favor INTEGER DEFAULT 0,
    games_contra INTEGER DEFAULT 0,
    diferencia_sets INTEGER GENERATED ALWAYS AS (sets_favor - sets_contra) STORED,
    diferencia_games INTEGER GENERATED ALWAYS AS (games_favor - games_contra) STORED,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (zona_id, pareja_id),
    FOREIGN KEY (zona_id) REFERENCES torneo_zonas(id) ON DELETE CASCADE,
    FOREIGN KEY (pareja_id) REFERENCES torneos_parejas(id) ON DELETE CASCADE
);

-- 13. Historial de cambios en el torneo (auditoría)
CREATE TABLE IF NOT EXISTS torneo_historial_cambios (
    id BIGSERIAL PRIMARY KEY,
    torneo_id BIGINT NOT NULL,
    tipo_cambio VARCHAR(50) NOT NULL CHECK (tipo_cambio IN ('pareja_inscrita', 'pareja_baja', 'jugador_reemplazado', 'zona_generada', 'partido_programado', 'resultado_cargado', 'partido_reprogramado', 'otro')),
    descripcion TEXT NOT NULL,
    realizado_por BIGINT NOT NULL,
    datos_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (torneo_id) REFERENCES torneos(id) ON DELETE CASCADE,
    FOREIGN KEY (realizado_por) REFERENCES usuarios(id_usuario)
);

-- ============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ============================================

CREATE INDEX IF NOT EXISTS idx_torneos_estado ON torneos(estado);
CREATE INDEX IF NOT EXISTS idx_torneos_fecha_inicio ON torneos(fecha_inicio);
CREATE INDEX IF NOT EXISTS idx_torneos_categoria ON torneos(categoria);

CREATE INDEX IF NOT EXISTS idx_torneos_parejas_torneo ON torneos_parejas(torneo_id);
CREATE INDEX IF NOT EXISTS idx_torneos_parejas_estado ON torneos_parejas(estado);
CREATE INDEX IF NOT EXISTS idx_torneos_parejas_jugadores ON torneos_parejas(jugador1_id, jugador2_id);

-- Índices para partidos de torneo (en tabla partidos)
-- Se crean en la migración migrar_partidos_torneos.py

CREATE INDEX IF NOT EXISTS idx_torneo_slots_torneo ON torneo_slots(torneo_id);
CREATE INDEX IF NOT EXISTS idx_torneo_slots_cancha ON torneo_slots(cancha_id);
CREATE INDEX IF NOT EXISTS idx_torneo_slots_fecha ON torneo_slots(fecha_hora_inicio);
CREATE INDEX IF NOT EXISTS idx_torneo_slots_ocupado ON torneo_slots(ocupado);

CREATE INDEX IF NOT EXISTS idx_torneo_bloqueos_jugador ON torneo_bloqueos_jugador(jugador_id);
CREATE INDEX IF NOT EXISTS idx_torneo_bloqueos_fecha ON torneo_bloqueos_jugador(fecha);

CREATE INDEX IF NOT EXISTS idx_torneo_tabla_zona ON torneo_tabla_posiciones(zona_id);
CREATE INDEX IF NOT EXISTS idx_torneo_tabla_puntos ON torneo_tabla_posiciones(puntos DESC);
