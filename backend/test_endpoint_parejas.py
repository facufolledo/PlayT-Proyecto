"""
Probar endpoint de parejas del torneo 17
"""
import requests
import json

def test_parejas_endpoint():
    base_url = "http://localhost:9308"  # Puerto correcto
    torneo_id = 17
    
    print(f"🔍 PROBANDO ENDPOINT: GET /torneos/{torneo_id}/parejas")
    
    try:
        # Probar sin autenticación primero
        response = requests.get(f"{base_url}/torneos/{torneo_id}/parejas")
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta exitosa!")
            print(f"📦 Tipo de respuesta: {type(data)}")
            
            if isinstance(data, list):
                print(f"👥 Total parejas: {len(data)}")
                if len(data) > 0:
                    print(f"🔍 Primera pareja: {json.dumps(data[0], indent=2, default=str)}")
                else:
                    print("❌ Lista vacía - no hay parejas")
            else:
                print(f"📄 Respuesta completa: {json.dumps(data, indent=2, default=str)}")
        
        elif response.status_code == 401:
            print("🔒 Error 401: Requiere autenticación")
            print("💡 El endpoint requiere token de Firebase")
        
        elif response.status_code == 404:
            print("❌ Error 404: Torneo no encontrado")
        
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: ¿Está el backend corriendo en localhost:9308?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_parejas_endpoint()