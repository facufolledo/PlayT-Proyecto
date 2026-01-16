"""
Verificar partidos del torneo 11
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.models.torneo_models import TorneoPareja, TorneoZona
from src.models.driveplus_models import Partido
from sqlalchemy import and_

def verificar_partidos():
    db = next(get_db())
    
    torneo_id = 11
    
    print(f"\n{'='*80}")
    print(f"PARTIDOS DEL TORNEO {torneo_id}")
    print(f"{'='*80}\n")
    
    partidos = db.query(Partido).filter(
        Partido.id_torneo == torneo_id
    ).order_by(Partido.fecha_hora).all()
    
    print(f"Total de partidos: {len(partidos)}\n")
    
    for partido in partidos:
        # Obtener nombres de parejas
        pareja1 = db.query(TorneoPareja).filter(TorneoPareja.id == partido.pareja1_id).first()
        pareja2 = db.query(TorneoPareja).filter(TorneoPareja.id == partido.pareja2_id).first()
        
        # Obtener zona
        zona = db.query(TorneoZona).filter(TorneoZona.id == partido.zona_id).first() if partido.zona_id else None
        
        print(f"Partido {partido.id_partido}:")
        print(f"  Zona: {zona.nombre if zona else 'Sin zona'} (Cat: {partido.categoria_id})")
        print(f"  Pareja 1: {pareja1.id if pareja1 else 'N/A'}")
        print(f"  Pareja 2: {pareja2.id if pareja2 else 'N/A'}")
        print(f"  Fecha/Hora: {partido.fecha_hora}")
        print(f"  Cancha: {partido.cancha_id}")
        print(f"  Estado: {partido.estado}")
        print(f"  Fase: {partido.fase}")
        
        # Verificar disponibilidad de parejas
        if pareja1:
            print(f"  Disponibilidad P1: {pareja1.disponibilidad_horaria}")
        if pareja2:
            print(f"  Disponibilidad P2: {pareja2.disponibilidad_horaria}")
        
        print()

if __name__ == "__main__":
    verificar_partidos()
