"""
Test para generar fixture del torneo 17 con algoritmo corregido
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database.config import get_db
from src.services.torneo_fixture_global_service import TorneoFixtureGlobalService
from src.models.torneo_models import Torneo

def test_generar_fixture_torneo17():
    """
    Genera fixture para el torneo 17 usando el servicio corregido
    """
    db = next(get_db())
    
    print("🧪 GENERANDO FIXTURE TORNEO 17 CON ALGORITMO CORREGIDO")
    print("="*60)
    
    torneo_id = 17
    
    try:
        # Verificar que el torneo existe y obtener el creador
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            print("❌ Torneo 17 no encontrado")
            return
        
        user_id = torneo.creado_por  # Usar el ID del creador real
        
        print(f"✅ Torneo encontrado: {torneo.nombre}")
        print(f"📅 Fechas: {torneo.fecha_inicio} - {torneo.fecha_fin}")
        print(f"👤 Creado por usuario ID: {user_id}")
        
        # Generar fixture completo
        resultado = TorneoFixtureGlobalService.generar_fixture_completo(
            db=db,
            torneo_id=torneo_id,
            user_id=user_id
        )
        
        print(f"\n📊 RESULTADOS:")
        print(f"   ✅ Partidos programados: {resultado['partidos_generados']}")
        print(f"   ❌ Partidos no programados: {resultado['partidos_no_programados']}")
        print(f"   🏟️ Zonas procesadas: {resultado['zonas_procesadas']}")
        print(f"   🎾 Canchas utilizadas: {resultado['canchas_utilizadas']}")
        print(f"   ⏰ Slots utilizados: {resultado['slots_utilizados']}")
        
        # Mostrar algunos partidos programados
        if resultado['partidos']:
            print(f"\n📋 PRIMEROS 5 PARTIDOS PROGRAMADOS:")
            for i, partido in enumerate(resultado['partidos'][:5]):
                print(f"   {i+1}. {partido['fecha']} {partido['hora']} - {partido['zona_nombre']} - {partido['cancha_nombre']}")
        
        # Mostrar partidos no programados si los hay
        if resultado['partidos_sin_programar']:
            print(f"\n⚠️ PARTIDOS NO PROGRAMADOS ({len(resultado['partidos_sin_programar'])}):")
            for partido in resultado['partidos_sin_programar'][:3]:  # Solo los primeros 3
                print(f"   🚨 {partido['categoria_nombre']} {partido['zona_nombre']}")
                print(f"      {partido['pareja1_nombre']} vs {partido['pareja2_nombre']}")
                print(f"      Motivo: {partido['motivo']}")
                print()
        
        # Calcular tasa de éxito
        total_partidos = resultado['partidos_generados'] + resultado['partidos_no_programados']
        if total_partidos > 0:
            tasa_exito = (resultado['partidos_generados'] / total_partidos) * 100
            print(f"\n📈 TASA DE ÉXITO: {tasa_exito:.1f}%")
        
        print(f"\n✅ Fixture generado exitosamente")
        
    except Exception as e:
        print(f"❌ Error al generar fixture: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_generar_fixture_torneo17()