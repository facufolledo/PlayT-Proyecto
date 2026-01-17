#!/usr/bin/env python3
"""
Test script para simular una pareja eliminada y verificar que las zonas la manejen correctamente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.services.torneo_zona_service import TorneoZonaService
from src.models.torneo_models import TorneoPareja

def test_simular_pareja_eliminada():
    """Test para simular eliminación de pareja y verificar manejo en zonas"""
    db = next(get_db())
    
    try:
        # Usar torneo 17 que tiene zonas generadas
        torneo_id = 17
        
        print(f"🔍 Simulando eliminación de pareja en torneo {torneo_id}...")
        
        # Encontrar una pareja para "eliminar" temporalmente
        pareja_test = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == torneo_id
        ).first()
        
        if not pareja_test:
            print("❌ No se encontró ninguna pareja para el test")
            return
        
        print(f"📝 Pareja original: ID {pareja_test.id}")
        
        # Guardar datos originales
        original_j1 = pareja_test.jugador1_id
        original_j2 = pareja_test.jugador2_id
        original_estado = pareja_test.estado
        
        # "Eliminar" la pareja temporalmente (simular eliminación)
        db.delete(pareja_test)
        db.commit()
        
        print(f"🗑️ Pareja {pareja_test.id} eliminada temporalmente")
        
        # Probar listar zonas
        zonas = TorneoZonaService.listar_zonas(db, torneo_id)
        
        print(f"\n📊 Verificando zonas después de eliminación:")
        
        pareja_eliminada_encontrada = False
        for zona in zonas:
            for pareja in zona['parejas']:
                if pareja.get('eliminada', False):
                    print(f"   ❌ ENCONTRADA: Zona {zona['nombre']} - Pareja {pareja['id']} ELIMINADA")
                    pareja_eliminada_encontrada = True
                    
                    # Probar tabla de posiciones de esta zona
                    tabla = TorneoZonaService.obtener_tabla_posiciones(db, zona['id'])
                    print(f"   📋 Tabla de {zona['nombre']}:")
                    for item in tabla['tabla']:
                        if item.get('eliminada', False):
                            print(f"      ❌ Pos {item['posicion']}: {item['pareja_nombre']} (ELIMINADA)")
                        else:
                            print(f"      ✅ Pos {item['posicion']}: {item['pareja_nombre']}")
                    break
            if pareja_eliminada_encontrada:
                break
        
        if pareja_eliminada_encontrada:
            print("✅ Test exitoso: Pareja eliminada detectada y manejada correctamente")
        else:
            print("⚠️ No se encontró la pareja eliminada en las zonas")
        
        # Restaurar la pareja
        nueva_pareja = TorneoPareja(
            id=pareja_test.id,
            torneo_id=torneo_id,
            jugador1_id=original_j1,
            jugador2_id=original_j2,
            estado=original_estado,
            categoria_id=pareja_test.categoria_id
        )
        db.add(nueva_pareja)
        db.commit()
        
        print(f"🔄 Pareja {pareja_test.id} restaurada")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_simular_pareja_eliminada()