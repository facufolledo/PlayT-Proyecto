# Algoritmo Elo V3 - Sistema Completamente Rediseñado 🎾

## 📋 Resumen Ejecutivo

El algoritmo Elo V3 es una mejora profunda del sistema de rating para pádel 2vs2 que soluciona todos los problemas de inconsistencia del sistema anterior.

### ✅ Problemas Solucionados

1. **Caps planos** → Ahora los caps escalan con el margen de victoria
2. **Upsets sin impacto** → Multiplicador de sorpresa amplifica victorias inesperadas
3. **Cambios ridículos** → Mínimos garantizados (+25 favorito, -15 underdog)
4. **K factors descontrolados** → Valores más conservadores y predecibles
5. **Distribución injusta** → Reparto 50/50 entre jugadores del equipo

---

## 🧮 Fórmula Completa (Paso a Paso)

### 1. Calcular Expectativa (E)
```
E_team = 1 / (1 + 10^(-(Ra - Rb) / 400))
```
- Ra = rating promedio equipo A
- Rb = rating promedio equipo B
- 400 = escala Elo estándar

### 2. Calcular Score Ajustado (S)
```
S_base = 1.0 si ganó, 0.0 si perdió
S_ajustado = S_base + ajuste_margen

ajuste_margen = (0.4 × sets_ratio + 0.6 × games_ratio) - 0.5
ajuste_margen ∈ [-0.25, +0.25]
```

### 3. Obtener Factor K
```
K_efectivo = K_base × volatilidad

K_base según experiencia:
- Nuevo (0-5 partidos): 100
- Intermedio (6-15 partidos): 80
- Estable (16-40 partidos): 50
- Experto (41+ partidos): 40
```

### 4. Calcular Delta Base
```
delta_base = K_efectivo × (S_ajustado - E)
```

### 5. Calcular Factor de Margen (0.70 a 1.30)
```
score_margen = 0.0

# Componente 1: Diferencia de sets (30%)
if sets_diff == 2: score += 0.30
elif sets_diff == 1: score += 0.10

# Componente 2: Diferencia de games (35%)
games_ratio = games_diff / total_games
if games_ratio >= 0.50: score += 0.35
elif games_ratio >= 0.35: score += 0.28
elif games_ratio >= 0.20: score += 0.18
elif games_ratio >= 0.10: score += 0.08

# Componente 3: Sets dominantes (20%)
if 2 sets dominantes (6-0, 6-1, 6-2): score += 0.20
elif 1 set dominante: score += 0.12

# Componente 4: Tie-breaks (15%, negativo)
if 2 tie-breaks (7-6): score -= 0.15
elif 1 tie-break: score -= 0.08

# Normalizar a rango [0.70, 1.30]
factor_margen = 0.70 + (score + 0.15) × 0.60
```

### 6. Calcular Multiplicador de Sorpresa (1.0 a 3.0)
```
Si NO es upset: mult_sorpresa = 1.0

Si ES upset (underdog gana):
  rating_diff = |Ra - Rb|
  normalized = min(rating_diff, 400) / 400
  
  Según tipo de partido:
  - Amistoso: mult = 1.0 + normalized × 0.3  → [1.0, 1.3]
  - Torneo: mult = 1.0 + normalized × 1.0    → [1.0, 2.0]
  - Final: mult = 1.0 + normalized × 2.0     → [1.0, 3.0]
```

### 7. Amplificar Delta
```
delta_amplified = delta_base × factor_margen × mult_sorpresa
```

### 8. Aplicar Mínimos Garantizados
```
Si favorito gana y 0 < delta < 25×factor_margen:
  delta = 25 × factor_margen

Si underdog pierde y -15×factor_margen < delta < 0:
  delta = -15 × factor_margen
```

### 9. Obtener Caps Dinámicos
```
caps_base según tipo de partido y rol (ver tabla abajo)
caps_dinámicos = caps_base × factor_margen
```

