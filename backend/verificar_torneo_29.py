"""
Script para verificar el estado del torneo ID 29
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from src.database.config import SessionLocal
from src.models.torneo_models import Torneo, TorneoPareja, TorneoZona, TorneoZonaPareja
from src.models.Drive+_models import Partido

def verificar_torneo():
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("VERIFICANDO TORNEO ID 29")
        print("="*70)
        
        # 1. Verificar torneo
        torneo = db.query(Torneo).filter(Torneo.id == 29).first()
        if not torneo:
            print("❌ No existe el torneo ID 29")
            return
        
        print(f"\n✅ Torneo encontrado:")
        print(f"   ID: {torneo.id}")
        print(f"   Nombre: {torneo.nombre}")
        print(f"   Estado: {torneo.estado}")
        print(f"   Creado por: {torneo.creado_por}")
        
        # 2. Verificar parejas
        parejas = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == 29
        ).all()
        
        print(f"\n📊 Parejas inscritas: {len(parejas)}")
        for pareja in parejas:
            print(f"   - ID {pareja.id}: Jugadores {pareja.jugador1_id}/{pareja.jugador2_id} - Estado: {pareja.estado}")
        
        # 3. Verificar zonas
        zonas = db.query(TorneoZona).filter(
            TorneoZona.torneo_id == 29
        ).all()
        
        print(f"\n🎯 Zonas creadas: {len(zonas)}")
        for zona in zonas:
            parejas_zona = db.query(TorneoZonaPareja).filter(
                TorneoZonaPareja.zona_id == zona.id
            ).count()
            print(f"   - {zona.nombre} (ID {zona.id}): {parejas_zona} parejas")
        
        # 4. Verificar partidos
        partidos = db.query(Partido).filter(
            Partido.id_torneo == 29
        ).all()
        
        print(f"\n📅 Partidos generados: {len(partidos)}")
        for partido in partidos:
            print(f"   - Partido {partido.id_partido}: Pareja {partido.pareja1_id} vs {partido.pareja2_id} - Estado: {partido.estado}")
        
        print("\n" + "="*70)
        
        # 5. Verificar endpoint de parejas
        print("\n🔍 Verificando datos para el endpoint /torneos/29/parejas:")
        
        # Simular query del endpoint
        parejas_query = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == 29
        ).all()
        
        print(f"   Total parejas: {len(parejas_query)}")
        for p in parejas_query:
            print(f"   - Pareja {p.id}:")
            print(f"     • Jugador 1: {p.jugador1_id}")
            print(f"     • Jugador 2: {p.jugador2_id}")
            print(f"     • Estado: {p.estado}")
            print(f"     • Categoría: {p.categoria_asignada}")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verificar_torneo()
