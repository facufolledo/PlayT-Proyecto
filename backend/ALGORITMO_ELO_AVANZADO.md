# Algoritmo Elo Avanzado para Pádel 2 vs 2

## Descripción General

Este documento describe la implementación del algoritmo Elo avanzado específicamente diseñado para el proyecto PlayT, optimizado para partidos de pádel 2 vs 2. El algoritmo considera múltiples factores que van más allá del Elo estándar, incluyendo experiencia de jugadores, margen de victoria, y suavizadores para favoritos.

## Características Principales

### 1. **Sistema de Equipos 2 vs 2**
- Calcula rating promedio del equipo basado en los ratings individuales
- Aplica cambios de rating a cada jugador individualmente
- Mantiene simetría entre equipos

### 2. **Factor K Dinámico por Experiencia**
- **Nuevo** (≤5 partidos): K = 48
- **Intermedio** (6-15 partidos): K = 40  
- **Estable** (16-40 partidos): K = 32
- **Experto** (>40 partidos): K = 24

### 3. **Multiplicador por Diferencia de Sets**
- Fórmula: `1 + 0.1 * |setsA - setsB|`
- Ejemplos:
  - 2-0: multiplicador = 1.2
  - 2-1: multiplicador = 1.1
  - 1-1: multiplicador = 1.0

### 4. **Margen de Games**
- Considera la diferencia total de games entre equipos
- Fórmula: `clamp((gamesA - gamesB) / max(12, totalGames) * 0.3, -0.15, 0.15)`
- Capado a ±0.15 para evitar que los games dominen el resultado

### 5. **Suavizador de Derrotas para Favoritos**
- Reduce el castigo cuando un favorito pierde por poco
- Fórmula: `0.6 + 0.4 * (actual_score / expected_score)`
- Solo se aplica cuando el favorito no cumple expectativas

### 6. **Caps por Rol**
- **Underdog**: +35/-25 (mayor premio por victoria)
- **Favorito**: +25/-35 (castigo moderado por derrota)

## Flujo del Algoritmo

### Paso 1: Cálculo de Ratings de Equipo
```
RA = (rA1 + rA2) / 2
RB = (rB1 + rB2) / 2
```

### Paso 2: Expectativa de Victora
```
E_A = 1 / (1 + 10^(-(RA - RB)/400))
E_B = 1 - E_A
```

### Paso 3: Puntuación Real
```
# Base por sets
S_sets_A = setsA / (setsA + setsB)

# Ajuste por games
g_margin = clamp((gamesA - gamesB)/max(12, totalGames) * 0.3, -0.15, 0.15)
S_A = clamp(S_sets_A + g_margin, 0, 1)
```

### Paso 4: Factores K y Multiplicadores
```
K_team_A = (K(rA1) + K(rA2)) / 2
f_sets = 1 + 0.1 * |setsA - setsB|
```

### Paso 5: Delta Base
```
Δ_base_A = K_team_A * (S_A - E_A) * f_sets
Δ_base_B = -Δ_base_A
```

### Paso 6: Suavizador de Derrotas
```
if (RA > RB and S_A < E_A):
    l_factor = 0.6 + 0.4 * (S_A / E_A)
else:
    l_factor = 1.0

Δ_soft_A = Δ_base_A * l_factor
```

### Paso 7: Aplicación de Caps
```
(cap_win, cap_loss) = get_role_caps(RA, RB)
Δ_cap_A = clamp(Δ_soft_A, cap_loss, cap_win)
```

### Paso 8: Reparto a Jugadores
```
Δ_A1 = Δ_A2 = Δ_cap_A / 2
Δ_B1 = Δ_B2 = -Δ_cap_A / 2
```

## Casos Especiales

### Walk Over (WO)
- Ganador: S = 1.0
- Perdedor: S = 0.0
- No se consideran games ni sets

### Retiro
- Puntuación ponderada por sets jugados
- Fórmula: `sets_ganados / total_sets_jugados`

## Ejemplo de Cálculo

