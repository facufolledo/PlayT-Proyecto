-- Verificar zonas y sus categorías
SELECT 
    tz.id as zona_id,
    tz.nombre as zona_nombre,
    tz.categoria_id,
    tc.nombre as categoria_nombre,
    tc.genero as categoria_genero,
    COUNT(tzp.pareja_id) as num_parejas
FROM torneo_zonas tz
LEFT JOIN torneo_categorias tc ON tz.categoria_id = tc.id
LEFT JOIN torneo_zona_parejas tzp ON tz.id = tzp.zona_id
WHERE tz.torneo_id = 11
GROUP BY tz.id, tz.nombre, tz.categoria_id, tc.nombre, tc.genero
ORDER BY tz.numero_orden;

-- Verificar parejas en cada zona y sus categorías
SELECT 
    tz.nombre as zona_nombre,
    tp.id as pareja_id,
    tp.categoria_id as pareja_categoria_id,
    tc.nombre as categoria_nombre
FROM torneo_zonas tz
JOIN torneo_zona_parejas tzp ON tz.id = tzp.zona_id
JOIN torneos_parejas tp ON tzp.pareja_id = tp.id
LEFT JOIN torneo_categorias tc ON tp.categoria_id = tc.id
WHERE tz.torneo_id = 11
ORDER BY tz.numero_orden, tp.id;
