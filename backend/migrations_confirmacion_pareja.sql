-- Migración: Sistema de confirmación de pareja para torneos

-- Agregar campos para confirmación
ALTER TABLE torneos_parejas 
ADD COLUMN IF NOT EXISTS codigo_confirmacion VARCHAR(8);

ALTER TABLE torneos_parejas 
ADD COLUMN IF NOT EXISTS confirmado_jugador1 BOOLEAN DEFAULT TRUE;

ALTER TABLE torneos_parejas 
ADD COLUMN IF NOT EXISTS confirmado_jugador2 BOOLEAN DEFAULT FALSE;

ALTER TABLE torneos_parejas 
ADD COLUMN IF NOT EXISTS fecha_expiracion TIMESTAMP;

ALTER TABLE torneos_parejas 
ADD COLUMN IF NOT EXISTS creado_por_id BIGINT;

-- Índice para búsqueda por código
CREATE INDEX IF NOT EXISTS idx_torneos_parejas_codigo ON torneos_parejas(codigo_confirmacion);

-- Actualizar parejas existentes como ya confirmadas
UPDATE torneos_parejas 
SET confirmado_jugador1 = TRUE, 
    confirmado_jugador2 = TRUE 
WHERE estado != 'baja';

SELECT 'Campos de confirmación agregados' as info;
