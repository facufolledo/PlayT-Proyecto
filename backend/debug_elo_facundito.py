#!/usr/bin/env python3
"""
Debug específico del sistema ELO para Facundito Folledo
Analizar por qué ganó pero bajó puntos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.driveplus_models import Usuario, PerfilUsuario, Partido, HistorialRating
from datetime import datetime

def debug_facundito_elo():
    """Debug del ELO de Facundito Folledo"""
    db = next(get_db())
    
    try:
        # Buscar Facundito Folledo
        facundito = db.query(Usuario).filter(
            Usuario.nombre_usuario.ilike('%facund%')
        ).first()
        
        if not facundito:
            # Buscar por email también
            facundito = db.query(Usuario).filter(
                Usuario.email.ilike('%facund%')
            ).first()
        
        if not facundito:
            # Mostrar todos los usuarios para debug
            usuarios = db.query(Usuario).filter(
                Usuario.nombre_usuario.ilike('%folledo%')
            ).all()
            print(f"🔍 Usuarios con 'folledo' encontrados: {len(usuarios)}")
            for u in usuarios:
                print(f"   - {u.nombre_usuario} (ID: {u.id_usuario}) - {u.email}")
            
            # Buscar por ID si conocemos alguno
            facundito = db.query(Usuario).filter(Usuario.id_usuario == 15).first()
            if facundito:
                print(f"✅ Encontrado usuario ID 15: {facundito.nombre_usuario}")
            else:
                print("❌ No se encontró usuario ID 15")
                return
        
        print(f"🔍 Analizando ELO de {facundito.nombre_usuario} (ID: {facundito.id_usuario})")
        print(f"📊 Rating actual: {facundito.rating}")
        
        # Obtener historial de rating
        historial = db.query(HistorialRating).filter(
            HistorialRating.id_usuario == facundito.id_usuario
        ).order_by(HistorialRating.creado_en.desc()).limit(10).all()
        
        print(f"\n📈 Últimos 10 cambios de rating:")
        for h in historial:
            partido = db.query(Partido).filter(Partido.id_partido == h.id_partido).first()
            fecha = h.creado_en.strftime("%d/%m/%Y %H:%M")
            
            # Determinar si ganó o perdió
            resultado_str = "?"
            if partido:
                # Verificar si Facundito está en el partido y si ganó
                if partido.resultado_padel:
                    resultado = partido.resultado_padel
                    sets = resultado.get('sets', [])
                    
                    # Contar sets ganados por cada equipo
                    sets_eq_a = 0
                    sets_eq_b = 0
                    
                    for set_data in sets:
                        if set_data.get('completado'):
                            ganador = set_data.get('ganador')
                            if ganador == 'equipoA':
                                sets_eq_a += 1
                            elif ganador == 'equipoB':
                                sets_eq_b += 1
                    
                    # Determinar quién ganó el partido
                    if sets_eq_a > sets_eq_b:
                        ganador_equipo = 'equipoA'
                    elif sets_eq_b > sets_eq_a:
                        ganador_equipo = 'equipoB'
                    else:
                        ganador_equipo = 'empate'
                    
                    # Verificar en qué equipo está Facundito
                    jugadores = resultado.get('jugadores', {})
                    equipo_a = jugadores.get('equipoA', [])
                    equipo_b = jugadores.get('equipoB', [])
                    
                    facundito_en_a = any(j.get('id') == facundito.id_usuario for j in equipo_a)
                    facundito_en_b = any(j.get('id') == facundito.id_usuario for j in equipo_b)
                    
                    if facundito_en_a and ganador_equipo == 'equipoA':
                        resultado_str = f"GANÓ {sets_eq_a}-{sets_eq_b}"
                    elif facundito_en_b and ganador_equipo == 'equipoB':
                        resultado_str = f"GANÓ {sets_eq_b}-{sets_eq_a}"
                    elif facundito_en_a and ganador_equipo == 'equipoB':
                        resultado_str = f"PERDIÓ {sets_eq_a}-{sets_eq_b}"
                    elif facundito_en_b and ganador_equipo == 'equipoA':
                        resultado_str = f"PERDIÓ {sets_eq_b}-{sets_eq_a}"
                    else:
                        resultado_str = f"EMPATE {sets_eq_a}-{sets_eq_b}"
            
            delta_color = "🟢" if h.delta > 0 else "🔴" if h.delta < 0 else "⚪"
            print(f"   {fecha}: {h.rating_antes} → {h.rating_despues} ({h.delta:+d}) {delta_color} | {resultado_str}")
        
        # Analizar el último partido en detalle
        if historial:
            ultimo = historial[0]
            partido = db.query(Partido).filter(Partido.id_partido == ultimo.id_partido).first()
            
            print(f"\n🔍 ANÁLISIS DETALLADO DEL ÚLTIMO PARTIDO:")
            print(f"   📅 Fecha: {ultimo.creado_en}")
            print(f"   📊 Rating antes: {ultimo.rating_antes}")
            print(f"   📊 Rating después: {ultimo.rating_despues}")
            print(f"   📈 Delta: {ultimo.delta:+d}")
            
            if partido and partido.resultado_padel:
                resultado = partido.resultado_padel
                print(f"   🎾 Resultado completo:")
                print(f"      {resultado}")
                
                # Extraer datos para recalcular ELO
                sets = resultado.get('sets', [])
                jugadores = resultado.get('jugadores', {})
                
                equipo_a = jugadores.get('equipoA', [])
                equipo_b = jugadores.get('equipoB', [])
                
                print(f"\n   👥 Equipos:")
                print(f"      Equipo A: {[j.get('nombre', 'N/A') for j in equipo_a]}")
                print(f"      Equipo B: {[j.get('nombre', 'N/A') for j in equipo_b]}")
                
                # Contar sets y games
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
                
                print(f"   🏆 Sets: A={sets_a}, B={sets_b}")
                print(f"   🎯 Games: A={games_a}, B={games_b}")
                
                # Determinar en qué equipo está Facundito
                facundito_en_a = any(j.get('id') == facundito.id_usuario for j in equipo_a)
                facundito_equipo = 'A' if facundito_en_a else 'B'
                print(f"   👤 Facundito en equipo: {facundito_equipo}")
                
                # Determinar quién ganó
                if sets_a > sets_b:
                    ganador = 'A'
                    facundito_gano = facundito_en_a
                elif sets_b > sets_a:
                    ganador = 'B'
                    facundito_gano = not facundito_en_a
                else:
                    ganador = 'EMPATE'
                    facundito_gano = None
                
                print(f"   🏅 Ganador del partido: Equipo {ganador}")
                print(f"   ✅ Facundito ganó: {facundito_gano}")
                
                # AQUÍ ESTÁ EL PROBLEMA: Si ganó pero bajó puntos
                if facundito_gano and ultimo.delta < 0:
                    print(f"\n   🚨 PROBLEMA DETECTADO:")
                    print(f"      Facundito GANÓ el partido pero PERDIÓ {abs(ultimo.delta)} puntos")
                    print(f"      Esto indica un BUG en el sistema ELO")
                    
                    # Obtener ratings de todos los jugadores para recalcular
                    print(f"\n   🔧 Datos para recálculo:")
                    for i, jugador in enumerate(equipo_a):
                        user_id = jugador.get('id')
                        if user_id:
                            user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
                            if user:
                                print(f"      Equipo A[{i}]: {jugador.get('nombre')} - Rating: {user.rating}")
                    
                    for i, jugador in enumerate(equipo_b):
                        user_id = jugador.get('id')
                        if user_id:
                            user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
                            if user:
                                print(f"      Equipo B[{i}]: {jugador.get('nombre')} - Rating: {user.rating}")
                
                elif not facundito_gano and ultimo.delta > 0:
                    print(f"\n   🚨 PROBLEMA DETECTADO:")
                    print(f"      Facundito PERDIÓ el partido pero GANÓ {ultimo.delta} puntos")
                    print(f"      Esto también indica un BUG en el sistema ELO")
                
                else:
                    print(f"\n   ✅ Resultado ELO correcto:")
                    if facundito_gano:
                        print(f"      Ganó el partido y subió {ultimo.delta} puntos")
                    else:
                        print(f"      Perdió el partido y bajó {abs(ultimo.delta)} puntos")
        
        print(f"\n✅ Análisis completado")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_facundito_elo()