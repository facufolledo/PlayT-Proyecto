#!/usr/bin/env python3
"""
Test completo del fix crítico del sistema ELO
Verifica que ganadores SIEMPRE suban puntos y perdedores SIEMPRE bajen puntos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.elo_service import EloService

def test_elo_fix_basico():
    """Test básico: ganador sube, perdedor baja"""
    print("🧪 TEST 1: Verificación básica - Ganador sube, perdedor baja")
    print("=" * 60)
    
    elo_service = EloService()
    
    # Caso 1: Favorito gana (debería subir pocos puntos)
    team_a_players = [
        {'id': 1, 'rating': 1500, 'partidos': 20, 'volatilidad': 1.0},
        {'id': 2, 'rating': 1520, 'partidos': 25, 'volatilidad': 1.0}
    ]
    
    team_b_players = [
        {'id': 3, 'rating': 1200, 'partidos': 15, 'volatilidad': 1.0},
        {'id': 4, 'rating': 1180, 'partidos': 10, 'volatilidad': 1.0}
    ]
    
    # A gana 2-0 (favorito gana fácil)
    resultado = elo_service.calculate_match_ratings(
        team_a_players=team_a_players,
        team_b_players=team_b_players,
        sets_a=2,
        sets_b=0,
        games_a=12,
        games_b=4
    )
    
    print(f"Equipo A (favorito) - Rating antes: {(1500+1520)/2:.1f}")
    print(f"Equipo A (favorito) - Rating después: {resultado['team_a']['new_rating']:.1f}")
    print(f"Equipo A (favorito) - Cambio: {resultado['team_a']['rating_change']:+.1f}")
    
    print(f"\nEquipo B (underdog) - Rating antes: {(1200+1180)/2:.1f}")
    print(f"Equipo B (underdog) - Rating después: {resultado['team_b']['new_rating']:.1f}")
    print(f"Equipo B (underdog) - Cambio: {resultado['team_b']['rating_change']:+.1f}")
    
    # Verificaciones críticas
    ganador_sube = resultado['team_a']['rating_change'] > 0
    perdedor_baja = resultado['team_b']['rating_change'] < 0
    
    print(f"\n✅ VERIFICACIONES:")
    print(f"   Ganador sube puntos: {'✅ SÍ' if ganador_sube else '❌ NO'}")
    print(f"   Perdedor baja puntos: {'✅ SÍ' if perdedor_baja else '❌ NO'}")
    
    if ganador_sube and perdedor_baja:
        print(f"   🎉 RESULTADO: CORRECTO")
    else:
        print(f"   🚨 RESULTADO: ERROR CRÍTICO")
    
    return ganador_sube and perdedor_baja

def test_elo_fix_underdog():
    """Test underdog: underdog gana, debería subir muchos puntos"""
    print("\n🧪 TEST 2: Underdog gana - Debería subir muchos puntos")
    print("=" * 60)
    
    elo_service = EloService()
    
    # Caso 2: Underdog gana (debería subir muchos puntos)
    team_a_players = [
        {'id': 1, 'rating': 1200, 'partidos': 10, 'volatilidad': 1.0},
        {'id': 2, 'rating': 1180, 'partidos': 8, 'volatilidad': 1.0}
    ]
    
    team_b_players = [
        {'id': 3, 'rating': 1500, 'partidos': 30, 'volatilidad': 1.0},
        {'id': 4, 'rating': 1520, 'partidos': 35, 'volatilidad': 1.0}
    ]
    
    # A gana 2-1 (underdog gana ajustado)
    resultado = elo_service.calculate_match_ratings(
        team_a_players=team_a_players,
        team_b_players=team_b_players,
        sets_a=2,
        sets_b=1,
        games_a=14,
        games_b=12
    )
    
    print(f"Equipo A (underdog) - Rating antes: {(1200+1180)/2:.1f}")
    print(f"Equipo A (underdog) - Rating después: {resultado['team_a']['new_rating']:.1f}")
    print(f"Equipo A (underdog) - Cambio: {resultado['team_a']['rating_change']:+.1f}")
    
    print(f"\nEquipo B (favorito) - Rating antes: {(1500+1520)/2:.1f}")
    print(f"Equipo B (favorito) - Rating después: {resultado['team_b']['new_rating']:.1f}")
    print(f"Equipo B (favorito) - Cambio: {resultado['team_b']['rating_change']:+.1f}")
    
    # Verificaciones críticas
    ganador_sube = resultado['team_a']['rating_change'] > 0
    perdedor_baja = resultado['team_b']['rating_change'] < 0
    underdog_sube_mucho = resultado['team_a']['rating_change'] > 10  # Underdog debería subir bastante
    
    print(f"\n✅ VERIFICACIONES:")
    print(f"   Ganador (underdog) sube puntos: {'✅ SÍ' if ganador_sube else '❌ NO'}")
    print(f"   Perdedor (favorito) baja puntos: {'✅ SÍ' if perdedor_baja else '❌ NO'}")
    print(f"   Underdog sube >10 puntos: {'✅ SÍ' if underdog_sube_mucho else '❌ NO'}")
    
    if ganador_sube and perdedor_baja:
        print(f"   🎉 RESULTADO: CORRECTO")
    else:
        print(f"   🚨 RESULTADO: ERROR CRÍTICO")
    
    return ganador_sube and perdedor_baja

def test_elo_fix_equipos_cercanos():
    """Test equipos cercanos: cambios moderados"""
    print("\n🧪 TEST 3: Equipos cercanos - Cambios moderados")
    print("=" * 60)
    
    elo_service = EloService()
    
    # Caso 3: Equipos muy cercanos
    team_a_players = [
        {'id': 1, 'rating': 1400, 'partidos': 20, 'volatilidad': 1.0},
        {'id': 2, 'rating': 1420, 'partidos': 22, 'volatilidad': 1.0}
    ]
    
    team_b_players = [
        {'id': 3, 'rating': 1390, 'partidos': 18, 'volatilidad': 1.0},
        {'id': 4, 'rating': 1410, 'partidos': 25, 'volatilidad': 1.0}
    ]
    
    # A gana 2-1 (partido parejo)
    resultado = elo_service.calculate_match_ratings(
        team_a_players=team_a_players,
        team_b_players=team_b_players,
        sets_a=2,
        sets_b=1,
        games_a=13,
        games_b=11
    )
    
    print(f"Equipo A - Rating antes: {(1400+1420)/2:.1f}")
    print(f"Equipo A - Rating después: {resultado['team_a']['new_rating']:.1f}")
    print(f"Equipo A - Cambio: {resultado['team_a']['rating_change']:+.1f}")
    
    print(f"\nEquipo B - Rating antes: {(1390+1410)/2:.1f}")
    print(f"Equipo B - Rating después: {resultado['team_b']['new_rating']:.1f}")
    print(f"Equipo B - Cambio: {resultado['team_b']['rating_change']:+.1f}")
    
    # Verificaciones críticas
    ganador_sube = resultado['team_a']['rating_change'] > 0
    perdedor_baja = resultado['team_b']['rating_change'] < 0
    cambios_moderados = abs(resultado['team_a']['rating_change']) < 15 and abs(resultado['team_b']['rating_change']) < 15
    
    print(f"\n✅ VERIFICACIONES:")
    print(f"   Ganador sube puntos: {'✅ SÍ' if ganador_sube else '❌ NO'}")
    print(f"   Perdedor baja puntos: {'✅ SÍ' if perdedor_baja else '❌ NO'}")
    print(f"   Cambios moderados (<15): {'✅ SÍ' if cambios_moderados else '❌ NO'}")
    
    if ganador_sube and perdedor_baja:
        print(f"   🎉 RESULTADO: CORRECTO")
    else:
        print(f"   🚨 RESULTADO: ERROR CRÍTICO")
    
    return ganador_sube and perdedor_baja

def test_caso_facundito():
    """Test del caso específico de Facundito Folledo"""
    print("\n🧪 TEST 4: Caso Facundito Folledo - Ganó 2-1 pero bajó puntos")
    print("=" * 60)
    
    elo_service = EloService()
    
    # Simular el caso de Facundito (aproximado)
    team_a_players = [
        {'id': 1, 'rating': 1216, 'partidos': 15, 'volatilidad': 1.0},  # Facundito
        {'id': 2, 'rating': 1200, 'partidos': 12, 'volatilidad': 1.0}   # Su compañero
    ]
    
    team_b_players = [
        {'id': 3, 'rating': 890, 'partidos': 8, 'volatilidad': 1.0},
        {'id': 4, 'rating': 900, 'partidos': 10, 'volatilidad': 1.0}
    ]
    
    # Facundito gana 2-1 (favorito gana ajustado)
    resultado = elo_service.calculate_match_ratings(
        team_a_players=team_a_players,
        team_b_players=team_b_players,
        sets_a=2,
        sets_b=1,
        games_a=13,
        games_b=10
    )
    
    print(f"Equipo Facundito - Rating antes: {(1216+1200)/2:.1f}")
    print(f"Equipo Facundito - Rating después: {resultado['team_a']['new_rating']:.1f}")
    print(f"Equipo Facundito - Cambio: {resultado['team_a']['rating_change']:+.1f}")
    
    print(f"\nEquipo rival - Rating antes: {(890+900)/2:.1f}")
    print(f"Equipo rival - Rating después: {resultado['team_b']['new_rating']:.1f}")
    print(f"Equipo rival - Cambio: {resultado['team_b']['rating_change']:+.1f}")
    
    # Verificaciones críticas
    facundito_sube = resultado['team_a']['rating_change'] > 0
    rival_baja = resultado['team_b']['rating_change'] < 0
    
    print(f"\n✅ VERIFICACIONES:")
    print(f"   Facundito (ganador) sube puntos: {'✅ SÍ' if facundito_sube else '❌ NO'}")
    print(f"   Rival (perdedor) baja puntos: {'✅ SÍ' if rival_baja else '❌ NO'}")
    
    if facundito_sube and rival_baja:
        print(f"   🎉 RESULTADO: CORRECTO - Facundito ya no pierde puntos ganando")
    else:
        print(f"   🚨 RESULTADO: ERROR CRÍTICO - El bug persiste")
    
    return facundito_sube and rival_baja

def main():
    """Ejecutar todos los tests del fix ELO"""
    print("🚨 TEST COMPLETO: Fix Crítico Sistema ELO Drive+")
    print("=" * 80)
    print("REGLA FUNDAMENTAL: Ganador SIEMPRE sube, perdedor SIEMPRE baja")
    print("=" * 80)
    
    tests_passed = 0
    total_tests = 4
    
    # Ejecutar todos los tests
    if test_elo_fix_basico():
        tests_passed += 1
    
    if test_elo_fix_underdog():
        tests_passed += 1
    
    if test_elo_fix_equipos_cercanos():
        tests_passed += 1
    
    if test_caso_facundito():
        tests_passed += 1
    
    # Resultado final
    print("\n" + "=" * 80)
    print(f"📊 RESUMEN FINAL: {tests_passed}/{total_tests} tests pasados")
    
    if tests_passed == total_tests:
        print("🎉 ¡ÉXITO! El sistema ELO está CORREGIDO")
        print("✅ Ganadores siempre suben puntos")
        print("✅ Perdedores siempre bajan puntos")
        print("✅ Listo para el torneo del 23 de enero")
    else:
        print("🚨 ¡ERROR! El sistema ELO aún tiene problemas")
        print("❌ Revisar la implementación")
        print("❌ NO usar en producción hasta corregir")
    
    print("=" * 80)

if __name__ == "__main__":
    main()