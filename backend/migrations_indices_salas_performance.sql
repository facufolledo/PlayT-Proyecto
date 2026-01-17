-- =====================================================
-- MIGRACIÓN: Índices para Performance de Salas
-- Fecha: 2026-01-17
-- Propósito: Optimizar queries de salas que tardan mucho
-- =====================================================

-- Índices para tabla SalaJugador (críticos para performance)
CREATE INDEX IF NOT EXISTS idx_sala_jugador_id_sala ON sala_jugador(id_sala);
CREATE INDEX IF NOT EXISTS idx_sala_jugador_id_usuario ON sala_jugador(id_usuario);
CREATE INDEX IF NOT EXISTS idx_sala_jugador_sala_usuario ON sala_jugador(id_sala, id_usuario);

-- Índices para tabla Sala
CREATE INDEX IF NOT EXISTS idx_sala_codigo_invitacion ON sala(codigo_invitacion);
CREATE INDEX IF NOT EXISTS idx_sala_estado ON sala(estado);
CREATE INDEX IF NOT EXISTS idx_sala_estado_creado ON sala(estado, creado_en);

-- Índices para tabla Usuario (para joins frecuentes)
CREATE INDEX IF NOT EXISTS idx_usuario_id_usuario ON usuario(id_usuario);

-- Índices para tabla PerfilUsuario (para joins frecuentes)
CREATE INDEX IF NOT EXISTS idx_perfil_usuario_id_usuario ON perfil_usuario(id_usuario);

-- Índices compuestos para queries específicas de salas
CREATE INDEX IF NOT EXISTS idx_sala_activa_reciente ON sala(estado, creado_en DESC) 
WHERE estado IN ('esperando', 'en_juego');

-- Estadísticas para el optimizador
ANALYZE sala;
ANALYZE sala_jugador;
ANALYZE usuario;
ANALYZE perfil_usuario;

-- Verificar que los índices se crearon correctamente
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename IN ('sala', 'sala_jugador', 'usuario', 'perfil_usuario')
ORDER BY tablename, indexname;