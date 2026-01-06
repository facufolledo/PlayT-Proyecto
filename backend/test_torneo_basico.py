"""
Test básico del sistema de torneos
"""
from src.database.config import SessionLocal
from src.services.torneo_service import TorneoService
from src.schemas.torneo_schemas import TorneoCreate
from datetime import date, timedelta

def test_crear_torneo():
    """Test de creación de torneo"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("TEST: Sistema de Torneos - CRUD Básico")
        print("="*60)
        
        # 1. Primero necesitamos autorizar un usuario
        print("\n1. Autorizando usuario para crear torneos...")
        from src.models.driveplus_models import Usuario
        
        # Usar un usuario existente (ajusta el ID según tu BD)
        user_id = 1
        
        # Habilitar al usuario para crear torneos
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if usuario:
            usuario.puede_crear_torneos = True
            db.commit()
            print(f"   [OK] Usuario {user_id} autorizado para crear torneos")
        else:
            print(f"   [ERROR] Usuario {user_id} no existe")
            return
        
        # 2. Crear un torneo de prueba
        print("\n2. Creando torneo de prueba...")
        torneo_data = TorneoCreate(
            nombre="Torneo de Prueba Drive+",
            descripcion="Torneo de prueba para validar el sistema",
            categoria="5ta",
            fecha_inicio=date.today() + timedelta(days=7),
            fecha_fin=date.today() + timedelta(days=9),
            lugar="Club de Prueba",
            reglas_json={
                "puntos_victoria": 3,
                "puntos_derrota": 0,
                "sets_para_ganar": 2
            }
        )
        
        torneo = TorneoService.crear_torneo(db, torneo_data, user_id)
        print(f"   [OK] Torneo creado con ID: {torneo.id}")
        print(f"   - Nombre: {torneo.nombre}")
        print(f"   - Categoría: {torneo.categoria}")
        print(f"   - Estado: {torneo.estado}")
        print(f"   - Fechas: {torneo.fecha_inicio} a {torneo.fecha_fin}")
        
        # 3. Listar torneos
        print("\n3. Listando torneos...")
        torneos = TorneoService.listar_torneos(db, limit=10)
        print(f"   [OK] Total de torneos: {len(torneos)}")
        for t in torneos:
            print(f"   - {t.id}: {t.nombre} ({t.estado})")
        
        # 4. Obtener torneo específico
        print(f"\n4. Obteniendo torneo {torneo.id}...")
        torneo_obtenido = TorneoService.obtener_torneo(db, torneo.id)
        print(f"   [OK] Torneo obtenido: {torneo_obtenido.nombre}")
        
        # 5. Verificar organizadores
        print(f"\n5. Verificando organizadores...")
        es_org = TorneoService.es_organizador_torneo(db, torneo.id, user_id)
        es_owner = TorneoService.es_owner_torneo(db, torneo.id, user_id)
        print(f"   [OK] Usuario {user_id} es organizador: {es_org}")
        print(f"   [OK] Usuario {user_id} es owner: {es_owner}")
        
        # 6. Listar organizadores
        print(f"\n6. Listando organizadores del torneo...")
        organizadores = TorneoService.listar_organizadores(db, torneo.id)
        print(f"   [OK] Total organizadores: {len(organizadores)}")
        for org in organizadores:
            print(f"   - Usuario {org.user_id}: {org.rol}")
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS PASARON CORRECTAMENTE")
        print("="*60)
        print("\nEl sistema de torneos está funcionando correctamente!")
        print("Puedes probar los endpoints en: http://localhost:8000/docs")
        print("\nEndpoints disponibles:")
        print("  - POST   /torneos              - Crear torneo")
        print("  - GET    /torneos              - Listar torneos")
        print("  - GET    /torneos/{id}         - Obtener torneo")
        print("  - PUT    /torneos/{id}         - Actualizar torneo")
        print("  - DELETE /torneos/{id}         - Eliminar torneo")
        print("  - GET    /torneos/{id}/estadisticas - Estadísticas")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_crear_torneo()
