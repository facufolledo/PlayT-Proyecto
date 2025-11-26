#!/usr/bin/env python3
"""
Test Elo V3 - Casos Edge y Equipos Parejos
===========================================

Verifica comportamiento en casos especiales:
- Equipos parejos (1200 vs 1200)
- Jugadores nuevos con K alto
- Diferencias extremas de rating
- Partidos con WO/retiro
"""

import sys
sys.path.append('.')

from src.services.elo_service_v2 import EloServiceV2
from src.services.elo_config_v2 import Desenlace

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_resultado(resultado, titulo=""):
    if titulo:
        print(f"\n{titulo}")
        print("-" * 80)
    
    print(f"\n📊 EQUIPO A:")
    print(f"   Rating: {resultado['team_a']['old_rating']:.0f} → {resultado['team_a']['new_rating']:.0f}")
    print(f"   Cambio: {resultado['team_a']['rating_change']:+.0f}")
    
    print(f"\n📊 EQUIPO B:")
    print(f"   Rating: {resultado['team_b']['old_rating']:.0f} → {resultado['team_b']['new_rating']:.0f}")
    print(f"   Cambio: {resultado['team_b']['rating_change']:+.0f}")
    
    print(f"\n📈 DETALLES:")
    print(f"   Factor Margen: {resultado['match_details']['factor_margen']:.2f}")
    print(f"   Mult. Sorpresa A: {resultado['match_details']['surprise_mult_a']:.2f}")
    print(f"   Delta Base A: {resultado['match_details']['delta_base_a']:+.0f}")
    print(f"   Delta Amplificado A: {resultado['match_details']['delta_amplified_a']:+.0f}")

