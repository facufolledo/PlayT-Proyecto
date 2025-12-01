"""
Test para el sistema de playoffs de torneos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.services.torneo_playoff_service import TorneoPlayoffService
from src.services.torneo_service import TorneoService
from src.services.torneo_zona_service import TorneoZonaService


def test_generar_playoffs():
    """Test de generación de playoffs"""
    print("\n🏆 TEST: Generar Playoffs")
    print("=" * 60)
    
    db = next(get_db())
    
    try:
        # Buscar un torneo en fase de grupos
        torneos = TorneoService.listar_torneos(db, estado="fase_grupos")
        
        if not torneos:
            print("❌ No hay torneos en fase de grupos para probar")
            print("   Crea un torneo, inscribe parejas, genera zonas y fixture primero")
            return
        
        torneo = torneos[0]
        print(f"\n📋 Torneo: {torneo.nombre} (ID: {torneo.id})")
        print(f"   Estado: {torneo.estado}")
        
        # Obtener zonas
        zonas = TorneoZonaService.listar_zonas(db, torneo.id)
        print(f"\n🎯 Zonas: {len(zonas)}")
        
        for zona in zonas:
            print(f"   - {zona['nombre']}: {len(zona.get('parejas', []))} parejas")
        
        # Generar playoffs
        print("\n⚡ Generando playoffs...")
        user_id = torneo.creado_por
        
        partidos = TorneoPlayoffService.generar_playoffs(
            db, torneo.id, user_id, clasificados_por_zona=2
        )
        
        print(f"✅ Playoffs generados: {len(partidos)} partidos")
        
        # Listar partidos por fase
        partidos_por_fase = TorneoPlayoffService.listar_partidos_playoffs(db, torneo.id)
        
        print("\n📊 Partidos por fase:")
        for fase, partidos_fase in partidos_por_fase.items():
            if partidos_fase:
                print(f"   {fase}: {len(partidos_fase)} partidos")
                for p in partidos_fase:
                    pareja1 = p.pareja1_id or "TBD"
                    pareja2 = p.pareja2_id or "TBD"
                    print(f"      Partido {p.numero_partido}: Pareja {pareja1} vs Pareja {pareja2}")
        
        print("\n✅ Test completado exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_listar_playoffs():
    """Test de listado de playoffs"""
    print("\n📋 TEST: Listar Playoffs")
    print("=" * 60)
    
    db = next(get_db())
    
    try:
        # Buscar un torneo en fase de eliminación
        torneos = TorneoService.listar_torneos(db, estado="fase_eliminacion")
        
        if not torneos:
            print("❌ No hay torneos en fase de eliminación para probar")
            return
        
        torneo = torneos[0]
        print(f"\n📋 Torneo: {torneo.nombre} (ID: {torneo.id})")
        
        # Listar playoffs
        partidos_por_fase = TorneoPlayoffService.listar_partidos_playoffs(db, torneo.id)
        
        print("\n📊 Bracket de Playoffs:")
        for fase, partidos in partidos_por_fase.items():
            if partidos:
                print(f"\n   {fase.upper()}:")
                for p in partidos:
                    estado_emoji = "✅" if p.estado == "finalizado" else "⏱️"
                    pareja1 = p.pareja1_id or "TBD"
                    pareja2 = p.pareja2_id or "TBD"
                    ganador = f" → Ganador: {p.ganador_pareja_id}" if p.ganador_pareja_id else ""
                    print(f"      {estado_emoji} Partido {p.numero_partido}: {pareja1} vs {pareja2}{ganador}")
        
        print("\n✅ Test completado exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎾 TESTS DEL SISTEMA DE PLAYOFFS")
    print("=" * 60)
    
    test_generar_playoffs()
    test_listar_playoffs()
    
    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS COMPLETADOS")
    print("=" * 60 + "\n")
