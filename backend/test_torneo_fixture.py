"""
Test para generación de fixture con disponibilidad horaria
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.config import get_db
from src.services.torneo_service import TorneoService
from src.services.torneo_inscripcion_service import TorneoInscripcionService
from src.services.torneo_fixture_service import TorneoFixtureService
from src.schemas.torneo_schemas import TorneoCreate, ParejaInscripcion
from src.models.torneo_models import TorneoBloqueoJugador
from datetime import datetime, timedelta, date


def test_fixture_con_disponibilidad():
    """Test de generación de fixture considerando disponibilidad horaria"""
    db = next(get_db())
    
    try:
        print("\n" + "="*60)
        print("TEST: Fixture con Disponibilidad Horaria")
        print("="*60)
        
        # 1. Crear torneo de prueba
        print("\n1. Creando torneo de prueba...")
        torneo_data = TorneoCreate(
            nombre="Torneo Test Fixture",
            descripcion="Torneo para probar fixture inteligente",
            categoria="5ta",
            fecha_inicio=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            fecha_fin=(datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d"),
            lugar="Club Test",
            max_parejas=6
        )
        
        user_id = 25  # Usuario administrador
        
        torneo = TorneoService.crear_torneo(db, torneo_data, user_id)
        print(f"✅ Torneo creado: ID {torneo.id} - {torneo.nombre}")
        
        # 2. Inscribir 6 parejas
        print("\n2. Inscribiendo 6 parejas...")
        parejas_ids = [
            (2, 3),
            (4, 5),
            (6, 7),
            (8, 9),
            (10, 11),
            (12, 13)
        ]
        
        parejas_creadas = []
        for j1, j2 in parejas_ids:
            try:
                pareja_data = ParejaInscripcion(
                    jugador1_id=j1,
                    jugador2_id=j2
                )
                pareja = TorneoInscripcionService.inscribir_pareja(
                    db, torneo.id, pareja_data, j1
                )
                pareja = TorneoInscripcionService.confirmar_pareja(db, pareja.id, user_id)
                parejas_creadas.append(pareja)
                print(f"   ✅ Pareja inscrita: {j1}/{j2}")
            except Exception as e:
                print(f"   ⚠️  Error al inscribir {j1}/{j2}: {e}")
        
        print(f"\n✅ Total parejas confirmadas: {len(parejas_creadas)}")
        
        # 3. Generar zonas (sin bloqueos por ahora, solo balanceo por rating)
        print("\n3. Generando zonas con balanceo por rating...")
        from src.services.torneo_zona_service import TorneoZonaService
        zonas = TorneoZonaService.generar_zonas_automaticas(
            db=db,
            torneo_id=torneo.id,
            user_id=user_id,
            num_zonas=2,
            balancear_por_rating=True
        )
        
        print(f"✅ Zonas generadas: {len(zonas)}")
        
        # 4. Verificar distribución
        print("\n4. Verificando distribución de parejas...")
        from src.services.torneo_zona_service import TorneoZonaService
        zonas_con_parejas = TorneoZonaService.listar_zonas(db, torneo.id)
        
        for zona in zonas_con_parejas:
            print(f"\n   {zona['nombre']}: {len(zona['parejas'])} parejas")
            for pareja in zona['parejas']:
                j1, j2 = pareja['jugador1_id'], pareja['jugador2_id']
                print(f"      - Pareja {j1}/{j2}")
        
        # 5. Generar fixture completo
        print("\n5. Generando fixture completo...")
        resultado = TorneoFixtureService.generar_fixture_completo(
            db=db,
            torneo_id=torneo.id,
            user_id=user_id
        )
        
        print(f"✅ Fixture generado:")
        print(f"   Total partidos: {resultado['total_partidos']}")
        print(f"   Zonas: {resultado['zonas']}")
        for zona_nombre, num_partidos in resultado['partidos_por_zona'].items():
            print(f"   {zona_nombre}: {num_partidos} partidos")
        
        # 6. Listar partidos generados
        print("\n6. Listando partidos generados...")
        from src.models.driveplus_models import Partido
        partidos = db.query(Partido).filter(Partido.id_torneo == torneo.id).all()
        
        print(f"\nPartidos generados ({len(partidos)} total):")
        for i, partido in enumerate(partidos, 1):
            print(f"   {i}. Pareja {partido.pareja1_id} vs Pareja {partido.pareja2_id} "
                  f"(Zona {partido.zona_id}, Estado: {partido.estado})")
        
        print("\n" + "="*60)
        print("✅ TEST COMPLETADO EXITOSAMENTE")
        print("="*60)
        
        # Limpiar
        print("\n¿Deseas eliminar el torneo de prueba? (s/n): ", end="")
        respuesta = input().strip().lower()
        if respuesta == 's':
            # Eliminar partidos primero
            db.query(Partido).filter(Partido.id_torneo == torneo.id).delete()
            TorneoService.eliminar_torneo(db, torneo.id, user_id)
            print("✅ Torneo eliminado")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_fixture_con_disponibilidad()
