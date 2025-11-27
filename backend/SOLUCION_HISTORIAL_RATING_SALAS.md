# Solución: Historial de Rating para Partidos de Sala

## Problema

Los partidos de sala mostraban "null" en el cambio de rating en el historial de MiPerfil, mientras que los partidos antiguos sí mostraban el cambio (+16, -9, etc.).

## Causa Raíz

El sistema de salas tiene un bug: cuando se aplica el Elo después de confirmar un resultado, actualiza los campos en la tabla `partido_jugadores`:
- `rating_antes`
- `rating_despues`
- `cambio_elo`

Pero NO crea entradas en la tabla `historial_rating`, que es la que usa el endpoint de historial para mostrar los cambios de rating.

## Solución Implementada

### 1. Script de Migración

Creado `crear_historial_rating_salas.py` que:
- Busca partidos con `elo_aplicado = true` y `id_sala IS NOT NULL`
- Verifica que NO tengan entrada en `historial_rating`
- Crea las entradas faltantes usando los datos de `partido_jugadores`

### 2. Resultados

Se crearon **12 entradas** de historial de rating para 3 partidos de sala:
- Partido 17: 4 jugadores
- Partido 19: 4 jugadores  
- Partido 20: 4 jugadores

### 3. Ejemplo de Datos Creados

**Partido 20 - Usuario facundo (ID: 14)**
- Rating antes: 1299
- Delta: -3
- Rating después: 1296

**Partido 19 - Usuario facundo (ID: 14)**
- Rating antes: 1296
- Delta: -3
- Rating después: 1293

## Verificación

Después de ejecutar el script, el endpoint `/partidos/usuario/14` ahora devuelve:

```json
{
  "id_partido": 20,
  "historial_rating": {
    "rating_antes": 1299,
    "delta": -3,
    "rating_despues": 1296
  }
}
```

En lugar de:
```json
{
  "id_partido": 20,
  "historial_rating": null
}
```

## Solución Permanente Recomendada

Para evitar este problema en el futuro, el sistema de salas debería modificarse para que cuando se aplica el Elo (en `confirmacion_service.py` o donde se procese), también cree las entradas en `historial_rating`.

Actualmente el código hace:
```python
# Actualizar partido_jugadores
pj.rating_antes = rating_actual
pj.rating_despues = nuevo_rating
pj.cambio_elo = delta
```

Debería también hacer:
```python
# Crear entrada en historial_rating
historial = HistorialRating(
    id_usuario=pj.id_usuario,
    id_partido=partido.id_partido,
    rating_antes=rating_actual,
    delta=delta,
    rating_despues=nuevo_rating
)
db.add(historial)
```

## Archivos Relacionados

- `backend/crear_historial_rating_salas.py` - Script de migración
- `backend/src/services/confirmacion_service.py` - Servicio que aplica Elo (necesita corrección)
- `backend/src/controllers/partido_controller.py` - Endpoint de historial
- `backend/src/models/playt_models.py` - Modelos de datos

## Estado Actual

✅ Problema resuelto para partidos existentes
⚠️ Pendiente: Corregir el código de salas para que cree historial_rating automáticamente en futuros partidos
