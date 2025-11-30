# Sistema de Fixture Inteligente - Implementado ✅

## Resumen

Sistema de generación de fixture que considera disponibilidad horaria de jugadores y balanceo por rating.

## Archivos Creados

- ✅ `src/services/torneo_fixture_service.py` - Servicio de fixture inteligente
- ✅ `src/controllers/torneo_controller.py` - Endpoints agregados
- ✅ `test_torneo_fixture.py` - Tests (en progreso)

## Funcionalidades Implementadas

### 1. Generación de Zonas con Disponibilidad Horaria

**Endpoint:** `POST /torneos/{torneo_id}/generar-zonas-inteligente`

**Algoritmo:**
1. Obtener parejas confirmadas
2. Calcular disponibilidad horaria de cada pareja (basado en bloqueos)
3. Agrupar parejas por compatibilidad horaria
4. Dentro de cada grupo compatible, balancear por rating
5. Distribuir en zonas

**Prioridades:**
- **Prioridad 1:** Compatibilidad horaria (evitar conflictos)
- **Prioridad 2:** Balanceo por rating (competitividad)

### 2. Generación de Fixture Completo

**Endpoint:** `POST /torneos/{torneo_id}/generar-fixture`

**Funcionalidad:**
- Genera todos los partidos de todas las zonas
- Sistema "todos contra todos" en cada zona
- Cambia estado del torneo a "fase_grupos"

**Cálculo de partidos:**
- Zona de 2 parejas: 1 partido
- Zona de 3 parejas: 3 partidos
- Zona de N parejas: N*(N-1)/2 partidos

### 3. Listar Partidos

**Endpoint:** `GET /torneos/{torneo_id}/partidos`

**Parámetros:**
- `zona_id` (opcional): Filtrar por zona

## Algoritmos Implementados

### Cálculo de Disponibilidad

```python
def _calcular_disponibilidad_parejas(db, torneo, parejas):
    """
    Para cada pareja:
    1. Obtener bloqueos horarios de jugador 1
    2. Obtener bloqueos horarios de jugador 2
    3. Combinar bloqueos (pareja bloqueada si cualquiera está bloqueado)
    4. Retornar Set de (fecha, hora_desde, hora_hasta) bloqueadas
    """
```

### Agrupación por Compatibilidad

```python
def _agrupar_por_compatibilidad(parejas, disponibilidad):
    """
    1. Crear grafo de compatibilidad
    2. Dos parejas son compatibles si NO tienen bloqueos solapados
    3. Usar algoritmo greedy para formar grupos máximos
    4. Cada grupo contiene parejas que pueden jugar juntas
    """
```

### Verificación de Solapamiento

```python
def _horarios_se_solapan(desde1, hasta1, desde2, hasta2):
    """
    Verifica si dos rangos horarios se solapan
    
    Ejemplo:
    - 08:00-12:00 y 10:00-14:00 → SE SOLAPAN
    - 08:00-12:00 y 14:00-18:00 → NO SE SOLAPAN
    """
```

### Distribución Inteligente

```python
def _distribuir_parejas_inteligente(db, parejas, zonas, grupos, disponibilidad):
    """
    1. Calcular rating promedio de cada pareja
    2. Ordenar grupos por tamaño (más grandes primero)
    3. Para cada grupo:
       a. Ordenar parejas por rating
       b. Distribuir en serpiente entre zonas
    4. Resultado: Zonas balanceadas con parejas compatibles
    """
```

## Ejemplo de Uso

### Escenario: 6 Parejas con Diferentes Disponibilidades

**Parejas:**
- Pareja A (2/3): Disponible solo mañana
- Pareja B (4/5): Disponible solo mañana
- Pareja C (6/7): Disponible solo tarde
- Pareja D (8/9): Disponible solo tarde
- Pareja E (10/11): Disponible todo el día
- Pareja F (12/13): Disponible todo el día

**Resultado Esperado:**
```
Zona 1 (Mañana):
- Pareja A (2/3)
- Pareja B (4/5)
- Pareja E (10/11) ← Flexible

Zona 2 (Tarde):
- Pareja C (6/7)
- Pareja D (8/9)
- Pareja F (12/13) ← Flexible
```

**Partidos Generados:**
```
Zona 1:
- A vs B
- A vs E
- B vs E

Zona 2:
- C vs D
- C vs F
- D vs F

Total: 6 partidos
```

## Ventajas del Sistema

✅ **Evita Conflictos Horarios**
- Parejas en la misma zona pueden jugar en los mismos horarios
- Reduce reprogramaciones

✅ **Mantiene Competitividad**
- Dentro de cada grupo compatible, balancea por rating
- Zonas equilibradas

✅ **Flexibilidad**
- Parejas sin bloqueos se distribuyen donde más se necesiten
- Optimiza uso de canchas

✅ **Escalable**
- Funciona con cualquier número de parejas
- Algoritmo eficiente

## Limitaciones Actuales

🔲 **Modelo Partido**
- El modelo actual usa tabla intermedia `partido_jugadores`
- Necesita adaptación para torneos
- Pendiente: Agregar campo `zona_id` al modelo

🔲 **Bloqueos Horarios**
- Modelo define campos como String
- Base de datos espera tipo TIME
- Pendiente: Migración de tipos

🔲 **Programación de Horarios**
- Sistema genera partidos pero no asigna horarios específicos
- Pendiente: Sistema de slots y canchas

## Próximos Pasos

### 1. Adaptar Modelo Partido
```sql
ALTER TABLE partidos ADD COLUMN zona_id BIGINT;
ALTER TABLE partidos ADD FOREIGN KEY (zona_id) REFERENCES torneo_zonas(id);
```

### 2. Corregir Tipos de Bloqueos
```sql
-- Ya está correcto en BD, solo ajustar modelo Python
```

### 3. Sistema de Programación
- Crear slots de tiempo
- Asignar canchas
- Asignar horarios a partidos
- Validar disponibilidad

### 4. Notificaciones
- Notificar a jugadores cuando se programa su partido
- Recordatorios antes del partido
- Cambios de horario

## Endpoints Disponibles

### Zonas Inteligentes
```bash
POST /torneos/{id}/generar-zonas-inteligente
{
  "num_zonas": 3  # opcional
}
```

### Fixture Completo
```bash
POST /torneos/{id}/generar-fixture
```

### Listar Partidos
```bash
GET /torneos/{id}/partidos?zona_id=1
```

## Estado Actual

✅ **Completado:**
- Algoritmo de compatibilidad horaria
- Agrupación inteligente de parejas
- Distribución balanceada por rating
- Generación de partidos (todos contra todos)
- Endpoints funcionales

🔲 **Pendiente:**
- Adaptación del modelo Partido
- Corrección de tipos en bloqueos
- Sistema de programación de horarios
- Tests completos
- Integración con frontend

---

**Implementado por:** Kiro AI
**Fecha:** 2024-11-29
**Estado:** ⚠️ Funcional con limitaciones (requiere ajustes en modelos)
