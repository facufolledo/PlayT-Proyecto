"""
Test para sistema de resultados en torneos
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.config import get_db
from src.services.torneo_service import TorneoService
from src.services.torneo_inscripcion_service import TorneoInscripcionService
from src.services.torneo_zona_service import TorneoZonaService
from src.services.torneo_fixture_service import TorneoFixtureService
from src.services.torneo_resultado_service import TorneoResultadoService
from src.schemas.torneo_schemas import TorneoCreate, ParejaInscripcion
from src.models.driveplus_models import Partido
from datetime import datetime, timedelta


def test_resultados_torneo():
    """Test completo de carga de resultados"""
    db = next(get_db())
    
    try:
        print("\n" + "="*70)
        print("TEST: Sistema de Resultados en Torneos")
        print("="*70)
        
        # 1. Crear torneo
        print("\n1. Creando torneo...")
        torneo_data = TorneoCreate(
            nombre="Torneo Test Resultados",
            descripcion="Test de resultados y tabla de posiciones",
            categoria="5ta",
            fecha_inicio=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            fecha_fin=(datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d"),
            lugar="Club Test",
            max_parejas=6
        )
        
        user_id = 25
        torneo = TorneoService.crear_torneo(db, torneo_data, user_id)
        print(f"✅ Torneo creado: ID {torneo.id}")
        
        # 2. Inscribir 6 parejas
        print("\n2. Inscribiendo 6 parejas...")
        parejas_ids = [(2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13)]
        
        for j1, j2 in parejas_ids:
            pareja_data = ParejaInscripcion(jugador1_id=j1, jugador2_id=j2)
            pareja = TorneoInscripcionService.inscribir_pareja(db, torneo.id, pareja_data, j1)
            TorneoInscripcionService.confirmar_pareja(db, pareja.id, user_id)
        
        print(f"✅ 6 parejas inscritas y confirmadas")
        
        # 3. Generar zonas
        print("\n3. Generando zonas...")
        zonas = TorneoZonaService.generar_zonas_automaticas(
            db, torneo.id, user_id, num_zonas=2, balancear_por_rating=True
        )
        print(f"✅ {len(zonas)} zonas generadas")
        
        # 4. Generar fixture
        print("\n4. Generando fixture...")
        resultado_fixture = TorneoFixtureService.generar_fixture_completo(
            db, torneo.id, user_id
        )
        print(f"✅ {resultado_fixture['total_partidos']} partidos generados")
        
        # 5. Obtener partidos de la primera zona
        print("\n5. Cargando resultados de partidos...")
        zona_a = zonas[0]
        partidos_zona_a = db.query(Partido).filter(
            Partido.zona_id == zona_a.id
        ).all()
        
        print(f"\nZona {zona_a.nombre}: {len(partidos_zona_a)} partidos")
        
        # 6. Cargar resultados de ejemplo
        resultados_ejemplo = [
            # Partido 1: Pareja 1 gana 6-4, 6-3
            {
                "sets": [
                    {"gamesEquipoA": 6, "gamesEquipoB": 4, "ganador": "equipoA", "completado": True},
                    {"gamesEquipoA": 6, "gamesEquipoB": 3, "ganador": "equipoA", "completado": True}
                ]
            },
            # Partido 2: Pareja 2 gana 7-5, 4-6, 6-3
            {
                "sets": [
                    {"gamesEquipoA": 7, "gamesEquipoB": 5, "ganador": "equipoA", "completado": True},
                    {"gamesEquipoA": 4, "gamesEquipoB": 6, "ganador": "equipoB", "completado": True},
                    {"gamesEquipoA": 6, "gamesEquipoB": 3, "ganador": "equipoA", "completado": True}
                ]
            },
            # Partido 3: Pareja 1 gana 6-2, 6-4
            {
                "sets": [
                    {"gamesEquipoA": 6, "gamesEquipoB": 2, "ganador": "equipoA", "completado": True},
                    {"gamesEquipoA": 6, "gamesEquipoB": 4, "ganador": "equipoA", "completado": True}
                ]
            }
        ]
        
        for i, partido in enumerate(partidos_zona_a):
            if i < len(resultados_ejemplo):
                resultado = TorneoResultadoService.cargar_resultado(
                    db, partido.id_partido, resultados_ejemplo[i], user_id
                )
                print(f"   ✅ Resultado cargado para partido {partido.id_partido}")
                print(f"      Ganador: Pareja {resultado.ganador_pareja_id}")
        
        # 7. Obtener tabla de posiciones actualizada
        print(f"\n6. Tabla de posiciones de {zona_a.nombre}:")
        tabla = TorneoZonaService.obtener_tabla_posiciones(db, zona_a.id)
        
        print(f"\n   {'Pos':<5} {'Pareja':<15} {'PJ':<5} {'PG':<5} {'PP':<5} {'SG':<5} {'SP':<5} {'GG':<5} {'GP':<5} {'Pts':<5}")
        print("   " + "-"*80)
        
        for item in tabla['tabla']:
            pareja_nombre = f"{item['jugador1_id']}/{item['jugador2_id']}"
            print(f"   {item['posicion']:<5} {pareja_nombre:<15} "
                  f"{item['partidos_jugados']:<5} {item['partidos_ganados']:<5} "
                  f"{item['partidos_perdidos']:<5} {item['sets_ganados']:<5} "
                  f"{item['sets_perdidos']:<5} {item['games_ganados']:<5} "
                  f"{item['games_perdidos']:<5} {item['puntos']:<5}")
        
        # 8. Obtener clasificados
        print(f"\n7. Clasificados de {zona_a.nombre}:")
        clasificados = TorneoResultadoService.obtener_clasificados_zona(db, zona_a.id, 2)
        
        for i, clasificado in enumerate(clasificados, 1):
            print(f"   {i}° lugar: Pareja {clasificado['jugador1_id']}/{clasificado['jugador2_id']} "
                  f"({clasificado['puntos']} puntos)")
        
        # 9. Verificar si zona está completa
        print(f"\n8. Verificando estado de la zona...")
        completa = TorneoResultadoService.verificar_zona_completa(db, zona_a.id)
        print(f"   Zona completa: {'✅ SÍ' if completa else '❌ NO (faltan partidos)'}")
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETADO - Sistema de resultados funcional")
        print("="*70)
        
        # Limpiar
        print("\n¿Deseas eliminar el torneo de prueba? (s/n): ", end="")
        respuesta = input().strip().lower()
        if respuesta == 's':
            db.query(Partido).filter(Partido.id_torneo == torneo.id).delete()
            torneo.estado = 'inscripcion'
            db.commit()
            TorneoService.eliminar_torneo(db, torneo.id, user_id)
            print("✅ Torneo eliminado")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_resultados_torneo()
