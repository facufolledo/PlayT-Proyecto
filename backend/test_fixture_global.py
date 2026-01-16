"""
Script para probar la generación de fixture global
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from src.database.config import SessionLocal
from src.services.torneo_fixture_global_service import TorneoFixtureGlobalService
from src.models.torneo_models import Torneo, TorneoZona, TorneoPareja, TorneoCancha
from src.models.driveplus_models import Partido

def test_fixture_global():
    db: Session = SessionLocal()
    
    try:
        torneo_id = 11
        user_id = 14  # facund10s
        
        print(f"\n{'='*60}")
        print(f"PRUEBA DE FIXTURE GLOBAL - TORNEO {torneo_id}")
        print(f"{'='*60}\n")
        
        # Verificar torneo
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            print(f"❌ Torneo {torneo_id} no encontrado")
            return
        
        print(f"✅ Torneo: {torneo.nombre}")
        print(f"   Fechas: {torneo.fecha_inicio} a {torneo.fecha_fin}")
        
        # Verificar zonas
        zonas = db.query(TorneoZona).filter(TorneoZona.torneo_id == torneo_id).all()
        print(f"\n📊 Zonas encontradas: {len(zonas)}")
        for zona in zonas:
            from src.models.torneo_models import TorneoZonaPareja
            parejas_count = db.query(TorneoZonaPareja).filter(
                TorneoZonaPareja.zona_id == zona.id
            ).count()
            print(f"   - {zona.nombre}: {parejas_count} parejas")
        
        # Verificar canchas
        canchas = db.query(TorneoCancha).filter(
            TorneoCancha.torneo_id == torneo_id,
            TorneoCancha.activa == True
        ).all()
        print(f"\n🏟️  Canchas activas: {len(canchas)}")
        for cancha in canchas:
            print(f"   - {cancha.nombre}")
        
        # Verificar partidos existentes
        partidos_existentes = db.query(Partido).filter(
            Partido.id_torneo == torneo_id
        ).count()
        print(f"\n⚠️  Partidos existentes: {partidos_existentes}")
        
        # Generar fixture
        print(f"\n🔄 Generando fixture global...")
        resultado = TorneoFixtureGlobalService.generar_fixture_completo(
            db, torneo_id, user_id
        )
        
        print(f"\n{'='*60}")
        print(f"RESULTADO")
        print(f"{'='*60}")
        print(f"✅ Partidos generados: {resultado['partidos_generados']}")
        print(f"✅ Zonas procesadas: {resultado['zonas_procesadas']}")
        print(f"✅ Canchas utilizadas: {resultado['canchas_utilizadas']}")
        print(f"✅ Slots utilizados: {resultado['slots_utilizados']}")
        
        # Mostrar algunos partidos de ejemplo
        print(f"\n📋 Primeros 5 partidos:")
        for i, partido in enumerate(resultado['partidos'][:5]):
            print(f"\n   Partido {i+1}:")
            print(f"   - Zona: {partido['zona_nombre']}")
            print(f"   - Fecha/Hora: {partido['fecha']} {partido['hora']}")
            print(f"   - Cancha: {partido['cancha_nombre']}")
            print(f"   - Parejas: {partido['pareja1_id']} vs {partido['pareja2_id']}")
        
        print(f"\n{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_fixture_global()
