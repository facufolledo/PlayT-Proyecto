# Lógica Detallada del Sistema de Torneos

## 1. Generación Automática de Zonas

### Algoritmo para dividir N parejas en zonas de 3 (y algunas de 2)

```python
def generar_zonas(parejas_confirmadas):
    """
    Divide parejas en zonas de 3, con algunas de 2 si es necesario
    
    Ejemplos:
    - 12 parejas → 4 zonas de 3
    - 13 parejas → 4 zonas de 3 + 1 zona de 1 (NO VÁLIDO) → 3 zonas de 3 + 2 zonas de 2
    - 14 parejas → 4 zonas de 3 + 1 zona de 2
    - 15 parejas → 5 zonas de 3
    - 16 parejas → 5 zonas de 3 + 1 zona de 1 (NO VÁLIDO) → 4 zonas de 3 + 2 zonas de 2
    """
    
    n = len(parejas_confirmadas)
    
    # Mezclar aleatoriamente para evitar sesgos
    random.shuffle(parejas_confirmadas)
    
    zonas = []
    i = 0
    
    while i < n:
        parejas_restantes = n - i
        
        # Si quedan exactamente 4, hacer 2 zonas de 2
        if parejas_restantes == 4:
            zonas.append(parejas_confirmadas[i:i+2])
            zonas.append(parejas_confirmadas[i+2:i+4])
            break
        
        # Si quedan 2, hacer zona de 2
        elif parejas_restantes == 2:
            zonas.append(parejas_confirmadas[i:i+2])
            break
        
        # Si quedan 5, hacer zona de 3 y zona de 2
        elif parejas_restantes == 5:
            zonas.append(parejas_confirmadas[i:i+3])
            zonas.append(parejas_confirmadas[i+3:i+5])
            break
        
        # Por defecto, hacer zona de 3
        else:
            zonas.append(parejas_confirmadas[i:i+3])
            i += 3
    
    return zonas
```

### Reglas de Zonas

- **Zona de 3 parejas**: Cada pareja juega 2 partidos (todos contra todos)
- **Zona de 2 parejas**: Juegan 1 partido entre sí
  - Ganador: 1° de zona
  - Perdedor: 2° de zona

## 2. Generación de Fixture de Zonas

### Para zona de 3 parejas (A, B, C)

```
Partido 1: A vs B
Partido 2: A vs C
Partido 3: B vs C
```

### Para zona de 2 parejas (A, B)

```
Partido 1: A vs B
```

### Programación Automática

```python
def programar_partidos_zona(zona, slots_disponibles, bloqueos_jugadores):
    """
    Asigna horarios y canchas a los partidos de una zona
    respetando restricciones de jugadores
    """
    
    partidos = generar_partidos_zona(zona)
    
    for partido in partidos:
        # Obtener los 4 jugadores del partido
        jugadores = [
            partido.jugador1a_id,
            partido.jugador1b_id,
            partido.jugador2a_id,
            partido.jugador2b_id
        ]
        
        # Buscar slot compatible
        slot_asignado = None
        
        for slot in slots_disponibles:
            if slot.ocupado:
                continue
            
            # Verificar que ningún jugador tenga bloqueo en ese horario
            if todos_jugadores_disponibles(jugadores, slot, bloqueos_jugadores):
                slot_asignado = slot
                break
        
        if slot_asignado:
            partido.cancha_id = slot_asignado.cancha_id
            partido.fecha_hora = slot_asignado.fecha_hora_inicio
            slot_asignado.ocupado = True
            slot_asignado.partido_id = partido.id
        else:
            # No hay slot compatible, marcar para programación manual
            partido.requiere_reprogramacion = True
            partido.observaciones = "No hay horarios compatibles con restricciones de jugadores"
```

## 3. Cálculo de Tabla de Posiciones

### Criterios de Desempate (en orden)

1. **Puntos totales**
2. **Diferencia de sets** (sets a favor - sets en contra)
3. **Diferencia de games** (games a favor - games en contra)
4. **Enfrentamiento directo** (si empatados en todo lo anterior)
5. **Sorteo** (último recurso)

