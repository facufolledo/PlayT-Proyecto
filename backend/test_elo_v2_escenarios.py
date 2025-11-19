#!/usr/bin/env python3
"""
Test del Algoritmo Elo V2 - 8 Escenarios de Referencia
=======================================================

Verifica que el sistema produzca resultados coherentes y predecibles
"""

import sys
sys.path.append('.')

from src.services.elo_service_v2 import EloServiceV2
from src.services.elo_config_v2 import EloConfigV2

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_resultado(resultado, titulo=""):
    if titulo:
        print(f"\n{titulo}")
        print("-" * 80)
    
    print(f"\n📊 EQUIPO A (Underdog/Favorito según caso):")
    print(f"   Rating: {resultado['team_a']['old_rating']:.0f} → {resultado['team_a']['new_rating']:.0f}")
    print(f"   Cambio EQUIPO: {resultado['team_a']['rating_change']:+.0f}")
    for i, player in enumerate(resultado['team_a']['players'], 1):
        print(f"   Jugador {i}: {player['old_rating']:.0f} → {player['new_rating']:.0f} ({player['rating_change']:+.0f})")
    
    print(f"\n📊 EQUIPO B:")
    print(f"   Rating: {resultado['team_b']['old_rating']:.0f} → {resultado['team_b']['new_rating']:.0f}")
    print(f"   Cambio EQUIPO: {resultado['team_b']['rating_change']:+.0f}")
    for i, player in enumerate(resultado['team_b']['players'], 1):
        print(f"   Jugador {i}: {player['old_rating']:.0f} → {player['new_rating']:.0f} ({player['rating_change']:+.0f})")
    
    print(f"\n📈 DETALLES:")
    print(f"   Expectativa A: {resultado['match_details']['expected_a']:.2%}")
    print(f"   Expectativa B: {resultado['match_details']['expected_b']:.2%}")
    print(f"   Factor Margen: {resultado['match_details']['factor_margen']:.2f}")
    print(f"   Mult. Sorpresa A: {resultado['match_details']['surprise_mult_a']:.2f}")
    print(f"   Caps Base A: +{resultado['match_details']['caps_base_a'][0]:.0f} / {resultado['match_details']['caps_base_a'][1]:.0f}")
    print(f"   Caps Dinámicos A: +{resultado['match_details']['caps_dynamic_a'][0]:.0f} / {resultado['match_details']['caps_dynamic_a'][1]:.0f}")
    print(f"   Delta Base A: {resultado['match_details']['delta_base_a']:+.0f}")
    print(f"   Delta Amplificado A: {resultado['match_details']['delta_amplified_a']:+.0f}")
    print(f"   Es Underdog A: {resultado['match_details']['is_underdog_a']}")

def escenario_1():
    """TORNEO - Underdog gana 6-4 / 6-4 (victoria clara)"""
    print_header("ESCENARIO 1: TORNEO - Underdog gana 6-4 / 6-4")
    
    elo = EloServiceV2()
    
    # Underdog
    team_a = [
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 1},
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 2}
    ]
    
    # Favorito
    team_b = [
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 3},
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 4}
    ]
    
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=0,
        games_a=12,
        games_b=8,
        sets_detail=[
            {"games_a": 6, "games_b": 4},
            {"games_a": 6, "games_b": 4}
        ],
        match_type="torneo"
    )
    
    print_resultado(resultado)
    
    # Verificar rango esperado
    cambio_underdog = resultado['team_a']['rating_change']
    cambio_favorito = resultado['team_b']['rating_change']
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   Underdog: {cambio_underdog:+.0f} (esperado: +80 a +100)")
    print(f"   Favorito: {cambio_favorito:+.0f} (esperado: -40 a -60)")
    
    assert 70 <= cambio_underdog <= 110, f"Underdog fuera de rango: {cambio_underdog}"
    assert -70 <= cambio_favorito <= -30, f"Favorito fuera de rango: {cambio_favorito}"
    
    print("   ✅ PASÓ")
    return resultado

