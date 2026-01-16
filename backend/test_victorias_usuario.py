"""
Test para verificar victorias de un usuario específico
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.models.driveplus_models import Usuario, HistorialRating, Partido
from sqlalchemy import and_

def test_victorias_usuario():
    db = next(get_db())
    
    # Usuario libre_1 (ID 11)
    usuario_id = 11
    
    print("\n" + "="*80)
    print(f"VERIFICAR VICTORIAS DEL USUARIO {usuario_id}")
    print("="*80 + "\n")
    
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    print(f"Usuario: {usuario.nombre_usuario}")
    print(f"Rating: {usuario.rating}")
    print(f"Partidos jugados: {usuario.partidos_jugados}\n")
    
    # Obtener historial de rating
    historial = db.query(HistorialRating).join(
        Partido, HistorialRating.id_partido == Partido.id_partido
    ).filter(
        and_(
            HistorialRating.id_usuario == usuario_id,
            Partido.estado.in_(["confirmado", "finalizado"])
        )
    ).order_by(HistorialRating.creado_en.desc()).all()
    
    print(f"Total de registros en historial_rating: {len(historial)}\n")
    
    victorias = 0
    derrotas = 0
    
    print("DETALLE DE PARTIDOS:")
    print("-" * 80)
    for h in historial:
        partido = db.query(Partido).filter(Partido.id_partido == h.id_partido).first()
        resultado = "VICTORIA" if h.delta > 0 else "DERROTA"
        if h.delta > 0:
            victorias += 1
        else:
            derrotas += 1
        
        print(f"Partido {h.id_partido}:")
        print(f"  Tipo: {partido.tipo}")
        print(f"  Estado: {partido.estado}")
        print(f"  Delta: {h.delta:+d}")
        print(f"  Resultado: {resultado}")
        print(f"  Rating antes: {h.rating_antes} → después: {h.rating_despues}")
        print()
    
    print("="*80)
    print(f"RESUMEN:")
    print(f"  Victorias: {victorias}")
    print(f"  Derrotas: {derrotas}")
    print(f"  Total: {victorias + derrotas}")
    print(f"  Winrate: {round(victorias / (victorias + derrotas) * 100)}%")
    print("="*80)

if __name__ == "__main__":
    test_victorias_usuario()
