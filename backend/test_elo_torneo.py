"""
Script para probar que el ELO se aplica correctamente en partidos de torneo
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.Drive+_models import Usuario, Partido, HistorialRating
from src.models.torneo_models import TorneoPareja, Torneo, TorneoZona
from src.services.torneo_resultado_service import TorneoResultadoService

# Conectar a la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def mostrar_rating_jugadores(jugadores_ids: list):
    """Muestra el rating actual de los jugadores"""
    print("\n📊 Rating actual de jugadores:")
    for jid in jugadores_ids:
        usuario = db.query(Usuario).filter(Usuario.id_usuario == jid).first()
        if usuario:
            print(f"  - Usuario {jid}: Rating={usuario.rating}, Partidos={usuario.partidos_jugados}")
        else:
            print(f"  - Usuario {jid}: NO ENCONTRADO")

def test_aplicar_elo_torneo():
    """Prueba la aplicación de ELO en un partido de torneo"""
    print("=" * 60)
    print("🧪 TEST: Aplicación de ELO en partidos de torneo")
    print("=" * 60)
    
    # Buscar un partido de torneo pendiente
    partido = db.query(Partido).filter(
        Partido.tipo == 'torneo',
        Partido.estado == 'pendiente',
        Partido.pareja1_id.isnot(None),
        Partido.pareja2_id.isnot(None)
    ).first()
    
    if not partido:
        print("❌ No hay partidos de torneo pendientes con parejas asignadas")
        print("\n📝 Buscando cualquier partido de torneo...")
        partido = db.query(Partido).filter(Partido.tipo == 'torneo').first()
        if partido:
            print(f"   Encontrado partido {partido.id_partido} con estado '{partido.estado}'")
        return
    
    print(f"\n✅ Partido encontrado: ID={partido.id_partido}")
    print(f"   Torneo ID: {partido.id_torneo}")
    print(f"   Pareja 1 ID: {partido.pareja1_id}")
    print(f"   Pareja 2 ID: {partido.pareja2_id}")
    print(f"   Estado: {partido.estado}")
    
    # Obtener parejas
    pareja1 = db.query(TorneoPareja).filter(TorneoPareja.id == partido.pareja1_id).first()
    pareja2 = db.query(TorneoPareja).filter(TorneoPareja.id == partido.pareja2_id).first()
    
    if not pareja1 or not pareja2:
        print("❌ No se encontraron las parejas")
        return
    
    print(f"\n👥 Pareja 1: Jugadores {pareja1.jugador1_id} y {pareja1.jugador2_id}")
    print(f"👥 Pareja 2: Jugadores {pareja2.jugador1_id} y {pareja2.jugador2_id}")
    
    # Obtener IDs de todos los jugadores
    jugadores_ids = [
        pareja1.jugador1_id, pareja1.jugador2_id,
        pareja2.jugador1_id, pareja2.jugador2_id
    ]
    
    # Mostrar rating ANTES
    print("\n📈 ANTES de cargar resultado:")
    mostrar_rating_jugadores(jugadores_ids)
    
    # Simular resultado: Pareja 1 gana 2-0
    resultado_data = {
        "sets": [
            {"gamesEquipoA": 6, "gamesEquipoB": 3, "ganador": "equipoA", "completado": True},
            {"gamesEquipoA": 6, "gamesEquipoB": 4, "ganador": "equipoA", "completado": True}
        ]
    }
    
    print(f"\n🎾 Cargando resultado: 6-3, 6-4 (Gana Pareja 1)")
    
    try:
        # Cargar resultado
        partido_actualizado = TorneoResultadoService.cargar_resultado(
            db, partido.id_partido, resultado_data, pareja1.jugador1_id
        )
        
        print(f"\n✅ Resultado cargado exitosamente")
        print(f"   Estado: {partido_actualizado.estado}")
        print(f"   Ganador: Pareja {partido_actualizado.ganador_pareja_id}")
        print(f"   ELO aplicado: {partido_actualizado.elo_aplicado}")
        
        # Refrescar datos de jugadores
        db.expire_all()
        
        # Mostrar rating DESPUÉS
        print("\n📈 DESPUÉS de cargar resultado:")
        mostrar_rating_jugadores(jugadores_ids)
        
        # Verificar historial de rating
        print("\n📜 Historial de rating creado:")
        for jid in jugadores_ids:
            historial = db.query(HistorialRating).filter(
                HistorialRating.id_usuario == jid,
                HistorialRating.id_partido == partido.id_partido
            ).first()
            if historial:
                print(f"  - Usuario {jid}: {historial.rating_antes} → {historial.rating_despues} (Δ{historial.delta:+d})")
            else:
                print(f"  - Usuario {jid}: Sin historial creado")
        
    except Exception as e:
        print(f"\n❌ Error al cargar resultado: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

def verificar_estado_actual():
    """Verifica el estado actual de torneos y partidos"""
    print("\n" + "=" * 60)
    print("📋 ESTADO ACTUAL DEL SISTEMA")
    print("=" * 60)
    
    # Contar torneos
    torneos = db.query(Torneo).count()
    print(f"\n🏆 Torneos: {torneos}")
    
    # Contar parejas
    parejas = db.query(TorneoPareja).count()
    print(f"👥 Parejas inscritas: {parejas}")
    
    # Contar partidos de torneo
    partidos_torneo = db.query(Partido).filter(Partido.tipo == 'torneo').count()
    partidos_pendientes = db.query(Partido).filter(
        Partido.tipo == 'torneo',
        Partido.estado == 'pendiente'
    ).count()
    partidos_confirmados = db.query(Partido).filter(
        Partido.tipo == 'torneo',
        Partido.estado == 'confirmado'
    ).count()
    
    print(f"\n🎾 Partidos de torneo:")
    print(f"   - Total: {partidos_torneo}")
    print(f"   - Pendientes: {partidos_pendientes}")
    print(f"   - Confirmados: {partidos_confirmados}")
    
    # Verificar partidos con ELO aplicado
    partidos_con_elo = db.query(Partido).filter(
        Partido.tipo == 'torneo',
        Partido.elo_aplicado == True
    ).count()
    print(f"   - Con ELO aplicado: {partidos_con_elo}")

if __name__ == "__main__":
    try:
        verificar_estado_actual()
        
        respuesta = input("\n¿Deseas probar la carga de resultado con ELO? (s/n): ")
        if respuesta.lower() == 's':
            test_aplicar_elo_torneo()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