### 10. Aplicar Caps
```
delta_final = clamp(delta_amplified, cap_loss_dinámico, cap_win_dinámico)
```

### 11. Distribuir Entre Jugadores
```
delta_jugador_1 = delta_final / 2
delta_jugador_2 = delta_final / 2
```

---

## 📊 Caps Base por Tipo de Partido

### Amistosos (cambios pequeños)
| Rol | Victoria | Derrota |
|-----|----------|---------|
| Underdog | +22 | -18 |
| Favorito | +12 | -22 |

### Torneos (cambios moderados)
| Rol | Victoria | Derrota |
|-----|----------|---------|
| Underdog | +90 | -35 |
| Favorito | +55 | -55 |

### Finales (cambios grandes)
| Rol | Victoria | Derrota |
|-----|----------|---------|
| Underdog | +170 | -70 |
| Favorito | +65 | -85 |

**IMPORTANTE:** Estos caps se multiplican por el factor de margen (0.70 a 1.30)

---

## 🎯 Resultados Esperados (Ejemplos)

### Escenario 1: Torneo - Underdog gana 6-4 / 6-4
- **Underdog:** +97 puntos (equipo), +49 por jugador
- **Favorito:** -49 puntos (equipo), -24 por jugador
- Factor margen: 1.08 (victoria clara)
- Mult. sorpresa: 2.0

### Escenario 2: Torneo - Underdog gana 7-6 / 7-6
- **Underdog:** +79 puntos (MENOS que esc.1)
- **Favorito:** -40 puntos
- Factor margen: 0.88 (muy ajustado)
- Mult. sorpresa: 2.0

### Escenario 3: Torneo - Underdog gana 6-0 / 6-1
- **Underdog:** +117 puntos (MÁS que esc.1)
- **Favorito:** -59 puntos
- Factor margen: 1.30 (paliza)
- Mult. sorpresa: 2.0

### Escenario 4: Final - Underdog gana 6-4 / 6-4
- **Underdog:** +147 puntos (mucho más que torneo)
- **Favorito:** -49 puntos
- Factor margen: 1.08
- Mult. sorpresa: 3.0 (final amplifica más)

### Escenario 5: Final - Underdog gana 6-0 / 6-0
- **Underdog:** +177 puntos (cerca del cap máximo)
- **Favorito:** -59 puntos
- Factor margen: 1.30
- Mult. sorpresa: 3.0

### Escenario 6: Torneo - Favorito gana 6-4 / 6-4
- **Favorito:** +27 puntos (ganó lo esperado)
- **Underdog:** -16 puntos
- Factor margen: 1.08
- Mult. sorpresa: 1.0 (sin sorpresa)

### Escenario 7: Torneo - Favorito gana 6-0 / 6-0
- **Favorito:** +32 puntos (un poco más que esc.6)
- **Underdog:** -19 puntos
- Factor margen: 1.30
- Mult. sorpresa: 1.0

### Escenario 8: Amistoso - Underdog gana 6-4 / 6-4
- **Underdog:** +24 puntos (MUCHO menos que torneo)
- **Favorito:** -24 puntos
- Factor margen: 1.08
- Mult. sorpresa: 1.3 (amistoso amplifica poco)

---

## 🔧 Cómo Ajustar el Sistema

### Para hacer el sistema MÁS AGRESIVO:
1. Aumentar K_FACTORS (×1.2)
2. Aumentar CAPS_BASE (×1.2)
3. Aumentar MARGIN_FACTOR_MAX (de 1.30 a 1.40)
4. Aumentar SURPRISE_MULTIPLIER_MAX (de 3.0 a 3.5 en finales)

### Para hacer el sistema MÁS CONSERVADOR:
1. Reducir K_FACTORS (×0.8)
2. Reducir CAPS_BASE (×0.8)
3. Reducir MARGIN_FACTOR_MAX (de 1.30 a 1.20)
4. Reducir SURPRISE_MULTIPLIER_MAX (de 3.0 a 2.5 en finales)

