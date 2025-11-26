# 🏓 Algoritmo Elo Avanzado para Pádel 2 vs 2

## 📋 Resumen

Este es un algoritmo Elo avanzado específicamente diseñado para pádel 2 vs 2, que implementa todas las mejores prácticas y funcionalidades modernas para sistemas de rating deportivo.

## ✨ Características Principales

### 🔧 Funcionalidades Básicas
- **Rating Elo estándar** con escala configurable (400 por defecto)
- **Factores K dinámicos** basados en experiencia del jugador
- **Cálculo de expectativas** usando modelo logístico
- **Caps por rol** (underdog vs favorito)
- **Suavizador de derrotas** para favoritos (bug corregido)

### 🚀 Funcionalidades Avanzadas

#### 1. **Volatilidad Dinámica**
- Factor de confianza que se ajusta según el desempeño del jugador
- Rango: 0.7-1.3 (configurable)
- Se estabiliza cuando el jugador cumple expectativas
- Aumenta cuando hay resultados sorpresivos

#### 2. **Anti-Abuso**
- Detecta partidos repetidos entre los mismos 4 jugadores
- Ventana de tiempo configurable (48h por defecto)
- Aplica multiplicador reductor (0.5 por defecto)
- Previene inflación artificial de ratings

#### 3. **Tipos de Partido**
- **Amistoso**: Caps reducidos (±15)
- **Torneo**: Caps normales (±25/35)
- **Final**: Caps aumentados (±28/38)
- Configuración completamente personalizable

#### 4. **Bonus por Margen de Victoria**
- **Sets dominantes**: Bonus por sets 6-0 o 6-1
- **Tie-breaks**: Reducción del impacto por sets 7-6
- **Games margin**: Consideración del margen total de games

#### 5. **Desenlaces Especiales**
- **Walk Over**: `wo_eq1`, `wo_eq2`
- **Retiro**: `ret_eq1`, `ret_eq2`
- Manejo específico para cada tipo de desenlace

#### 6. **Decay por Inactividad**
- Reducción gradual del rating por inactividad
- 0.5% por mes, máximo 5%
- Se aplica automáticamente en rankings

#### 7. **Configuraciones Predefinidas**
- **Amateur**: Mayor volatilidad, más incentivos
- **Profesional**: Menor volatilidad, más estabilidad
- **Desarrollo**: Máxima volatilidad para pruebas

## 🛠️ Instalación y Configuración

### 1. Dependencias
```bash
pip install -r requirements.txt
```

### 2. Migración de Base de Datos
```sql
-- Ejecutar el archivo migrations_elo_advanced.sql
-- Esto agrega todos los nuevos campos necesarios
```

### 3. Configuración Inicial
```python
from src.services.elo_config import EloConfig, TournamentConfigs

# Usar configuración por defecto
config = EloConfig.get_config_summary()

# O aplicar configuración específica
amateur_config = TournamentConfigs.get_amateur_config()
apply_custom_config(amateur_config)
```

## 📖 Uso Básico

### Cálculo Simple
```python
from src.services.elo_service import EloService

elo_service = EloService()

# Datos de jugadores
team_a = [
    {"rating": 1200, "partidos": 10, "volatilidad": 1.0, "id": 1},
    {"rating": 1100, "partidos": 5, "volatilidad": 1.2, "id": 2}
]

team_b = [
    {"rating": 1300, "partidos": 20, "volatilidad": 0.8, "id": 3},
    {"rating": 1250, "partidos": 15, "volatilidad": 0.9, "id": 4}
]

# Calcular ratings
result = elo_service.calculate_match_ratings(
    team_a_players=team_a,
    team_b_players=team_b,
    sets_a=2,
    sets_b=1,
    games_a=18,
    games_b=12,
    match_type="torneo"
)

print(f"Cambio Equipo A: {result['team_a']['rating_change']}")
print(f"Cambio Equipo B: {result['team_b']['rating_change']}")
```

### Cálculo con Detalles de Sets
```python
sets_detail = [
    {"games_a": 6, "games_b": 4},  # Set normal
    {"games_a": 6, "games_b": 1},  # Set dominante
    {"games_a": 7, "games_b": 6},  # Tie-break
]

result = elo_service.calculate_match_ratings(
    team_a_players=team_a,
    team_b_players=team_b,
    sets_a=2,
    sets_b=1,
    games_a=19,
    games_b=11,
    sets_detail=sets_detail,
    match_type="torneo"
)
```

