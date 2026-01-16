"""
Script para debuggear en detalle por qué no se programan partidos
"""
import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from src.models.torneo_models import TorneoPareja, Torneo, TorneoZona

load_dotenv()

def debug_fixture():
    """
    Debug detallado del proceso de generación de fixture
    """
    print("=" * 80)
    print("DEBUG DETALLADO: GENERACIÓN DE FIXTURE")
    print("=" * 80)
    
    try:
        database_url = os.getenv("DATABASE_URL")
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        torneo_id = 11
        
        # Obtener torneo
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        print(f"\n📋 Torneo: {torneo.nombre}")
        print(f"   Fechas: {torneo.fecha_inicio} al {torneo.fecha_fin}")
        
        # Calcular qué días de la semana son
        fecha_actual = torneo.fecha_inicio
        print(f"\n📅 Días del torneo:")
        dias_torneo = []
        while fecha_actual <= torneo.fecha_fin:
            dia_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'][fecha_actual.weekday()]
            dias_torneo.append(dia_semana)
            print(f"   {fecha_actual} = {dia_semana}")
            fecha_actual += timedelta(days=1)
        
        # Generar slots del torneo
        print(f"\n⏰ Generando slots del torneo...")
        horarios_torneo = torneo.horarios_disponibles or {}
        slots_torneo = []
        
        fecha_actual = torneo.fecha_inicio
        while fecha_actual <= torneo.fecha_fin:
            dia_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'][fecha_actual.weekday()]
            tipo_dia = 'finDeSemana' if dia_semana in ['sabado', 'domingo'] else 'semana'
            franjas = horarios_torneo.get(tipo_dia, [])
            
            if not franjas:
                franjas = [{'desde': '08:00', 'hasta': '23:00'}]
            
            for franja in franjas:
                hora_desde = franja.get('desde', '08:00')
                hora_hasta = franja.get('hasta', '23:00')
                
                hora_actual = datetime.strptime(hora_desde, '%H:%M')
                hora_limite = datetime.strptime(hora_hasta, '%H:%M')
                
                while hora_actual < hora_limite:
                    slots_torneo.append((
                        fecha_actual.strftime('%Y-%m-%d'),
                        dia_semana,
                        hora_actual.strftime('%H:%M')
                    ))
                    hora_actual += timedelta(minutes=50)
            
            fecha_actual += timedelta(days=1)
        
        print(f"   Total slots generados: {len(slots_torneo)}")
        print(f"   Primeros 5 slots:")
        for slot in slots_torneo[:5]:
            print(f"      {slot}")
        
        # Obtener primera zona y sus parejas
        zona = db.query(TorneoZona).filter(TorneoZona.torneo_id == torneo_id).first()
        if not zona:
            print("\n❌ No hay zonas")
            return
        
        print(f"\n🏆 Zona: {zona.nombre}")
        
        # Obtener parejas de la zona
        from src.models.torneo_models import TorneoZonaPareja
        parejas = db.query(TorneoPareja).join(
            TorneoZonaPareja,
            TorneoZonaPareja.pareja_id == TorneoPareja.id
        ).filter(
            TorneoZonaPareja.zona_id == zona.id
        ).limit(2).all()
        
        if len(parejas) < 2:
            print("\n❌ No hay suficientes parejas en la zona")
            return
        
        p1 = parejas[0]
        p2 = parejas[1]
        
        print(f"\n🎾 Analizando partido: Pareja {p1.id} vs Pareja {p2.id}")
        
        # Generar slots de disponibilidad de cada pareja
        def generar_slots_pareja(pareja):
            disp = pareja.disponibilidad_horaria or {}
            slots = set()
            
            if not disp or not disp.get('franjas'):
                return set()  # Sin restricciones
            
            franjas = disp.get('franjas', [])
            for franja in franjas:
                dias = franja.get('dias', [])
                hora_inicio = franja.get('horaInicio', '08:00')
                hora_fin = franja.get('horaFin', '23:00')
                
                hora_actual = datetime.strptime(hora_inicio, '%H:%M')
                hora_limite = datetime.strptime(hora_fin, '%H:%M')
                
                for dia in dias:
                    h = hora_actual
                    while h < hora_limite:
                        slots.add((dia, h.strftime('%H:%M')))
                        h += timedelta(minutes=50)
            
            return slots
        
        slots_p1 = generar_slots_pareja(p1)
        slots_p2 = generar_slots_pareja(p2)
        
        print(f"\n   Pareja 1 (ID {p1.id}):")
        print(f"      Disponibilidad RAW: {p1.disponibilidad_horaria}")
        print(f"      Slots generados: {len(slots_p1)}")
        if slots_p1:
            print(f"      Primeros 5: {list(slots_p1)[:5]}")
        else:
            print(f"      Sin restricciones")
        
        print(f"\n   Pareja 2 (ID {p2.id}):")
        print(f"      Disponibilidad RAW: {p2.disponibilidad_horaria}")
        print(f"      Slots generados: {len(slots_p2)}")
        if slots_p2:
            print(f"      Primeros 5: {list(slots_p2)[:5]}")
        else:
            print(f"      Sin restricciones")
        
        # Buscar slots compatibles
        print(f"\n🔍 Buscando slots compatibles...")
        slots_compatibles = []
        
        for fecha, dia, hora in slots_torneo:
            p1_disponible = len(slots_p1) == 0 or (dia, hora) in slots_p1
            p2_disponible = len(slots_p2) == 0 or (dia, hora) in slots_p2
            
            if p1_disponible and p2_disponible:
                slots_compatibles.append((fecha, dia, hora))
        
        print(f"   Slots compatibles encontrados: {len(slots_compatibles)}")
        if slots_compatibles:
            print(f"   ✅ PUEDEN JUGAR")
            print(f"   Primeros 5 slots compatibles:")
            for slot in slots_compatibles[:5]:
                print(f"      {slot}")
        else:
            print(f"   ❌ NO PUEDEN JUGAR")
            print(f"\n   Análisis detallado:")
            print(f"   Días del torneo: {dias_torneo}")
            if slots_p1:
                dias_p1 = set(s[0] for s in slots_p1)
                print(f"   Días disponibles P1: {dias_p1}")
            else:
                print(f"   P1: Sin restricciones")
            if slots_p2:
                dias_p2 = set(s[0] for s in slots_p2)
                print(f"   Días disponibles P2: {dias_p2}")
            else:
                print(f"   P2: Sin restricciones")
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_fixture()
