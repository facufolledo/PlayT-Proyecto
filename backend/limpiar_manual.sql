-- Script SQL para limpiar base de datos manualmente
-- Ejecutar en Railway PostgreSQL Query

-- IMPORTANTE: Esto borrará TODOS los datos
-- Ejecuta línea por línea o todo junto

-- 1. Borrar en orden (de dependientes a independientes)
DELETE FROM historial_enfrentamientos;
DELETE FROM partidos;
DELETE FROM salas;
DELETE FROM torneos;
DELETE FROM usuarios;

-- 2. Resetear secuencias (IDs vuelven a 1)
ALTER SEQUENCE usuarios_id_usuario_seq RESTART WITH 1;
ALTER SEQUENCE salas_id_sala_seq RESTART WITH 1;
ALTER SEQUENCE partidos_id_partido_seq RESTART WITH 1;

-- 3. Verificar que todo está limpio
SELECT 'usuarios' as tabla, COUNT(*) as registros FROM usuarios
UNION ALL
SELECT 'salas', COUNT(*) FROM salas
UNION ALL
SELECT 'torneos', COUNT(*) FROM torneos
UNION ALL
SELECT 'partidos', COUNT(*) FROM partidos
UNION ALL
SELECT 'categorias', COUNT(*) FROM categorias;
