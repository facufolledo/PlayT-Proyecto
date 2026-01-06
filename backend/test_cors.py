#!/usr/bin/env python3
"""
Script para probar CORS desde el backend
"""
import requests
import json
from datetime import datetime

# URLs a probar
BASE_URL = "https://drive-plus-production.up.railway.app"
FRONTEND_ORIGIN = "https://kioskito.click"

def test_cors_preflight():
    """Probar preflight request (OPTIONS)"""
    print("🔍 Probando preflight request (OPTIONS)...")
    
    try:
        response = requests.options(
            f"{BASE_URL}/api/test-cors",
            headers={
                "Origin": FRONTEND_ORIGIN,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Verificar headers CORS
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
        }
        
        print(f"CORS Headers: {cors_headers}")
        
        if response.status_code == 200:
            print("✅ Preflight request exitoso")
        else:
            print(f"❌ Preflight request falló: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en preflight: {e}")

def test_cors_actual_request():
    """Probar request real con CORS"""
    print("\n🔍 Probando request real con CORS...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/test-cors",
            headers={
                "Origin": FRONTEND_ORIGIN,
                "Content-Type": "application/json"
            }
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Verificar headers CORS
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
        }
        
        print(f"CORS Headers: {cors_headers}")
        
        if response.status_code == 200:
            print("✅ Request real exitoso")
        else:
            print(f"❌ Request real falló: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en request real: {e}")

def test_health_endpoint():
    """Probar endpoint de health"""
    print("\n🔍 Probando endpoint de health...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/health",
            headers={
                "Origin": FRONTEND_ORIGIN
            }
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Health endpoint exitoso")
        else:
            print(f"❌ Health endpoint falló: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en health endpoint: {e}")

def test_cors_debug():
    """Probar endpoint de debug CORS"""
    print("\n🔍 Probando endpoint de debug CORS...")
    
    try:
        response = requests.get(f"{BASE_URL}/debug/cors")
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            debug_info = response.json()
            print("Debug CORS Info:")
            for key, value in debug_info.items():
                print(f"  {key}: {value}")
            print("✅ Debug CORS exitoso")
        else:
            print(f"❌ Debug CORS falló: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en debug CORS: {e}")

if __name__ == "__main__":
    print(f"🚀 Probando CORS para {BASE_URL}")
    print(f"🌐 Origin: {FRONTEND_ORIGIN}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("=" * 50)
    
    test_cors_debug()
    test_health_endpoint()
    test_cors_preflight()
    test_cors_actual_request()
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas")
