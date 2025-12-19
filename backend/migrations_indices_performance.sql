-- ============================================
-- ÍNDICES PARA PERFORMANCE - PlayT
-- Ejecutar en Neon/PostgreSQL para optimizar queries
-- ============================================

-- ============ USUARIOS ============
-- Ranking por rating (muy usado)
CREATE INDEX IF NOT EXISTS idx_usuarios_rating ON usuarios(rating DESC);

-- Búsqueda por email (login)
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);

-- Filtro por sexo en rankings
CREATE INDEX IF NOT EXISTS idx_usuarios_sexo_rating ON usuarios(sexo, rating DESC);

-- Búsqueda por firebase_uid (auth)
CREATE INDEX IF NOT EXISTS idx_usuarios_firebase_uid ON usuarios(firebase_uid);


-- ============ PARTIDOS ============
-- Partidos por fecha (historial, estadísticas)
CREATE INDEX IF NOT EXISTS idx_partidos_fecha ON partidos(fecha DESC);

-- Partidos por estado (filtros)
CREATE INDEX IF NOT EXISTS idx_partidos_estado ON partidos(estado);

-- Partidos por creador
CREATE INDEX IF NOT EXISTS idx_partidos_creador ON partidos(creado_por);

-- Combinado: estado + fecha (queries comunes)
CREATE INDEX IF NOT EXISTS idx_partidos_estado_fecha ON partidos(estado, fecha DESC);


-- ============ PARTIDO_JUGADORES ============
-- Búsqueda por usuario (historial de partidos)
CREATE INDEX IF NOT EXISTS idx_partido_jugadores_usuario ON partido_jugadores(id_usuario);

-- Búsqueda por partido
CREATE INDEX IF NOT EXISTS idx_partido_jugadores_partido ON partido_jugadores(id_partido);

-- Combinado para queries de equipo
CREATE INDEX IF NOT EXISTS idx_partido_jugadores_partido_equipo ON partido_jugadores(id_partido, equipo);


-- ============ RESULTADOS_PARTIDOS ============
-- Por partido (join común)
CREATE INDEX IF NOT EXISTS idx_resultados_partido ON resultados_partidos(id_partido);

-- Por confirmación (filtros)
CREATE INDEX IF NOT EXISTS idx_resultados_confirmado ON resultados_partidos(confirmado);


-- ============ HISTORIAL_RATING ============
-- Por usuario (gráficos de evolución)
CREATE INDEX IF NOT EXISTS idx_historial_rating_usuario ON historial_rating(id_usuario);

-- Por fecha (ordenamiento)
CREATE INDEX IF NOT EXISTS idx_historial_rating_fecha ON historial_rating(fecha DESC);

-- Combinado usuario + fecha
CREATE INDEX IF NOT EXISTS idx_historial_rating_usuario_fecha ON historial_rating(id_usuario, fecha DESC);


-- ============ SALAS ============
-- Por código (unirse a sala)
CREATE INDEX IF NOT EXISTS idx_salas_codigo ON salas(codigo_invitacion);

-- Por estado (listar activas)
CREATE INDEX IF NOT EXISTS idx_salas_estado ON salas(estado);

-- Por creador
CREATE INDEX IF NOT EXISTS idx_salas_creador ON salas(creado_por);


-- ============ CONFIRMACIONES ============
-- Por partido (verificar confirmaciones)
CREATE INDEX IF NOT EXISTS idx_confirmaciones_partido ON confirmaciones(id_partido);

-- Por usuario
CREATE INDEX IF NOT EXISTS idx_confirmaciones_usuario ON confirmaciones(id_usuario);

-- Combinado partido + tipo
CREATE INDEX IF NOT EXISTS idx_confirmaciones_partido_tipo ON confirmaciones(id_partido, tipo);


-- ============ HISTORIAL_ENFRENTAMIENTOS (Anti-trampa) ============
-- Por hash de trío (búsqueda rápida anti-trampa)
CREATE INDEX IF NOT EXISTS idx_historial_hash1 ON historial_enfrentamientos(hash_trio_1);
CREATE INDEX IF NOT EXISTS idx_historial_hash2 ON historial_enfrentamientos(hash_trio_2);

-- Por fecha (limpieza de antiguos)
CREATE INDEX IF NOT EXISTS idx_historial_fecha ON historial_enfrentamientos(fecha DESC);


-- ============ TORNEOS ============
-- Por estado (listar activos)
CREATE INDEX IF NOT EXISTS idx_torneos_estado ON torneos(estado);

-- Por fecha inicio
CREATE INDEX IF NOT EXISTS idx_torneos_fecha ON torneos(fecha_inicio);

-- Por creador
CREATE INDEX IF NOT EXISTS idx_torneos_creador ON torneos(creado_por);


-- ============ INSCRIPCIONES_TORNEO ============
-- Por torneo
CREATE INDEX IF NOT EXISTS idx_inscripciones_torneo ON inscripciones_torneo(id_torneo);

-- Por usuario (mis torneos)
CREATE INDEX IF NOT EXISTS idx_inscripciones_usuario ON inscripciones_torneo(id_usuario);

-- Combinado torneo + estado
CREATE INDEX IF NOT EXISTS idx_inscripciones_torneo_estado ON inscripciones_torneo(id_torneo, estado);


-- ============ PARTIDOS_TORNEO ============
-- Por torneo
CREATE INDEX IF NOT EXISTS idx_partidos_torneo_torneo ON partidos_torneo(id_torneo);

-- Por fase
CREATE INDEX IF NOT EXISTS idx_partidos_torneo_fase ON partidos_torneo(fase);

-- Combinado torneo + zona + jornada (fixture)
CREATE INDEX IF NOT EXISTS idx_partidos_torneo_fixture ON partidos_torneo(id_torneo, id_zona, jornada);


-- ============ ZONAS_TORNEO ============
-- Por torneo
CREATE INDEX IF NOT EXISTS idx_zonas_torneo ON zonas_torneo(id_torneo);


-- ============ PERFILES ============
-- Por usuario (join común)
CREATE INDEX IF NOT EXISTS idx_perfiles_usuario ON perfiles_usuarios(id_usuario);


-- ============================================
-- VERIFICAR ÍNDICES CREADOS
-- ============================================
-- SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename;
