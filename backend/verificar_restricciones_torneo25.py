"""
Verificar restricciones del torneo 25
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.database.config import get_db
from src.models.torneo_models import TorneoPareja
from src.models.driveplus_models import PerfilUsuario
import json

TORNEO_ID = 25

def verificar():
    db = next(get_db())
    
    try:
        parejas = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == TORNEO_ID
        ).order_by(TorneoPareja.id).all()
        
        print(f"TORNEO {TORNEO_ID} - Total parejas: {len(parejas)}\n")
        
        for pareja in parejas:
            p1 = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == pareja.jugador1_id
            ).first()
            p2 = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == pareja.jugador2_id
            ).first()
            
            nombre_j1 = f"{p1.nombre} {p1.apellido}" if p1 else f"Usuario {pareja.jugador1_id}"
            nombre_j2 = f"{p2.nombre} {p2.apellido}" if p2 else f"Usuario {pareja.jugador2_id}"
            
            tiene = "SI" if pareja.disponibilidad_horaria else "NO"
            
            print(f"ID {pareja.id:3} | {tiene:2} | {pareja.estado:12} | {nombre_j1:30} / {nombre_j2}")
            
            if pareja.disponibilidad_horaria:
                print(f"      Restricciones: {json.dumps(pareja.disponibilidad_horaria, ensure_ascii=False)}")
        
        con_restricciones = sum(1 for p in parejas if p.disponibilidad_horaria)
        print(f"\nCon restricciones: {con_restricciones}/{len(parejas)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verificar()
