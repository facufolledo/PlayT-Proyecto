#!/usr/bin/env python3
"""
Test para verificar que el fix del ELO funciona correctamente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.driveplus_models import Usuario, Partido, HistorialRating
from src.services.elo_service import EloService
from datetime import datetime

def test_fix_elo():
    """Test del fix del ELO"""
    db = next(get_db())
    
    try:
        print("🧪 PROBANDO FIX DEL SISTEMA ELO")
        
        # Simular un partido donde:
        # - Equipo A (ratings bajos) GANA contra Equipo B (ratings altos)
        # - Debería subir muchos puntos (victoria sorpresiva)
        
        team_a_players = [
            {"rating": 900, "partidos": 10, "volatilidad": 1.0, "id": 1},
            {"rating": 950, "partidos": 12, "volatilidad": 1.0, "id": 2}
        ]
        
        team_b_players = [
            {"rating": 1300, "partidos": 20, "volatilidad": 1.0, "id": 3},
            {"rating": 1250, "partidos": 18, "volatilidad": 1.0, "id": 4}
        ]
        
        print(f"👥 Equipo A (underdogs): {[p['rating'] for p in team_a_players]} (promedio: {(team_a_players[0]['rating'] + team_a_players[1]['rating'])/2})")
        print(f"👥 Equipo B (favoritos): {[p['rating'] for p in team_b_players]} (promedio: {(team_b_players[0]['rating'] + team_b_players[1]['rating'])/2})")
        
        # Caso 1: Equipo A GANA 2-1 (victoria sorpresiva)
        print(f"\n🏆 CASO 1: Equipo A GANA 2-1 (victoria sorpresiva)")
        
        elo_service = EloService()
        resultado = elo_service.calculate_match_ratings(
            team_a_players=team_a_players,
            team_b_players=team_b_players,
            sets_a=2,  # Equipo A ganó 2 sets
            sets_b=1,  # Equipo B ganó 1 set
            games_a=13,
            games_b=11,
            desenlace="normal",
            match_type="amistoso"
        )
        
        delta_a = resultado['team_a']['rating_change']
        delta_b = resultado['team_b']['rating_change']
        
        print(f"   📈 Equipo A (ganador): {delta_a:+.1f} puntos")
        print(f"   📉 Equipo B (perdedor): {delta_b:+.1f} puntos")
        
        # Verificar lógica
        if delta_a > 0 and delta_b < 0:
            print(f"   ✅ CORRECTO: Ganador sube, perdedor baja")
        else:
            print(f"   🚨 ERROR: Lógica incorrecta")
        
        # Caso 2: Equipo B GANA 2-0 (resultado esperado)
        print(f"\n🏆 CASO 2: Equipo B GANA 2-0 (resultado esperado)")
        
        resultado2 = elo_service.calculate_match_ratings(
            team_a_players=team_a_players,
            team_b_players=team_b_players,
            sets_a=0,  # Equipo A ganó 0 sets
            sets_b=2,  # Equipo B ganó 2 sets
            games_a=4,
            games_b=12,
            desenlace="normal",
            match_type="amistoso"
        )
        
        delta_a2 = resultado2['team_a']['rating_change']
        delta_b2 = resultado2['team_b']['rating_change']
        
        print(f"   📉 Equipo A (perdedor): {delta_a2:+.1f} puntos")
        print(f"   📈 Equipo B (ganador): {delta_b2:+.1f} puntos")
        
        # Verificar lógica
        if delta_a2 < 0 and delta_b2 > 0:
            print(f"   ✅ CORRECTO: Perdedor baja, ganador sube")
        else:
            print(f"   🚨 ERROR: Lógica incorrecta")
        
        # Caso 3: Verificar que victoria sorpresiva da más puntos que victoria esperada
        print(f"\n🔍 CASO 3: Comparación de cambios")
        print(f"   Victoria sorpresiva (A gana): +{delta_a:.1f} puntos")
        print(f"   Victoria esperada (B gana): +{delta_b2:.1f} puntos")
        
        if abs(delta_a) > abs(delta_b2):
            print(f"   ✅ CORRECTO: Victoria sorpresiva da más puntos")
        else:
            print(f"   ⚠️ ADVERTENCIA: Victoria sorpresiva debería dar más puntos")
        
        print(f"\n✅ Test del fix ELO completado")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_fix_elo()