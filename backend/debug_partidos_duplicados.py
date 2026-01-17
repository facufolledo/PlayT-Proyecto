"""
Debug de partidos duplicados
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from sqlalchemy import text

def debug_duplicados():
    db = next(get_db())
    
    print("🔍 DEBUG PARTIDOS DUPLICADOS")
    print("="*60)
    
    # Buscar jugadores con múltiples partidos en el mismo horario
    duplicados = db.execute(text("""
        WITH jugador_partidos AS (
            SELECT 
                u.nombre_usuario,
                u.id_usuario,
                p.fecha_hora,
                p.id_partido,
                tc.nombre as categoria,
                tz.nombre as zona
            FROM partidos p
            JOIN torneo_zonas tz ON p.zona_id = tz.id
            JOIN torneo_categorias tc ON tz.categoria_id = tc.id
            JOIN torneos_parejas tp1 ON p.pareja1_id = tp1.id
            JOIN usuarios u ON (tp1.jugador1_id = u.id_usuario OR tp1.jugador2_id = u.id_usuario)
            WHERE p.fase = 'zona' AND p.id_torneo = 17
            
            UNION ALL
            
            SELECT 
                u.nombre_usuario,
                u.id_usuario,
                p.fecha_hora,
                p.id_partido,
                tc.nombre as categoria,
                tz.nombre as zona
            FROM partidos p
            JOIN torneo_zonas tz ON p.zona_id = tz.id
            JOIN torneo_categorias tc ON tz.categoria_id = tc.id
            JOIN torneos_parejas tp2 ON p.pareja2_id = tp2.id
            JOIN usuarios u ON (tp2.jugador1_id = u.id_usuario OR tp2.jugador2_id = u.id_usuario)
            WHERE p.fase = 'zona' AND p.id_torneo = 17
        )
        SELECT 
            nombre_usuario,
            fecha_hora,
            COUNT(*) as num_partidos,
            STRING_AGG(DISTINCT categoria || ' ' || zona, ', ') as partidos_info
        FROM jugador_partidos
        GROUP BY nombre_usuario, fecha_hora
        HAVING COUNT(*) > 1
        ORDER BY nombre_usuario, fecha_hora
    """)).fetchall()
    
    if duplicados:
        print(f"❌ JUGADORES CON PARTIDOS DUPLICADOS ({len(duplicados)}):")
        for d in duplicados:
            print(f"   🚨 {d.nombre_usuario}")
            print(f"      Hora: {d.fecha_hora}")
            print(f"      Partidos: {d.num_partidos}")
            print(f"      Categorías: {d.partidos_info}")
            print()
    else:
        print("✅ No se encontraron partidos duplicados")
    
    # Verificar partidos con diferencia de 50 minutos exactos
    print(f"\n🔍 VERIFICANDO PARTIDOS CON 50 MINUTOS DE DIFERENCIA:")
    
    partidos_50min = db.execute(text("""
        WITH jugador_partidos AS (
            SELECT 
                u.nombre_usuario,
                p.fecha_hora,
                tc.nombre as categoria,
                tz.nombre as zona
            FROM partidos p
            JOIN torneo_zonas tz ON p.zona_id = tz.id
            JOIN torneo_categorias tc ON tz.categoria_id = tc.id
            JOIN torneos_parejas tp1 ON p.pareja1_id = tp1.id
            JOIN usuarios u ON (tp1.jugador1_id = u.id_usuario OR tp1.jugador2_id = u.id_usuario)
            WHERE p.fase = 'zona' AND p.id_torneo = 17
            
            UNION ALL
            
            SELECT 
                u.nombre_usuario,
                p.fecha_hora,
                tc.nombre as categoria,
                tz.nombre as zona
            FROM partidos p
            JOIN torneo_zonas tz ON p.zona_id = tz.id
            JOIN torneo_categorias tc ON tz.categoria_id = tc.id
            JOIN torneos_parejas tp2 ON p.pareja2_id = tp2.id
            JOIN usuarios u ON (tp2.jugador1_id = u.id_usuario OR tp2.jugador2_id = u.id_usuario)
            WHERE p.fase = 'zona' AND p.id_torneo = 17
        ),
        partidos_ordenados AS (
            SELECT 
                nombre_usuario,
                fecha_hora,
                categoria,
                zona,
                LAG(fecha_hora) OVER (PARTITION BY nombre_usuario ORDER BY fecha_hora) as fecha_anterior
            FROM jugador_partidos
        )
        SELECT 
            nombre_usuario,
            fecha_anterior,
            fecha_hora,
            categoria,
            zona,
            EXTRACT(EPOCH FROM (fecha_hora - fecha_anterior))/60 as diferencia_minutos
        FROM partidos_ordenados
        WHERE fecha_anterior IS NOT NULL
        AND EXTRACT(EPOCH FROM (fecha_hora - fecha_anterior))/60 = 50
        ORDER BY nombre_usuario, fecha_hora
    """)).fetchall()
    
    if partidos_50min:
        print(f"⚠️ PARTIDOS CON EXACTAMENTE 50 MINUTOS DE DIFERENCIA ({len(partidos_50min)}):")
        for p in partidos_50min:
            print(f"   ⚠️ {p.nombre_usuario}")
            print(f"      Partido 1: {p.fecha_anterior.strftime('%H:%M')}")
            print(f"      Partido 2: {p.fecha_hora.strftime('%H:%M')} - {p.categoria} {p.zona}")
            print(f"      Diferencia: {p.diferencia_minutos} minutos")
            print()
    else:
        print("✅ No hay partidos con exactamente 50 minutos de diferencia")
    
    db.close()

if __name__ == "__main__":
    debug_duplicados()