### Datos del Partido
- **Equipo A**: Jugadores con ratings 1250 y 1260 (promedio: 1255)
- **Equipo B**: Jugadores con ratings 1110 y 1090 (promedio: 1100)
- **Resultado**: Equipo B gana 2-1
- **Games**: Equipo B +3 games de diferencia

### Cálculos
1. **Expectativa**: A = 0.709, B = 0.291
2. **Puntuación por sets**: A = 0.333, B = 0.667
3. **Margen de games**: +0.075
4. **Puntuación final**: A = 0.258, B = 0.742
5. **Factor K promedio**: A = 24 (estable), B = 32 (intermedio)
6. **Multiplicador sets**: 1.1
7. **Delta base**: A = -11.91
8. **Suavizador**: 0.746 (A era favorito y perdió)
9. **Delta final**: A = -8.88, B = +8.88

### Resultado Final
- **Equipo A**: 1255.0 → 1247.3 (Δ: -15.3)
- **Equipo B**: 1100.0 → 1107.9 (Δ: +15.9)

## Parámetros Configurables

### Escala Elo
- **Valor actual**: 400
- **Efecto**: Reducir aumenta cambios por misma diferencia de rating

### Factores K por Experiencia
- **Rangos**: Personalizables según necesidades del torneo
- **Efecto**: Valores más altos = cambios más rápidos

### Multiplicador por Sets
- **Valor actual**: 0.1 por set de diferencia
- **Efecto**: Ajusta la importancia de la diferencia de sets

### Margen de Games
- **Cap actual**: ±0.15
- **Multiplicador**: 0.3
- **Efecto**: Controla la influencia de los games en el resultado

### Suavizador de Derrotas
- **Piso actual**: 0.6
- **Techo actual**: 1.0
- **Efecto**: Reduce castigo a favoritos que pierden por poco

### Caps por Rol
- **Underdog**: Personalizables
- **Favorito**: Personalizables
- **Efecto**: Controla la volatilidad del sistema

## Ventajas del Algoritmo

1. **Justicia**: Considera múltiples factores del partido
2. **Estabilidad**: Suavizadores evitan cambios extremos
3. **Flexibilidad**: Adaptable a diferentes niveles de competencia
4. **Transparencia**: Cálculos claros y auditables
5. **Especialización**: Diseñado específicamente para pádel 2 vs 2

## Implementación Técnica

### Archivos Principales
- `src/services/elo_service.py`: Lógica principal del algoritmo
- `src/controllers/partido_controller.py`: Integración con la API
- `test_elo_advanced.py`: Pruebas y validación

### Clases y Métodos
- `EloService.calculate_match_ratings()`: Método principal
- `EloService.calculate_expected_score()`: Expectativa Elo
- `EloService.calculate_games_margin()`: Margen de games
- `EloService.calculate_loss_softener()`: Suavizador de derrotas

### Estructura de Respuesta
```python
{
    "team_a": {
        "old_rating": float,
        "new_rating": float,
        "rating_change": float,
        "players": [...]
    },
    "team_b": {...},
    "match_details": {
        "expected_a": float,
        "expected_b": float,
        "actual_score_a": float,
        "actual_score_b": float,
        "sets_multiplier": float,
        "team_a_k": float,
        "team_b_k": float,
        "loss_softener_a": float,
        "loss_softener_b": float,
        "caps_a": tuple,
        "caps_b": tuple
    }
}
```

## Próximas Mejoras

1. **Configuración por Torneo**: Diferentes parámetros según el evento
2. **Historial de Cambios**: Tracking de modificaciones en parámetros
3. **Análisis Estadístico**: Métricas de rendimiento del algoritmo
4. **Ajuste Automático**: Optimización de parámetros basada en datos
5. **Interfaz de Configuración**: Panel para ajustar parámetros

## Conclusión

El algoritmo Elo avanzado implementado proporciona un sistema de rating robusto y justo para pádel 2 vs 2, considerando múltiples factores que van más allá del Elo estándar. Su diseño modular permite fácil personalización y mantenimiento, mientras que los suavizadores y caps aseguran estabilidad en el sistema de rankings.

