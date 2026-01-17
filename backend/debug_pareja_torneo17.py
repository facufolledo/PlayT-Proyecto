"""
Debug específico de parejas del torneo 17
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.models.torneo_models import TorneoPareja
from src.models.driveplus_models import Usuario
import json

def debug_pareja_torneo17():
    db = next(get_db())
    
    print("🔍 DEBUG PAREJAS TORNEO 17")
    print("="*60)
    
    # Buscar parejas con disponibilidad específica
    parejas = db.query(TorneoPareja).filter(
        TorneoPareja.torneo_id == 17,
        TorneoPareja.disponibilidad_horaria.isnot(None)
    ).limit(5).all()
    
    for pareja in parejas:
        print(f"\n🎾 Pareja {pareja.id}")
        
        # Obtener nombres de jugadores
        j1 = db.query(Usuario).filter(Usuario.id_usuario == pareja.jugador1_id).first()
        j2 = db.query(Usuario).filter(Usuario.id_usuario == pareja.jugador2_id).first()
        
        j1_nombre = j1.nombre_usuario if j1 else f"Usuario {pareja.jugador1_id}"
        j2_nombre = j2.nombre_usuario if j2 else f"Usuario {pareja.jugador2_id}"
        
        print(f"   Jugadores: {j1_nombre} & {j2_nombre}")
        print(f"   Disponibilidad: {json.dumps(pareja.disponibilidad_horaria, indent=2)}")
        
        # Verificar formato
        disp = pareja.disponibilidad_horaria
        if 'franjas' in disp:
            for i, franja in enumerate(disp['franjas']):
                print(f"   Franja {i+1}: {franja['dias']} {franja['horaInicio']}-{franja['horaFin']}")
    
    db.close()

if __name__ == "__main__":
    debug_pareja_torneo17()