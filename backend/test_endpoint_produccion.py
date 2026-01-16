"""
Test del endpoint de búsqueda en producción
"""
import requests

BACKEND_URL = "https://drive-plus-production.up.railway.app"

def test_busqueda():
    print("=" * 60)
    print("TEST: Endpoint de búsqueda en producción")
    print("=" * 60)
    
    # Test 1: Búsqueda con "fac"
    print("\n🔍 Test 1: Búsqueda con 'fac'")
    url = f"{BACKEND_URL}/usuarios/buscar-publico?q=fac&limit=20"
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resultados: {len(data)}")
            for jugador in data[:3]:  # Mostrar primeros 3
                print(f"  - {jugador.get('nombre')} {jugador.get('apellido')} (@{jugador.get('nombre_usuario')})")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 2: Búsqueda con "cass"
    print("\n🔍 Test 2: Búsqueda con 'cass'")
    url = f"{BACKEND_URL}/usuarios/buscar-publico?q=cass&limit=20"
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resultados: {len(data)}")
            for jugador in data[:3]:
                print(f"  - {jugador.get('nombre')} {jugador.get('apellido')} (@{jugador.get('nombre_usuario')})")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 3: Health check
    print("\n🏥 Test 3: Health check")
    url = f"{BACKEND_URL}/health"
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Backend está activo")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Backend no responde correctamente")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_busqueda()