### Sistema de Puntos

```python
# Configuración por defecto (puede variar según reglas del torneo)
PUNTOS_VICTORIA = 3
PUNTOS_VICTORIA_TIEBREAK = 2  # Si se define victoria en tie-break del 3er set
PUNTOS_DERROTA = 0
```

### Actualización Después de Cada Partido

```python
def actualizar_tabla_posiciones(partido):
    """
    Actualiza la tabla de posiciones después de un partido
    """
    
    # Obtener sets del partido
    sets = obtener_sets_partido(partido.id)
    
    # Calcular ganador
    sets_p1 = sum(1 for s in sets if s.games_pareja1 > s.games_pareja2)
    sets_p2 = sum(1 for s in sets if s.games_pareja2 > s.games_pareja1)
    
    ganador_id = partido.pareja1_id if sets_p1 > sets_p2 else partido.pareja2_id
    perdedor_id = partido.pareja2_id if sets_p1 > sets_p2 else partido.pareja1_id
    
    # Calcular games totales
    games_p1 = sum(s.games_pareja1 for s in sets)
    games_p2 = sum(s.games_pareja2 for s in sets)
    
    # Actualizar tabla para ganador
    actualizar_fila_tabla(
        zona_id=partido.zona_id,
        pareja_id=ganador_id,
        puntos=PUNTOS_VICTORIA,
        partidos_jugados=1,
        partidos_ganados=1,
        sets_favor=sets_p1 if ganador_id == partido.pareja1_id else sets_p2,
        sets_contra=sets_p2 if ganador_id == partido.pareja1_id else sets_p1,
        games_favor=games_p1 if ganador_id == partido.pareja1_id else games_p2,
        games_contra=games_p2 if ganador_id == partido.pareja1_id else games_p1
    )
    
    # Actualizar tabla para perdedor
    actualizar_fila_tabla(
        zona_id=partido.zona_id,
        pareja_id=perdedor_id,
        puntos=PUNTOS_DERROTA,
        partidos_jugados=1,
        partidos_perdidos=1,
        sets_favor=sets_p2 if perdedor_id == partido.pareja2_id else sets_p1,
        sets_contra=sets_p1 if perdedor_id == partido.pareja2_id else sets_p2,
        games_favor=games_p2 if perdedor_id == partido.pareja2_id else games_p1,
        games_contra=games_p1 if perdedor_id == partido.pareja2_id else games_p2
    )
```

## 4. Generación de Cuadro de Eliminación

### Paso 1: Obtener Clasificados

```python
def obtener_clasificados(torneo_id):
    """
    Obtiene todas las parejas clasificadas ordenadas por rendimiento
    """
    
    clasificados = []
    
    # Obtener todas las zonas
    zonas = obtener_zonas_torneo(torneo_id)
    
    for zona in zonas:
        # Obtener tabla ordenada
        tabla = obtener_tabla_zona_ordenada(zona.id)
        
        # Clasifican 1° y 2°
        if len(tabla) >= 1:
            primero = tabla[0]
            primero.posicion_zona = 1
            primero.tipo_clasificacion = 'primero'
            clasificados.append(primero)
        
        if len(tabla) >= 2:
            segundo = tabla[1]
            segundo.posicion_zona = 2
            segundo.tipo_clasificacion = 'segundo'
            clasificados.append(segundo)
    
    # Ordenar clasificados: primeros primero, luego segundos
    # Dentro de cada grupo, ordenar por rendimiento
    clasificados.sort(key=lambda x: (
        0 if x.tipo_clasificacion == 'primero' else 1,
        -x.puntos,
        -x.diferencia_sets,
        -x.diferencia_games
    ))
    
    return clasificados
```

### Paso 2: Calcular Fase Inicial y Byes

