"""
Script para verificar el rating de un usuario específico
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import SessionLocal
from src.models.driveplus_models import Usuario, HistorialRating, PartidoJugador

def verificar_rating():
    """Verificar rating de usuario"""
    db = SessionLocal()
    
    try:
        # Buscar usuario Facundo2
        usuario = db.query(Usuario).filter(
            Usuario.nombre_usuario == 'facundo2'
        ).first()
        
        if not usuario:
            print("Usuario no encontrado")
            return
        
        print(f"\n=== RATING DE {usuario.nombre_usuario} ===\n")
        print(f"Rating actual en BD: {usuario.rating}")
        print(f"Partidos jugados: {usuario.partidos_jugados}")
        
        # Obtener historial de rating
        print("\n--- Historial de Rating (últimos 5) ---")
        historial = db.query(HistorialRating).filter(
            HistorialRating.id_usuario == usuario.id_usuario
        ).order_by(HistorialRating.id_historial.desc()).limit(5).all()
        
        for h in historial:
            print(f"Partido {h.id_partido}: {h.rating_antes} → {h.rating_despues} ({'+' if h.delta > 0 else ''}{h.delta})")
        
        # Verificar último partido
        print("\n--- Último Partido Jugado ---")
        ultimo_partido = db.query(PartidoJugador).filter(
            PartidoJugador.id_usuario == usuario.id_usuario
        ).order_by(PartidoJugador.id_partido.desc()).first()
        
        if ultimo_partido:
            print(f"ID Partido: {ultimo_partido.id_partido}")
            print(f"Rating antes: {ultimo_partido.rating_antes}")
            print(f"Rating después: {ultimo_partido.rating_despues}")
            print(f"Cambio Elo: {ultimo_partido.cambio_elo}")
        
        print("\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    verificar_rating()
