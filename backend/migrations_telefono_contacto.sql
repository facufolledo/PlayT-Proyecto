-- Migración: Agregar campo telefono_contacto a torneos
-- Fecha: 2026-01-19
-- Descripción: Campo para que el organizador indique a qué número enviar comprobantes de pago

-- Agregar columna telefono_contacto
ALTER TABLE torneos 
ADD COLUMN IF NOT EXISTS telefono_contacto VARCHAR(20);

-- Comentario
COMMENT ON COLUMN torneos.telefono_contacto IS 'Teléfono para enviar comprobante de pago';

-- Verificar
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'torneos' AND column_name = 'telefono_contacto';