### Para dar MÁS PESO al margen de victoria:
1. Aumentar MARGIN_FACTOR_MAX (de 1.30 a 1.50)
2. Reducir MARGIN_FACTOR_MIN (de 0.70 a 0.60)

### Para dar MENOS PESO al margen de victoria:
1. Reducir MARGIN_FACTOR_MAX (de 1.30 a 1.15)
2. Aumentar MARGIN_FACTOR_MIN (de 0.70 a 0.85)

---

## 📁 Archivos del Sistema

### Configuración
- `backend/src/services/elo_config_v2.py` - Todas las constantes y configuración

### Servicio
- `backend/src/services/elo_service_v2.py` - Lógica de cálculo

### Tests
- `backend/test_elo_v2_escenarios.py` - 8 escenarios de referencia

---

## 🎓 Conceptos Clave

### Umbral de Favorito/Underdog
- **Diferencia < 65 puntos:** Equipos PAREJOS
  - Ejemplo: 1400 vs 1360 (40 pts) → Sin multiplicador de sorpresa
  - Ejemplo: 1400 vs 1340 (60 pts) → Sin multiplicador de sorpresa
- **Diferencia ≥ 65 puntos:** Favorito/Underdog
  - Ejemplo: 1400 vs 1320 (80 pts) → Con multiplicador de sorpresa
  - Ejemplo: 1400 vs 1250 (150 pts) → Multiplicador moderado
  - Ejemplo: 1400 vs 1000 (400 pts) → Multiplicador máximo

### Factor de Margen
Ajusta el impacto según cómo fue la victoria:
- **0.70-0.80:** Victoria muy ajustada (tie-breaks)
- **0.95-1.05:** Victoria normal
- **1.20-1.30:** Paliza total

### Multiplicador de Sorpresa
Amplifica los upsets según:
- Diferencia de rating entre equipos (≥65 puntos)
- Tipo de partido (amistoso < torneo < final)
- Solo se aplica cuando el underdog gana

**IMPORTANTE:** Equipos con diferencia < 65 puntos se consideran PAREJOS (sin multiplicador)

### Caps Dinámicos
Los caps NO son fijos, sino que escalan con el margen:
- Victoria ajustada → cerca del cap mínimo
- Victoria por paliza → cerca del cap máximo

### Mínimos Garantizados
Evitan cambios ridículos:
- Favorito que gana: mínimo +25 (ajustado por margen)
- Underdog que pierde: mínimo -15 (ajustado por margen)

### WO (Walk Over)
Cambio fijo independiente del rating:
- **Equipo ganador:** +10 puntos (+5 por jugador)
- **Equipo perdedor:** -20 puntos (-10 por jugador, penalización por irresponsabilidad)
- No se aplica ningún multiplicador ni factor de margen
- La volatilidad no cambia en WO
- El perdedor recibe el doble de penalización por no presentarse

---

## ✅ Ventajas del Sistema V3

1. **Predecible:** Los resultados son consistentes y lógicos
2. **Justo:** Diferencia entre victoria ajustada y paliza
3. **Escalable:** Funciona bien en todos los tipos de partido
4. **Configurable:** Fácil de ajustar sin tocar la lógica
5. **Robusto:** No genera cambios absurdos (+2, -1, etc.)
6. **Motivador:** Los upsets tienen impacto real

---

## 🚀 Próximos Pasos

1. ✅ Implementar en producción
2. ✅ Ejecutar migración de datos
3. ⏳ Monitorear resultados reales
4. ⏳ Ajustar constantes si es necesario
5. ⏳ Documentar casos edge

---

## 📞 Soporte

Si necesitas ajustar el sistema:
1. Revisa la sección "Cómo Ajustar el Sistema"
2. Modifica las constantes en `elo_config_v2.py`
3. Ejecuta los tests: `python backend/test_elo_v2_escenarios.py`
4. Verifica que todos los escenarios pasen

**NUNCA** modifiques la lógica de cálculo sin entender completamente el sistema.
