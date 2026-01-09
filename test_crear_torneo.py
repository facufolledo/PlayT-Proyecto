#!/usr/bin/env python3
"""
Script para probar la creación de torneos y diagnosticar el error "Method Not Allowed"
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Prueba los endpoints de torneos"""
    
    print("🧪 Probando endpoints de torneos...")
    
    # 1. Probar endpoint simple (sin auth)
    try:
        response = requests.get(f"{BASE_URL}/torneos/test-simple")
        print(f"✅ GET /test-simple - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en GET /test-simple: {e}")
    
    # 2. Probar listar torneos
    try:
        response = requests.get(f"{BASE_URL}/torneos")
        print(f"✅ GET /torneos - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Torneos encontrados: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en GET /torneos: {e}")
    
    # 3. Probar POST sin autenticación (debería dar 401)
    try:
        test_data = {
            "nombre": "Torneo de Prueba",
            "categoria": "5ta",
            "fecha_inicio": "2026-01-15",
            "fecha_fin": "2026-01-22"
        }
        response = requests.post(f"{BASE_URL}/torneos", json=test_data)
        print(f"✅ POST /torneos (sin auth) - Status: {response.status_code}")
        if response.status_code == 401:
            print(f"   ✅ Correcto: Requiere autenticación")
        else:
            print(f"   ⚠️ Inesperado: {response.text}")
    except Exception as e:
        print(f"❌ Error en POST /torneos: {e}")
    
    # 4. Probar OPTIONS (CORS preflight)
    try:
        headers = {
            'Origin': 'http://localhost:5174',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        response = requests.options(f"{BASE_URL}/torneos", headers=headers)
        print(f"✅ OPTIONS /torneos - Status: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        print(f"   CORS headers: {cors_headers}")
        
    except Exception as e:
        print(f"❌ Error en OPTIONS /torneos: {e}")

def test_method_not_allowed():
    """Prueba específica para el error Method Not Allowed"""
    
    print("\n🔍 Diagnosticando 'Method Not Allowed'...")
    
    # Probar diferentes métodos HTTP
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    
    for method in methods:
        try:
            response = requests.request(method, f"{BASE_URL}/torneos")
            print(f"   {method} /torneos - Status: {response.status_code}")
        except Exception as e:
            print(f"   {method} /torneos - Error: {e}")
    
    print("\n🔍 Probando con trailing slash...")
    
    for method in methods:
        try:
            response = requests.request(method, f"{BASE_URL}/torneos/")
            print(f"   {method} /torneos/ - Status: {response.status_code}")
        except Exception as e:
            print(f"   {method} /torneos/ - Error: {e}")

def test_server_running():
    """Verifica que el servidor esté corriendo"""
    
    print("\n🌐 Verificando servidor...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Servidor corriendo - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Health check: {response.json()}")
    except Exception as e:
        print(f"❌ Servidor no responde: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de creación de torneos...\n")
    
    if not test_server_running():
        print("\n❌ El servidor no está corriendo. Inicialo con:")
        print("   cd backend && python main.py")
        exit(1)
    
    test_endpoints()
    test_method_not_allowed()
    
    print("\n💡 Posibles causas del error 'Method Not Allowed':")
    print("   1. El endpoint POST /torneos no está registrado correctamente")
    print("   2. Problema con el router de FastAPI")
    print("   3. Conflicto entre rutas (ej: /torneos vs /torneos/)")
    print("   4. Middleware bloqueando el método POST")
    print("   5. Problema de CORS en preflight request")
    
    print("\n🔧 Para solucionarlo:")
    print("   1. Verificar que el router esté incluido en main.py")
    print("   2. Revisar el orden de las rutas en el controlador")
    print("   3. Verificar logs del servidor backend")
    print("   4. Probar con curl: curl -X POST http://localhost:8000/torneos")