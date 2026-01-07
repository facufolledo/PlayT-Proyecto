#!/usr/bin/env python3
"""
Test completo del algoritmo Elo avanzado
Simula varios escenarios de partidos y verifica los cálculos
"""

import sys
sys.path.append('.')

from src.services.elo_service import EloService
from src.services.elo_config import EloConfig
from datetime import datetime

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_resultado(resultado, titulo=""):
    if titulo:
        print(f"\n{titulo}")
        print("-" * 80)
    
    print(f"\n📊 EQUIPO A:")
    print(f"   Rating: {resultado['team_a']['old_rating']:.0f} → {resultado['team_a']['new_rating']:.0f} ({resultado['team_a']['rating_change']:+.0f})")
    for i, player in enumerate(resultado['team_a']['players'], 1):
        print(f"   Jugador {i}: {player['old_rating']:.0f} → {player['new_rating']:.0f} ({player['rating_change']:+.0f})")
    
    print(f"\n📊 EQUIPO B:")
    print(f"   Rating: {resultado['team_b']['old_rating']:.0f} → {resultado['team_b']['new_rating']:.0f} ({resultado['team_b']['rating_change']:+.0f})")
    for i, player in enumerate(resultado['team_b']['players'], 1):
        print(f"   Jugador {i}: {player['old_rating']:.0f} → {player['new_rating']:.0f} ({player['rating_change']:+.0f})")
    
    print(f"\n📈 DETALLES:")
    print(f"   Expectativa A: {resultado['match_details']['expected_a']:.2%}")
    print(f"   Expectativa B: {resultado['match_details']['expected_b']:.2%}")
    print(f"   Score Real A: {resultado['match_details']['actual_score_a']:.2%}")
    print(f"   Score Real B: {resultado['match_details']['actual_score_b']:.2%}")
    print(f"   Factor K A: {resultado['match_details']['team_a_k']:.1f}")
    print(f"   Factor K B: {resultado['match_details']['team_b_k']:.1f}")
    print(f"   Multiplicador Sets: {resultado['match_details']['sets_multiplier']:.2f}")

def test_caso_1_equipos_parejos():
    """Test 1: Equipos con rating similar"""
    print_header("TEST 1: Equipos Parejos (1200 vs 1200)")
    
    elo = EloService()
    
    team_a = [
        {"rating": 1200, "partidos": 10, "volatilidad": 1.0, "id": 1},
        {"rating": 1200, "partidos": 10, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1200, "partidos": 10, "volatilidad": 1.0, "id": 3},
        {"rating": 1200, "partidos": 10, "volatilidad": 1.0, "id": 4}
    ]
    
    # Equipo A gana 2-0
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=0,
        games_a=12,
        games_b=4,
        sets_detail=[
            {"games_a": 6, "games_b": 2},
            {"games_a": 6, "games_b": 2}
        ]
    )
    
    print_resultado(resultado, "Resultado: Equipo A gana 2-0 (6-2, 6-2)")
    
    # Verificaciones
    assert resultado['team_a']['rating_change'] > 0, "Equipo A debería ganar puntos"
    assert resultado['team_b']['rating_change'] < 0, "Equipo B debería perder puntos"
    assert abs(resultado['team_a']['rating_change']) > 10, "Cambio debería ser significativo"
    
    print("\n✅ Test 1 PASADO")
    return resultado

def test_caso_2_underdog_gana():
    """Test 2: Underdog gana (sorpresa)"""
    print_header("TEST 2: Underdog Gana (1000 vs 1400)")
    
    elo = EloService()
    
    team_a = [
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 1},
        {"rating": 1000, "partidos": 20, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 3},
        {"rating": 1400, "partidos": 30, "volatilidad": 1.0, "id": 4}
    ]
    
    # Underdog (A) gana 2-1
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=1,
        games_a=14,
        games_b=12,
        sets_detail=[
            {"games_a": 6, "games_b": 4},
            {"games_a": 4, "games_b": 6},
            {"games_a": 6, "games_b": 2}
        ]
    )
    
    print_resultado(resultado, "Resultado: Underdog gana 2-1 (6-4, 4-6, 6-2)")
    
    # Verificaciones
    assert resultado['team_a']['rating_change'] > 0, "Underdog debería ganar muchos puntos"
    assert resultado['team_a']['rating_change'] > resultado['team_b']['rating_change'] * -1, "Underdog gana más de lo que favorito pierde"
    
    print("\n✅ Test 2 PASADO")
    return resultado

