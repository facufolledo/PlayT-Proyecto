"""
Script para arreglar partidos de playoffs existentes
Mueve los ganadores de partidos ya finalizados a la siguiente fase
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

def arreglar_playoffs(torneo_id: int):
    """Arregla los playoffs de un torneo específico"""
    from src.models.playt_models import Partido
    
    # Obtener todos los partidos de playoffs del torneo
    partidos = db.query(Partido).filter(
        Partido.id_torneo == torneo_id,
        Partido.fase != 'zona',
        Partido.fase.isnot(None)
    ).order_by(Partido.numero_partido).all()
    
    print(f"\n=== Partidos de playoffs del torneo {torneo_id} ===")
    for p in partidos:
        print(f"  ID: {p.id_partido}, Fase: {p.fase}, Num: {p.numero_partido}")
        print(f"    Pareja1: {p.pareja1_id}, Pareja2: {p.pareja2_id}")
        print(f"    Estado: {p.estado}, Ganador: {p.ganador_pareja_id}")
    
    # Buscar partidos confirmados que tienen ganador
    partidos_con_ganador = [p for p in partidos if p.ganador_pareja_id and p.estado == 'confirmado']
    
    print(f"\n=== Partidos con ganador ({len(partidos_con_ganador)}) ===")
    
    # Mapeo directo de fase actual a siguiente fase
    siguiente_fase_map = {
        '16avos': '8vos',
        '8vos': '4tos',
        '4tos': 'semis',
        'cuartos': 'semis',
        'semis': 'final',
        'semifinal': 'final'
    }
    
    for partido in partidos_con_ganador:
        fase_actual = partido.fase
        
        # Si es la final, no hay siguiente fase
        if fase_actual == 'final':
            print(f"  Partido {partido.id_partido} es la final, no hay siguiente fase")
            continue
        
        # Determinar siguiente fase
        siguiente_fase = siguiente_fase_map.get(fase_actual)
        if not siguiente_fase:
            print(f"  No se pudo determinar siguiente fase para {fase_actual}")
            continue
        
        print(f"\n  Partido {partido.id_partido} ({fase_actual}) -> Ganador {partido.ganador_pareja_id}")
        print(f"    Siguiente fase: {siguiente_fase}")
        
        # Buscar partido de siguiente fase
        numero_partido = partido.numero_partido or 1
        numero_siguiente = (numero_partido + 1) // 2
        
        # Buscar partido de la siguiente fase específicamente
        partido_siguiente = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase == siguiente_fase
        ).first()
        
        # Si no hay partido de siguiente fase con ese numero, buscar cualquiera de esa fase
        if not partido_siguiente:
            partido_siguiente = db.query(Partido).filter(
                Partido.id_torneo == torneo_id,
                Partido.fase.in_([siguiente_fase, 'final'])
            ).first()
        
        if partido_siguiente:
            print(f"    Encontrado partido siguiente: {partido_siguiente.id_partido}")
            print(f"    Pareja1 actual: {partido_siguiente.pareja1_id}")
            print(f"    Pareja2 actual: {partido_siguiente.pareja2_id}")
            
            # Asignar ganador a la posición correcta
            if numero_partido % 2 == 1:
                if partido_siguiente.pareja1_id != partido.ganador_pareja_id:
                    print(f"    -> Asignando ganador a pareja1")
                    partido_siguiente.pareja1_id = partido.ganador_pareja_id
                else:
                    print(f"    -> Ya está asignado correctamente en pareja1")
            else:
                if partido_siguiente.pareja2_id != partido.ganador_pareja_id:
                    print(f"    -> Asignando ganador a pareja2")
                    partido_siguiente.pareja2_id = partido.ganador_pareja_id
                else:
                    print(f"    -> Ya está asignado correctamente en pareja2")
        else:
            print(f"    No se encontró partido de siguiente fase, creando...")
            nuevo_partido = Partido(
                id_torneo=torneo_id,
                fase=siguiente_fase,
                numero_partido=numero_siguiente,
                estado='pendiente',
                fecha=partido.fecha,
                id_creador=partido.id_creador,
                tipo='torneo'
            )
            if numero_partido % 2 == 1:
                nuevo_partido.pareja1_id = partido.ganador_pareja_id
            else:
                nuevo_partido.pareja2_id = partido.ganador_pareja_id
            db.add(nuevo_partido)
            print(f"    -> Creado nuevo partido de {siguiente_fase}")
    
    db.commit()
    print("\n=== Cambios guardados ===")
    
    # Mostrar estado final
    print("\n=== Estado final de playoffs ===")
    partidos = db.query(Partido).filter(
        Partido.id_torneo == torneo_id,
        Partido.fase != 'zona',
        Partido.fase.isnot(None)
    ).order_by(Partido.numero_partido).all()
    
    for p in partidos:
        print(f"  {p.fase}: Partido {p.numero_partido}")
        print(f"    Pareja1: {p.pareja1_id}, Pareja2: {p.pareja2_id}")
        print(f"    Ganador: {p.ganador_pareja_id}, Estado: {p.estado}")

if __name__ == "__main__":
    # Obtener torneo_id del argumento o usar uno por defecto
    torneo_id = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    print(f"Arreglando playoffs del torneo {torneo_id}...")
    arreglar_playoffs(torneo_id)
    db.close()
