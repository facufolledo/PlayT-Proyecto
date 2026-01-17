"""
Debug de jugadores específicos mencionados en la verificación
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from sqlalchemy import text

def debug_jugadores_especificos():
    db = next(get_db())
    
    print("🔍 DEBUG JUGADORES ESPECÍFICOS")
    print("="*60)
    
    # Jugadores mencionados en la verificación
    jugadores_problema = ['demo', 'santiagogfolledo', 'rotobon425', '4ta_2', 'samirlin28', 'an858h8mja', 'facundo2', 'facundo']
    
    for jugador in jugadores_problema:
        print(f"\n🎾 JUGADOR: {jugador}")
        
        # Buscar todos los partidos de este jugador
        partidos = db.execute(text("""
            SELECT DISTINCT
                p.id_partido,
                p.fecha_hora,
                tc.nombre as categoria,
                tz.nombre as zona,
                CASE 
                    WHEN tp1.jugador1_id = u.id_usuario OR tp1.jugador2_id = u.id_usuario THEN 'pareja1'
                    ELSE 'pareja2'
                END as posicion
            FROM partidos p
            JOIN torneo_zonas tz ON p.zona_id = tz.id
            JOIN torneo_categorias tc ON tz.categoria_id = tc.id
            LEFT JOIN torneos_parejas tp1 ON p.pareja1_id = tp1.id
            LEFT JOIN torneos_parejas tp2 ON p.pareja2_id = tp2.id
            JOIN usuarios u ON u.nombre_usuario = :jugador
            WHERE p.fase = 'zona' 
            AND p.id_torneo = 17
            AND (
                tp1.jugador1_id = u.id_usuario OR tp1.jugador2_id = u.id_usuario OR
                tp2.jugador1_id = u.id_usuario OR tp2.jugador2_id = u.id_usuario
            )
            ORDER BY p.fecha_hora
        """), {"jugador": jugador}).fetchall()
        
        if partidos:
            print(f"   📋 Partidos ({len(partidos)}):")
            for i, p in enumerate(partidos):
                print(f"      {i+1}. {p.fecha_hora.strftime('%Y-%m-%d %H:%M')} - {p.categoria} {p.zona} (ID: {p.id_partido})")
            
            # Calcular diferencias
            if len(partidos) > 1:
                print(f"   ⏱️ Diferencias:")
                for i in range(len(partidos) - 1):
                    p1 = partidos[i]
                    p2 = partidos[i + 1]
                    diferencia = (p2.fecha_hora - p1.fecha_hora).total_seconds() / 60
                    print(f"      Entre partido {i+1} y {i+2}: {diferencia:.0f} minutos")
        else:
            print(f"   ❌ No se encontraron partidos")
    
    db.close()

if __name__ == "__main__":
    debug_jugadores_especificos()