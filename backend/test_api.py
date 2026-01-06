#!/usr/bin/env python3
"""
Script para probar todos los endpoints de Drive+ API
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, endpoint, data=None, headers=None, description=""):
    """Función para probar un endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 {description}")
    print(f"   {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code < 400:
            try:
                result = response.json()
                print(f"   ✅ Respuesta: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}...")
                return result
            except:
                print(f"   ✅ Respuesta: {response.text[:100]}...")
                return response.text
        else:
            print(f"   ❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"   💥 Excepción: {str(e)}")
        return None

def main():
    print("🚀 TESTING Drive+ API")
    print("=" * 50)
    
    # 1. Test endpoints básicos
    test_endpoint("GET", "/", description="Endpoint raíz")
    test_endpoint("GET", "/health", description="Health check")
    test_endpoint("GET", "/api/info", description="Información de la API")
    
    # 2. Test categorías
    test_endpoint("GET", "/categorias", description="Listar categorías")
    
    # 3. Test registro de usuario
    user_data = {
        "nombre_usuario": "testuser_" + str(int(time.time())),
        "email": f"test_{int(time.time())}@example.com",
        "password": "password123",
        "nombre": "Test",
        "apellido": "User",
        "ciudad": "Buenos Aires",
        "pais": "Argentina"
    }
    
    register_result = test_endpoint("POST", "/auth/register", data=user_data, 
                                  description="Registrar nuevo usuario")
    
    if register_result:
        # 4. Test login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        login_result = test_endpoint("POST", "/auth/login", data=login_data,
                                   description="Login de usuario")
        
        if login_result and "access_token" in login_result:
            # 5. Test endpoints autenticados
            headers = {"Authorization": f"Bearer {login_result['access_token']}"}
            
            test_endpoint("GET", "/auth/me", headers=headers,
                        description="Obtener información del usuario actual")
            
            # 6. Test crear partido (si está disponible)
            test_endpoint("GET", "/partidos", headers=headers,
                        description="Listar partidos")
    
    print("\n" + "=" * 50)
    print("✅ Testing completado!")

if __name__ == "__main__":
    main()

