-- Migración para crear tablas de Salas
-- Ejecutar en la base de datos PostgreSQL

-- Tabla de Salas
CREATE TABLE IF NOT EXISTS salas (
    id_sala BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    codigo_invitacion VARCHAR(10) UNIQUE NOT NULL,
    fecha TIMESTAMP WITH TIME ZONE NOT NULL,
    estado VARCHAR(20) DEFAULT 'esperando' NOT NULL,
    id_creador BIGINT NOT NULL REFERENCES usuarios(id_usuario),
    max_jugadores INTEGER DEFAULT 4 NOT NULL,
    id_partido BIGINT REFERENCES partidos(id_partido),
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (estado IN ('esperando', 'en_juego', 'finalizada'))
);

-- Índices para salas
CREATE INDEX idx_salas_codigo ON salas(codigo_invitacion);
CREATE INDEX idx_salas_creador ON salas(id_creador);
CREATE INDEX idx_salas_estado ON salas(estado);

-- Tabla de relación Sala-Jugadores
CREATE TABLE IF NOT EXISTS sala_jugadores (
    id_sala BIGINT NOT NULL REFERENCES salas(id_sala) ON DELETE CASCADE,
    id_usuario BIGINT NOT NULL REFERENCES usuarios(id_usuario),
    equipo INTEGER CHECK (equipo IN (1, 2)),
    orden INTEGER NOT NULL,
    unido_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id_sala, id_usuario)
);

-- Índices para sala_jugadores
CREATE INDEX idx_sala_jugadores_sala ON sala_jugadores(id_sala);
CREATE INDEX idx_sala_jugadores_usuario ON sala_jugadores(id_usuario);

-- Comentarios
COMMENT ON TABLE salas IS 'Salas de juego para partidos colaborativos';
COMMENT ON COLUMN salas.codigo_invitacion IS 'Código único de 6 caracteres para unirse';
COMMENT ON COLUMN salas.estado IS 'Estado de la sala: esperando, en_juego, finalizada';
COMMENT ON COLUMN sala_jugadores.orden IS 'Orden de llegada del jugador (1-4)';
COMMENT ON COLUMN sala_jugadores.equipo IS 'Equipo asignado: 1 o 2';
