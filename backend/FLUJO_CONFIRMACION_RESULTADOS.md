# Flujo de Confirmación de Resultados - PlayT

## Descripción General

Este documento describe el nuevo flujo implementado para la confirmación de resultados de partidos en PlayT. El sistema ahora requiere que ambos equipos estén de acuerdo antes de calcular y aplicar los cambios de rating Elo, con responsabilidades completamente separadas.

## 🔄 Flujo de Estados

```
PENDIENTE → REPORTADO → CONFIRMADO → ELO_CALCULADO
     ↓           ↓          ↓           ↓
   Crear    Reportar    Confirmar   Calcular
  Partido   Resultado   Resultado     Elo
            (Sin Elo)   (Sin Elo)   (Con Elo)
```

## 📋 Endpoints Disponibles

### 1. Reportar Resultado
```
POST /partidos/{partido_id}/resultado
```

**Propósito**: Reportar el resultado de un partido sin calcular Elo aún.

**Estado del partido**: `pendiente` → `reportado`

**Validaciones**:
- Partido debe estar en estado "pendiente"
- Usuario debe ser jugador del partido
- Solo se guarda el resultado, NO se calcula Elo

**Respuesta**:
```json
{
    "message": "Resultado reportado exitosamente. El equipo rival debe confirmarlo para calcular el ranking Elo.",
    "estado": "reportado",
    "resultado": {
        "sets_equipo1": 2,
        "sets_equipo2": 1,
        "desenlace": "normal",
        "reportado_por": "usuario123"
    }
}
```

### 2. Confirmar Resultado
```
POST /partidos/{partido_id}/confirmar
```

**Propósito**: Confirmar el resultado reportado (sin calcular Elo aún).

**Estado del partido**: `reportado` → `confirmado`

**Validaciones**:
- Partido debe estar en estado "reportado"
- Usuario NO debe ser el que reportó el resultado
- Usuario debe ser jugador del partido rival
- Solo se confirma el resultado, NO se calcula Elo

**Respuesta**:
```json
{
    "message": "Resultado confirmado exitosamente. Ahora se puede calcular el ranking Elo.",
    "estado": "confirmado",
    "resultado": {
        "sets_equipo1": 2,
        "sets_equipo2": 1,
        "desenlace": "normal",
        "confirmado_por": "usuario456"
    }
}
```

### 3. Calcular Elo
```
POST /partidos/{partido_id}/calcular-elo
```

**Propósito**: Calcular el ranking Elo para un partido confirmado.

**Estado del partido**: `confirmado` → `confirmado` (estado no cambia, pero se marca como Elo calculado)

**Validaciones**:
- Partido debe estar en estado "confirmado"
- Usuario debe ser jugador del partido
- Elo no debe haber sido calculado previamente
- Solo se calcula Elo, NO se cambia estado

**Respuesta**:
```json
{
    "message": "Ranking Elo avanzado calculado y aplicado exitosamente",
    "equipo1": {
        "sets": 2,
        "rating_antes": 1255.0,
        "rating_despues": 1247.3,
        "cambio": -15.3,
        "jugadores": [...]
    },
    "equipo2": {
        "sets": 1,
        "rating_antes": 1100.0,
        "rating_despues": 1107.9,
        "cambio": +15.9,
        "jugadores": [...]
    },
    "detalles_elo": {
        "expectativa_equipo1": 0.709,
        "expectativa_equipo2": 0.291,
        "puntuacion_real_equipo1": 0.258,
        "puntuacion_real_equipo2": 0.742,
        "multiplicador_sets": 1.1,
        "factor_k_equipo1": 32.0,
        "factor_k_equipo2": 32.0,
        "suavizador_equipo1": 0.964,
        "suavizador_equipo2": 1.0,
        "caps_equipo1": [25, -35],
        "caps_equipo2": [35, -25]
    }
}
```

## 🛡️ Validaciones de Seguridad

### Para Reportar Resultado
- ✅ Usuario autenticado
- ✅ Usuario es jugador del partido
- ✅ Partido en estado "pendiente"
- ✅ Datos de resultado válidos

