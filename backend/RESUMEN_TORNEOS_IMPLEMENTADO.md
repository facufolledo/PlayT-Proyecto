# Resumen: Sistema de Torneos - Base de Datos Completada

## ✅ Lo que ya está hecho

### 1. Tablas de Torneos Creadas (12 tablas)
- ✅ `organizadores_autorizados` - Usuarios que pueden crear torneos
- ✅ `torneos` - Información principal de cada torneo
- ✅ `torneos_organizadores` - Organizadores por torneo (owner + colaboradores)
- ✅ `torneos_parejas` - Parejas inscritas en torneos
- ✅ `torneo_zonas` - Zonas de cada torneo
- ✅ `torneo_zona_parejas` - Asignación de parejas a zonas
- ✅ `torneo_canchas` - Canchas disponibles por torneo
- ✅ `torneo_slots` - Slots de horarios disponibles
- ✅ `torneo_bloqueos_jugador` - Restricciones horarias de jugadores
- ✅ `torneo_tabla_posiciones` - Tabla de posiciones por zona
- ✅ `torneo_historial_cambios` - Auditoría de cambios

### 2. Tabla Partidos Unificada
- ✅ Tabla `partidos` existente extendida con columnas para torneos:
  - `zona_id` - Zona del torneo (si aplica)
  - `fase` - Fase del torneo (zona, 16avos, 8vos, 4tos, semis, final)
  - `numero_partido` - Número de partido en la fase
  - `pareja1_id` - Pareja 1 (para torneos)
  - `pareja2_id` - Pareja 2 (para torneos)
  - `cancha_id` - Cancha asignada
  - `fecha_hora` - Fecha y hora programada
  - `ganador_pareja_id` - Pareja ganadora
  - `origen` - auto/manual (generado automáticamente o editado)
  - `requiere_reprogramacion` - Flag para reprogramar
  - `observaciones` - Notas del organizador

### 3. Tabla de Sets
- ✅ `partido_sets` - Sets de cualquier partido (AMD o torneo)
  - Reemplaza el JSON `resultado_padel` con estructura relacional
  - Soporta hasta 3 sets
  - Marca si es tiebreak

### 4. Integración con Sistema Existente
- ✅ Usa la tabla `partidos` existente para TODO
- ✅ Diferencia por columna `tipo`:
  - `tipo='amistoso'` → Partidos AMD
  - `tipo='torneo'` → Partidos de torneo
- ✅ Columna `id_torneo` referencia al torneo
- ✅ Compatible con sistema ELO actual
- ✅ Compatible con historial de jugadores

## 📋 Próximos Pasos

### Paso 1: Servicios Básicos (AHORA)
Crear `backend/src/services/torneo_service.py`:
- Crear torneo
- Listar torneos
- Obtener torneo por ID
- Actualizar torneo
- Validar permisos de organizador

### Paso 2: Sistema de Inscripciones
Crear `backend/src/services/torneo_inscripcion_service.py`:
- Inscribir pareja
- Confirmar/rechazar pareja
- Dar de baja pareja
- Reemplazar jugador
- Listar parejas inscritas

### Paso 3: Generación de Zonas
Crear `backend/src/services/torneo_zona_service.py`:
- Algoritmo de generación de zonas (3 y 2 parejas)
- Generar fixture de zona (todos contra todos)
- Calcular tabla de posiciones
- Determinar clasificados

### Paso 4: Programación de Partidos
Crear `backend/src/services/torneo_fixture_service.py`:
- Crear slots de horarios
- Registrar bloqueos de jugadores
- Programar partidos automáticamente
- Reprogramar partidos

### Paso 5: Resultados e Integración ELO
Crear `backend/src/services/torneo_resultado_service.py`:
- Cargar resultado de partido
- Validar sets
- Actualizar tabla de posiciones
- **Llamar a EloController existente**
- Guardar en historial_rating

### Paso 6: Fase de Eliminación
Crear `backend/src/services/torneo_eliminacion_service.py`:
- Obtener clasificados
- Calcular byes
- Generar cuadro de eliminación
- Avanzar ganadores

### Paso 7: Controller y Endpoints
Crear `backend/src/controllers/torneo_controller.py`:
- Endpoints REST para todas las operaciones
- Validación de permisos
- Manejo de errores

### Paso 8: Frontend (Después)
- Páginas de torneos
- Inscripción
- Vista de zonas y fixture
- Cuadro de eliminación
- Panel de administración

## 🎯 Ventajas de esta Arquitectura

1. **Unificación**: Un solo lugar para todos los partidos
2. **ELO Consistente**: Mismo cálculo para AMD y torneos
3. **Historial Único**: Todo en `historial_rating`
4. **Flexibilidad**: Fácil agregar nuevos tipos de partidos
5. **Compatibilidad**: No rompe nada existente

## 📊 Estructura de Datos

### Partido AMD (actual)
```python
{
    "tipo": "amistoso",
    "id_torneo": null,
    "id_sala": 123,
    "zona_id": null,
    "fase": null,
    # ... resto de campos AMD
}
```

### Partido de Torneo (nuevo)
```python
{
    "tipo": "torneo",
    "id_torneo": 5,
    "id_sala": null,
    "zona_id": 12,
    "fase": "zona",
    "pareja1_id": 45,
    "pareja2_id": 46,
    "cancha_id": 3,
    "fecha_hora": "2025-11-30 18:00:00",
    # ... resto de campos
}
```

## 🔄 Flujo Completo de un Torneo

1. Organizador crea torneo → `torneos`
2. Jugadores se inscriben → `torneos_parejas`
3. Jugadores cargan restricciones → `torneo_bloqueos_jugador`
4. Organizador define canchas → `torneo_canchas`
5. Organizador crea slots → `torneo_slots`
6. Sistema genera zonas → `torneo_zonas`, `torneo_zona_parejas`
7. Sistema genera fixture → `partidos` (tipo='torneo', fase='zona')
8. Sistema programa horarios → actualiza `partidos.fecha_hora`, `partidos.cancha_id`
9. Se juegan partidos → organizador carga resultados
10. Sistema actualiza ELO → `historial_rating`
11. Sistema actualiza tabla → `torneo_tabla_posiciones`
12. Sistema genera cuadro final → `partidos` (fase='8vos', '4tos', etc.)
13. Se juega eliminación → campeón

## 🚀 ¿Empezamos con el Paso 1?

Puedo crear ahora `torneo_service.py` con las operaciones CRUD básicas.
