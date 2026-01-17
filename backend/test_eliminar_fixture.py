"""
Test para probar el endpoint de eliminar fixture
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
TORNEO_ID = 17

def test_eliminar_fixture_completo():
    """Test: Eliminar fixture completo"""
    print("\n" + "="*80)
    print("TEST: Eliminar fixture completo")
    print("="*80)
    
    url = f"{BASE_URL}/torneos/{TORNEO_ID}/fixture"
    
    print(f"\nURL: {url}")
    print("Método: DELETE")
    
    try:
        response = requests.delete(url)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")

def test_eliminar_fixture_categoria():
    """Test: Eliminar fixture de una categoría específica"""
    print("\n" + "="*80)
    print("TEST: Eliminar fixture de categoría específica")
    print("="*80)
    
    categoria_id = 1  # Cambiar por una categoría que exista
    url = f"{BASE_URL}/torneos/{TORNEO_ID}/fixture?categoria_id={categoria_id}"
    
    print(f"\nURL: {url}")
    print("Método: DELETE")
    
    try:
        response = requests.delete(url)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")

def verificar_partidos_restantes():
    """Verificar cuántos partidos quedan después de eliminar"""
    print("\n" + "="*80)
    print("VERIFICACIÓN: Partidos restantes")
    print("="*80)
    
    url = f"{BASE_URL}/torneos/{TORNEO_ID}/partidos"
    
    try:
        response = requests.get(url)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            partidos = response.json()
            print(f"📊 Partidos restantes: {len(partidos)}")
            
            # Contar por fase
            fases = {}
            for partido in partidos:
                fase = partido.get('fase', 'sin_fase')
                fases[fase] = fases.get(fase, 0) + 1
            
            print("📋 Por fase:")
            for fase, count in fases.items():
                print(f"   {fase}: {count} partidos")
                
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")

if __name__ == "__main__":
    print("\n🧪 PRUEBAS DE ENDPOINT: DELETE /torneos/{id}/fixture")
    print("\n⚠️  NOTA: Estos tests requieren que el backend esté ejecutándose")
    print("   y que existan partidos en el torneo para poder eliminarlos")
    
    # Verificar estado inicial
    verificar_partidos_restantes()
    
    # Test 1: Eliminar fixture completo
    test_eliminar_fixture_completo()
    
    # Verificar después de eliminar
    verificar_partidos_restantes()
    
    print("\n" + "="*80)
    print("✅ Tests completados")
    print("="*80)