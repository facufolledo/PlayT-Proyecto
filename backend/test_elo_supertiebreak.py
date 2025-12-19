"""
Test del cálculo de Elo para partidos con supertiebreak
Simula el escenario de la imagen: 7-5 / 5-7 / 11-9 (supertiebreak)
"""
import sys
sys.path.insert(0, '.')

from src.services.elo_service import EloService

def test_partido_supertiebreak():
    """
    Test del partido mostrado en la imagen:
    - Equipo A (ganadores): Facundito Folledo + loco 123
    - Equipo B (perdedores): Santi Folledo + nacho Romero
    - Resultado: 2-1 (7-5 / 5-7 / 11-9 supertiebreak)
    - Rating antes: ~1099 (según imagen muestra 1095 después)
    """
    print("=" * 60)
    print("TEST: Partido con Supertiebreak 2-1")
    print("=" * 60)
    
    elo_service = EloService()
    
    # Simular ratings similares (partido parejo)
    # Equipo A (ganadores) - Rating ~1099
    team_a_players = [
        {"id": 1, "rating": 1099, "partidos": 1, "volatilidad": 1.0},  # Facundito Folledo
        {"id": 2, "rating": 1099, "partidos": 1, "volatilidad": 1.0},  # loco 123
    ]
    
    # Equipo B (perdedores) - Rating similar
    team_b_players = [
        {"id": 3, "rating": 1100, "partidos": 5, "volatilidad": 1.0},  # Santi Folledo
        {"id": 4, "rating": 1100, "partidos": 5, "volatilidad": 1.0},  # nacho Romero
    ]
    
    # Resultado: 2-1 con supertiebreak
    sets_a = 2  # Equipo A ganó 2 sets
    sets_b = 1  # Equipo B ganó 1 set
    
    # Games totales: 7+5 + 5+7 + 11+9 = 44 games
    games_a = 7 + 5 + 11  # 23 games
    games_b = 5 + 7 + 9   # 21 games
    
    # Detalle de sets
    sets_detail = [
        {"games_a": 7, "games_b": 5},   # Set 1: 7-5 (A gana)
        {"games_a": 5, "games_b": 7},   # Set 2: 5-7 (B gana)
        {"games_a": 11, "games_b": 9},  # Set 3: 11-9 supertiebreak (A gana)
    ]
    
    print(f"\nEquipo A (ganadores):")
    print(f"  - Jugador 1: Rating {team_a_players[0]['rating']}, Partidos: {team_a_players[0]['partidos']}")
    print(f"  - Jugador 2: Rating {team_a_players[1]['rating']}, Partidos: {team_a_players[1]['partidos']}")
    
    print(f"\nEquipo B (perdedores):")
    print(f"  - Jugador 1: Rating {team_b_players[0]['rating']}, Partidos: {team_b_players[0]['partidos']}")
    print(f"  - Jugador 2: Rating {team_b_players[1]['rating']}, Partidos: {team_b_players[1]['partidos']}")
    
    print(f"\nResultado: {sets_a}-{sets_b}")
    print(f"  Set 1: 7-5")
    print(f"  Set 2: 5-7")
    print(f"  Set 3 (Supertiebreak): 11-9")
    print(f"  Games totales: A={games_a}, B={games_b}")
    
    # Calcular Elo
    resultado = elo_service.calculate_match_ratings(
        team_a_players=team_a_players,
        team_b_players=team_b_players,
        sets_a=sets_a,
        sets_b=sets_b,
        games_a=games_a,
        games_b=games_b,
        sets_detail=sets_detail,
        match_type="amistoso"
    )
    
    print("\n" + "=" * 60)
    print("RESULTADOS DEL CÁLCULO ELO:")
    print("=" * 60)
    
    # Equipo A (ganadores)
    print(f"\n🏆 EQUIPO A (GANADORES):")
    print(f"  Rating equipo antes: {resultado['team_a']['old_rating']}")
    print(f"  Rating equipo después: {resultado['team_a']['new_rating']}")
    print(f"  Cambio total equipo: {resultado['team_a']['rating_change']:+.2f}")
    
    for i, player in enumerate(resultado['team_a']['players']):
        print(f"\n  Jugador {i+1}:")
        print(f"    Rating antes: {player['old_rating']}")
        print(f"    Rating después: {player['new_rating']}")
        print(f"    Cambio: {player['rating_change']:+.2f}")
    
    # Equipo B (perdedores)
    print(f"\n❌ EQUIPO B (PERDEDORES):")
    print(f"  Rating equipo antes: {resultado['team_b']['old_rating']}")
    print(f"  Rating equipo después: {resultado['team_b']['new_rating']}")
    print(f"  Cambio total equipo: {resultado['team_b']['rating_change']:+.2f}")
    
    for i, player in enumerate(resultado['team_b']['players']):
        print(f"\n  Jugador {i+1}:")
        print(f"    Rating antes: {player['old_rating']}")
        print(f"    Rating después: {player['new_rating']}")
        print(f"    Cambio: {player['rating_change']:+.2f}")
    
    # Detalles del cálculo
    details = resultado['match_details']
    print(f"\n📊 DETALLES DEL CÁLCULO:")
    print(f"  Expectativa A: {details['expected_a']:.4f}")
    print(f"  Expectativa B: {details['expected_b']:.4f}")
    print(f"  Score real A: {details['actual_score_a']:.4f}")
    print(f"  Score real B: {details['actual_score_b']:.4f}")
    print(f"  Multiplicador sets: {details['sets_multiplier']:.4f}")
    print(f"  Factor K equipo A: {details['team_a_k']:.2f}")
    print(f"  Factor K equipo B: {details['team_b_k']:.2f}")
    print(f"  Caps A: win={details['caps_a'][0]}, loss={details['caps_a'][1]}")
    print(f"  Caps B: win={details['caps_b'][0]}, loss={details['caps_b'][1]}")
    
    # Verificaciones
    print("\n" + "=" * 60)
    print("VERIFICACIONES:")
    print("=" * 60)
    
    cambio_a = resultado['team_a']['rating_change']
    cambio_b = resultado['team_b']['rating_change']
    
    # El ganador debe ganar puntos
    if cambio_a > 0:
        print(f"✅ Ganadores GANAN puntos: {cambio_a:+.2f}")
    else:
        print(f"❌ ERROR: Ganadores PIERDEN puntos: {cambio_a:+.2f}")
    
    # El perdedor debe perder puntos
    if cambio_b < 0:
        print(f"✅ Perdedores PIERDEN puntos: {cambio_b:+.2f}")
    else:
        print(f"❌ ERROR: Perdedores GANAN puntos: {cambio_b:+.2f}")
    
    # Los cambios deben ser razonables para un amistoso
    if abs(cambio_a) <= 15 and abs(cambio_b) <= 15:
        print(f"✅ Cambios dentro de caps de amistoso (±15)")
    else:
        print(f"⚠️ Cambios fuera de caps esperados")
    
    return resultado