### Walk Over y Retiros
```python
from src.services.elo_config import Desenlace

# Walk Over ganado por equipo A
result = elo_service.calculate_match_ratings(
    team_a_players=team_a,
    team_b_players=team_b,
    sets_a=2,
    sets_b=0,
    desenlace=Desenlace.WO_EQ1.value,
    match_type="torneo"
)

# Retiro ganado por equipo B
result = elo_service.calculate_match_ratings(
    team_a_players=team_a,
    team_b_players=team_b,
    sets_a=1,
    sets_b=0,
    desenlace=Desenlace.RET_EQ2.value,
    match_type="torneo"
)
```

## ⚙️ Configuración Avanzada

### Parámetros Principales
```python
# Escala Elo
EloConfig.ELO_SCALE = 400

# Volatilidad
EloConfig.VOLATILIDAD_MIN = 0.7
EloConfig.VOLATILIDAD_MAX = 1.3

# Anti-abuso
EloConfig.ABUSE_CHECK_WINDOW_H = 48
EloConfig.ABUSE_SAME4_THRESHOLD = 3
EloConfig.ABUSE_MULTIPLIER = 0.5

# Bonus por margen
EloConfig.DOMINANT_SET_BONUS = 0.05
EloConfig.TIEBREAK_REDUCTION = 0.7

# Decay por inactividad
EloConfig.DECAY_PER_MONTH = 0.005
EloConfig.DECAY_MAX = 0.05
```

### Caps por Tipo de Partido
```python
EloConfig.MATCH_TYPE_CAPS = {
    "amistoso": {"win": 15, "loss": -15},
    "torneo": {"win": 25, "loss": -35},
    "final": {"win": 28, "loss": -38}
}
```

### Factores K por Experiencia
```python
EloConfig.K_FACTORS = {
    "nuevo": {"max_partidos": 5, "k_value": 48},
    "intermedio": {"max_partidos": 15, "k_value": 40},
    "estable": {"max_partidos": 40, "k_value": 32},
    "experto": {"max_partidos": float('inf'), "k_value": 24}
}
```

## 🧪 Testing

### Ejecutar Tests Unitarios
```bash
python test_elo_advanced_complete.py
```

### Ejecutar Ejemplo Completo
```bash
python example_elo_advanced_usage.py
```

## 📊 Estructura de Datos

### Entrada de Jugadores
```python
player = {
    "rating": 1200,           # Rating actual
    "partidos": 10,           # Número de partidos jugados
    "volatilidad": 1.0,       # Factor de volatilidad
    "id": 1,                  # ID único del jugador
    "nombre": "Juan"          # Nombre (opcional)
}
```

### Resultado del Cálculo
```python
result = {
    "team_a": {
        "old_rating": 1150.0,
        "new_rating": 1175.0,
        "rating_change": 25.0,
        "players": [
            {
                "player_index": 0,
                "old_rating": 1200,
                "new_rating": 1212,
                "rating_change": 12.2,
                "old_volatility": 1.0,
                "new_volatility": 1.02
            }
        ]
    },
    "team_b": { /* similar structure */ },
    "match_details": {
        "expected_a": 0.4,
        "expected_b": 0.6,
        "actual_score_a": 0.67,
        "actual_score_b": 0.33,
        "sets_multiplier": 1.1,
        "dominant_bonus": 0.05,
        "tiebreak_reduction": 0.9,
        "team_a_k": 44.0,
        "team_b_k": 28.0,
        "loss_softener_a": 1.0,
        "loss_softener_b": 0.74,
        "caps_a": (35, -25),
        "caps_b": (25, -35),
        "match_type": "torneo",
        "abuse_detected": False,
        "desenlace": "normal"
    }
}
```

## 🔍 Funciones Utilitarias

### Validación de Configuración
```python
is_valid = EloConfig.validate_config()
```

### Aplicar Configuración Personalizada
```python
from src.services.elo_config import apply_custom_config

custom_config = {
    "volatilidad_min": 0.6,
    "volatilidad_max": 1.4,
    "dominant_set_bonus": 0.08
}

apply_custom_config(custom_config)
```

