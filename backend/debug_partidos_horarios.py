"""
Script para debuggear los horarios de los partidos del torneo 11
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Conectar a la base de datos
DATABASE_URL = "postgresql+pg8000://postgres:vZTwMxqfXXqPqPPqJqvXxqPPqPPPPPPP@autorack.proxy.rlwy.net:28517/railway"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    print("=" * 60)
    print("DEBUG: HORARIOS DE PARTIDOS - TORNEO 11")
    print("=" * 60)
    
    # Ver horarios del torneo
    torneo_query = text("""
        SELECT id, nombre, horarios_disponibles, fecha_inicio, fecha_fin
        FROM torneos 
        WHERE id = 11
    """)
    torneo = db.execute(torneo_query).fetchone()
    
    print(f"\n📋 TORNEO:")
    print(f"  ID: {torneo[0]}")
    print(f"  Nombre: {torneo[1]}")
    print(f"  Horarios: {torneo[2]}")
    print(f"  Fecha inicio: {torneo[3]}")
    print(f"  Fecha fin: {torneo[4]}")
    
    # Ver partidos con horarios problemáticos
    partidos_query = text("""
        SELECT 
            p.id_partido,
            p.fecha_hora,
            p.cancha_id,
            z.nombre as zona_nombre,
            par1.jugador1_id as p1_j1,
            par1.jugador2_id as p1_j2,
            par2.jugador1_id as p2_j1,
            par2.jugador2_id as p2_j2
        FROM partidos p
        LEFT JOIN torneo_zonas z ON p.zona_id = z.id
        LEFT JOIN torneos_parejas par1 ON p.pareja1_id = par1.id
        LEFT JOIN torneos_parejas par2 ON p.pareja2_id = par2.id
        WHERE p.torneo_id = 11
        ORDER BY p.fecha_hora
        LIMIT 20
    """)
    
    partidos = db.execute(partidos_query).fetchall()
    
    print(f"\n⚽ PARTIDOS (primeros 20):")
    print(f"  Total encontrados: {len(partidos)}")
    
    for partido in partidos:
        fecha_hora = partido[1]
        if fecha_hora:
            # Verificar si es datetime o string
            if isinstance(fecha_hora, datetime):
                hora_str = fecha_hora.strftime('%H:%M')
                fecha_str = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
                dia_semana = fecha_hora.strftime('%A')
            else:
                fecha_str = str(fecha_hora)
                hora_str = "N/A"
                dia_semana = "N/A"
            
            print(f"\n  Partido #{partido[0]}:")
            print(f"    Fecha/Hora completa: {fecha_str}")
            print(f"    Hora: {hora_str}")
            print(f"    Día: {dia_semana}")
            print(f"    Zona: {partido[3]}")
            print(f"    Cancha: {partido[2]}")
            
            # Marcar si es problemático
            if isinstance(fecha_hora, datetime):
                hora_num = fecha_hora.hour
                if hora_num < 8:
                    print(f"    ⚠️ PROBLEMA: Hora antes de las 08:00!")
    
    # Ver disponibilidad de parejas
    print(f"\n👥 DISPONIBILIDAD DE PAREJAS:")
    parejas_query = text("""
        SELECT 
            id,
            jugador1_id,
            jugador2_id,
            disponibilidad_horaria
        FROM torneos_parejas
        WHERE torneo_id = 11
        LIMIT 5
    """)
    
    parejas = db.execute(parejas_query).fetchall()
    for pareja in parejas:
        print(f"\n  Pareja #{pareja[0]}:")
        print(f"    Jugadores: {pareja[1]} / {pareja[2]}")
        print(f"    Disponibilidad: {pareja[3]}")
    
except Exception as e:
    import traceback
    print(f"\n❌ Error: {e}")
    print(traceback.format_exc())
finally:
    db.close()
