# Sistema de Torneos Clásico - PlayT

## Descripción General

Sistema completo para gestionar torneos de pádel formato "Clásico" con:
- Zonas de 3 parejas (y algunas de 2 cuando los números no son exactos)
- Fase de grupos + eliminación directa
- Inscripciones abiertas hasta último momento
- Cambios de parejas y jugadores de última hora
- Restricciones horarias de jugadores
- Programación automática de partidos con canchas disponibles
- Integración total con sistema ELO existente
- Control total para organizadores autorizados

## Características Principales

### 1. Roles y Permisos
- **Organizadores Autorizados**: Solo cuentas autorizadas pueden crear torneos
- **Organizadores del Torneo**: Owner + colaboradores pueden gestionar todo
- **Jugadores**: Se inscriben, cargan restricciones horarias, ven fixture

### 2. Flujo del Torneo
1. Organizador crea torneo (inscripción abierta)
2. Jugadores se inscriben formando parejas
3. Jugadores cargan restricciones horarias (jue/vie principalmente)
4. Organizador define canchas y horarios disponibles
5. Organizador cierra inscripción y genera zonas automáticamente
6. Sistema arma fixture de zonas respetando restricciones
7. Se juegan partidos de zona (organizador carga resultados)
8. Sistema actualiza ELO después de cada partido
9. Organizador genera cuadro final cuando terminan zonas
10. Sistema calcula clasificados, byes, y arma eliminación
11. Se juega fase final hasta el campeón

### 3. Gestión de Cambios de Último Momento
- Parejas pueden darse de baja
- Jugadores pueden ser reemplazados
- Organizador puede mover parejas entre zonas
- Organizador puede reasignar horarios y canchas
- Sistema recalcula fixture automáticamente

### 4. Integración con ELO
- Cada partido de torneo cuenta como partido individual
- Se usa el EloController existente
- Se actualiza historial de cada jugador
- Se guarda en historial_rating_salas
- Tipo de partido: "torneo"

### 5. Zonas Dinámicas
- Preferencia: zonas de 3 parejas
- Si números no cuadran: algunas zonas de 2
- Algoritmo inteligente para distribuir parejas
- Clasifican 1° y 2° de cada zona

### 6. Fase de Eliminación con Byes
- Calcula siguiente potencia de 2
- Asigna byes a mejores primeros
- Segundos juegan ronda previa
- Organizador puede editar manualmente

### 7. Restricciones Horarias
- Jugadores bloquean horarios no disponibles
- Sistema solo programa en slots compatibles
- Si no hay slots: marca para programación manual
- Organizador puede forzar horarios

## Estructura de Base de Datos

Ver archivo: `crear_tablas_torneos.sql`

## Endpoints API

Ver archivo: `torneo_controller.py`

## Servicios

- `torneo_service.py`: Lógica principal de torneos
- `torneo_zona_service.py`: Generación y gestión de zonas
- `torneo_fixture_service.py`: Generación de fixture y programación
- `torneo_eliminacion_service.py`: Cuadros finales y byes
- `torneo_resultado_service.py`: Carga de resultados e integración con ELO

## Modelos

Ver archivo: `torneo_models.py`

## Schemas

Ver archivo: `torneo_schemas.py`
