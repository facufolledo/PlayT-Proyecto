#!/usr/bin/env python3
"""
FIX CRÍTICO: Bug en asignación de equipos para cálculo ELO

PROBLEMA IDENTIFICADO:
- El sistema usa equipoA/equipoB en el resultado JSON
- Pero pasa equipo1/equipo2 al cálculo ELO
- No hay garantía de que equipo1 = equipoA

SOLUCIÓN:
- Mapear correctamente equipoA/equipoB con equipo1/equipo2
- O cambiar la lógica para usar consistentemente la misma nomenclatura
"""

# CÓDIGO PROBLEMÁTICO ACTUAL (líneas 519-521 en partido_controller.py):
"""
nuevos_ratings = elo_service.calculate_match_ratings(
    team_a_players=equipo1_players,  # equipo1 != equipoA necesariamente
    team_b_players=equipo2_players,  # equipo2 != equipoB necesariamente  
    sets_a=resultado.sets_eq1,       # sets de equipoA
    sets_b=resultado.sets_eq2,       # sets de equipoB
    ...
)
"""

# CÓDIGO CORREGIDO PROPUESTO:
"""
# Determinar qué equipo (1 o 2) corresponde a equipoA y equipoB
# basándose en los jugadores del partido

# Obtener jugadores de equipoA y equipoB del resultado JSON
resultado_json = partido.resultado_padel
jugadores_equipoA = resultado_json.get('jugadores', {}).get('equipoA', [])
jugadores_equipoB = resultado_json.get('jugadores', {}).get('equipoB', [])

# Mapear con equipo1 y equipo2
equipo1_es_equipoA = False
if jugadores_equipoA and equipo1:
    # Verificar si algún jugador de equipo1 está en equipoA
    ids_equipo1 = {j.id_usuario for j in equipo1}
    ids_equipoA = {j.get('id') for j in jugadores_equipoA if j.get('id')}
    equipo1_es_equipoA = bool(ids_equipo1.intersection(ids_equipoA))

# Asignar correctamente los sets
if equipo1_es_equipoA:
    sets_equipo1 = resultado.sets_eq1  # equipo1 = equipoA
    sets_equipo2 = resultado.sets_eq2  # equipo2 = equipoB
else:
    sets_equipo1 = resultado.sets_eq2  # equipo1 = equipoB
    sets_equipo2 = resultado.sets_eq1  # equipo2 = equipoA

# Llamar al ELO con la asignación correcta
nuevos_ratings = elo_service.calculate_match_ratings(
    team_a_players=equipo1_players,
    team_b_players=equipo2_players,
    sets_a=sets_equipo1,  # Ahora corresponde correctamente
    sets_b=sets_equipo2,  # Ahora corresponde correctamente
    ...
)
"""

print("🚨 BUG CRÍTICO IDENTIFICADO EN SISTEMA ELO")
print("📍 Archivo: backend/src/controllers/partido_controller.py")
print("📍 Líneas: 519-521")
print()
print("🔍 PROBLEMA:")
print("   - equipo1_players se pasa como team_a_players")
print("   - equipo2_players se pasa como team_b_players") 
print("   - sets_eq1 (equipoA) se pasa como sets_a")
print("   - sets_eq2 (equipoB) se pasa como sets_b")
print("   - Pero equipo1 != equipoA necesariamente")
print()
print("💡 SOLUCIÓN:")
print("   - Mapear correctamente equipoA/equipoB con equipo1/equipo2")
print("   - Usar información de jugadores para determinar correspondencia")
print()
print("🎯 RESULTADO ESPERADO:")
print("   - Ganadores suben puntos ELO")
print("   - Perdedores bajan puntos ELO")
print("   - Sin inversiones ilógicas")