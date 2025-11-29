-- Migración: Agregar campos puede_crear_torneos y es_administrador a la tabla usuarios
-- Fecha: 2025-11-27
-- Descripción: Agrega permisos de administrador y creación de torneos

-- Agregar columna puede_crear_torneos
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS puede_crear_torneos BOOLEAN NOT NULL DEFAULT FALSE;

-- Agregar columna es_administrador
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS es_administrador BOOLEAN NOT NULL DEFAULT FALSE;

-- Comentarios
COMMENT ON COLUMN usuarios.puede_crear_torneos IS 'Permiso para crear torneos';
COMMENT ON COLUMN usuarios.es_administrador IS 'Usuario con permisos de administrador';

-- Verificar que las columnas se agregaron correctamente
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'usuarios' 
AND column_name IN ('puede_crear_torneos', 'es_administrador');
