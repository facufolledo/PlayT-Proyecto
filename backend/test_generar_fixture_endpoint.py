"""
Test del endpoint de generar fixture
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
TORNEO_ID = 11

# Token de autenticación (debes obtenerlo del frontend o Firebase)
# Por ahora, vamos a probar sin autenticación para ver el error
TOKEN = None

def test_generar_fixture_sin_categoria():
    """Test: Generar fixture sin especificar categoría"""
    print("\n" + "="*80)
    print("TEST 1: Generar fixture SIN categoría")
    print("="*80)
    
    url = f"{BASE_URL}/torneos/{TORNEO_ID}/generar-fixture"
    headers = {}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    
    print(f"\nURL: {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.post(url, headers=headers, json={})
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")

def test_generar_fixture_con_categoria():
    """Test: Generar fixture especificando categoría"""
    print("\n" + "="*80)
    print("TEST 2: Generar fixture CON categoría")
    print("="*80)
    
    categoria_id = 12
    url = f"{BASE_URL}/torneos/{TORNEO_ID}/generar-fixture?categoria_id={categoria_id}"
    headers = {}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    
    print(f"\nURL: {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.post(url, headers=headers, json={})
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    print("\n🧪 PRUEBAS DE ENDPOINT: /torneos/{id}/generar-fixture")
    print("\n⚠️  NOTA: Estos tests fallarán con 401 si no hay token de autenticación")
    print("   El objetivo es verificar que el endpoint acepta los parámetros correctamente")
    
    test_generar_fixture_sin_categoria()
    test_generar_fixture_con_categoria()
    
    print("\n" + "="*80)
    print("✅ Tests completados")
    print("="*80)
