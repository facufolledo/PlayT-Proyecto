"""
Debug de pareja específica (Facundo y Facundito - IDs 14 y 15)
"""
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.models.torneo_models import TorneoPareja
from src.models.driveplus_models import Partido

load_dotenv()

def debug_pareja():
    print("=" * 80)
    print("DEBUG: PAREJA FACUNDO Y FACUNDITO (IDs 14 y 15)")
    print("=" * 80)
    
    try:
        database_url = os.getenv("DATABASE_URL")
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        torneo_id = 11
        
        # Buscar la pareja con jugadores 14 y 15
        pareja = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == torneo_id,
            (
                ((TorneoPareja.jugador1_id == 14) & (TorneoPareja.jugador2_id == 15)) |
                ((TorneoPareja.jugador1_id == 15) & (TorneoPareja.jugador2_id == 14))
            )
        ).first()
        
        if not pareja:
            print("\n❌ No se encontró la pareja")
            return
        
        print(f"\n🎾 Pareja encontrada:")
        print(f"   ID: {pareja.id}")
        print(f"   Jugador 1: {pareja.jugador1_id}")
        print(f"   Jugador 2: {pareja.jugador2_id}")
        print(f"   Categoría: {pareja.categoria_id}")
        print(f"   Estado: {pareja.estado}")
        
        print(f"\n📅 Disponibilidad horaria:")
        print(f"   {pareja.disponibilidad_horaria}")
        
        # Buscar partidos de esta pareja
        partidos = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            (
                (Partido.pareja1_id == pareja.id) |
                (Partido.pareja2_id == pareja.id)
            )
        ).all()
        
        print(f"\n⚽ Partidos programados: {len(partidos)}")
        print("=" * 80)
        
        for partido in partidos:
            print(f"\n   Partido ID: {partido.id_partido}")
            print(f"   Pareja 1: {partido.pareja1_id}")
            print(f"   Pareja 2: {partido.pareja2_id}")
            print(f"   Fecha/Hora: {partido.fecha_hora}")
            print(f"   Cancha: {partido.cancha_id}")
            print(f"   Zona: {partido.zona_id}")
            print(f"   Estado: {partido.estado}")
            
            # Extraer día de la semana y hora
            if partido.fecha_hora:
                dia_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'][partido.fecha_hora.weekday()]
                hora = partido.fecha_hora.strftime('%H:%M')
                print(f"   Día: {dia_semana}")
                print(f"   Hora: {hora}")
                
                # Verificar si está dentro de la disponibilidad
                disp = pareja.disponibilidad_horaria or {}
                if disp and disp.get('franjas'):
                    franjas = disp['franjas']
                    esta_disponible = False
                    
                    for franja in franjas:
                        dias = franja.get('dias', [])
                        hora_inicio = franja.get('horaInicio', '00:00')
                        hora_fin = franja.get('horaFin', '23:59')
                        
                        if dia_semana in dias:
                            # Convertir a minutos
                            hora_mins = int(hora.split(':')[0]) * 60 + int(hora.split(':')[1])
                            inicio_mins = int(hora_inicio.split(':')[0]) * 60 + int(hora_inicio.split(':')[1])
                            fin_mins = int(hora_fin.split(':')[0]) * 60 + int(hora_fin.split(':')[1])
                            
                            if inicio_mins <= hora_mins < fin_mins:
                                esta_disponible = True
                                print(f"   ✅ DENTRO de disponibilidad ({dia_semana} {hora_inicio}-{hora_fin})")
                                break
                    
                    if not esta_disponible:
                        # Verificar si el día NO está en restricciones (disponible todo el día)
                        dias_restringidos = set()
                        for franja in franjas:
                            dias_restringidos.update(franja.get('dias', []))
                        
                        if dia_semana not in dias_restringidos:
                            print(f"   ✅ Día sin restricciones (disponible todo el día)")
                        else:
                            print(f"   ❌ FUERA de disponibilidad")
                            print(f"      Restricciones: {franjas}")
                else:
                    print(f"   ✅ Sin restricciones (disponible siempre)")
            
            print("-" * 80)
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pareja()
