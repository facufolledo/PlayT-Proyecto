-- ============================================
-- QUERY: Ver parejas pendientes de confirmación
-- ============================================

-- Ver todas las parejas pendientes con detalles completos
SELECT 
    pt.id_pareja,
    pt.id_torneo,
    t.nombre as torneo_nombre,
    pt.nombre_pareja,
    
    -- Jugador 1
    pt.jugador1_id,
    u1.nombre_usuario as jugador1_username,
    CONCAT(p1.nombre, ' ', p1.apellido) as jugador1_nombre_completo,
    pt.confirmado_jugador1,
    
    -- Jugador 2
    pt.jugador2_id,
    u2.nombre_usuario as jugador2_username,
    CONCAT(p2.nombre, ' ', p2.apellido) as jugador2_nombre_completo,
    pt.confirmado_jugador2,
    
    -- Estado
    pt.estado,
    pt.created_at as fecha_creacion,
    
    -- Quién falta confirmar
    CASE 
        WHEN NOT pt.confirmado_jugador1 AND NOT pt.confirmado_jugador2 THEN 'Ambos'
        WHEN NOT pt.confirmado_jugador1 THEN CONCAT(p1.nombre, ' ', p1.apellido)
        WHEN NOT pt.confirmado_jugador2 THEN CONCAT(p2.nombre, ' ', p2.apellido)
        ELSE 'Ninguno'
    END as falta_confirmar
    
FROM parejas_torneo pt
INNER JOIN torneos t ON pt.id_torneo = t.id_torneo
LEFT JOIN usuarios u1 ON pt.jugador1_id = u1.id_usuario
LEFT JOIN perfil_usuario p1 ON u1.id_usuario = p1.id_usuario
LEFT JOIN usuarios u2 ON pt.jugador2_id = u2.id_usuario
LEFT JOIN perfil_usuario p2 ON u2.id_usuario = p2.id_usuario
WHERE pt.estado = 'pendiente'
ORDER BY pt.created_at DESC;


-- ============================================
-- QUERY: Resumen de parejas pendientes por torneo
-- ============================================

SELECT 
    t.id_torneo,
    t.nombre as torneo,
    COUNT(*) as total_parejas_pendientes,
    COUNT(CASE WHEN NOT pt.confirmado_jugador1 THEN 1 END) as falta_confirmar_j1,
    COUNT(CASE WHEN NOT pt.confirmado_jugador2 THEN 1 END) as falta_confirmar_j2,
    COUNT(CASE WHEN NOT pt.confirmado_jugador1 AND NOT pt.confirmado_jugador2 THEN 1 END) as falta_confirmar_ambos
FROM parejas_torneo pt
INNER JOIN torneos t ON pt.id_torneo = t.id_torneo
WHERE pt.estado = 'pendiente'
GROUP BY t.id_torneo, t.nombre
ORDER BY total_parejas_pendientes DESC;


-- ============================================
-- QUERY: Ver parejas de un torneo específico
-- ============================================

-- Reemplaza <ID_TORNEO> con el ID del torneo que quieres consultar
SELECT 
    pt.id_pareja,
    pt.nombre_pareja,
    CONCAT(p1.nombre, ' ', p1.apellido) as jugador1,
    u1.nombre_usuario as jugador1_username,
    pt.confirmado_jugador1,
    CONCAT(p2.nombre, ' ', p2.apellido) as jugador2,
    u2.nombre_usuario as jugador2_username,
    pt.confirmado_jugador2,
    pt.estado,
    pt.created_at
FROM parejas_torneo pt
LEFT JOIN usuarios u1 ON pt.jugador1_id = u1.id_usuario
LEFT JOIN perfil_usuario p1 ON u1.id_usuario = p1.id_usuario
LEFT JOIN usuarios u2 ON pt.jugador2_id = u2.id_usuario
LEFT JOIN perfil_usuario p2 ON u2.id_usuario = p2.id_usuario
WHERE pt.id_torneo = <ID_TORNEO>
ORDER BY 
    CASE pt.estado 
        WHEN 'pendiente' THEN 1 
        WHEN 'confirmada' THEN 2 
        ELSE 3 
    END,
    pt.created_at DESC;


-- ============================================
-- QUERY: Ver solo parejas donde falta confirmar jugador 2
-- ============================================

SELECT 
    pt.id_pareja,
    t.nombre as torneo,
    pt.nombre_pareja,
    CONCAT(p1.nombre, ' ', p1.apellido) as quien_invito,
    u1.nombre_usuario as invito_username,
    CONCAT(p2.nombre, ' ', p2.apellido) as quien_debe_confirmar,
    u2.nombre_usuario as debe_confirmar_username,
    u2.email as email_debe_confirmar,
    pt.created_at as fecha_invitacion
FROM parejas_torneo pt
INNER JOIN torneos t ON pt.id_torneo = t.id_torneo
LEFT JOIN usuarios u1 ON pt.jugador1_id = u1.id_usuario
LEFT JOIN perfil_usuario p1 ON u1.id_usuario = p1.id_usuario
LEFT JOIN usuarios u2 ON pt.jugador2_id = u2.id_usuario
LEFT JOIN perfil_usuario p2 ON u2.id_usuario = p2.id_usuario
WHERE pt.estado = 'pendiente'
  AND pt.confirmado_jugador1 = TRUE
  AND pt.confirmado_jugador2 = FALSE
ORDER BY pt.created_at DESC;


-- ============================================
-- QUERY: Estadísticas generales
-- ============================================

SELECT 
    COUNT(*) as total_parejas,
    COUNT(CASE WHEN estado = 'pendiente' THEN 1 END) as pendientes,
    COUNT(CASE WHEN estado = 'confirmada' THEN 1 END) as confirmadas,
    COUNT(CASE WHEN estado = 'rechazada' THEN 1 END) as rechazadas,
    COUNT(CASE WHEN estado = 'eliminada' THEN 1 END) as eliminadas
FROM parejas_torneo;
