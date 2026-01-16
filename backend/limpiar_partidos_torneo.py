"""
Script para limpiar partidos de un torneo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.config import SessionLocal
from src.models.driveplus_models import Partido

def limpiar_partidos(torneo_id=11):
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print(f"LIMPIANDO PARTIDOS DEL TORNEO {torneo_id}")
        print("=" * 80)
        
        # Contar partidos antes
        count_antes = db.query(Partido).filter(Partido.id_torneo == torneo_id).count()
        print(f"\n📊 Partidos antes: {count_antes}")
        
        if count_antes == 0:
            print("✅ No hay partidos para eliminar")
            return
        
        # Eliminar partidos
        db.query(Partido).filter(Partido.id_torneo == torneo_id).delete()
        db.commit()
        
        # Verificar después
        count_despues = db.query(Partido).filter(Partido.id_torneo == torneo_id).count()
        print(f"📊 Partidos después: {count_despues}")
        
        print(f"\n✅ Se eliminaron {count_antes - count_despues} partidos")
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    torneo_id = int(sys.argv[1]) if len(sys.argv) > 1 else 11
    
    respuesta = input(f"¿Estás seguro de eliminar TODOS los partidos del torneo {torneo_id}? (si/no): ")
    if respuesta.lower() in ['si', 's', 'yes', 'y']:
        limpiar_partidos(torneo_id)
    else:
        print("Operación cancelada")
