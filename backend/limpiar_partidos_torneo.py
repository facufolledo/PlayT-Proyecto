"""
Limpiar todos los partidos del torneo 11 para regenerar fixture
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.models.driveplus_models import Partido

def limpiar_partidos():
    db = next(get_db())
    
    torneo_id = 11
    
    print(f"\n{'='*80}")
    print(f"LIMPIAR PARTIDOS DEL TORNEO {torneo_id}")
    print(f"{'='*80}\n")
    
    # Contar partidos
    partidos = db.query(Partido).filter(Partido.id_torneo == torneo_id).all()
    total = len(partidos)
    
    print(f"Total de partidos a eliminar: {total}\n")
    
    if total == 0:
        print("✅ No hay partidos para eliminar")
        return
    
    confirmacion = input(f"⚠️  ¿Estás seguro de eliminar {total} partidos? (escribe 'SI' para confirmar): ")
    
    if confirmacion != "SI":
        print("❌ Operación cancelada")
        return
    
    # Eliminar partidos
    db.query(Partido).filter(Partido.id_torneo == torneo_id).delete()
    db.commit()
    
    print(f"\n✅ {total} partidos eliminados exitosamente")
    print(f"\n💡 Ahora puedes regenerar el fixture desde el frontend")

if __name__ == "__main__":
    limpiar_partidos()