def test_caso_3_favorito_gana():
    """Test 3: Favorito gana (esperado)"""
    print_header("TEST 3: Favorito Gana (1500 vs 1100)")
    
    elo = EloService()
    
    team_a = [
        {"rating": 1500, "partidos": 40, "volatilidad": 1.0, "id": 1},
        {"rating": 1500, "partidos": 40, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1100, "partidos": 15, "volatilidad": 1.0, "id": 3},
        {"rating": 1100, "partidos": 15, "volatilidad": 1.0, "id": 4}
    ]
    
    # Favorito (A) gana 2-0
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=0,
        games_a=12,
        games_b=3,
        sets_detail=[
            {"games_a": 6, "games_b": 1},
            {"games_a": 6, "games_b": 2}
        ]
    )
    
    print_resultado(resultado, "Resultado: Favorito gana 2-0 (6-1, 6-2)")
    
    # Verificaciones
    assert resultado['team_a']['rating_change'] > 0, "Favorito debería ganar puntos"
    assert resultado['team_a']['rating_change'] < 20, "Favorito gana pocos puntos (era esperado)"
    
    print("\n✅ Test 3 PASADO")
    return resultado

def test_caso_4_favorito_pierde():
    """Test 4: Favorito pierde (sorpresa negativa)"""
    print_header("TEST 4: Favorito Pierde (1600 vs 1200)")
    
    elo = EloService()
    
    team_a = [
        {"rating": 1600, "partidos": 50, "volatilidad": 1.0, "id": 1},
        {"rating": 1600, "partidos": 50, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1200, "partidos": 25, "volatilidad": 1.0, "id": 3},
        {"rating": 1200, "partidos": 25, "volatilidad": 1.0, "id": 4}
    ]
    
    # Favorito (A) pierde 0-2
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=0,
        sets_b=2,
        games_a=5,
        games_b=12,
        sets_detail=[
            {"games_a": 2, "games_b": 6},
            {"games_a": 3, "games_b": 6}
        ]
    )
    
    print_resultado(resultado, "Resultado: Favorito pierde 0-2 (2-6, 3-6)")
    
    # Verificaciones
    assert resultado['team_a']['rating_change'] < 0, "Favorito debería perder puntos"
    assert resultado['team_b']['rating_change'] > 0, "Underdog debería ganar muchos puntos"
    
    print("\n✅ Test 4 PASADO")
    return resultado

def test_caso_5_jugadores_nuevos():
    """Test 5: Jugadores nuevos (alto K factor)"""
    print_header("TEST 5: Jugadores Nuevos (K alto)")
    
    elo = EloService()
    
    team_a = [
        {"rating": 1200, "partidos": 2, "volatilidad": 1.0, "id": 1},  # Nuevo
        {"rating": 1200, "partidos": 3, "volatilidad": 1.0, "id": 2}   # Nuevo
    ]
    
    team_b = [
        {"rating": 1200, "partidos": 60, "volatilidad": 1.0, "id": 3},  # Experto
        {"rating": 1200, "partidos": 70, "volatilidad": 1.0, "id": 4}   # Experto
    ]
    
    # Nuevos ganan 2-1
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=1,
        games_a=13,
        games_b=11,
        sets_detail=[
            {"games_a": 6, "games_b": 4},
            {"games_a": 3, "games_b": 6},
            {"games_a": 6, "games_b": 1}
        ]
    )
    
    print_resultado(resultado, "Resultado: Nuevos ganan 2-1 (6-4, 3-6, 6-1)")
    
    # Verificaciones
    assert resultado['match_details']['team_a_k'] > resultado['match_details']['team_b_k'], "Nuevos deberían tener K mayor"
    assert abs(resultado['team_a']['rating_change']) > abs(resultado['team_b']['rating_change']), "Nuevos cambian más"
    
    print("\n✅ Test 5 PASADO")
    return resultado

