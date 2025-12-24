# Sistema de Byes en Playoffs - PlayT

## Problema Original
Cuando el número de clasificados no es potencia de 2 (ej: 6 clasificados), algunas parejas deben avanzar automáticamente (bye) a la siguiente ronda. El sistema anterior no manejaba esto correctamente.

## Solución Implementada

### 1. Generación de Bracket con Byes (`torneo_playoff_service.py`)

La función `_generar_bracket_con_byes` ahora:

1. **Calcula la potencia de 2 más cercana** al número de clasificados
   - 6 clasificados → bracket de 8 → 2 byes
   - 5 clasificados → bracket de 8 → 3 byes

2. **Asigna seeds** a los clasificados (primeros de zona tienen mejor seed)

3. **Usa emparejamientos estándar de bracket**:
   - 8 parejas: (1vs8), (4vs5), (2vs7), (3vs6)
   - Los mejores seeds se enfrentan a los peores

4. **Crea partidos de primera ronda** solo donde hay 2 parejas reales

5. **Pre-asigna ganadores de bye** a la siguiente fase:
   - Si seed 8 no existe, seed 1 avanza automáticamente a semis
   - El partido de semis se crea con `pareja1_id = seed1` y `pareja2_id = None`

### 2. Avance de Ganadores (`torneo_resultado_service.py`)

La función `_avanzar_ganador_playoff`:

1. Cuando un partido termina, asigna el ganador al partido de siguiente fase
2. Usa la lógica: partido impar → pareja1, partido par → pareja2
3. Verifica si el partido siguiente ya tiene ambas parejas (una de bye + ganador)

### 3. Simulación (`simular_torneo_completo.py`)

La función `simular_playoffs`:

1. Itera por cada fase en orden
2. Solo simula partidos que tienen ambas parejas asignadas
3. Los partidos con una sola pareja esperan al ganador del partido anterior

## Ejemplo con 6 Clasificados

```
Clasificados: A, B, C, D, E, F (seeds 1-6)
Bracket size: 8
Byes: 2 (seeds 7 y 8 no existen)

Primera Ronda (4tos):
- Partido 1: Seed 1 vs Seed 8 → BYE, Seed 1 avanza
- Partido 2: Seed 4 vs Seed 5 → Partido normal
- Partido 3: Seed 2 vs Seed 7 → BYE, Seed 2 avanza  
- Partido 4: Seed 3 vs Seed 6 → Partido normal

Semis (pre-creadas):
- Semi 1: Seed 1 (bye) vs Ganador(P2)
- Semi 2: Seed 2 (bye) vs Ganador(P4)

Final:
- Ganador(Semi1) vs Ganador(Semi2)
```

## Archivos Modificados

1. `backend/src/services/torneo_playoff_service.py`
   - `_generar_bracket_con_byes()` - Reestructurada completamente

2. `backend/src/services/torneo_resultado_service.py`
   - `_avanzar_ganador_playoff()` - Agregada verificación de partido listo
   - `_verificar_partido_listo()` - Nueva función

3. `backend/simular_torneo_completo.py`
   - `generar_playoffs()` - Nueva lógica con byes
   - `simular_playoffs()` - Manejo de partidos incompletos

## Testing

Para probar el sistema:

```bash
cd backend
.\venv\Scripts\activate
python simular_torneo_completo.py
```

El script:
1. Limpia torneos anteriores de prueba
2. Crea un torneo con todas las parejas disponibles
3. Genera zonas (máx 3 parejas por zona)
4. Simula fase de grupos
5. Genera playoffs con byes correctamente
6. Simula playoffs hasta la final