def test_partido_dominante():
    """Test de partido dominante 2-0 (6-2, 6-1)"""
    print("\n" + "=" * 60)
    print("TEST: Partido Dominante 2-0 (6-2, 6-1)")
    print("=" * 60)
    
    elo_service = EloService()
    
    team_a_players = [
        {"id": 1, "rating": 1200, "partidos": 10, "volatilidad": 1.0},
        {"id": 2, "rating": 1200, "partidos": 10, "volatilidad": 1.0},
    ]
    
    team_b_players = [
        {"id": 3, "rating": 1200, "partidos": 10, "volatilidad": 1.0},
        {"id": 4, "rating": 1200, "partidos": 10, "volatilidad": 1.0},
    ]
    
    resultado = elo_service.calculate_match_ratings(
        team_a_players=team_a_players,
        team_b_players=team_b_players,
        sets_a=2,
        sets_b=0,
        games_a=12,  # 6+6
        games_b=3,   # 2+1
        sets_detail=[
            {"games_a": 6, "games_b": 2},
            {"games_a": 6, "games_b": 1},
        ],
        match_type="amistoso"
    )
    
    cambio_a = resultado['team_a']['rating_change']
    cambio_b = resultado['team_b']['rating_change']
    
    print(f"\nResultado: 2-0 (6-2, 6-1)")
    print(f"Cambio ganadores: {cambio_a:+.2f}")
    print(f"Cambio perdedores: {cambio_b:+.2f}")
    
    if cambio_a > 0:
        print(f"✅ Ganadores GANAN puntos")
    else:
        print(f"❌ ERROR: Ganadores PIERDEN puntos")
    
    return resultado


def test_upset_underdog_gana():
    """Test donde el underdog (rating bajo) gana al favorito"""
    print("\n" + "=" * 60)
    print("TEST: Upset - Underdog gana al Favorito")
    print("=" * 60)
    
    elo_service = EloService()
    
    # Underdog (rating bajo)
    team_a_players = [
        {"id": 1, "rating": 1000, "partidos": 5, "volatilidad": 1.0},
        {"id": 2, "rating": 1000, "partidos": 5, "volatilidad": 1.0},
    ]
    
    # Favorito (rating alto)
    team_b_players = [
        {"id": 3, "rating": 1300, "partidos": 20, "volatilidad": 1.0},
        {"id": 4, "rating": 1300, "partidos": 20, "volatilidad": 1.0},
    ]
    
    resultado = elo_service.calculate_match_ratings(
        team_a_players=team_a_players,
        team_b_players=team_b_players,
        sets_a=2,  # Underdog gana
        sets_b=1,
        games_a=19,
        games_b=17,
        sets_detail=[
            {"games_a": 6, "games_b": 4},
            {"games_a": 4, "games_b": 6},
            {"games_a": 9, "games_b": 7},
        ],
        match_type="amistoso"
    )
    
    cambio_a = resultado['team_a']['rating_change']
    cambio_b = resultado['team_b']['rating_change']
    
    print(f"\nUnderdog (1000) vs Favorito (1300)")
    print(f"Resultado: Underdog gana 2-1")
    print(f"Cambio underdog (ganador): {cambio_a:+.2f}")
    print(f"Cambio favorito (perdedor): {cambio_b:+.2f}")
    
    if cambio_a > 0:
        print(f"✅ Underdog GANA puntos por upset")
    else:
        print(f"❌ ERROR: Underdog PIERDE puntos")
    
    if cambio_b < 0:
        print(f"✅ Favorito PIERDE puntos por perder")
    else:
        print(f"❌ ERROR: Favorito GANA puntos")
    
    return resultado


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TESTS DE CÁLCULO ELO - CORRECCIÓN DE BUG")
    print("=" * 60)
    
    test_partido_supertiebreak()
    test_partido_dominante()
    test_upset_underdog_gana()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETADOS")
    print("=" * 60)
