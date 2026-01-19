#!/usr/bin/env python3
"""
Test para generar fixture del torneo 24 categoría 64
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.torneo_models import Torneo, TorneoCategoria
from src.services.torneo_fixture_global_service import TorneoFixtureGlobalService
import traceback

def test_generar_fixture():
    """Test de generación de fixture"""
    db = next(get_db())
    
    try:
        torneo_id = 24
        categoria_id = 64
        
        print(f"🧪 Test: Generar fixture torneo {torneo_id}, categoría {categoria_id}")
        print("="*60)
        
        # Verificar torneo
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            print(f"❌ Torneo {torneo_id} no existe")
            return
        
        print(f"✅ Torneo: {torneo.nombre}")
        print(f"📅 Fechas: {torneo.fecha_inicio} al {torneo.fecha_fin}")
        print(f"⏰ Horarios: {torneo.horarios_disponibles}")
        
        # Verificar categoría
        categoria = db.query(TorneoCategoria).filter(
            TorneoCategoria.id == categoria_id,
            TorneoCategoria.torneo_id == torneo_id
        ).first()
        
        if not categoria:
            print(f"❌ Categoría {categoria_id} no existe en torneo {torneo_id}")
            return
        
        print(f"✅ Categoría: {categoria.nombre}")
        
        # Intentar generar fixture
        print(f"\n🔄 Generando fixture...")
        
        resultado = TorneoFixtureGlobalService.generar_fixture_completo(
            db=db,
            torneo_id=torneo_id,
            user_id=14,  # Usuario creador del torneo
            categoria_id=categoria_id
        )
        
        print(f"\n✅ Fixture generado exitosamente!")
        print(f"📊 Resultado: {resultado}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"\n📋 Traceback completo:")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_generar_fixture()