### Para Confirmar Resultado
- ✅ Usuario autenticado
- ✅ Usuario es jugador del partido
- ✅ Partido en estado "reportado"
- ✅ Usuario NO es el que reportó
- ✅ Resultado existe en la base de datos

### Para Calcular Elo
- ✅ Usuario autenticado
- ✅ Usuario es jugador del partido
- ✅ Partido en estado "confirmado"
- ✅ Elo no ha sido calculado previamente

## 🔐 Reglas de Negocio

1. **Un equipo no puede confirmar su propio resultado**
   - Solo el equipo rival puede confirmar
   - Previene confirmaciones automáticas o fraudulentas

2. **El Elo solo se calcula tras confirmación**
   - Garantiza que ambos equipos estén de acuerdo
   - Evita cambios de rating por resultados incorrectos

3. **Estados secuenciales obligatorios**
   - No se puede saltar de "pendiente" a "confirmado"
   - No se puede calcular Elo sin confirmación previa
   - Flujo controlado y auditado

4. **Transacciones atómicas**
   - Si falla cualquier paso, se hace rollback
   - Consistencia de datos garantizada

5. **Responsabilidades separadas**
   - Reportar: Solo guarda resultado
   - Confirmar: Solo confirma resultado
   - Calcular Elo: Solo calcula y aplica ratings

## 📊 Casos de Uso

### Caso 1: Partido Normal
1. Equipo A reporta resultado (2-1)
2. Equipo B confirma resultado
3. Cualquier jugador calcula Elo
4. Ratings se actualizan y partido queda completo

### Caso 2: Resultado Incorrecto
1. Equipo A reporta resultado incorrecto (2-0)
2. Equipo B puede disputar o reportar resultado correcto
3. No se confirma hasta que haya acuerdo
4. No se calcula Elo hasta confirmación

### Caso 3: Partido Abandonado
1. Equipo A reporta resultado con desenlace "retiro"
2. Equipo B confirma el abandono
3. Se calcula Elo considerando sets jugados

## 🚀 Ventajas del Nuevo Sistema

1. **Seguridad**: Triple verificación antes de aplicar cambios
2. **Auditoría**: Historial completo de reportes, confirmaciones y cálculos Elo
3. **Flexibilidad**: Posibilidad de disputar resultados incorrectos
4. **Consistencia**: Elo solo se calcula con acuerdo mutuo
5. **Escalabilidad**: Fácil agregar lógicas adicionales (notificaciones, etc.)
6. **Separación de Responsabilidades**: Cada endpoint tiene una función específica
7. **Reutilización**: El endpoint de calcular Elo puede usarse independientemente

## 🔧 Implementación Técnica

### Archivos Modificados
- `src/controllers/partido_controller.py`: Tres endpoints separados
- `src/services/elo_service.py`: Algoritmo Elo avanzado
- `src/services/elo_config.py`: Configuración del sistema

### Base de Datos
- Tabla `partidos`: Campo `estado` con valores: `pendiente`, `reportado`, `confirmado`
- Tabla `resultados_partido`: Almacena resultados reportados
- Tabla `historial_rating`: Historial de cambios de rating (previene doble cálculo)

### Transacciones
- Cada endpoint maneja transacciones de base de datos
- Rollback automático en caso de error
- Consistencia de datos garantizada

## 📝 Próximas Mejoras

1. **Notificaciones**: Alertar cuando se reporta o confirma un resultado
2. **Timeouts**: Confirmación automática después de cierto tiempo
3. **Disputas**: Sistema para resolver desacuerdos
4. **Auditoría**: Logs detallados de todas las acciones
5. **API de Estado**: Endpoint para consultar estado actual del partido
6. **Batch Elo**: Calcular Elo para múltiples partidos confirmados

## 🎯 Conclusión

El nuevo sistema de confirmación proporciona un flujo seguro y controlado para la gestión de resultados de partidos con responsabilidades completamente separadas. Al requerir confirmación del equipo rival antes de permitir el cálculo de Elo, se garantiza la integridad del sistema de rankings y se previene la manipulación de resultados. La separación en tres endpoints permite mayor flexibilidad y control sobre cada etapa del proceso.
