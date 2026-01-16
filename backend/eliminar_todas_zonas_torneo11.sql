-- Eliminar todas las zonas del torneo 11 para regenerarlas correctamente

-- 1. Eliminar partidos de las zonas
DELETE FROM partidos 
WHERE zona_id IN (
    SELECT id FROM torneo_zonas WHERE torneo_id = 11
);

-- 2. Eliminar tablas de posiciones
DELETE FROM torneo_tabla_posiciones 
WHERE zona_id IN (
    SELECT id FROM torneo_zonas WHERE torneo_id = 11
);

-- 3. Eliminar relaciones zona-pareja
DELETE FROM torneo_zona_parejas 
WHERE zona_id IN (
    SELECT id FROM torneo_zonas WHERE torneo_id = 11
);

-- 4. Eliminar zonas
DELETE FROM torneo_zonas 
WHERE torneo_id = 11;

-- Verificar que se eliminaron
SELECT COUNT(*) as zonas_restantes FROM torneo_zonas WHERE torneo_id = 11;
