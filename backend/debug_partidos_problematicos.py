"""
Debug de partidos con horarios problemáticos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from sqlalchemy import text

def debug_partidos_problematicos():
    db = next(get_db())
    
    print("🔍 DEBUG PARTIDOS CON HORARIOS PROBLEMÁTICOS")
    print("="*60)
    
    # Buscar partidos con horarios extraños
    partidos = db.execute(text("""
        SELECT 
            p.id_partido,
            p.fecha_hora,
            tc.nombre as categoria,
            tz.nombre as zona,
            EXTRACT(hour FROM p.fecha_hora) as hora,
            EXTRACT(minute FROM p.fecha_hora) as minuto
        FROM partidos p
        JOIN torneo_zonas tz ON p.zona_id = tz.id
        JOIN torneo_categorias tc ON tz.categoria_id = tc.id
        WHERE p.fase = 'zona'
        AND p.id_torneo = 17
        ORDER BY p.fecha_hora
        LIMIT 10
    """)).fetchall()
    
    print(f"📋 PRIMEROS 10 PARTIDOS:")
    for p in partidos:
        hora_str = f"{int(p.hora):02d}:{int(p.minuto):02d}"
        print(f"   Partido {p.id_partido}: {p.fecha_hora.strftime('%Y-%m-%d')} {hora_str} - {p.categoria} {p.zona}")
    
    # Buscar partidos después de medianoche
    partidos_noche = db.execute(text("""
        SELECT 
            p.id_partido,
            p.fecha_hora,
            tc.nombre as categoria,
            tz.nombre as zona,
            EXTRACT(hour FROM p.fecha_hora) as hora
        FROM partidos p
        JOIN torneo_zonas tz ON p.zona_id = tz.id
        JOIN torneo_categorias tc ON tz.categoria_id = tc.id
        WHERE p.fase = 'zona'
        AND p.id_torneo = 17
        AND EXTRACT(hour FROM p.fecha_hora) < 6
        ORDER BY p.fecha_hora
    """)).fetchall()
    
    if partidos_noche:
        print(f"\n❌ PARTIDOS DESPUÉS DE MEDIANOCHE ({len(partidos_noche)}):")
        for p in partidos_noche:
            print(f"   Partido {p.id_partido}: {p.fecha_hora} - {p.categoria} {p.zona}")
    else:
        print(f"\n✅ No hay partidos después de medianoche")
    
    db.close()

if __name__ == "__main__":
    debug_partidos_problematicos()