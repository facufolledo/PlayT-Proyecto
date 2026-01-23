"""
Script para listar todas las parejas del torneo 25
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.database.config import get_db
from src.models.torneo_models import TorneoPareja
from src.models.driveplus_models import PerfilUsuario

TORNEO_ID = 25

def listar_parejas():
    """Lista todas las parejas del torneo"""
    
    db = next(get_db())
    
    try:
        print("=" * 80)
        print(f"PAREJAS DEL TORNEO {TORNEO_ID}")
        print("=" * 80)
        
        parejas = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == TORNEO_ID
        ).order_by(TorneoPareja.id).all()
        
        print(f"\nTotal de parejas: {len(parejas)}\n")
        
        for i, pareja in enumerate(parejas, 1):
            # Obtener perfiles
            p1 = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == pareja.jugador1_id
            ).first()
            p2 = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == pareja.jugador2_id
            ).first()
            
            nombre_j1 = f"{p1.nombre} {p1.apellido}" if p1 else f"Usuario {pareja.jugador1_id}"
            nombre_j2 = f"{p2.nombre} {p2.apellido}" if p2 else f"Usuario {pareja.jugador2_id}"
            
            tiene_restricciones = "✅" if pareja.disponibilidad_horaria else "❌"
            
            print(f"{i:2}. ID: {pareja.id:3} | {tiene_restricciones} | {pareja.estado:12} | {nombre_j1:30} / {nombre_j2}")
            
            if pareja.disponibilidad_horaria:
                print(f"    Restricciones: {pareja.disponibilidad_horaria}")
        
        # Contar con/sin restricciones
        con_restricciones = sum(1 for p in parejas if p.disponibilidad_horaria)
        sin_restricciones = len(parejas) - con_restricciones
        
        print(f"\n{'=' * 80}")
        print(f"Con restricciones: {con_restricciones}")
        print(f"Sin restricciones: {sin_restricciones}")
        print(f"{'=' * 80}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    listar_parejas()
