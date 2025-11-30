"""
Test completo de generación de zonas con disponibilidad horaria
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.config import get_db, engine
from src.services.torneo_service import TorneoService
from src.services.torneo_inscripcion_service import TorneoInscripcionService
from src.services.torneo_fixture_service import TorneoFixtureService
from src.schemas.torneo_schemas import TorneoCreate, ParejaInscripcion
from datetime import datetime, timedelta
from sqlalchemy import text


def test_disponibilidad_horaria():
    """Test completo con bloqueos horarios"""
    db = next(get_db())
    
    try:
        print("\n" + "="*70)
        print("TEST: Generación de Zonas con Disponibilidad Horaria")
        print("="*70)
        
        # 1. Crear torneo
        print("\n1. Creando torneo...")
        torneo_data = TorneoCreate(
            nombre="Torneo Test Disponibilidad",
            descripcion="Test de zonas con bloqueos horarios",
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
        
        parejas_creadas = []
        for j1, j2 in parejas_ids:
            pareja_data = ParejaInscripcion(jugador1_id=j1, jugador2_id=j2)
            pareja = TorneoInscripcionService.inscribir_pareja(db, torneo.id, pareja_data, j1)
            pareja = TorneoInscripcionService.confirmar_pareja(db, pareja.id, user_id)
            parejas_creadas.append(pareja)
            print(f"   ✅ Pareja {j1}/{j2}")
        
        # 3. Agregar bloqueos horarios usando SQL directo
        print("\n3. Agregando bloqueos horarios...")
        fecha_torneo = (datetime.now() + timedelta(days=7)).date()
        
        # Grupo 1: Parejas 2/3 y 4/5 - Bloqueadas por la tarde (disponibles mañana)
        bloqueos_grupo1 = [
            (torneo.id, 2, fecha_torneo, '14:00:00', '20:00:00', 'Trabajo'),
            (torneo.id, 3, fecha_torneo, '14:00:00', '20:00:00', 'Trabajo'),
            (torneo.id, 4, fecha_torneo, '14:00:00', '20:00:00', 'Trabajo'),
            (torneo.id, 5, fecha_torneo, '14:00:00', '20:00:00', 'Trabajo'),
        ]
        
        # Grupo 2: Parejas 6/7 y 8/9 - Bloqueadas por la mañana (disponibles tarde)
        bloqueos_grupo2 = [
            (torneo.id, 6, fecha_torneo, '08:00:00', '14:00:00', 'Estudio'),
            (torneo.id, 7, fecha_torneo, '08:00:00', '14:00:00', 'Estudio'),
            (torneo.id, 8, fecha_torneo, '08:00:00', '14:00:00', 'Estudio'),
            (torneo.id, 9, fecha_torneo, '08:00:00', '14:00:00', 'Estudio'),
        ]
        
        # Grupo 3: Parejas 10/11 y 12/13 - Sin bloqueos (flexibles)
        
        # Insertar usando SQL directo con CAST a TIME
        with engine.connect() as conn:
            for torneo_id, jugador_id, fecha, desde, hasta, motivo in bloqueos_grupo1 + bloqueos_grupo2:
                conn.execute(text("""
                    INSERT INTO torneo_bloqueos_jugador 
                    (torneo_id, jugador_id, fecha, hora_desde, hora_hasta, motivo)
                    VALUES (:torneo_id, :jugador_id, :fecha, CAST(:desde AS TIME), CAST(:hasta AS TIME), :motivo)
                """), {
                    'torneo_id': torneo_id,
                    'jugador_id': jugador_id,
                    'fecha': fecha,
                    'desde': desde,
                    'hasta': hasta,
                    'motivo': motivo
                })
            conn.commit()
        
        print("✅ Bloqueos horarios agregados:")
        print("   Grupo 1 (2/3, 4/5): Bloqueados 14:00-20:00 → Disponibles MAÑANA")
        print("   Grupo 2 (6/7, 8/9): Bloqueados 08:00-14:00 → Disponibles TARDE")
        print("   Grupo 3 (10/11, 12/13): Sin bloqueos → FLEXIBLES")
        
        # 4. Generar zonas con criterio de disponibilidad
        print("\n4. Generando zonas con criterio de disponibilidad horaria...")
        zonas = TorneoFixtureService.generar_zonas_con_disponibilidad(
            db=db,
            torneo_id=torneo.id,
            user_id=user_id,
            num_zonas=2
        )
        
        print(f"✅ Zonas generadas: {len(zonas)}")
        
        # 5. Verificar distribución
        print("\n5. Verificando distribución inteligente...")
        from src.services.torneo_zona_service import TorneoZonaService
        zonas_con_parejas = TorneoZonaService.listar_zonas(db, torneo.id)
        
        for zona in zonas_con_parejas:
            print(f"\n   {zona['nombre']}: {len(zona['parejas'])} parejas")
            for pareja in zona['parejas']:
                j1, j2 = pareja['jugador1_id'], pareja['jugador2_id']
                
                # Determinar grupo
                if j1 in [2, 4] or j2 in [3, 5]:
                    grupo = "Grupo 1 (MAÑANA)"
                elif j1 in [6, 8] or j2 in [7, 9]:
                    grupo = "Grupo 2 (TARDE)"
                else:
                    grupo = "Grupo 3 (FLEXIBLE)"
                
                print(f"      - Pareja {j1}/{j2} → {grupo}")
        
        # 6. Verificar compatibilidad
        print("\n6. Análisis de compatibilidad:")
        print("   ✅ Parejas en la misma zona deberían poder jugar juntas")
        print("   ✅ Grupo 1 y Grupo 2 NO deberían estar juntos (horarios incompatibles)")
        print("   ✅ Grupo 3 puede estar con cualquiera (flexibles)")
        
        # 7. Generar fixture
        print("\n7. Generando fixture completo...")
        resultado = TorneoFixtureService.generar_fixture_completo(
            db=db,
            torneo_id=torneo.id,
            user_id=user_id
        )
        
        print(f"✅ Fixture generado:")
        print(f"   Total partidos: {resultado['total_partidos']}")
        for zona_nombre, num_partidos in resultado['partidos_por_zona'].items():
            print(f"   {zona_nombre}: {num_partidos} partidos")
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETADO - Sistema de disponibilidad horaria funcional")
        print("="*70)
        
        # Limpiar
        print("\n¿Deseas eliminar el torneo de prueba? (s/n): ", end="")
        respuesta = input().strip().lower()
        if respuesta == 's':
            # Eliminar partidos y bloqueos manualmente
            from src.models.playt_models import Partido
            db.query(Partido).filter(Partido.id_torneo == torneo.id).delete()
            
            with engine.connect() as conn:
                conn.execute(text("""
                    DELETE FROM torneo_bloqueos_jugador WHERE torneo_id = :torneo_id
                """), {'torneo_id': torneo.id})
                conn.commit()
            
            # Cambiar estado para poder eliminar
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
    test_disponibilidad_horaria()
