-- Actualización de Categorías Balanceadas
-- Sistema más justo con rangos uniformes de 200 puntos

-- ============================================
-- CATEGORÍAS MASCULINAS (Balanceadas)
-- ============================================

-- Eliminar categorías antiguas masculinas
DELETE FROM categorias WHERE sexo = 'masculino';

-- Insertar nuevas categorías balanceadas
INSERT INTO categorias (nombre, descripcion, rating_min, rating_max, sexo) VALUES
('Principiante', 'Jugadores muy nuevos, aprendiendo fundamentos', 0, 699, 'masculino'),
('8va', 'Principiantes avanzados, golpes básicos sólidos', 700, 899, 'masculino'),
('7ma', 'Jugadores intermedios, mejor dominio técnico', 900, 1099, 'masculino'),
('6ta', 'Buenos jugadores, estrategia y consistencia', 1100, 1299, 'masculino'),
('5ta', 'Muy buenos jugadores, técnica + táctica', 1300, 1499, 'masculino'),
('4ta', 'Jugadores avanzados, alto nivel técnico', 1500, 1699, 'masculino'),
('Libre', 'Élite local, top de la región', 1700, NULL, 'masculino');

-- ============================================
-- CATEGORÍAS FEMENINAS (Balanceadas)
-- ============================================

-- Eliminar categorías antiguas femeninas
DELETE FROM categorias WHERE sexo = 'femenino';

-- Insertar nuevas categorías balanceadas
INSERT INTO categorias (nombre, descripcion, rating_min, rating_max, sexo) VALUES
('Principiante', 'Jugadoras muy nuevas, aprendiendo fundamentos', 0, 699, 'femenino'),
('8va', 'Principiantes avanzadas, golpes básicos sólidos', 700, 899, 'femenino'),
('7ma', 'Jugadoras intermedias, mejor dominio técnico', 900, 1099, 'femenino'),
('6ta', 'Buenas jugadoras, estrategia y consistencia', 1100, 1299, 'femenino'),
('5ta', 'Muy buenas jugadoras, técnica + táctica', 1300, 1499, 'femenino'),
('4ta', 'Jugadoras avanzadas, alto nivel técnico', 1500, 1699, 'femenino'),
('Libre', 'Élite local, top de la región', 1700, NULL, 'femenino');

-- ============================================
-- VERIFICACIÓN
-- ============================================

-- Ver categorías masculinas
SELECT nombre, rating_min, rating_max, (rating_max - rating_min) as rango
FROM categorias 
WHERE sexo = 'masculino'
ORDER BY rating_min;

-- Ver categorías femeninas
SELECT nombre, rating_min, rating_max, (rating_max - rating_min) as rango
FROM categorias 
WHERE sexo = 'femenino'
ORDER BY rating_min;

-- ============================================
-- NOTAS
-- ============================================

/*
CAMBIOS PRINCIPALES:
1. Principiante: 0-699 (nueva categoría para muy nuevos)
2. 8va: 700-899 (reducido de 500-899)
3. 7ma-4ta: Rangos uniformes de 200 puntos
4. Libre: 1700+ (aumentado de 1500+)

VENTAJAS:
- Rangos uniformes = progresión más justa
- Ganar torneo en 8va (600→750) = casi sube
- Más motivante para principiantes
- Libre más exclusiva (1700+ es realmente élite)

IMPACTO EN JUGADORES EXISTENTES:
- Jugadores 500-699: Bajan a "Principiante" (temporal)
- Jugadores 700-899: Se mantienen en 8va
- Jugadores 1500-1699: Bajan a 4ta (temporal)
- Jugadores 1700+: Se mantienen en Libre

NOTA: Los jugadores subirán naturalmente con el nuevo sistema
*/