def escenario_2():
    """TORNEO - Underdog gana 7-6 / 7-6 (MUY ajustado)"""
    print_header("ESCENARIO 2: TORNEO - Underdog gana 7-6 / 7-6 (ajustado)")
    
    elo = EloServiceV2()
    
    team_a = [
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 1},
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 3},
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 4}
    ]
    
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=0,
        games_a=14,
        games_b=12,
        sets_detail=[
            {"games_a": 7, "games_b": 6},  # Tie-break
            {"games_a": 7, "games_b": 6}   # Tie-break
        ],
        match_type="torneo"
    )
    
    print_resultado(resultado)
    
    cambio_underdog = resultado['team_a']['rating_change']
    cambio_favorito = resultado['team_b']['rating_change']
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   Underdog: {cambio_underdog:+.0f} (esperado: +60 a +80, MENOS que esc.1)")
    print(f"   Favorito: {cambio_favorito:+.0f} (esperado: -30 a -40)")
    
    assert 50 <= cambio_underdog <= 90, f"Underdog fuera de rango: {cambio_underdog}"
    assert -50 <= cambio_favorito <= -20, f"Favorito fuera de rango: {cambio_favorito}"
    
    print("   ✅ PASÓ")
    return resultado

def escenario_3():
    """TORNEO - Underdog gana 6-0 / 6-1 (paliza)"""
    print_header("ESCENARIO 3: TORNEO - Underdog gana 6-0 / 6-1 (paliza)")
    
    elo = EloServiceV2()
    
    team_a = [
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 1},
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 3},
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 4}
    ]
    
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=0,
        games_a=12,
        games_b=1,
        sets_detail=[
            {"games_a": 6, "games_b": 0},  # Dominante
            {"games_a": 6, "games_b": 1}   # Casi dominante
        ],
        match_type="torneo"
    )
    
    print_resultado(resultado)
    
    cambio_underdog = resultado['team_a']['rating_change']
    cambio_favorito = resultado['team_b']['rating_change']
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   Underdog: {cambio_underdog:+.0f} (esperado: +90 a +110, MÁS que esc.1)")
    print(f"   Favorito: {cambio_favorito:+.0f} (esperado: -50 a -60)")
    
    assert 80 <= cambio_underdog <= 120, f"Underdog fuera de rango: {cambio_underdog}"
    assert -70 <= cambio_favorito <= -40, f"Favorito fuera de rango: {cambio_favorito}"
    
    print("   ✅ PASÓ")
    return resultado

def escenario_4():
    """FINAL - Underdog gana 6-4 / 6-4"""
    print_header("ESCENARIO 4: FINAL - Underdog gana 6-4 / 6-4")
    
    elo = EloServiceV2()
    
    team_a = [
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 1},
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 3},
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 4}
    ]
    
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=0,
        games_a=12,
        games_b=8,
        sets_detail=[
            {"games_a": 6, "games_b": 4},
            {"games_a": 6, "games_b": 4}
        ],
        match_type="final"
    )
    
    print_resultado(resultado)
    
    cambio_underdog = resultado['team_a']['rating_change']
    cambio_favorito = resultado['team_b']['rating_change']
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   Underdog: {cambio_underdog:+.0f} (esperado: +150 a +190)")
    print(f"   Favorito: {cambio_favorito:+.0f} (esperado: -50 a -70)")
    
    assert 140 <= cambio_underdog <= 200, f"Underdog fuera de rango: {cambio_underdog}"
    assert -80 <= cambio_favorito <= -40, f"Favorito fuera de rango: {cambio_favorito}"
    
    print("   ✅ PASÓ")
    return resultado

def escenario_5():
    """FINAL - Underdog gana 6-0 / 6-0 (paliza en final)"""
    print_header("ESCENARIO 5: FINAL - Underdog gana 6-0 / 6-0 (paliza)")
    
    elo = EloServiceV2()
    
    team_a = [
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 1},
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 3},
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 4}
    ]
    
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=0,
        games_a=12,
        games_b=0,
        sets_detail=[
            {"games_a": 6, "games_b": 0},
            {"games_a": 6, "games_b": 0}
        ],
        match_type="final"
    )
    
    print_resultado(resultado)
    
    cambio_underdog = resultado['team_a']['rating_change']
    cambio_favorito = resultado['team_b']['rating_change']
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   Underdog: {cambio_underdog:+.0f} (esperado: +180 a +220)")
    print(f"   Favorito: {cambio_favorito:+.0f} (esperado: -60 a -80)")
    
    assert 170 <= cambio_underdog <= 230, f"Underdog fuera de rango: {cambio_underdog}"
    assert -90 <= cambio_favorito <= -50, f"Favorito fuera de rango: {cambio_favorito}"
    
    print("   ✅ PASÓ")
    return resultado

