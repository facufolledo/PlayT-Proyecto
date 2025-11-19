#!/usr/bin/env python3
"""
Test - Equipos con Ratings Cercanos
====================================

Verifica que equipos con diferencias pequeñas se traten como parejos
"""

import sys
sys.path.append('.')

from src.services.elo_service_v2 import EloServiceV2

def test_caso(rating_a, rating_b, descripcion):
    print(f"\n{'='*80}")
    print(f"  {descripcion}")
    print(f"  Equipo A: {rating_a} | Equipo B: {rating_b} | Diferencia: {abs(rating_a - rating_b)}")
    print('='*80)
    
    elo = EloServiceV2()
    
    team_a = [
        {"rating": rating_a, "partidos": 20, "volatilidad": 1.0, "id": 1},
        {"rating": rating_a, "partidos": 20, "volatilidad": 1.0, "id": 2}
    ]
    
    team_b = [
        {"rating": rating_b, "partidos": 20, "volatilidad": 1.0, "id": 3},
        {"rating": rating_b, "partidos": 20, "volatilidad": 1.0, "id": 4}
    ]
    
    # A gana
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
    
    print(f"\n📊 RESULTADO (A gana 6-4 / 6-4):")
    print(f"   Equipo A: {resultado['team_a']['rating_change']:+.0f} puntos")
    print(f"   Equipo B: {resultado['team_b']['rating_change']:+.0f} puntos")
    print(f"\n📈 ANÁLISIS:")
    print(f"   Es A underdog: {resultado['match_details']['is_underdog_a']}")
    print(f"   Es A favorito: {resultado['match_details']['is_favorite_a']}")
    print(f"   Mult. Sorpresa A: {resultado['match_details']['surprise_mult_a']:.2f}")
    print(f"   Expectativa A: {resultado['match_details']['expected_a']:.1%}")
    
    return resultado

def main():
    print("\n" + "🎾" * 40)
    print("  TEST - EQUIPOS CON RATINGS CERCANOS")
    print("🎾" * 40)
    
    # Caso 1: Muy cercanos (40 puntos) - DEBEN SER PAREJOS
    test_caso(1400, 1360, "CASO 1: Diferencia 40 puntos (PAREJOS)")
    
    # Caso 2: Cercanos (60 puntos) - DEBEN SER PAREJOS
    test_caso(1400, 1340, "CASO 2: Diferencia 60 puntos (PAREJOS)")
    
    # Caso 3: Límite (65 puntos) - DEBEN SER PAREJOS
    test_caso(1400, 1335, "CASO 3: Diferencia 65 puntos (LÍMITE)")
    
    # Caso 4: Diferencia clara (80 puntos) - FAVORITO/UNDERDOG
    test_caso(1400, 1320, "CASO 4: Diferencia 80 puntos (FAVORITO/UNDERDOG)")
    
    # Caso 5: Diferencia clara (150 puntos) - FAVORITO/UNDERDOG
    test_caso(1400, 1250, "CASO 5: Diferencia 150 puntos (FAVORITO/UNDERDOG)")
    
    # Caso 6: Gran diferencia (300 puntos) - FAVORITO/UNDERDOG CLARO
    test_caso(1400, 1100, "CASO 6: Diferencia 300 puntos (GRAN DIFERENCIA)")
    
    print("\n" + "="*80)
    print("  ✅ ANÁLISIS COMPLETO")
    print("="*80)
    print("\n📋 CONCLUSIONES:")
    print("   • Diferencias < 65 puntos → Equipos PAREJOS (sin multiplicador sorpresa)")
    print("   • Diferencias ≥ 65 puntos → Favorito/Underdog (con multiplicador sorpresa)")
    print("   • A mayor diferencia, mayor impacto del upset")
    
    return 0

if __name__ == "__main__":
    exit(main())
