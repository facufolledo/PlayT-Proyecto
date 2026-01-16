"""
Test de generación de fixture por categoría
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.services.torneo_fixture_global_service import TorneoFixtureGlobalService

def test_fixture_categoria():
    db = next(get_db())
    
    torneo_id = 11
    user_id = 14  # Facundo
    categoria_id = 12  # 8va Masculino
    
    print(f"\n{'='*80}")
    print(f"TEST: Generar fixture para categoría {categoria_id} del torneo {torneo_id}")
    print(f"{'='*80}\n")
    
    try:
        resultado = TorneoFixtureGlobalService.generar_fixture_completo(
            db, torneo_id, user_id, categoria_id
        )
        
        print(f"✅ Fixture generado exitosamente")
        print(f"\n📊 RESUMEN:")
        print(f"   Partidos generados: {resultado['partidos_generados']}")
        print(f"   Partidos no programados: {resultado['partidos_no_programados']}")
        print(f"   Zonas procesadas: {resultado['zonas_procesadas']}")
        print(f"   Canchas utilizadas: {resultado['canchas_utilizadas']}")
        print(f"   Slots utilizados: {resultado['slots_utilizados']}")
        
        if resultado['partidos_sin_programar']:
            print(f"\n⚠️  PARTIDOS SIN PROGRAMAR:")
            for partido in resultado['partidos_sin_programar']:
                print(f"\n   Zona: {partido['zona_nombre']}")
                print(f"   {partido['pareja1_nombre']} vs {partido['pareja2_nombre']}")
                print(f"   Motivo: {partido['motivo']}")
                print(f"   Disp P1: {partido['disponibilidad_pareja1']}")
                print(f"   Disp P2: {partido['disponibilidad_pareja2']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixture_categoria()
