#!/usr/bin/env python3
"""Script para probar el endpoint de completar perfil"""
import requests
import json

# URL del backend
BASE_URL = "http://localhost:8000"

def test_completar_perfil():
    """Prueba el endpoint de completar perfil"""
    
    print("🧪 Probando endpoint /usuarios/completar-perfil")
    print("-" * 50)
    
    # Datos de prueba
    datos = {
        "nombre": "Juan",
        "apellido": "Pérez",
        "dni": "12345678",
        "fecha_nacimiento": "1990-05-15",
        "genero": "masculino",
        "categoria_inicial": "8va",
        "mano_habil": "derecha",
        "posicion_preferida": "drive",
        "telefono": "+54 9 11 1234-5678",
        "ciudad": "Buenos Aires",
        "pais": "Argentina"
    }
    
    print("\n📤 Datos a enviar:")
    print(json.dumps(datos, indent=2, ensure_ascii=False))
    
    # Nota: Este test requiere un token válido
    # Por ahora solo verificamos que el endpoint existe
    try:
        response = requests.post(
            f"{BASE_URL}/usuarios/completar-perfil",
            json=datos,
            timeout=5
        )
        
        print(f"\n📥 Respuesta: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Endpoint existe (requiere autenticación)")
        elif response.status_code == 200:
            print("✅ Perfil completado exitosamente")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"⚠️ Respuesta inesperada: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al backend. ¿Está corriendo?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_completar_perfil()
