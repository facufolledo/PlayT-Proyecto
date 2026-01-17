#!/usr/bin/env python3
"""
Debug de la llamada al método ELO para entender por qué falla
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.driveplus_models import Usuario, Partido, HistorialRating
from src.services.elo_service import EloService
from datetime import datetime

def debug_elo_llamada():
    """Debug de la llamada al ELO"""
    db = next(get_db())
    
    try:
        # Buscar el último partido de Facundito
        facundito = db.query(Usuario).filter(Usuario.id_usuario == 17).first()
        if not facundito:
            print("❌ No se encontró Facundito")
            return
        
        # Obtener su último cambio de rating
        ultimo_historial = db.query(HistorialRating).filter(
            HistorialRating.id_usuario == facundito.id_usuario
        ).order_by(HistorialRating.creado_en.desc()).first()
        
        if not ultimo_historial:
            print("❌ No se encontró historial de rating")
            return
        
        # Obtener el partido correspondiente
        partido = db.query(Partido).filter(
            Partido.id_partido == ultimo_historial.id_partido
        ).first()
        
        if not partido:
            print("❌ No se encontró el partido")
            return
        
        print(f"🔍 Analizando partido ID: {partido.id_partido}")
        print(f"📅 Fecha: {partido.fecha}")
        print(f"🎾 Resultado: {partido.resultado_padel}")
        
        if not partido.resultado_padel:
            print("❌ No hay resultado guardado")
            return
        
        resultado = partido.resultado_padel
        sets = resultado.get('sets', [])
        
        # Contar sets
        sets_a = 0
        sets_b = 0
        games_a = 0
        games_b = 0
        
        for set_data in sets:
            if set_data.get('completado'):
                games_eq_a = set_data.get('gamesEquipoA', 0)
                games_eq_b = set_data.get('gamesEquipoB', 0)
                
                games_a += games_eq_a
                games_b += games_eq_b
                
                ganador = set_data.get('ganador')
                if ganador == 'equipoA':
                    sets_a += 1
                elif ganador == 'equipoB':
                    sets_b += 1
        
        print(f"📊 Sets calculados: A={sets_a}, B={sets_b}")
        print(f"🎯 Games calculados: A={games_a}, B={games_b}")
        
        # Simular la llamada al ELO con datos de prueba
        print(f"\n🧪 SIMULANDO LLAMADA AL ELO:")
        
        # Crear datos de prueba para los equipos
        # Asumiendo que Facundito está en equipo B y ganó
        team_a_players = [
            {"rating": 1200, "partidos": 10, "volatilidad": 1.0, "id": 100},
            {"rating": 1100, "partidos": 8, "volatilidad": 1.0, "id": 101}
        ]
        
        team_b_players = [
            {"rating": facundito.rating + ultimo_historial.delta, "partidos": facundito.partidos_jugados - 1, "volatilidad": 1.0, "id": facundito.id_usuario},  # Rating antes del partido
            {"rating": 1000, "partidos": 5, "volatilidad": 1.0, "id": 102}
        ]
        
        print(f"👥 Equipo A (oponentes): {[p['rating'] for p in team_a_players]}")
        print(f"👥 Equipo B (Facundito): {[p['rating'] for p in team_b_players]}")
        
        # Llamar al método ELO
        elo_service = EloService()
        
        try:
            resultado_elo = elo_service.calculate_match_ratings(
                team_a_players=team_a_players,
                team_b_players=team_b_players,
                sets_a=sets_a,
                sets_b=sets_b,
                games_a=games_a,
                games_b=games_b,
                desenlace="normal",
                match_type="amistoso"
            )
            
            print(f"\n📈 RESULTADO DEL CÁLCULO ELO:")
            print(f"   Equipo A rating change: {resultado_elo['team_a']['rating_change']:.2f}")
            print(f"   Equipo B rating change: {resultado_elo['team_b']['rating_change']:.2f}")
            
            print(f"\n🔍 DETALLES DEL MATCH:")
            match_details = resultado_elo['match_details']
            print(f"   Expected A: {match_details['expected_a']:.3f}")
            print(f"   Expected B: {match_details['expected_b']:.3f}")
            print(f"   Actual score A: {match_details['actual_score_a']:.3f}")
            print(f"   Actual score B: {match_details['actual_score_b']:.3f}")
            
            # Verificar si el resultado es lógico
            facundito_gano = sets_b > sets_a
            facundito_delta = resultado_elo['team_b']['players'][0]['rating_change']
            
            print(f"\n🏅 VERIFICACIÓN:")
            print(f"   Facundito ganó: {facundito_gano}")
            print(f"   Delta de Facundito: {facundito_delta:.2f}")
            
            if facundito_gano and facundito_delta < 0:
                print(f"   🚨 BUG CONFIRMADO: Ganó pero perdió puntos")
            elif not facundito_gano and facundito_delta > 0:
                print(f"   🚨 BUG CONFIRMADO: Perdió pero ganó puntos")
            else:
                print(f"   ✅ Resultado lógico")
                
        except Exception as e:
            print(f"❌ Error en cálculo ELO: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_elo_llamada()