### Calcular Decay por Inactividad
```python
from datetime import datetime, timedelta

last_match = datetime.now() - timedelta(days=90)
decay_factor = elo_service.calculate_inactivity_decay(last_match)
```

## 🗄️ Base de Datos

### Nuevos Campos en `usuarios`
- `volatilidad`: Factor de volatilidad (REAL)
- `ultimo_partido_at`: Fecha del último partido (TIMESTAMPTZ)
- `categoria_sugerida`: Categoría basada en rating (VARCHAR)

### Nuevos Campos en `partidos`
- `tipo`: Tipo de partido (VARCHAR)
- `detalle_sets`: Detalles de sets (JSONB)
- `desenlace`: Tipo de desenlace (VARCHAR)
- `flag_abuso`: Flag de abuso (BOOLEAN)

### Nuevos Campos en `elo_history`
- `volatilidad_anterior` / `volatilidad_nueva`
- `factor_k_aplicado`
- `multiplicador_sets` / `bonus_dominante` / `reduccion_tiebreak`
- `suavizador_aplicado`
- `cap_win` / `cap_loss`
- `tipo_partido` / `desenlace` / `flag_abuso`

## 📈 Vistas Útiles

### Ranking con Decay
```sql
SELECT * FROM ranking_con_decay;
```

### Partidos Sospechosos
```sql
SELECT * FROM partidos_sospechosos;
```

## 🎯 Casos de Uso

### 1. Torneo Amateur
```python
# Aplicar configuración amateur
amateur_config = TournamentConfigs.get_amateur_config()
apply_custom_config(amateur_config)

# Calcular partidos con mayor volatilidad
result = elo_service.calculate_match_ratings(
    team_a_players=team_a,
    team_b_players=team_b,
    sets_a=2,
    sets_b=1,
    match_type="torneo"
)
```

### 2. Detección de Abuso
```python
# Verificar abuso antes del cálculo
abuse_detected = elo_service.check_abuse_pattern(
    team_a, team_b, match_date, recent_matches
)

if abuse_detected:
    print("⚠️ Patrón de abuso detectado")
```

### 3. Actualización de Volatilidad
```python
# Actualizar volatilidad después del partido
for player in team_a:
    new_vol = elo_service.update_player_volatility(
        player, actual_score, expected_score
    )
    # Guardar new_vol en la base de datos
```

## 🔧 Mantenimiento

### Job de Decay Mensual
```python
# Ejecutar mensualmente para aplicar decay
def apply_monthly_decay():
    # Obtener usuarios inactivos
    inactive_users = get_inactive_users()
    
    for user in inactive_users:
        decay_factor = elo_service.calculate_inactivity_decay(
            user.last_match_date
        )
        new_rating = int(user.rating * decay_factor)
        update_user_rating(user.id, new_rating)
```

### Limpieza de Datos
```python
# Limpiar flags de abuso antiguos
def cleanup_abuse_flags():
    # Resetear flags de abuso después de 48h
    reset_old_abuse_flags()
```

## 📝 Notas de Implementación

### Bug Corregido: Suavizador de Derrotas
El suavizador original tenía un bug en la fórmula:
```python
# ❌ Incorrecto (bug original)
soft_factor = FLOOR + CEILING * (actual/expected)

# ✅ Correcto (bug corregido)
span = CEILING - FLOOR
ratio = actual/expected
soft_factor = FLOOR + span * ratio
```

### Redondeo de Ratings
Los ratings se redondean al aplicar para evitar acumulación de decimales:
```python
new_rating = int(round(old_rating + delta))
```

### Validaciones Defensivas
- Verificación de equipos de 2 jugadores
- Validación de rangos de volatilidad
- Comprobación de división por cero
- Manejo de valores NaN/Inf

## 🤝 Contribución

Para contribuir al proyecto:

1. Ejecutar tests: `python test_elo_advanced_complete.py`
2. Verificar configuración: `EloConfig.validate_config()`
3. Seguir el formato de código existente
4. Documentar nuevas funcionalidades

## 📄 Licencia

Este proyecto es parte de PlayT y está sujeto a los términos de licencia del proyecto principal.

---

**Desarrollado para PlayT - Sistema de Gestión de Torneos de Pádel**