```python
def calcular_fase_inicial(num_clasificados):
    """
    Determina en qué fase arranca la eliminación y cuántos byes hay
    
    Ejemplos:
    - 8 clasificados → cuartos (8), 0 byes
    - 10 clasificados → 16avos (16), 6 byes
    - 12 clasificados → 16avos (16), 4 byes
    - 14 clasificados → 16avos (16), 2 byes
    - 16 clasificados → 8vos (16), 0 byes
    """
    
    # Siguiente potencia de 2
    potencia = 1
    while potencia < num_clasificados:
        potencia *= 2
    
    byes = potencia - num_clasificados
    
    # Determinar fase
    if potencia == 4:
        fase = 'semis'
    elif potencia == 8:
        fase = '4tos'
    elif potencia == 16:
        fase = '8vos'
    elif potencia == 32:
        fase = '16avos'
    else:
        fase = '4tos'  # Por defecto
    
    return fase, byes, potencia
```

### Paso 3: Asignar Byes y Generar Partidos

```python
def generar_cuadro_eliminacion(torneo_id):
    """
    Genera el cuadro de eliminación con byes
    """
    
    clasificados = obtener_clasificados(torneo_id)
    num_clasificados = len(clasificados)
    
    fase, byes, potencia = calcular_fase_inicial(num_clasificados)
    
    # Los mejores primeros reciben bye
    parejas_con_bye = clasificados[:byes]
    parejas_juegan = clasificados[byes:]
    
    # Generar partidos de la primera fase
    partidos = []
    num_partidos = len(parejas_juegan) // 2
    
    for i in range(num_partidos):
        partido = crear_partido_eliminacion(
            torneo_id=torneo_id,
            fase=fase,
            numero_partido=i+1,
            pareja1=parejas_juegan[i*2],
            pareja2=parejas_juegan[i*2+1]
        )
        partidos.append(partido)
    
    # Registrar byes (pasan directo a siguiente fase)
    for pareja in parejas_con_bye:
        registrar_bye(torneo_id, pareja, fase)
    
    return partidos
```

## 5. Integración con Sistema ELO

### Actualización de ELO Después de Cada Partido

```python
def procesar_resultado_torneo(partido_id):
    """
    Procesa el resultado de un partido de torneo y actualiza ELO
    """
    
    partido = obtener_partido(partido_id)
    sets = obtener_sets_partido(partido_id)
    
    # Preparar datos para EloController
    match_data = {
        'jugador1a_id': partido.jugador1a_id,
        'jugador1b_id': partido.jugador1b_id,
        'jugador2a_id': partido.jugador2a_id,
        'jugador2b_id': partido.jugador2b_id,
        'sets': [
            {
                'games_equipo1': s.games_pareja1,
                'games_equipo2': s.games_pareja2
            }
            for s in sets
        ],
        'tipo_partido': 'torneo',
        'torneo_id': partido.torneo_id,
        'fecha': partido.fecha_hora
    }
    
    # Llamar al EloController existente
    resultado_elo = elo_controller.process_match(match_data)
    
    # Actualizar historial de cada jugador
    for jugador_id in [partido.jugador1a_id, partido.jugador1b_id, 
                       partido.jugador2a_id, partido.jugador2b_id]:
        guardar_historial_rating(
            jugador_id=jugador_id,
            partido_id=partido_id,
            tipo='torneo',
            resultado=resultado_elo[jugador_id]
        )
    
    # Actualizar tabla de posiciones si es fase de zona
    if partido.fase == 'zona':
        actualizar_tabla_posiciones(partido)
    
    return resultado_elo
```

## 6. Gestión de Cambios de Último Momento

### Reemplazo de Jugador en Pareja