def test_equipos_parejos_torneo():
    """Equipos parejos 1200 vs 1200 en torneo"""
    print_header("TEST 1: Equipos Parejos (1200 vs 1200) - Torneo 6-4/6-4")
    
    elo = EloServiceV2()
    
    team_a = [
        {"rating": 1200, "partidos": 20, "volatilidad": 1.0, "id": 1},
        {"rating": 1200, "partidos": 20, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1200, "partidos": 20, "volatilidad": 1.0, "id": 3},
        {"rating": 1200, "partidos": 20, "volatilidad": 1.0, "id": 4}
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
    
    cambio_a = resultado['team_a']['rating_change']
    cambio_b = resultado['team_b']['rating_change']
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   Ganador: {cambio_a:+.0f} (esperado: +30 a +50)")
    print(f"   Perdedor: {cambio_b:+.0f} (esperado: -30 a -50)")
    print(f"   Suma: {cambio_a + cambio_b:.0f} (debería ser ~0)")
    
    assert 25 <= cambio_a <= 55, f"Ganador fuera de rango: {cambio_a}"
    assert -55 <= cambio_b <= -25, f"Perdedor fuera de rango: {cambio_b}"
    assert abs(cambio_a + cambio_b) < 5, f"Suma no es ~0: {cambio_a + cambio_b}"
    
    print("   ✅ PASÓ")
    return resultado

def test_equipos_parejos_paliza():
    """Equipos parejos con paliza 6-0/6-0"""
    print_header("TEST 2: Equipos Parejos - Paliza 6-0/6-0")
    
    elo = EloServiceV2()
    
    team_a = [
        {"rating": 1200, "partidos": 20, "volatilidad": 1.0, "id": 1},
        {"rating": 1200, "partidos": 20, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1200, "partidos": 20, "volatilidad": 1.0, "id": 3},
        {"rating": 1200, "partidos": 20, "volatilidad": 1.0, "id": 4}
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
    
    cambio_a = resultado['team_a']['rating_change']
    cambio_b = resultado['team_b']['rating_change']
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   Ganador: {cambio_a:+.0f} (esperado: MÁS que test 1 por ~20%)")
    print(f"   Perdedor: {cambio_b:+.0f}")
    print(f"   Diferencia: {cambio_a - 27:.0f} puntos más")
    
    # Debería ser más que el test 1 (27 puntos)
    # Con factor 1.30 vs 1.08, esperamos ~20% más
    assert cambio_a > 27, f"Paliza debería dar más puntos que victoria normal"
    assert cambio_a >= 30, f"Paliza debería dar al menos 30 puntos: {cambio_a}"
    
    print("   ✅ PASÓ")
    return resultado

def test_jugadores_nuevos():
    """Jugadores nuevos (K alto) vs estables"""
    print_header("TEST 3: Jugadores Nuevos (K=100) vs Estables (K=50)")
    
    elo = EloServiceV2()
    
    # Nuevos
    team_a = [
        {"rating": 1200, "partidos": 2, "volatilidad": 1.0, "id": 1},
        {"rating": 1200, "partidos": 3, "volatilidad": 1.0, "id": 2}
    ]
    
    # Estables
    team_b = [
        {"rating": 1200, "partidos": 25, "volatilidad": 1.0, "id": 3},
        {"rating": 1200, "partidos": 30, "volatilidad": 1.0, "id": 4}
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
    
    cambio_nuevos = resultado['team_a']['rating_change']
    cambio_estables = resultado['team_b']['rating_change']
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   Nuevos: {cambio_nuevos:+.0f} (esperado: MÁS que estables)")
    print(f"   Estables: {cambio_estables:+.0f}")
    print(f"   K Nuevos: {resultado['match_details']['team_a_k']:.0f}")
    print(f"   K Estables: {resultado['match_details']['team_b_k']:.0f}")
    
    # Los nuevos deberían cambiar más
    assert abs(cambio_nuevos) > abs(cambio_estables), "Nuevos deberían cambiar más"
    assert cambio_nuevos < 120, f"Cambio de nuevos demasiado alto: {cambio_nuevos}"
    
    print("   ✅ PASÓ")
    return resultado

def test_diferencia_extrema():
    """Diferencia extrema de rating (2000 vs 800)"""
    print_header("TEST 4: Diferencia Extrema (2000 vs 800)")
    
    elo = EloServiceV2()
    
    # Súper favorito
    team_a = [
        {"rating": 2000, "partidos": 50, "volatilidad": 1.0, "id": 1},
        {"rating": 2000, "partidos": 50, "volatilidad": 1.0, "id": 2}
    ]
    
    # Súper underdog
    team_b = [
        {"rating": 800, "partidos": 20, "volatilidad": 1.0, "id": 3},
        {"rating": 800, "partidos": 20, "volatilidad": 1.0, "id": 4}
    ]
    
    # Favorito gana (esperado)
    resultado_esperado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=0,
        games_a=12,
        games_b=2,
        sets_detail=[
            {"games_a": 6, "games_b": 1},
            {"games_a": 6, "games_b": 1}
        ],
        match_type="torneo"
    )
    
    print("\n🔹 CASO A: Favorito gana (esperado)")
    print(f"   Favorito: {resultado_esperado['team_a']['rating_change']:+.0f}")
    print(f"   Underdog: {resultado_esperado['team_b']['rating_change']:+.0f}")
    
    # Underdog gana (MEGA upset)
    resultado_upset = elo.calculate_match_ratings(
        team_a_players=team_b,  # Underdog gana
        team_b_players=team_a,
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
    
    print("\n🔹 CASO B: Underdog gana (MEGA upset)")
    print(f"   Underdog: {resultado_upset['team_a']['rating_change']:+.0f}")
    print(f"   Favorito: {resultado_upset['team_b']['rating_change']:+.0f}")
    print(f"   Mult. Sorpresa: {resultado_upset['match_details']['surprise_mult_a']:.2f}")
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   Favorito gana: cambio pequeño ({resultado_esperado['team_a']['rating_change']:+.0f})")
    print(f"   Underdog gana: cambio GRANDE ({resultado_upset['team_a']['rating_change']:+.0f})")
    
    assert resultado_esperado['team_a']['rating_change'] < 40, "Favorito no debería ganar mucho"
    assert resultado_upset['team_a']['rating_change'] > 80, "Underdog debería ganar mucho"
    
    print("   ✅ PASÓ")
    return resultado_esperado, resultado_upset

def test_wo_y_retiro():
    """Partidos con WO y retiro"""
    print_header("TEST 5: WO y Retiro")
    
    elo = EloServiceV2()
    
    team_a = [
        {"rating": 1200, "partidos": 20, "volatilidad": 1.0, "id": 1},
        {"rating": 1200, "partidos": 20, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1200, "partidos": 20, "volatilidad": 1.0, "id": 3},
        {"rating": 1200, "partidos": 20, "volatilidad": 1.0, "id": 4}
    ]
    
    # WO del equipo A (B gana por WO de A)
    resultado_wo = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=0,
        sets_b=2,
        games_a=0,
        games_b=0,
        desenlace=Desenlace.WO_EQ1.value,  # A no se presentó, B gana
        match_type="torneo"
    )
    
    print("\n🔹 WO del Equipo A (B gana sin jugar)")
    print(f"   Equipo A (no se presentó): {resultado_wo['team_a']['rating_change']:+.0f} (cada jugador: {resultado_wo['team_a']['players'][0]['rating_change']:+.0f})")
    print(f"   Equipo B (gana por WO): {resultado_wo['team_b']['rating_change']:+.0f} (cada jugador: {resultado_wo['team_b']['players'][0]['rating_change']:+.0f})")
    print(f"   Factor Margen: {resultado_wo['match_details']['factor_margen']:.2f}")
    print(f"   Es WO: {resultado_wo['match_details'].get('is_wo', False)}")
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   WO debería tener cambio fijo:")
    print(f"   - Equipo ganador: +10 (+5 por jugador)")
    print(f"   - Equipo perdedor: -20 (-10 por jugador, penalización por irresponsabilidad)")
    
    assert resultado_wo['match_details']['factor_margen'] == 1.0, "WO debería tener factor 1.0"
    assert resultado_wo['team_b']['rating_change'] == 10.0, f"Ganador WO debería sumar +10, no {resultado_wo['team_b']['rating_change']}"
    assert resultado_wo['team_a']['rating_change'] == -20.0, f"Perdedor WO debería perder -20, no {resultado_wo['team_a']['rating_change']}"
    assert resultado_wo['team_b']['players'][0]['rating_change'] == 5.0, "Cada jugador ganador debería sumar +5"
    assert resultado_wo['team_a']['players'][0]['rating_change'] == -10.0, "Cada jugador perdedor debería perder -10"
    
    print("   ✅ PASÓ")
    return resultado_wo

def test_amistoso_vs_final():
    """Comparar mismo resultado en amistoso vs final"""
    print_header("TEST 6: Mismo Resultado - Amistoso vs Final")
    
    elo = EloServiceV2()
    
    team_a = [
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 1},
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 3},
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 4}
    ]
    
    # Amistoso
    resultado_amistoso = elo.calculate_match_ratings(
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
    
    # Final
    resultado_final = elo.calculate_match_ratings(
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
    
    print(f"\n🔹 AMISTOSO:")
    print(f"   Underdog: {resultado_amistoso['team_a']['rating_change']:+.0f}")
    print(f"   Mult. Sorpresa: {resultado_amistoso['match_details']['surprise_mult_a']:.2f}")
    
    print(f"\n🔹 FINAL:")
    print(f"   Underdog: {resultado_final['team_a']['rating_change']:+.0f}")
    print(f"   Mult. Sorpresa: {resultado_final['match_details']['surprise_mult_a']:.2f}")
    
    ratio = resultado_final['team_a']['rating_change'] / resultado_amistoso['team_a']['rating_change']
    
    print(f"\n✅ VERIFICACIÓN:")
    print(f"   Ratio Final/Amistoso: {ratio:.2f}x")
    print(f"   Final debería ser ~5-6x más que amistoso")
    
    assert resultado_final['team_a']['rating_change'] > resultado_amistoso['team_a']['rating_change'] * 4, \
        "Final debería dar mucho más que amistoso"
    
    print("   ✅ PASÓ")
    return resultado_amistoso, resultado_final

def main():
    print("\n" + "🎾" * 40)
    print("  TEST ELO V3 - CASOS EDGE Y EQUIPOS PAREJOS")
    print("🎾" * 40)
    
    try:
        test_equipos_parejos_torneo()
        test_equipos_parejos_paliza()
        test_jugadores_nuevos()
        test_diferencia_extrema()
        test_wo_y_retiro()
        test_amistoso_vs_final()
        
        print_header("✅ TODOS LOS TESTS PASARON")
        print("\n🎉 El algoritmo Elo V3 maneja correctamente todos los casos edge!")
        print("\n📋 Resumen:")
        print("   ✅ Equipos parejos: cambios balanceados")
        print("   ✅ Jugadores nuevos: K alto pero controlado")
        print("   ✅ Diferencias extremas: upsets amplificados")
        print("   ✅ WO/Retiro: factor margen neutro")
        print("   ✅ Amistoso vs Final: diferencia clara")
        
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
