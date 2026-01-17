#!/usr/bin/env python3
"""
Test script para verificar que las zonas manejen correctamente parejas eliminadas
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.services.torneo_zona_service import TorneoZonaService

def test_zonas_con_parejas_eliminadas():
    """Test para verificar que las zonas muestren parejas eliminadas"""
    db = next(get_db())
    
    try:
        # Usar torneo 17 que tiene zonas generadas
        torneo_id = 17
        
        print(f"🔍 Probando zonas del torneo {torneo_id}...")
        
        # Listar zonas
        zonas = TorneoZonaService.listar_zonas(db, torneo_id)
        
        print(f"\n📊 Encontradas {len(zonas)} zonas:")
        
        for zona in zonas:
            print(f"\n🏆 {zona['nombre']} (ID: {zona['id']}, Categoría: {zona['categoria_id']})")
            print(f"   Parejas: {len(zona['parejas'])}")
            
            for pareja in zona['parejas']:
                if pareja.get('eliminada', False):
                    print(f"   ❌ Pareja {pareja['id']} - ELIMINADA")
                else:
                    print(f"   ✅ Pareja {pareja['id']} - {pareja['estado']}")
        
        # Probar tabla de posiciones de la primera zona
        if zonas:
            primera_zona = zonas[0]
            print(f"\n📋 Tabla de posiciones de {primera_zona['nombre']}:")
            
            tabla = TorneoZonaService.obtener_tabla_posiciones(db, primera_zona['id'])
            
            for item in tabla['tabla']:
                if item.get('eliminada', False):
                    print(f"   ❌ Pos {item['posicion']}: {item['pareja_nombre']} (ELIMINADA)")
                else:
                    print(f"   ✅ Pos {item['posicion']}: {item['pareja_nombre']} - {item['puntos']} pts")
        
        print("\n✅ Test completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_zonas_con_parejas_eliminadas()