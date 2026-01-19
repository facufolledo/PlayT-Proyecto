#!/usr/bin/env python3
"""
Debug de restricciones de usuarios 14 y 15
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.torneo_models import TorneoPareja
import json

def debug_restricciones():
    """Ver restricciones de usuarios 14 y 15"""
    db = next(get_db())
    
    try:
        torneo_id = 24
        usuarios = [14, 15]
        
        print(f"🔍 Restricciones de usuarios {usuarios} en torneo {torneo_id}")
        print("="*60)
        
        for user_id in usuarios:
            # Buscar parejas donde este usuario participa
            parejas = db.query(TorneoPareja).filter(
                TorneoPareja.torneo_id == torneo_id,
                ((TorneoPareja.jugador1_id == user_id) | (TorneoPareja.jugador2_id == user_id))
            ).all()
            
            print(f"\n👤 Usuario {user_id}:")
            for pareja in parejas:
                print(f"   Pareja ID: {pareja.id}")
                print(f"   Jugadores: {pareja.jugador1_id} / {pareja.jugador2_id}")
                print(f"   Estado: {pareja.estado}")
                print(f"   Disponibilidad: {json.dumps(pareja.disponibilidad_horaria, indent=6, ensure_ascii=False)}")
                print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_restricciones()
