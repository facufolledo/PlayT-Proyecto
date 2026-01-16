"""
Script para verificar partidos de un torneo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.config import SessionLocal
from src.models.driveplus_models import Partido

def verificar_partidos(torneo_id=11):
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print(f"VERIFICANDO PARTIDOS DEL TORNEO {torneo_id}")
        print("=" * 80)
        
        # Buscar partidos del torneo
        partidos = db.query(Partido).filter(
            Partido.id_torneo == torneo_id
        ).all()
        
        print(f"\n📊 Total de partidos encontrados: {len(partidos)}")
        
        if len(partidos) == 0:
            print("\n✅ No hay partidos creados para este torneo")
            print("   Esto es correcto si aún no has generado las zonas y el fixture")
        else:
            print("\n⚠️  Se encontraron partidos:")
            for partido in partidos[:10]:  # Mostrar primeros 10
                print(f"   - Partido ID {partido.id_partido}: Estado {partido.estado}")
                print(f"     Zona: {partido.zona_id}, Fecha: {partido.fecha}")
        
        # Verificar partidos de otros torneos
        print(f"\n📋 Partidos de otros torneos:")
        otros_torneos = db.query(Partido.id_torneo).distinct().all()
        for (tid,) in otros_torneos:
            if tid != torneo_id:
                count = db.query(Partido).filter(Partido.id_torneo == tid).count()
                print(f"   - Torneo {tid}: {count} partidos")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    torneo_id = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    verificar_partidos(torneo_id)
