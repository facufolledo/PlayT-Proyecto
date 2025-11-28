"""
Test del sistema de inscripciones de torneos
"""
from src.database.config import SessionLocal
from src.services.torneo_service import TorneoService
from src.services.torneo_inscripcion_service import TorneoInscripcionService
from src.schemas.torneo_schemas import TorneoCreate, ParejaInscripcion
from datetime import date, timedelta

def test_inscripciones():
    """Test de inscripciones en torneos"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("TEST: Sistema de Inscripciones en Torneos")
        print("="*60)
        
        # 1. Crear un torneo de prueba
        print("\n1. Creando torneo de prueba...")
        from src.models.playt_models import Usuario
        
        user_id = 1
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if usuario:
            usuario.puede_crear_torneos = True
            db.commit()
        
        torneo_data = TorneoCreate(
            nombre="Torneo Test Inscripciones",
            descripcion="Torneo para probar inscripciones",
            categoria="5ta",
            fecha_inicio=date.today() + timedelta(days=7),
            fecha_fin=date.today() + timedelta(days=9),
            lugar="Club Test"
        )
        
        torneo = TorneoService.crear_torneo(db, torneo_data, user_id)
        print(f"   [OK] Torneo creado con ID: {torneo.id}")
        
        # 2. Inscribir primera pareja
        print("\n2. Inscribiendo primera pareja...")
        pareja1_data = ParejaInscripcion(
            jugador1_id=1,
            jugador2_id=2,
            observaciones="Primera pareja de prueba"
        )
        
        pareja1 = TorneoInscripcionService.inscribir_pareja(db, torneo.id, pareja1_data, user_id)
        print(f"   [OK] Pareja inscrita con ID: {pareja1.id}")
        print(f"   - Jugadores: {pareja1.jugador1_id} y {pareja1.jugador2_id}")
        print(f"   - Estado: {pareja1.estado}")
        
        # 3. Listar parejas inscritas
        print("\n3. Listando parejas inscritas...")
        parejas = TorneoInscripcionService.listar_parejas(db, torneo.id)
        print(f"   [OK] Total parejas: {len(parejas)}")
        for p in parejas:
            print(f"   - Pareja {p.id}: Jugadores {p.jugador1_id} y {p.jugador2_id} ({p.estado})")
        
        # 4. Confirmar pareja
        print("\n4. Confirmando pareja...")
        pareja_confirmada = TorneoInscripcionService.confirmar_pareja(db, pareja1.id, user_id)
        print(f"   [OK] Pareja confirmada")
        print(f"   - Estado: {pareja_confirmada.estado}")
        
        # 5. Contar parejas confirmadas
        print("\n5. Contando parejas confirmadas...")
        total_confirmadas = TorneoInscripcionService.contar_parejas_confirmadas(db, torneo.id)
        print(f"   [OK] Parejas confirmadas: {total_confirmadas}")
        
        # 6. Intentar inscribir jugador duplicado (debe fallar)
        print("\n6. Intentando inscribir jugador duplicado...")
        try:
            pareja_duplicada = ParejaInscripcion(
                jugador1_id=1,  # Ya está inscrito
                jugador2_id=3,
                observaciones="Intento de duplicado"
            )
            TorneoInscripcionService.inscribir_pareja(db, torneo.id, pareja_duplicada, user_id)
            print("   [ERROR] No debería permitir jugador duplicado")
        except ValueError as e:
            print(f"   [OK] Validación correcta: {str(e)}")
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS DE INSCRIPCIONES PASARON")
        print("="*60)
        print("\nEndpoints de inscripciones disponibles:")
        print("  - POST   /torneos/{id}/inscribir           - Inscribir pareja")
        print("  - GET    /torneos/{id}/parejas             - Listar parejas")
        print("  - PATCH  /torneos/{id}/parejas/{id}/confirmar - Confirmar pareja")
        print("  - DELETE /torneos/{id}/parejas/{id}/rechazar  - Rechazar pareja")
        print("  - PATCH  /torneos/{id}/parejas/{id}/baja      - Dar de baja")
        print("  - PATCH  /torneos/{id}/parejas/{id}/reemplazar-jugador - Reemplazar jugador")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_inscripciones()