def test_caso_6_partido_ajustado():
    """Test 6: Partido muy ajustado con tie-break"""
    print_header("TEST 6: Partido Ajustado con Tie-break")
    
    elo = EloService()
    
    team_a = [
        {"rating": 1300, "partidos": 30, "volatilidad": 1.0, "id": 1},
        {"rating": 1300, "partidos": 30, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1320, "partidos": 35, "volatilidad": 1.0, "id": 3},
        {"rating": 1320, "partidos": 35, "volatilidad": 1.0, "id": 4}
    ]
    
    # Partido ajustado con tie-break
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=1,
        games_a=19,
        games_b=18,
        sets_detail=[
            {"games_a": 7, "games_b": 6},  # Tie-break
            {"games_a": 5, "games_b": 7},
            {"games_a": 7, "games_b": 5}
        ]
    )
    
    print_resultado(resultado, "Resultado: 2-1 con tie-break (7-6, 5-7, 7-5)")
    
    # Verificaciones
    assert resultado['match_details']['tiebreak_reduction'] < 1.0, "Debería haber reducción por tie-break"
    assert abs(resultado['team_a']['rating_change']) < 20, "Cambio debería ser moderado (partido ajustado)"
    
    print("\n✅ Test 6 PASADO")
    return resultado

def test_caso_7_set_dominante():
    """Test 7: Set dominante (6-0)"""
    print_header("TEST 7: Set Dominante (6-0)")
    
    elo = EloService()
    
    team_a = [
        {"rating": 1400, "partidos": 25, "volatilidad": 1.0, "id": 1},
        {"rating": 1400, "partidos": 25, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1350, "partidos": 20, "volatilidad": 1.0, "id": 3},
        {"rating": 1350, "partidos": 20, "volatilidad": 1.0, "id": 4}
    ]
    
    # Con set dominante
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
        ]
    )
    
    print_resultado(resultado, "Resultado: 2-0 con set dominante (6-0, 6-1)")
    
    # Verificaciones
    assert resultado['match_details']['dominant_bonus'] > 0, "Debería haber bonus por set dominante"
    assert resultado['team_a']['rating_change'] > 8, "Cambio debería ser significativo por dominio"
    
    print("\n✅ Test 7 PASADO")
    return resultado

def test_caso_8_walkover():
    """Test 8: Walk Over"""
    print_header("TEST 8: Walk Over")
    
    elo = EloService()
    
    team_a = [
        {"rating": 1300, "partidos": 20, "volatilidad": 1.0, "id": 1},
        {"rating": 1300, "partidos": 20, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1300, "partidos": 20, "volatilidad": 1.0, "id": 3},
        {"rating": 1300, "partidos": 20, "volatilidad": 1.0, "id": 4}
    ]
    
    # Walk Over ganado por equipo 1
    resultado = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=0,
        sets_b=0,
        games_a=0,
        games_b=0,
        desenlace="wo_eq1"
    )
    
    print_resultado(resultado, "Resultado: Walk Over (Equipo A gana)")
    
    # Verificaciones
    assert resultado['match_details']['actual_score_a'] == 1.0, "WO debería dar score 1.0"
    assert resultado['match_details']['actual_score_b'] == 0.0, "WO debería dar score 0.0"
    
    print("\n✅ Test 8 PASADO")
    return resultado

