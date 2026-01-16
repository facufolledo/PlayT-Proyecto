"""
Verificar estructura de partidos y resultados
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.models.driveplus_models import Partido, ResultadoPartido, PartidoJugador
from sqlalchemy import func

def verificar():
    db = next(get_db())
    
    print("\n" + "="*80)
    print("VERIFICAR ESTRUCTURA DE PARTIDOS Y RESULTADOS")
    print("="*80 + "\n")
    
    # Contar partidos por estado
    print("📊 PARTIDOS POR ESTADO:")
    estados = db.query(Partido.estado, func.count(Partido.id_partido)).group_by(Partido.estado).all()
    for estado, count in estados:
        print(f"  {estado}: {count}")
    
    print("\n📊 RESULTADOS:")
    total_resultados = db.query(ResultadoPartido).count()
    resultados_confirmados = db.query(ResultadoPartido).filter(ResultadoPartido.confirmado == True).count()
    print(f"  Total resultados: {total_resultados}")
    print(f"  Confirmados: {resultados_confirmados}")
    
    print("\n📊 PARTIDO_JUGADORES:")
    total_pj = db.query(PartidoJugador).count()
    print(f"  Total registros: {total_pj}")
    
    # Ver un ejemplo de partido con resultado
    print("\n🔍 EJEMPLO DE PARTIDO CON RESULTADO:")
    partido = db.query(Partido).filter(Partido.estado.in_(["confirmado", "finalizado"])).first()
    if partido:
        print(f"  ID Partido: {partido.id_partido}")
        print(f"  Estado: {partido.estado}")
        print(f"  Tipo: {partido.tipo}")
        
        resultado = db.query(ResultadoPartido).filter(ResultadoPartido.id_partido == partido.id_partido).first()
        if resultado:
            print(f"\n  Resultado:")
            print(f"    Sets Eq1: {resultado.sets_eq1}")
            print(f"    Sets Eq2: {resultado.sets_eq2}")
            print(f"    Confirmado: {resultado.confirmado}")
        else:
            print(f"\n  ❌ No tiene resultado en tabla resultado_partidos")
        
        jugadores = db.query(PartidoJugador).filter(PartidoJugador.id_partido == partido.id_partido).all()
        print(f"\n  Jugadores ({len(jugadores)}):")
        for j in jugadores:
            print(f"    Usuario {j.id_usuario} - Equipo {j.equipo}")
    else:
        print("  ❌ No hay partidos confirmados/finalizados")
    
    # Verificar si hay partidos con resultado_padel (JSON)
    print("\n🔍 PARTIDOS CON RESULTADO_PADEL (JSON):")
    partidos_json = db.query(Partido).filter(Partido.resultado_padel != None).limit(5).all()
    print(f"  Total con resultado_padel: {len(partidos_json)}")
    if partidos_json:
        for p in partidos_json[:2]:
            print(f"\n  Partido {p.id_partido}:")
            print(f"    Estado: {p.estado}")
            print(f"    Resultado JSON: {p.resultado_padel}")

if __name__ == "__main__":
    verificar()
