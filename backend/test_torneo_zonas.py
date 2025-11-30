"""
Test para generación de zonas en torneos
"""
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.config import get_db
from src.services.torneo_service import TorneoService
from src.services.torneo_inscripcion_service import TorneoInscripcionService
from src.services.torneo_zona_service import TorneoZonaService
from src.schemas.torneo_schemas import TorneoCreate, ParejaInscripcion
from datetime import datetime, timedelta


def test_generar_zonas():
    """Test de generación de zonas"""
    db = next(get_db())
    
    try:
        print("\n" + "="*60)
        print("TEST: Generación de Zonas en Torneos")
        print("="*60)
        
        # 1. Crear torneo de prueba
        print("\n1. Creando torneo de prueba...")
        torneo_data = TorneoCreate(
            nombre="Torneo Test Zonas",
            descripcion="Torneo para probar generación de zonas",
            categoria="5ta",
            fecha_inicio=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            fecha_fin=(datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d"),
            lugar="Club Test",
            max_parejas=8
        )
        
        # Usuario organizador (debe ser administrador)
        user_id = 25  # Usuario administrador
        
        torneo = TorneoService.crear_torneo(db, torneo_data, user_id)
        print(f"✅ Torneo creado: ID {torneo.id} - {torneo.nombre}")
        
        # 2. Inscribir 8 parejas
        print("\n2. Inscribiendo 8 parejas...")
        parejas_ids = [
            (2, 3),
            (4, 5),
            (6, 7),
            (8, 9),
            (10, 11),
            (12, 13),
            (14, 15),
            (16, 17)
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
                # Confirmar pareja
                pareja = TorneoInscripcionService.confirmar_pareja(db, pareja.id, user_id)
                parejas_creadas.append(pareja)
                print(f"   ✅ Pareja inscrita y confirmada: {j1}/{j2}")
            except Exception as e:
                print(f"   ⚠️  Error al inscribir {j1}/{j2}: {e}")
        
        print(f"\n✅ Total parejas confirmadas: {len(parejas_creadas)}")
        
        # 3. Generar zonas automáticamente
        print("\n3. Generando zonas automáticamente...")
        zonas = TorneoZonaService.generar_zonas_automaticas(
            db=db,
            torneo_id=torneo.id,
            user_id=user_id,
            num_zonas=3,  # 3 zonas: 2-3-3 parejas
            balancear_por_rating=True
        )
        
        print(f"✅ Zonas generadas: {len(zonas)}")
        for zona in zonas:
            print(f"   - {zona.nombre} (ID: {zona.id})")
        
        # 4. Listar zonas con parejas
        print("\n4. Listando zonas con parejas asignadas...")
        zonas_con_parejas = TorneoZonaService.listar_zonas(db, torneo.id)
        
        for zona in zonas_con_parejas:
            print(f"\n   {zona['nombre']}:")
            for pareja in zona['parejas']:
                print(f"      - Pareja {pareja['jugador1_id']}/{pareja['jugador2_id']} (ID: {pareja['id']})")
        
        # 5. Obtener tabla de posiciones (vacía por ahora)
        print("\n5. Obteniendo tabla de posiciones...")
        for zona in zonas:
            tabla = TorneoZonaService.obtener_tabla_posiciones(db, zona.id)
            print(f"\n   Tabla {tabla['zona_nombre']}:")
            print(f"   {'Pos':<5} {'Pareja':<20} {'PJ':<5} {'PG':<5} {'PP':<5} {'Pts':<5}")
            print("   " + "-"*50)
            for item in tabla['tabla']:
                pareja_nombre = f"{item['jugador1_id']}/{item['jugador2_id']}"
                print(f"   {item['posicion']:<5} {pareja_nombre:<20} "
                      f"{item['partidos_jugados']:<5} {item['partidos_ganados']:<5} "
                      f"{item['partidos_perdidos']:<5} {item['puntos']:<5}")
        
        # 6. Probar mover pareja entre zonas
        print("\n6. Probando mover pareja entre zonas...")
        if len(zonas) >= 2 and len(parejas_creadas) >= 1:
            pareja_a_mover = parejas_creadas[0]
            zona_destino = zonas[1]
            
            TorneoZonaService.mover_pareja_entre_zonas(
                db=db,
                pareja_id=pareja_a_mover.id,
                zona_destino_id=zona_destino.id,
                user_id=user_id
            )
            print(f"✅ Pareja {pareja_a_mover.jugador1_id}/{pareja_a_mover.jugador2_id} movida a {zona_destino.nombre}")
            
            # Listar zonas nuevamente
            print("\n   Zonas después del movimiento:")
            zonas_actualizadas = TorneoZonaService.listar_zonas(db, torneo.id)
            for zona in zonas_actualizadas:
                print(f"\n   {zona['nombre']}: {len(zona['parejas'])} parejas")
                for pareja in zona['parejas']:
                    print(f"      - {pareja['jugador1_id']}/{pareja['jugador2_id']}")
        
        print("\n" + "="*60)
        print("✅ TEST COMPLETADO EXITOSAMENTE")
        print("="*60)
        
        # Limpiar (opcional)
        print("\n¿Deseas eliminar el torneo de prueba? (s/n): ", end="")
        respuesta = input().strip().lower()
        if respuesta == 's':
            TorneoService.eliminar_torneo(db, torneo.id, user_id)
            print("✅ Torneo eliminado")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_generar_zonas()
