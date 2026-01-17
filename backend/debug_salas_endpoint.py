#!/usr/bin/env python3
"""
Debug del endpoint de salas para ver por qué no se están listando
"""

import requests
import json

def test_salas_endpoint():
    """Test del endpoint de salas"""
    
    # URL del backend en producción
    base_url = "https://drive-plus-production.up.railway.app"
    
    print("🔍 DEBUGGING ENDPOINT DE SALAS")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Salas sin autenticación (debería dar 401)
    print("\n2. Testing salas sin auth...")
    try:
        response = requests.get(f"{base_url}/salas/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Verificar que el endpoint existe
    print("\n3. Testing OPTIONS en salas...")
    try:
        response = requests.options(f"{base_url}/salas/", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Verificar CORS
    print("\n4. Testing CORS...")
    try:
        headers = {
            'Origin': 'https://drive-plus.com.ar',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'authorization,content-type'
        }
        response = requests.options(f"{base_url}/salas/", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_salas_endpoint()