```python
def reemplazar_jugador_pareja(pareja_id, jugador_saliente_id, jugador_entrante_id, organizador_id):
    """
    Reemplaza un jugador en una pareja
    """
    
    pareja = obtener_pareja(pareja_id)
    
    # Actualizar pareja
    if pareja.jugador1_id == jugador_saliente_id:
        pareja.jugador1_id = jugador_entrante_id
    elif pareja.jugador2_id == jugador_saliente_id:
        pareja.jugador2_id = jugador_entrante_id
    else:
        raise ValueError("Jugador no pertenece a esta pareja")
    
    # Actualizar partidos futuros (no jugados)
    partidos_futuros = obtener_partidos_pareja_no_jugados(pareja_id)
    
    for partido in partidos_futuros:
        # Actualizar IDs de jugadores en el partido
        if partido.pareja1_id == pareja_id:
            if partido.jugador1a_id == jugador_saliente_id:
                partido.jugador1a_id = jugador_entrante_id
            elif partido.jugador1b_id == jugador_saliente_id:
                partido.jugador1b_id = jugador_entrante_id
        
        elif partido.pareja2_id == pareja_id:
            if partido.jugador2a_id == jugador_saliente_id:
                partido.jugador2a_id = jugador_entrante_id
            elif partido.jugador2b_id == jugador_saliente_id:
                partido.jugador2b_id = jugador_entrante_id
        
        # Marcar para reprogramación (por si el nuevo jugador tiene restricciones)
        partido.requiere_reprogramacion = True
    
    # Registrar cambio en historial
    registrar_cambio_torneo(
        torneo_id=pareja.torneo_id,
        tipo='jugador_reemplazado',
        descripcion=f"Jugador {jugador_saliente_id} reemplazado por {jugador_entrante_id} en pareja {pareja_id}",
        realizado_por=organizador_id
    )
```

### Baja de Pareja

```python
def dar_baja_pareja(pareja_id, organizador_id):
    """
    Da de baja una pareja del torneo
    """
    
    pareja = obtener_pareja(pareja_id)
    pareja.estado = 'baja'
    
    # Cancelar partidos no jugados
    partidos_futuros = obtener_partidos_pareja_no_jugados(pareja_id)
    
    for partido in partidos_futuros:
        partido.estado = 'cancelado'
        
        # Liberar slot si estaba asignado
        if partido.cancha_id and partido.fecha_hora:
            liberar_slot(partido.torneo_id, partido.cancha_id, partido.fecha_hora)
    
    # Si ya jugó partidos en zona, marcar como W.O. los restantes
    partidos_zona = obtener_partidos_zona_pareja(pareja_id)
    
    for partido in partidos_zona:
        if partido.estado == 'pendiente':
            # Determinar ganador por W.O.
            ganador_id = partido.pareja2_id if partido.pareja1_id == pareja_id else partido.pareja1_id
            partido.estado = 'w_o'
            partido.ganador_pareja_id = ganador_id
            
            # Actualizar tabla (victoria por W.O.)
            actualizar_tabla_wo(partido)
    
    # Registrar cambio
    registrar_cambio_torneo(
        torneo_id=pareja.torneo_id,
        tipo='pareja_baja',
        descripcion=f"Pareja {pareja_id} dada de baja",
        realizado_por=organizador_id
    )
```

## 7. Validaciones y Reglas de Negocio

### Validaciones al Crear Torneo

- Organizador debe estar autorizado
- Fecha inicio < fecha fin
- Categoría válida
- Nombre único (opcional)

### Validaciones al Inscribir Pareja

- Torneo en estado 'inscripcion'
- Jugadores no pueden estar en otra pareja del mismo torneo
- Jugadores deben existir y estar activos
- Categoría de jugadores compatible con categoría del torneo

### Validaciones al Cargar Resultado

- Partido debe existir y estar en estado 'pendiente' o 'en_juego'
- Usuario debe ser organizador del torneo
- Sets deben ser válidos (formato pádel)
- Debe haber un ganador claro

### Validaciones al Generar Zonas

- Torneo en estado 'inscripcion'
- Al menos 4 parejas confirmadas
- No debe haber zonas ya generadas

### Validaciones al Generar Cuadro Final

- Torneo en estado 'fase_grupos'
- Todos los partidos de zona deben estar finalizados
- Debe haber clasificados suficientes
