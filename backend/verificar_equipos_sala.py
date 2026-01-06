#!/usr/bin/env python3
"""
Script para verificar el estado de equipos en una sala
"""
import sys
from src.database.config import get_db
from src.models.sala import Sala, SalaJugador
from src.models.Drive+_models import Usuario

def verificar_equipos_sala(sala_id=None):
    """Verificar equipos asignados en salas"""
    
    db = next(get_db())
    
    try:
        # Obtener salas
        if sala_id:
            salas = db.query(Sala).filter(Sala.id_sala == sala_id).all()
        else:
            salas = db.query(Sala).filter(Sala.estado == 'esperando').order_by(Sala.creado_en.desc()).limit(5).all()
        
        if not salas:
            print("❌ No se encontraron salas")
            return
        
        for sala in salas:
            print(f"\n{'='*60}")
            print(f"🏠 Sala: {sala.nombre} (ID: {sala.id_sala})")
            print(f"   Estado: {sala.estado}")
            print(f"   Código: {sala.codigo_invitacion}")
            
            # Obtener jugadores
            jugadores_data = db.query(SalaJugador, Usuario).join(
                Usuario, SalaJugador.id_usuario == Usuario.id_usuario
            ).filter(SalaJugador.id_sala == sala.id_sala).order_by(SalaJugador.orden).all()
            
            print(f"\n   👥 Jugadores ({len(jugadores_data)}/4):")
            
            equipo_a = []
            equipo_b = []
            sin_equipo = []
            
            for sala_jugador, usuario in jugadores_data:
                equipo_str = f"Equipo {sala_jugador.equipo}" if sala_jugador.equipo else "Sin asignar"
                print(f"      - {usuario.nombre_usuario} (ID: {usuario.id_usuario}) → {equipo_str}")
                
                if sala_jugador.equipo == 1:
                    equipo_a.append(usuario.nombre_usuario)
                elif sala_jugador.equipo == 2:
                    equipo_b.append(usuario.nombre_usuario)
                else:
                    sin_equipo.append(usuario.nombre_usuario)
            
            print(f"\n   📊 Resumen:")
            print(f"      Equipo A: {', '.join(equipo_a) if equipo_a else 'Vacío'}")
            print(f"      Equipo B: {', '.join(equipo_b) if equipo_b else 'Vacío'}")
            if sin_equipo:
                print(f"      ⚠️  Sin asignar: {', '.join(sin_equipo)}")
            
            # Verificar si puede iniciar
            puede_iniciar = len(jugadores_data) == 4 and not sin_equipo
            print(f"\n   {'✅' if puede_iniciar else '❌'} Puede iniciar partido: {'Sí' if puede_iniciar else 'No'}")
            
            if not puede_iniciar:
                if len(jugadores_data) < 4:
                    print(f"      Razón: Faltan {4 - len(jugadores_data)} jugadores")
                if sin_equipo:
                    print(f"      Razón: Hay jugadores sin equipo asignado")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    sala_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    verificar_equipos_sala(sala_id)
