#!/usr/bin/env python3
"""
Simulación de un torneo completo para un jugador de 8va
"""

import sys
sys.path.append('.')

from src.services.elo_service import EloService

def simular_torneo_8va():
    """Simular un jugador de 600 puntos ganando un torneo"""
    
    print("=" * 80)
    print("  🏆 SIMULACIÓN: Jugador de 8va (600) Gana Torneo Completo")
    print("=" * 80)
    
    elo = EloService()
    
    # Jugador protagonista
    jugador = {"rating": 600, "partidos": 3, "volatilidad": 1.0, "id": 1}
    compañero = {"rating": 650, "partidos": 4, "volatilidad": 1.0, "id": 2}
    
    print(f"\n📊 INICIO:")
    print(f"   Jugador: {jugador['rating']} puntos (8va)")
    print(f"   Compañero: {compañero['rating']} puntos (8va)")
    print(f"   Equipo promedio: {(jugador['rating'] + compañero['rating']) / 2:.0f}")
    
    partidos = [
        {
            "nombre": "Fase de Grupos - Partido 1",
            "rivales": [{"rating": 620, "partidos": 5}, {"rating": 630, "partidos": 6}],
            "resultado": {"sets_a": 2, "sets_b": 0, "games_a": 12, "games_b": 5},
            "tipo": "torneo"
        },
        {
            "nombre": "Fase de Grupos - Partido 2",
            "rivales": [{"rating": 680, "partidos": 8}, {"rating": 690, "partidos": 9}],
            "resultado": {"sets_a": 2, "sets_b": 1, "games_a": 13, "games_b": 11},
            "tipo": "torneo"
        },
        {
            "nombre": "Cuartos de Final",
            "rivales": [{"rating": 720, "partidos": 12}, {"rating": 730, "partidos": 13}],
            "resultado": {"sets_a": 2, "sets_b": 1, "games_a": 14, "games_b": 10},
            "tipo": "cuartos"
        },
        {
            "nombre": "Semifinal",
            "rivales": [{"rating": 750, "partidos": 15}, {"rating": 760, "partidos": 16}],
            "resultado": {"sets_a": 2, "sets_b": 1, "games_a": 13, "games_b": 12},
            "tipo": "semi"
        },
        {
            "nombre": "FINAL",
            "rivales": [{"rating": 800, "partidos": 20}, {"rating": 810, "partidos": 21}],
            "resultado": {"sets_a": 2, "sets_b": 0, "games_a": 12, "games_b": 6},
            "tipo": "final"
        }
    ]
    
    rating_inicial = jugador['rating']
    
    for i, partido in enumerate(partidos, 1):
        print(f"\n{'=' * 80}")
        print(f"  PARTIDO {i}: {partido['nombre']}")
        print(f"{'=' * 80}")
        
        # Preparar equipos
        team_a = [
            jugador.copy(),
            compañero.copy()
        ]
        
        team_b = [
            {**partido['rivales'][0], "volatilidad": 1.0, "id": 10+i*2},
            {**partido['rivales'][1], "volatilidad": 1.0, "id": 11+i*2}
        ]
        
        rating_rival = (team_b[0]['rating'] + team_b[1]['rating']) / 2
        
        print(f"\n📊 Antes del partido:")
        print(f"   Tu equipo: {(team_a[0]['rating'] + team_a[1]['rating']) / 2:.0f}")
        print(f"   Rival: {rating_rival:.0f}")
        print(f"   Diferencia: {rating_rival - (team_a[0]['rating'] + team_a[1]['rating']) / 2:+.0f}")
        
        # Calcular resultado
        resultado = elo.calculate_match_ratings(
            team_a_players=team_a,
            team_b_players=team_b,
            sets_a=partido['resultado']['sets_a'],
            sets_b=partido['resultado']['sets_b'],
            games_a=partido['resultado']['games_a'],
            games_b=partido['resultado']['games_b'],
            match_type=partido['tipo']
        )
        
        # Actualizar ratings
        jugador['rating'] = resultado['team_a']['players'][0]['new_rating']
        compañero['rating'] = resultado['team_a']['players'][1]['new_rating']
        jugador['partidos'] += 1
        compañero['partidos'] += 1
        
        print(f"\n✅ RESULTADO: {partido['resultado']['sets_a']}-{partido['resultado']['sets_b']}")
        print(f"\n📈 Cambios:")
        print(f"   Tú: {resultado['team_a']['players'][0]['old_rating']:.0f} → "
              f"{resultado['team_a']['players'][0]['new_rating']:.0f} "
              f"({resultado['team_a']['players'][0]['rating_change']:+.0f})")
        print(f"   Compañero: {resultado['team_a']['players'][1]['old_rating']:.0f} → "
              f"{resultado['team_a']['players'][1]['new_rating']:.0f} "
              f"({resultado['team_a']['players'][1]['rating_change']:+.0f})")
        
        print(f"\n🎯 Detalles:")
        print(f"   Expectativa: {resultado['match_details']['expected_a']:.1%}")
        print(f"   Factor K: {resultado['match_details']['team_a_k']:.0f}")
        print(f"   Caps: +{resultado['match_details']['caps_a'][0]} / {resultado['match_details']['caps_a'][1]}")
    
    # Resumen final
    print(f"\n{'=' * 80}")
    print(f"  🏆 RESUMEN FINAL DEL TORNEO")
    print(f"{'=' * 80}")
    
    ganancia_total = jugador['rating'] - rating_inicial
    
    print(f"\n📊 TU PROGRESIÓN:")
    print(f"   Rating inicial: {rating_inicial}")
    print(f"   Rating final: {jugador['rating']:.0f}")
    print(f"   Ganancia total: +{ganancia_total:.0f} puntos")
    print(f"   Partidos jugados: {jugador['partidos']}")
    
    print(f"\n🎯 CATEGORÍA:")
    if jugador['rating'] < 700:
        categoria = "Principiante (0-699)"
        print(f"   Actual: {categoria}")
        print(f"   Faltan {700 - jugador['rating']:.0f} puntos para 8va")
    elif jugador['rating'] < 900:
        categoria = "8va (700-899)"
        print(f"   Actual: {categoria}")
        print(f"   Faltan {900 - jugador['rating']:.0f} puntos para 7ma")
    elif jugador['rating'] < 1100:
        categoria = "7ma (900-1099)"
        print(f"   Actual: {categoria} ⭐ ¡ASCENDISTE!")
        print(f"   Faltan {1100 - jugador['rating']:.0f} puntos para 6ta")
    else:
        print(f"   ¡Estás en {jugador['rating']:.0f}! 🚀")
    
    print(f"\n💡 ANÁLISIS:")
    if ganancia_total >= 200:
        print(f"   ✅ Ganancia EXCELENTE (+{ganancia_total:.0f})")
        print(f"   ✅ Ganar un torneo tiene un impacto significativo")
    elif ganancia_total >= 150:
        print(f"   ✅ Ganancia BUENA (+{ganancia_total:.0f})")
        print(f"   ✅ Progresión adecuada para un torneo ganado")
    elif ganancia_total >= 100:
        print(f"   ⚠️  Ganancia MODERADA (+{ganancia_total:.0f})")
        print(f"   ⚠️  Podría ser un poco más para un torneo completo")
    else:
        print(f"   ❌ Ganancia BAJA (+{ganancia_total:.0f})")
        print(f"   ❌ Muy poco para ganar un torneo completo")
    
    if jugador['rating'] >= 900:
        print(f"\n   🎉 ¡ASCENDISTE A 7MA!")
    elif jugador['rating'] >= 850:
        print(f"\n   🔥 ¡Casi subes! Muy cerca de 7ma")
    else:
        print(f"\n   📈 Buen progreso, sigue así")
    
    print(f"\n{'=' * 80}\n")
    
    return jugador['rating'], ganancia_total

if __name__ == "__main__":
    rating_final, ganancia = simular_torneo_8va()
    
    print("\n🎯 CONCLUSIÓN:")
    if ganancia >= 200 and rating_final >= 900:
        print("   ✅ Sistema PERFECTO: Gana torneo → Sube de categoría")
    elif ganancia >= 150:
        print("   ✅ Sistema BUENO: Progresión significativa")
    elif ganancia >= 100:
        print("   ⚠️  Sistema MEJORABLE: Podría dar más puntos")
    else:
        print("   ❌ Sistema NECESITA AJUSTE: Muy poco impacto")
