#!/usr/bin/env python3
"""
Prueba final del sistema ELO con caps máximos de 140 puntos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.elo_service import EloService
from src.services.elo_config import Desenlace

def test_final_caps_140():
    """Prueba final con caps máximos de 140 puntos"""
    
    print("🏆 PRUEBA FINAL: Caps Máximos de 140 Puntos")
    print("=" * 60)
    
    elo_service = EloService()
    
    # Estructura de categorías con caps específicos
    categories = [
        {"name": "Principiante", "min": 0, "max": 499, "expected_cap": 350, "test_ratings": [100, 200, 300, 400, 450, 490]},
        {"name": "8va", "min": 500, "max": 999, "expected_cap": 350, "test_ratings": [500, 600, 700, 800, 900, 950, 990]},
        {"name": "7ma", "min": 1000, "max": 1199, "expected_cap": 60, "test_ratings": [1000, 1050, 1100, 1150, 1190]},
        {"name": "6ta", "min": 1200, "max": 1399, "expected_cap": 60, "test_ratings": [1200, 1250, 1300, 1350, 1390]},
        {"name": "5ta", "min": 1400, "max": 1599, "expected_cap": 60, "test_ratings": [1400, 1450, 1500, 1550, 1590]},
        {"name": "4ta", "min": 1600, "max": 1799, "expected_cap": 60, "test_ratings": [1600, 1650, 1700, 1750, 1790]},
        {"name": "Libre", "min": 1800, "max": None, "expected_cap": 50, "test_ratings": [1800, 1850, 1900, 1950, 2000]}
    ]
    
    results = {}
    
    for category in categories:
        print(f"\n🎾 CATEGORÍA: {category['name']} (Caps esperados: {category['expected_cap']} pts)")
        print("-" * 60)
        
        category_results = []
        
        for starting_rating in category['test_ratings']:
            # Simular torneo completo
            main_player = {
                "rating": starting_rating,
                "partidos": 15,
                "volatilidad": 1.0,
                "id": 1
            }
            
            partner = {
                "rating": starting_rating + 50,
                "partidos": 12,
                "volatilidad": 1.0,
                "id": 2
            }
            
            # Simular 5 partidos ganados consecutivamente
            total_gain = 0
            
            # Tipos de partido en orden
            match_types = ["zona", "zona", "cuartos", "semi", "final"]
            
            for i, match_type in enumerate(match_types):
                # Oponente con rating similar
                opponent_team = [
                    {"rating": starting_rating + 20 + i*10, "partidos": 10, "volatilidad": 1.0, "id": 3},
                    {"rating": starting_rating + 30 + i*10, "partidos": 10, "volatilidad": 1.0, "id": 4}
                ]
                
                # Simular victoria 2-0
                result = elo_service.calculate_match_ratings(
                    team_a_players=[main_player, partner],
                    team_b_players=opponent_team,
                    sets_a=2, sets_b=0,
                    games_a=12, games_b=8,
                    match_type=match_type
                )
                
                # Actualizar ratings
                main_player["rating"] = result["team_a"]["players"][0]["new_rating"]
                partner["rating"] = result["team_a"]["players"][1]["new_rating"]
                
                total_gain += result["team_a"]["players"][0]["rating_change"]
            
            categoria_inicial = get_categoria_por_rating(starting_rating)
            categoria_final = get_categoria_por_rating(main_player["rating"])
            subio = categoria_final != categoria_inicial
            
            result_data = {
                "rating_inicial": starting_rating,
                "rating_final": main_player["rating"],
                "ganancia": total_gain,
                "categoria_inicial": categoria_inicial,
                "categoria_final": categoria_final,
                "subio": subio,
                "expected_cap": category['expected_cap']
            }
            
            category_results.append(result_data)
            
            status = "✅" if subio else "❌"
            cap_achieved = "🎯" if total_gain >= category['expected_cap'] * 0.8 else "⚠️"
            print(f"   {status} {cap_achieved} {starting_rating:4d} → {main_player['rating']:4d} (+{total_gain:5.1f}) | {categoria_inicial} → {categoria_final}")
        
        results[category['name']] = category_results
    
    # Análisis por categoría
    print(f"\n📊 ANÁLISIS DETALLADO:")
    print("=" * 60)
    
    total_subieron = 0
    total_jugadores = 0
    
    for category_name, category_results in results.items():
        subieron = sum(1 for r in category_results if r["subio"])
        total = len(category_results)
        ganancia_promedio = sum(r["ganancia"] for r in category_results) / total
        expected_cap = category_results[0]["expected_cap"]
        
        total_subieron += subieron
        total_jugadores += total
        
        print(f"\n{category_name}:")
        print(f"   Subieron: {subieron}/{total} ({subieron/total:.1%})")
        print(f"   Ganancia promedio: {ganancia_promedio:.1f} puntos")
        print(f"   Caps esperados: {expected_cap} puntos")
        print(f"   Ratio logrado: {ganancia_promedio/expected_cap:.1%}")
        
        # Verificar si se alcanzaron los caps esperados
        if ganancia_promedio >= expected_cap * 0.8:
            print(f"   ✅ Caps alcanzados (≥80% del esperado)")
        else:
            print(f"   ❌ Caps insuficientes (<80% del esperado)")
    
    # Análisis general
    porcentaje_general = total_subieron / total_jugadores
    
    print(f"\n🎯 RESULTADO GENERAL:")
    print("=" * 50)
    print(f"Total de campeones: {total_jugadores}")
    print(f"Total que subieron: {total_subieron}")
    print(f"Porcentaje que subió: {porcentaje_general:.1%}")
    
    # Verificar caps específicos
    print(f"\n🎯 VERIFICACIÓN DE CAPS ESPECÍFICOS:")
    print("=" * 50)
    
    for category_name, category_results in results.items():
        ganancia_promedio = sum(r["ganancia"] for r in category_results) / len(category_results)
        expected_cap = category_results[0]["expected_cap"]
        
        if category_name in ["Principiante", "8va"]:
            if ganancia_promedio >= 200:  # Al menos 200 de 350 esperados
                print(f"✅ {category_name}: {ganancia_promedio:.1f} pts (≥200 esperados)")
            else:
                print(f"❌ {category_name}: {ganancia_promedio:.1f} pts (<200 esperados)")
        elif category_name in ["7ma", "6ta", "5ta", "4ta"]:
            if ganancia_promedio <= 140:  # Máximo 140 puntos
                print(f"✅ {category_name}: {ganancia_promedio:.1f} pts (≤140 máximo)")
            else:
                print(f"❌ {category_name}: {ganancia_promedio:.1f} pts (>140 máximo)")
        else:  # Libre
            if ganancia_promedio <= 140:  # Máximo 140 puntos
                print(f"✅ {category_name}: {ganancia_promedio:.1f} pts (≤140 máximo)")
            else:
                print(f"❌ {category_name}: {ganancia_promedio:.1f} pts (>140 máximo)")
    
    return results

def get_categoria_por_rating(rating):
    """Determinar categoría por rating con nueva estructura"""
    if rating >= 1800:
        return "Libre"
    elif rating >= 1600:
        return "4ta"
    elif rating >= 1400:
        return "5ta"
    elif rating >= 1200:
        return "6ta"
    elif rating >= 1000:
        return "7ma"
    elif rating >= 500:
        return "8va"
    else:
        return "Principiante"

if __name__ == "__main__":
    test_final_caps_140()
