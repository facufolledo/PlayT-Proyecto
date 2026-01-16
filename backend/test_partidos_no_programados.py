"""
Script para probar el sistema de detección de partidos no programados
por incompatibilidad horaria
"""
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.config import get_database_url
from src.services.torneo_fixture_global_service import TorneoFixtureGlobalService

def test_partidos_no_programados():
    """
    Prueba la generación de fixture y detección de partidos no programados
    """
    print("=" * 60)
    print("TEST: DETECCIÓN DE PARTIDOS NO PROGRAMADOS")
    print("=" * 60)
    
    # Conectar a la base de datos
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Torneo de prueba (ID 11)
        torneo_id = 11
        user_id = 1  # Organizador
        
        print(f"\n📋 Generando fixture para torneo {torneo_id}...")
        
        try:
            resultado = TorneoFixtureGlobalService.generar_fixture_completo(
                db, torneo_id, user_id
            )
            
            print(f"\n✅ Fixture generado exitosamente")
            print(f"   • Partidos programados: {resultado['partidos_generados']}")
            print(f"   • Partidos NO programados: {resultado['partidos_no_programados']}")
            print(f"   • Zonas procesadas: {resultado['zonas_procesadas']}")
            print(f"   • Canchas utilizadas: {resultado['canchas_utilizadas']}")
            print(f"   • Slots utilizados: {resultado['slots_utilizados']}")
            
            # Mostrar detalles de partidos no programados
            if resultado['partidos_sin_programar']:
                print(f"\n⚠️  PARTIDOS NO PROGRAMADOS:")
                print("=" * 60)
                for partido in resultado['partidos_sin_programar']:
                    print(f"\n   Zona: {partido['zona_nombre']}")
                    print(f"   Pareja 1: {partido['pareja1_nombre']}")
                    print(f"   Pareja 2: {partido['pareja2_nombre']}")
                    print(f"   Motivo: {partido['motivo']}")
                    print(f"   Disponibilidad P1: {partido['disponibilidad_pareja1']}")
                    print(f"   Disponibilidad P2: {partido['disponibilidad_pareja2']}")
                    print("-" * 60)
            else:
                print(f"\n✅ Todos los partidos fueron programados exitosamente")
            
        except ValueError as e:
            print(f"\n❌ Error de validación: {e}")
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_partidos_no_programados()
