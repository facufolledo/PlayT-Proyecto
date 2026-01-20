"""
Script para probar el endpoint de perfil en producción
"""
import requests
import json

def test_perfil(username):
    """Probar endpoint de perfil público"""
    url = f"https://drive-plus-production.up.railway.app/usuarios/perfil-publico/{username}"
    
    print(f"\n{'='*80}")
    print(f"Testing: {url}")
    print(f"{'='*80}\n")
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\nResponse Body:")
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
        
        if response.status_code == 200:
            print(f"\n✅ SUCCESS - Perfil cargado correctamente")
        elif response.status_code == 404:
            print(f"\n⚠️  NOT FOUND - Usuario no existe")
        elif response.status_code == 500:
            print(f"\n❌ ERROR 500 - Error interno del servidor")
            print(f"   El backend aún no ha desplegado los cambios o hay un error")
        else:
            print(f"\n⚠️  Status {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - El servidor no respondió a tiempo")
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - No se pudo conectar al servidor")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    # Probar usuarios problemáticos
    usuarios = [
        "qezequiel96",
        "francoayet07",
        "facufolledo"  # Este debería funcionar
    ]
    
    for username in usuarios:
        test_perfil(username)
        print("\n")
