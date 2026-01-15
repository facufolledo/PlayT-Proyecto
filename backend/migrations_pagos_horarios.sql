-- Migración para agregar sistema de pagos y franjas horarias
-- Fecha: 2026-01-08

-- 1. Agregar campos de pago a torneos_parejas
ALTER TABLE torneos_parejas 
ADD COLUMN IF NOT EXISTS pago_estado VARCHAR(20) DEFAULT 'pendiente',
ADD COLUMN IF NOT EXISTS pago_monto DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS pago_comprobante_url TEXT,
ADD COLUMN IF NOT EXISTS pago_fecha_acreditacion TIMESTAMP,
ADD COLUMN IF NOT EXISTS pago_verificado_por BIGINT REFERENCES usuarios(id_usuario),
ADD COLUMN IF NOT EXISTS motivo_rechazo_pago TEXT;

-- Estados posibles de pago: 'pendiente', 'pagado', 'verificado', 'rechazado', 'reembolsado'

-- 2. Agregar campos de disponibilidad horaria (JSON para flexibilidad)
ALTER TABLE torneos_parejas
ADD COLUMN IF NOT EXISTS disponibilidad_horaria JSONB;

-- Formato JSON: 
-- {
--   "lunes": ["08:00-10:00", "17:00-19:00"],
--   "martes": ["17:00-21:00"],
--   "sabado": ["todo_el_dia"],
--   "domingo": ["todo_el_dia"]
-- }

-- 3. Agregar campo para tracking de cambios de compañero
ALTER TABLE torneos_parejas
ADD COLUMN IF NOT EXISTS jugador2_anterior_id BIGINT REFERENCES usuarios(id_usuario),
ADD COLUMN IF NOT EXISTS fecha_cambio_jugador2 TIMESTAMP,
ADD COLUMN IF NOT EXISTS motivo_cambio TEXT;

-- 4. Agregar campos de pago al torneo (con alias CBU/CVU)
ALTER TABLE torneos
ADD COLUMN IF NOT EXISTS monto_inscripcion DECIMAL(10,2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS requiere_pago BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS alias_cbu_cvu VARCHAR(100),
ADD COLUMN IF NOT EXISTS titular_cuenta VARCHAR(200),
ADD COLUMN IF NOT EXISTS banco VARCHAR(100);

-- 5. Crear tabla de historial de pagos
CREATE TABLE IF NOT EXISTS torneos_pagos_historial (
    id BIGSERIAL PRIMARY KEY,
    pareja_id BIGINT REFERENCES torneos_parejas(id) ON DELETE CASCADE,
    estado_anterior VARCHAR(20),
    estado_nuevo VARCHAR(20),
    monto DECIMAL(10,2),
    comprobante_url TEXT,
    observaciones TEXT,
    modificado_por BIGINT REFERENCES usuarios(id_usuario),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Crear índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_torneos_parejas_pago_estado ON torneos_parejas(pago_estado);
CREATE INDEX IF NOT EXISTS idx_torneos_pagos_historial_pareja ON torneos_pagos_historial(pareja_id);
CREATE INDEX IF NOT EXISTS idx_torneos_requiere_pago ON torneos(requiere_pago);

-- 7. Comentarios para documentación
COMMENT ON COLUMN torneos_parejas.pago_estado IS 'Estado del pago: pendiente, pagado, verificado, rechazado, reembolsado';
COMMENT ON COLUMN torneos_parejas.disponibilidad_horaria IS 'JSON con disponibilidad horaria por día de la semana';
COMMENT ON COLUMN torneos.monto_inscripcion IS 'Monto en pesos argentinos para la inscripción';
COMMENT ON COLUMN torneos.alias_cbu_cvu IS 'Alias, CBU o CVU para transferencias';
