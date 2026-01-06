#!/usr/bin/env python3
"""
Script para probar el endpoint de perfil público
"""
import requests
import json

# URLs a probar
BACKEND_URL = "https://drive-plus-production.up.railway.app"
USERNAME = "maurinho2"

def test_perfil_publico():
    """Probar el endpoint de perfil público"""
    
    print(f"🔍 Probando perfil público para usuario: {USERNAME}")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print("-" * 50)
    
    # Probar endpoint
    url = f"{BACKEND_URL}/usuarios/perfil-publico/{USERNAME}"
    
    try:
        print(f"📡 GET {url}")
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Perfil encontrado:")
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        elif response.status_code == 404:
            print("❌ Usuario no encontrado")
            print(f"📄 Response: {response.text}")
        else:
            print(f"⚠️ Error {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"🚨 Error de conexión: {e}")
    
    print("-" * 50)

def test_listar_usuarios():
    """Probar listar algunos usuarios para ver qué usernames existen"""
    
    print("🔍 Probando listar usuarios...")
    url = f"{BACKEND_URL}/usuarios/buscar"
    
    try:
        # Buscar usuarios que contengan "maur"
        params = {"q": "maur", "limit": 10}
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Usuarios encontrados:")
            for usuario in data.get('usuarios', []):
                print(f"  - {usuario.get('nombre_usuario')} ({usuario.get('nombre')} {usuario.get('apellido')})")
        else:
            print(f"⚠️ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"🚨 Error de conexión: {e}")

if __name__ == "__main__":
    test_perfil_publico()
    print()
    test_listar_usuarios()