def test_caso_9_torneo_vs_amistoso():
    """Test 9: Comparar partido de torneo vs amistoso"""
    print_header("TEST 9: Torneo vs Amistoso")
    
    elo = EloService()
    
    team_a = [
        {"rating": 1200, "partidos": 15, "volatilidad": 1.0, "id": 1},
        {"rating": 1200, "partidos": 15, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": 1200, "partidos": 15, "volatilidad": 1.0, "id": 3},
        {"rating": 1200, "partidos": 15, "volatilidad": 1.0, "id": 4}
    ]
    
    # Mismo resultado, diferentes tipos
    print("\n🏆 TORNEO:")
    resultado_torneo = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=0,
        games_a=12,
        games_b=4,
        match_type="torneo"
    )
    print(f"   Cambio Equipo A: {resultado_torneo['team_a']['rating_change']:+.0f}")
    print(f"   Caps: {resultado_torneo['match_details']['caps_a']}")
    
    print("\n🤝 AMISTOSO:")
    resultado_amistoso = elo.calculate_match_ratings(
        team_a_players=team_a,
        team_b_players=team_b,
        sets_a=2,
        sets_b=0,
        games_a=12,
        games_b=4,
        match_type="amistoso"
    )
    print(f"   Cambio Equipo A: {resultado_amistoso['team_a']['rating_change']:+.0f}")
    print(f"   Caps: {resultado_amistoso['match_details']['caps_a']}")
    
    # Verificaciones
    assert abs(resultado_torneo['team_a']['rating_change']) > abs(resultado_amistoso['team_a']['rating_change']), \
        "Torneo debería tener mayor impacto que amistoso"
    
    print("\n✅ Test 9 PASADO")
    return resultado_torneo, resultado_amistoso

def test_resumen_configuracion():
    """Mostrar configuración actual del Elo"""
    print_header("CONFIGURACIÓN DEL ALGORITMO ELO")
    
    config = EloConfig.get_config_summary()
    
    print("\n📊 FACTORES K:")
    for nivel, datos in config['k_factors'].items():
        print(f"   {nivel.capitalize()}: K={datos['k_value']} (hasta {datos['max_partidos']} partidos)")
    
    print("\n🎯 CAPS POR ROL:")
    print(f"   Underdog: +{config['underdog_caps']['win']} / {config['underdog_caps']['loss']}")
    print(f"   Favorito: +{config['favorite_caps']['win']} / {config['favorite_caps']['loss']}")
    
    print("\n🏆 CAPS POR TIPO DE PARTIDO:")
    for tipo, caps in config['match_type_caps'].items():
        print(f"   {tipo.capitalize()}: +{caps['win']} / {caps['loss']}")
    
    print("\n⚙️  MULTIPLICADORES:")
    print(f"   Sets: {config['sets_multiplier']}")
    print(f"   Games (cap): {config['games_margin_cap']}")
    print(f"   Set dominante (bonus): {config['dominant_set_bonus']}")
    print(f"   Tie-break (reducción): {config['tiebreak_reduction']}")
    
    print("\n🔒 ANTI-ABUSO:")
    print(f"   Máx partidos/día: {config.get('max_matches_per_day', 'N/A')}")
    print(f"   Multiplicador abuso: {config['abuse_multiplier']}")
    
    print("\n✅ Configuración válida:", config['is_valid'])

def main():
    print("\n" + "🎾" * 40)
    print("  TEST COMPLETO DEL ALGORITMO ELO AVANZADO - DRIVE+")
    print("🎾" * 40)
    
    try:
        # Mostrar configuración
        test_resumen_configuracion()
        
        # Ejecutar tests
        test_caso_1_equipos_parejos()
        test_caso_2_underdog_gana()
        test_caso_3_favorito_gana()
        test_caso_4_favorito_pierde()
        test_caso_5_jugadores_nuevos()
        test_caso_6_partido_ajustado()
        test_caso_7_set_dominante()
        test_caso_8_walkover()
        test_caso_9_torneo_vs_amistoso()
        
        # Resumen final
        print_header("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("\n🎉 El algoritmo Elo está funcionando correctamente!")
        print("\n📋 Resumen:")
        print("   ✅ Equipos parejos: Cambios balanceados")
        print("   ✅ Underdog gana: Gana muchos puntos")
        print("   ✅ Favorito gana: Gana pocos puntos")
        print("   ✅ Favorito pierde: Pierde muchos puntos")
        print("   ✅ Jugadores nuevos: K factor alto")
        print("   ✅ Partido ajustado: Cambios moderados")
        print("   ✅ Set dominante: Bonus aplicado")
        print("   ✅ Walk Over: Manejo correcto")
        print("   ✅ Tipos de partido: Caps diferentes")
        
        print("\n" + "=" * 80)
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
