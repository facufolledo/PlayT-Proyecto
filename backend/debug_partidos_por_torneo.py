"""
Debug de partidos por torneo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from sqlalchemy import text

def debug_partidos_por_torneo():
    db = next(get_db())
    
    print("🔍 DEBUG PARTIDOS POR TORNEO")
    print("="*60)
    
    # Contar partidos por torneo
    partidos_por_torneo = db.execute(text("""
        SELECT 
            id_torneo,
            COUNT(*) as num_partidos
        FROM partidos 
        WHERE fase = 'zona'
        GROUP BY id_torneo
        ORDER BY id_torneo
    """)).fetchall()
    
    print("📊 PARTIDOS POR TORNEO:")
    for p in partidos_por_torneo:
        print(f"   Torneo {p.id_torneo}: {p.num_partidos} partidos")
    
    # Verificar si hay partidos de otros torneos que puedan estar interfiriendo
    if len(partidos_por_torneo) > 1:
        print(f"\n⚠️ HAY PARTIDOS DE MÚLTIPLES TORNEOS")
        print("   Esto podría estar causando interferencia en la verificación")
    
    # Verificar específicamente el torneo 17
    partidos_t17 = db.execute(text("""
        SELECT COUNT(*) as total
        FROM partidos 
        WHERE fase = 'zona' AND id_torneo = 17
    """)).fetchone()
    
    print(f"\n🎾 TORNEO 17: {partidos_t17.total} partidos")
    
    db.close()

if __name__ == "__main__":
    debug_partidos_por_torneo()