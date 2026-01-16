"""
Script para debuggear la disponibilidad horaria y ver por qué no se programan partidos
"""
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.torneo_models import TorneoPareja, Torneo

def debug_disponibilidad():
    """
    Analiza la disponibilidad horaria de las parejas del torneo 11
    """
    print("=" * 80)
    print("DEBUG: DISPONIBILIDAD HORARIA - TORNEO 11")
    print("=" * 80)
    
    try:
        # Usar DATABASE_URL directamente
        from dotenv import load_dotenv
        load_dotenv()
        database_url = os.getenv("DATABASE_URL")
        
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        torneo_id = 11
        
        # Obtener torneo
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            print("❌ Torneo no encontrado")
            return
        
        print(f"\n📋 Torneo: {torneo.nombre}")
        print(f"   Fecha inicio: {torneo.fecha_inicio}")
        print(f"   Fecha fin: {torneo.fecha_fin}")
        print(f"\n   Horarios del torneo:")
        print(f"   {torneo.horarios_disponibles}")
        
        # Obtener parejas
        parejas = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == torneo_id
        ).all()
        
        print(f"\n📊 Total de parejas: {len(parejas)}")
        print("=" * 80)
        
        for pareja in parejas[:10]:  # Primeras 10 parejas
            print(f"\n🎾 Pareja {pareja.id}")
            print(f"   Jugador 1: {pareja.jugador1_id}")
            print(f"   Jugador 2: {pareja.jugador2_id}")
            print(f"   Categoría: {pareja.categoria_id}")
            print(f"   Estado: {pareja.estado}")
            print(f"\n   Disponibilidad horaria RAW:")
            print(f"   {pareja.disponibilidad_horaria}")
            
            # Analizar disponibilidad
            disp = pareja.disponibilidad_horaria or {}
            if not disp or not disp.get('franjas'):
                print(f"   ✅ Sin restricciones (disponible en cualquier horario)")
            else:
                franjas = disp.get('franjas', [])
                print(f"\n   📅 Franjas horarias ({len(franjas)}):")
                for i, franja in enumerate(franjas, 1):
                    dias = franja.get('dias', [])
                    hora_inicio = franja.get('horaInicio', 'N/A')
                    hora_fin = franja.get('horaFin', 'N/A')
                    print(f"      {i}. Días: {dias}")
                    print(f"         Horario: {hora_inicio} - {hora_fin}")
            
            print("-" * 80)
        
        # Analizar compatibilidad entre dos parejas de ejemplo
        if len(parejas) >= 2:
            print("\n" + "=" * 80)
            print("🔍 ANÁLISIS DE COMPATIBILIDAD: Pareja 1 vs Pareja 2")
            print("=" * 80)
            
            p1 = parejas[0]
            p2 = parejas[1]
            
            print(f"\nPareja 1 (ID {p1.id})")
            disp1 = p1.disponibilidad_horaria or {}
            print(f"Disponibilidad: {disp1}")
            
            print(f"\nPareja 2 (ID {p2.id})")
            disp2 = p2.disponibilidad_horaria or {}
            print(f"Disponibilidad: {disp2}")
            
            # Simular la lógica del servicio
            from datetime import datetime, timedelta
            
            # Generar slots de pareja 1
            slots_p1 = set()
            if disp1 and disp1.get('franjas'):
                for franja in disp1['franjas']:
                    dias = franja.get('dias', [])
                    hora_inicio = franja.get('horaInicio', '08:00')
                    hora_fin = franja.get('horaFin', '23:00')
                    
                    hora_actual = datetime.strptime(hora_inicio, '%H:%M')
                    hora_limite = datetime.strptime(hora_fin, '%H:%M')
                    
                    for dia in dias:
                        h = hora_actual
                        while h < hora_limite:
                            slots_p1.add((dia, h.strftime('%H:%M')))
                            h += timedelta(minutes=50)
            
            # Generar slots de pareja 2
            slots_p2 = set()
            if disp2 and disp2.get('franjas'):
                for franja in disp2['franjas']:
                    dias = franja.get('dias', [])
                    hora_inicio = franja.get('horaInicio', '08:00')
                    hora_fin = franja.get('horaFin', '23:00')
                    
                    hora_actual = datetime.strptime(hora_inicio, '%H:%M')
                    hora_limite = datetime.strptime(hora_fin, '%H:%M')
                    
                    for dia in dias:
                        h = hora_actual
                        while h < hora_limite:
                            slots_p2.add((dia, h.strftime('%H:%M')))
                            h += timedelta(minutes=50)
            
            print(f"\n📊 Slots generados:")
            print(f"   Pareja 1: {len(slots_p1)} slots")
            if slots_p1:
                print(f"   Primeros 5: {list(slots_p1)[:5]}")
            else:
                print(f"   (Sin restricciones)")
            
            print(f"\n   Pareja 2: {len(slots_p2)} slots")
            if slots_p2:
                print(f"   Primeros 5: {list(slots_p2)[:5]}")
            else:
                print(f"   (Sin restricciones)")
            
            # Verificar compatibilidad
            if len(slots_p1) == 0 or len(slots_p2) == 0:
                print(f"\n✅ COMPATIBLES (al menos una sin restricciones)")
            else:
                slots_comunes = slots_p1.intersection(slots_p2)
                print(f"\n   Slots en común: {len(slots_comunes)}")
                if slots_comunes:
                    print(f"   ✅ COMPATIBLES")
                    print(f"   Primeros 5 slots comunes: {list(slots_comunes)[:5]}")
                else:
                    print(f"   ❌ NO COMPATIBLES")
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_disponibilidad()
