-- Script para asignar categoria_id a zonas existentes basándose en sus parejas
-- Torneo 11

-- Primero verificar el estado actual
SELECT 
    tz.id,
    tz.nombre,
    tz.categoria_id as zona_categoria_actual,
    tp.categoria_id as pareja_categoria,
    COUNT(*) as num_parejas_con_esta_categoria
FROM torneo_zonas tz
JOIN torneo_zona_parejas tzp ON tz.id = tzp.zona_id
JOIN torneos_parejas tp ON tzp.pareja_id = tp.id
WHERE tz.torneo_id = 11
GROUP BY tz.id, tz.nombre, tz.categoria_id, tp.categoria_id
ORDER BY tz.numero_orden;

-- Actualizar cada zona con la categoría de sus parejas
-- (Solo funciona si todas las parejas de una zona tienen la misma categoría)

-- Zona A
UPDATE torneo_zonas 
SET categoria_id = (
    SELECT DISTINCT tp.categoria_id
    FROM torneo_zona_parejas tzp
    JOIN torneos_parejas tp ON tzp.pareja_id = tp.id
    WHERE tzp.zona_id = torneo_zonas.id
    LIMIT 1
)
WHERE torneo_id = 11 AND nombre = 'Zona A' AND categoria_id IS NULL;

-- Zona B
UPDATE torneo_zonas 
SET categoria_id = (
    SELECT DISTINCT tp.categoria_id
    FROM torneo_zona_parejas tzp
    JOIN torneos_parejas tp ON tzp.pareja_id = tp.id
    WHERE tzp.zona_id = torneo_zonas.id
    LIMIT 1
)
WHERE torneo_id = 11 AND nombre = 'Zona B' AND categoria_id IS NULL;

-- Zona C
UPDATE torneo_zonas 
SET categoria_id = (
    SELECT DISTINCT tp.categoria_id
    FROM torneo_zona_parejas tzp
    JOIN torneos_parejas tp ON tzp.pareja_id = tp.id
    WHERE tzp.zona_id = torneo_zonas.id
    LIMIT 1
)
WHERE torneo_id = 11 AND nombre = 'Zona C' AND categoria_id IS NULL;

-- Zona D
UPDATE torneo_zonas 
SET categoria_id = (
    SELECT DISTINCT tp.categoria_id
    FROM torneo_zona_parejas tzp
    JOIN torneos_parejas tp ON tzp.pareja_id = tp.id
    WHERE tzp.zona_id = torneo_zonas.id
    LIMIT 1
)
WHERE torneo_id = 11 AND nombre = 'Zona D' AND categoria_id IS NULL;

-- Verificar resultado
SELECT 
    tz.id,
    tz.nombre,
    tz.categoria_id,
    tc.nombre as categoria_nombre,
    tc.genero
FROM torneo_zonas tz
LEFT JOIN torneo_categorias tc ON tz.categoria_id = tc.id
WHERE tz.torneo_id = 11
ORDER BY tz.numero_orden;
