"""
Debug de la generación de slots
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.services.torneo_fixture_global_service import TorneoFixtureGlobalService
from src.models.torneo_models import Torneo

def debug_slots():
    db = next(get_db())
    
    print("🔍 DEBUG GENERACIÓN DE SLOTS")
    print("="*60)
    
    # Obtener torneo 17
    torneo = db.query(Torneo).filter(Torneo.id == 17).first()
    if not torneo:
        print("❌ Torneo no encontrado")
        return
    
    print(f"🏆 Torneo: {torneo.nombre}")
    print(f"📅 Fechas: {torneo.fecha_inicio} - {torneo.fecha_fin}")
    print(f"⏰ Horarios: {torneo.horarios_disponibles}")
    
    # Generar slots
    slots = TorneoFixtureGlobalService._generar_slots_torneo(
        torneo, torneo.horarios_disponibles or {}
    )
    
    print(f"\n📋 SLOTS GENERADOS ({len(slots)}):")
    
    # Agrupar por fecha
    slots_por_fecha = {}
    for fecha, dia, hora in slots:
        if fecha not in slots_por_fecha:
            slots_por_fecha[fecha] = []
        slots_por_fecha[fecha].append((dia, hora))
    
    for fecha in sorted(slots_por_fecha.keys()):
        print(f"\n📅 {fecha}:")
        slots_dia = sorted(slots_por_fecha[fecha], key=lambda x: x[1])
        
        # Mostrar primeros y últimos slots
        if len(slots_dia) <= 10:
            for dia, hora in slots_dia:
                print(f"   {hora} ({dia})")
        else:
            print(f"   Primeros 5:")
            for dia, hora in slots_dia[:5]:
                print(f"     {hora} ({dia})")
            print(f"   ...")
            print(f"   Últimos 5:")
            for dia, hora in slots_dia[-5:]:
                print(f"     {hora} ({dia})")
    
    # Verificar si hay slots problemáticos
    print(f"\n🔍 ANÁLISIS DE SLOTS:")
    slots_problematicos = []
    
    for fecha, dia, hora in slots:
        hora_mins = int(hora.split(':')[0]) * 60 + int(hora.split(':')[1])
        
        # Verificar si está fuera de horarios razonables
        if hora_mins < 360 or hora_mins > 1440:  # Antes de 6:00 AM o después de 24:00
            slots_problematicos.append((fecha, dia, hora, hora_mins))
    
    if slots_problematicos:
        print(f"❌ SLOTS PROBLEMÁTICOS ({len(slots_problematicos)}):")
        for fecha, dia, hora, mins in slots_problematicos[:10]:
            print(f"   {fecha} {hora} ({mins} minutos)")
    else:
        print("✅ No se encontraron slots problemáticos")
    
    db.close()

if __name__ == "__main__":
    debug_slots()