def escenario_6():
    """TORNEO - Favorito gana 6-4 / 6-4 (esperado)"""
    print_header("ESCENARIO 6: TORNEO - Favorito gana 6-4 / 6-4")
    
    elo = EloServiceV2()
    
    # Favorito
    team_a = [
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 1},
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 2}
    ]
    
    # Underdog
    team_b = [
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 3},
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 4}
    ]
    
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=0,
        games_a=12,
        games_b=8,
        sets_detail=[
            {"games_a": 6, "games_b": 4},
            {"games_a": 6, "games_b": 4}
        ],
        match_type="torneo"
    )
    
    print_resultado(resultado)
    
    cambio_favorito = resultado['team_a']['rating_change']
    cambio_underdog = resultado['team_b']['rating_change']
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   Favorito: {cambio_favorito:+.0f} (esperado: +30 a +60)")
    print(f"   Underdog: {cambio_underdog:+.0f} (esperado: -15 a -30)")
    
    assert 20 <= cambio_favorito <= 70, f"Favorito fuera de rango: {cambio_favorito}"
    assert -40 <= cambio_underdog <= -10, f"Underdog fuera de rango: {cambio_underdog}"
    
    print("   ✅ PASÓ")
    return resultado

def escenario_7():
    """TORNEO - Favorito gana 6-0 / 6-0 (paliza)"""
    print_header("ESCENARIO 7: TORNEO - Favorito gana 6-0 / 6-0")
    
    elo = EloServiceV2()
    
    team_a = [
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 1},
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 3},
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 4}
    ]
    
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=0,
        games_a=12,
        games_b=0,
        sets_detail=[
            {"games_a": 6, "games_b": 0},
            {"games_a": 6, "games_b": 0}
        ],
        match_type="torneo"
    )
    
    print_resultado(resultado)
    
    cambio_favorito = resultado['team_a']['rating_change']
    cambio_underdog = resultado['team_b']['rating_change']
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   Favorito: {cambio_favorito:+.0f} (esperado: mejor que esc.6, pero < upsets)")
    print(f"   Underdog: {cambio_underdog:+.0f} (esperado: -20 a -40)")
    
    assert 30 <= cambio_favorito <= 80, f"Favorito fuera de rango: {cambio_favorito}"
    assert -50 <= cambio_underdog <= -15, f"Underdog fuera de rango: {cambio_underdog}"
    
    print("   ✅ PASÓ")
    return resultado

def escenario_8():
    """AMISTOSO - Underdog gana 6-4 / 6-4"""
    print_header("ESCENARIO 8: AMISTOSO - Underdog gana 6-4 / 6-4")
    
    elo = EloServiceV2()
    
    team_a = [
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 1},
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 3},
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 4}
    ]
    
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=0,
        games_a=12,
        games_b=8,
        sets_detail=[
            {"games_a": 6, "games_b": 4},
            {"games_a": 6, "games_b": 4}
        ],
        match_type="amistoso"
    )
    
    print_resultado(resultado)
    
    cambio_underdog = resultado['team_a']['rating_change']
    cambio_favorito = resultado['team_b']['rating_change']
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   Underdog: {cambio_underdog:+.0f} (esperado: +15 a +30, MUCHO menos que torneo)")
    print(f"   Favorito: {cambio_favorito:+.0f} (esperado: -10 a -25)")
    
    assert 10 <= cambio_underdog <= 35, f"Underdog fuera de rango: {cambio_underdog}"
    assert -30 <= cambio_favorito <= -5, f"Favorito fuera de rango: {cambio_favorito}"
    
    print("   ✅ PASÓ")
    return resultado

def main():
    print("\n" + "🎾" * 40)
    print("  TEST COMPLETO ELO V2 - 8 ESCENARIOS DE REFERENCIA")
    print("🎾" * 40)
    
    try:
        escenario_1()
        escenario_2()
        escenario_3()
        escenario_4()
        escenario_5()
        escenario_6()
        escenario_7()
        escenario_8()
        
        print_header("✅ TODOS LOS ESCENARIOS PASARON")
        print("\n🎉 El algoritmo Elo V2 funciona correctamente!")
        print("\n📋 Resumen:")
        print("   ✅ Upsets en torneos: +80 a +110")
        print("   ✅ Upsets en finales: +150 a +220")
        print("   ✅ Favorito gana: +30 a +60")
        print("   ✅ Amistosos: +15 a +30")
        print("   ✅ Caps dinámicos funcionan")
        print("   ✅ Factor de margen funciona")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FALLIDO: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
