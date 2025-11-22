-- Actualizar sala 18 a estado en_juego
-- Para que aparezca en el listado mientras espera confirmaciones

-- Ver estado actual
SELECT 
    s.id_sala,
    s.nombre,
    s.estado,
    s.id_partido,
    p.estado_confirmacion,
    p.elo_aplicado
FROM salas s
LEFT JOIN partidos p ON s.id_partido = p.id_partido
WHERE s.id_sala = 18;

-- Actualizar estado
UPDATE salas 
SET estado = 'en_juego'
WHERE id_sala = 18;

-- Verificar cambio
SELECT 
    s.id_sala,
    s.nombre,
    s.estado,
    s.id_partido,
    p.estado_confirmacion,
    p.elo_aplicado
FROM salas s
LEFT JOIN partidos p ON s.id_partido = p.id_partido
WHERE s.id_sala = 18;

-- Si quieres actualizar TODAS las salas finalizadas sin Elo aplicado:
-- UPDATE salas 
-- SET estado = 'en_juego'
-- WHERE estado = 'finalizada'
-- AND id_partido IN (
--     SELECT id_partido 
--     FROM partidos 
--     WHERE elo_aplicado = false OR elo_aplicado IS NULL
-- );
