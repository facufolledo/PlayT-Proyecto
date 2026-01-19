#!/usr/bin/env python3
"""
Script para eliminar fixture del torneo 24
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.torneo_models import TorneoZona, TorneoSlot
from src.models.driveplus_models import Partido

def eliminar_fixture():
    """Eliminar fixture del torneo 24"""
    db = next(get_db())
    
    try:
        torneo_id = 24
        
        print(f"🗑️ Eliminando fixture del torneo {torneo_id}...")
        
        # Obtener zonas del torneo
        zonas = db.query(TorneoZona).filter(TorneoZona.torneo_id == torneo_id).all()
        zona_ids = [z.id for z in zonas]
        
        # Eliminar partidos de esas zonas
        if zona_ids:
            partidos = db.query(Partido).filter(Partido.zona_id.in_(zona_ids)).all()
            print(f"   🗑️ Eliminando {len(partidos)} partidos...")
            for partido in partidos:
                db.delete(partido)
        else:
            print(f"   ℹ️ No hay zonas en el torneo")
            partidos = []
        
        # Eliminar slots
        slots = db.query(TorneoSlot).filter(TorneoSlot.torneo_id == torneo_id).all()
        print(f"   🗑️ Eliminando {len(slots)} slots...")
        for slot in slots:
            db.delete(slot)
        
        db.commit()
        
        print(f"\n✅ Fixture eliminado exitosamente")
        print(f"   • {len(partidos)} partidos eliminados")
        print(f"   • {len(slots)} slots eliminados")
        print(f"\n💡 Las zonas se mantienen intactas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🗑️ ELIMINAR FIXTURE TORNEO 24")
    print("="*60)
    if eliminar_fixture():
        print(f"\n✅ Listo para generar nuevo fixture")
    else:
        print(f"\n❌ Error al eliminar fixture")
