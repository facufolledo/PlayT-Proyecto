-- Migración: Agregar campos adicionales a perfil_usuarios
-- Fecha: 2025-11-19
-- Descripción: Agregar campos para completar perfil de usuario (DNI, fecha nacimiento, teléfono, preferencias deportivas)

-- Agregar columna DNI
ALTER TABLE perfil_usuarios 
ADD COLUMN IF NOT EXISTS dni VARCHAR(20);

-- Agregar columna fecha de nacimiento
ALTER TABLE perfil_usuarios 
ADD COLUMN IF NOT EXISTS fecha_nacimiento DATE;

-- Agregar columna teléfono
ALTER TABLE perfil_usuarios 
ADD COLUMN IF NOT EXISTS telefono VARCHAR(20);

-- Agregar columna mano hábil
ALTER TABLE perfil_usuarios 
ADD COLUMN IF NOT EXISTS mano_habil VARCHAR(10) CHECK (mano_habil IN ('derecha', 'zurda'));

-- Agregar columna posición preferida
ALTER TABLE perfil_usuarios 
ADD COLUMN IF NOT EXISTS posicion_preferida VARCHAR(15) CHECK (posicion_preferida IN ('drive', 'reves', 'indiferente'));

-- Crear índice en DNI para búsquedas rápidas (opcional)
CREATE INDEX IF NOT EXISTS idx_perfil_usuarios_dni ON perfil_usuarios(dni);

-- Comentarios para documentación
COMMENT ON COLUMN perfil_usuarios.dni IS 'Documento Nacional de Identidad del usuario';
COMMENT ON COLUMN perfil_usuarios.fecha_nacimiento IS 'Fecha de nacimiento del usuario';
COMMENT ON COLUMN perfil_usuarios.telefono IS 'Número de teléfono de contacto';
COMMENT ON COLUMN perfil_usuarios.mano_habil IS 'Mano hábil del jugador: derecha o zurda';
COMMENT ON COLUMN perfil_usuarios.posicion_preferida IS 'Posición preferida en la cancha: drive, reves o indiferente';
