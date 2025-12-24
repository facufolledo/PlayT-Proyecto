-- Migración: Agregar estado 'bye' a partidos

-- Aumentar el tamaño del campo estado
ALTER TABLE partidos ALTER COLUMN estado TYPE VARCHAR(20);

-- Eliminar el constraint existente
ALTER TABLE partidos DROP CONSTRAINT IF EXISTS partidos_estado_check;

-- Crear nuevo constraint con todos los estados posibles (incluyendo los existentes)
ALTER TABLE partidos ADD CONSTRAINT partidos_estado_check 
CHECK (estado IN ('pendiente', 'en_juego', 'finalizado', 'w_o', 'cancelado', 'confirmado', 'bye', 'sin_resultado', 'reportado'));

SELECT 'Estado bye agregado a partidos' as info;
