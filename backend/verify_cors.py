#!/usr/bin/env python3
"""
Script para verificar la configuración CORS del backend
"""
import os
import json
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_cors_configuration():
    """Verificar configuración CORS"""
    print("🔍 Verificando configuración CORS...")
    
    # Obtener origins configurados
    _default_origins = '["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "https://kioskito.click", "https://www.kioskito.click"]'
    
    try:
        origins = json.loads(os.getenv("CORS_ORIGINS", _default_origins))
        print(f"✅ CORS Origins configurados: {origins}")
        
        # Verificar que kioskito.click esté incluido
        if "https://kioskito.click" in origins:
            print("✅ kioskito.click está incluido en CORS")
        else:
            print("❌ kioskito.click NO está incluido en CORS")
            
        if "https://www.kioskito.click" in origins:
            print("✅ www.kioskito.click está incluido en CORS")
        else:
            print("❌ www.kioskito.click NO está incluido en CORS")
            
    except Exception as e:
        print(f"❌ Error parseando CORS_ORIGINS: {e}")
        origins = json.loads(_default_origins)
        print(f"🔄 Usando origins por defecto: {origins}")
    
    return origins

def test_backend_health(backend_url):
    """Probar conectividad con el backend"""
    print(f"\n🔍 Probando conectividad con {backend_url}...")
    
    try:
        # Test básico de health
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend responde correctamente")
            print(f"📊 Respuesta: {response.json()}")
        else:
            print(f"❌ Backend respondió con status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando al backend: {e}")

def test_cors_preflight(backend_url, origin):
    """Probar preflight CORS request"""
    print(f"\n🔍 Probando CORS preflight desde {origin}...")
    
    try:
        headers = {
            'Origin': origin,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        response = requests.options(f"{backend_url}/api/test-cors", headers=headers, timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        # Verificar headers CORS
        if 'Access-Control-Allow-Origin' in response.headers:
            print(f"✅ Access-Control-Allow-Origin: {response.headers['Access-Control-Allow-Origin']}")
        else:
            print("❌ Access-Control-Allow-Origin header missing")
            
        if 'Access-Control-Allow-Methods' in response.headers:
            print(f"✅ Access-Control-Allow-Methods: {response.headers['Access-Control-Allow-Methods']}")
        else:
            print("❌ Access-Control-Allow-Methods header missing")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en preflight request: {e}")

if __name__ == "__main__":
    print("🚀 Verificador CORS para Drive+ Backend\n")
    
    # Verificar configuración
    origins = test_cors_configuration()
    
    # URL del backend
    backend_url = "https://drive-plus-production.up.railway.app"
    
    # Probar conectividad
    test_backend_health(backend_url)
    
    # Probar CORS desde kioskito.click
    test_cors_preflight(backend_url, "https://kioskito.click")
    test_cors_preflight(backend_url, "https://www.kioskito.click")
    
    print("\n🏁 Verificación completada")
