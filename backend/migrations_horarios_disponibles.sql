-- Migración: Agregar campo horarios_disponibles a la tabla torneos
-- Fecha: 2026-01-14
-- Descripción: Permite configurar horarios diferentes para días de semana y fin de semana

-- Agregar columna horarios_disponibles
ALTER TABLE torneos 
ADD COLUMN IF NOT EXISTS horarios_disponibles JSON;

-- Comentario explicativo
COMMENT ON COLUMN torneos.horarios_disponibles IS 'Horarios disponibles del torneo separados por semana y fin de semana: {"semana": [{"desde": "18:00", "hasta": "23:00"}], "finDeSemana": [{"desde": "08:00", "hasta": "23:00"}]}';
