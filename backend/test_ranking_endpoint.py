"""
Test del endpoint de ranking para verificar que devuelve partidos_jugados y partidos_ganados
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.controllers.ranking_controller import _get_ranking_from_db

def test_ranking():
    db = next(get_db())
    
    print("\n" + "="*80)
    print("TEST: Endpoint de Ranking")
    print("="*80 + "\n")
    
    # Obtener primeros 5 jugadores
    usuarios = _get_ranking_from_db(db, limit=5, offset=0, sexo=None)
    
    print(f"Total de usuarios obtenidos: {len(usuarios)}\n")
    
    for i, usuario in enumerate(usuarios, 1):
        print(f"Usuario {i}:")
        print(f"  ID: {usuario['id_usuario']}")
        print(f"  Nombre: {usuario['nombre_usuario']}")
        print(f"  Rating: {usuario['rating']}")
        print(f"  Partidos jugados: {usuario['partidos_jugados']}")
        print(f"  Partidos ganados: {usuario['partidos_ganados']}")
        print(f"  Sexo: {usuario['sexo']}")
        
        # Calcular porcentaje
        if usuario['partidos_jugados'] > 0:
            porcentaje = round((usuario['partidos_ganados'] / usuario['partidos_jugados']) * 100)
            print(f"  % Victoria: {porcentaje}%")
        else:
            print(f"  % Victoria: 0%")
        
        print()

if __name__ == "__main__":
    test_ranking()
