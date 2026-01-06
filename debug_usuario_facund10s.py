#!/usr/bin/env python3
"""
Script para debuggear el problema con el usuario facund10s
"""
import requests
import json

BACKEND_URL = "https://drive-plus-production.up.railway.app"
USERNAME = "facund10s"

def test_buscar_usuario():
    """Probar endpoint de búsqueda"""
    print("🔍 Probando endpoint de búsqueda...")
    url = f"{BACKEND_URL}/usuarios/buscar-publico"
    
    try:
        params = {"q": "facund", "limit": 10}
        response = requests.get(url, params=params, timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Usuarios encontrados: {len(data)}")
            
            # Buscar específicamente facund10s
            facund10s = None
            for usuario in data:
                print(f"  - {usuario.get('nombre_usuario')} ({usuario.get('nombre')} {usuario.get('apellido')})")
                if usuario.get('nombre_usuario') == USERNAME:
                    facund10s = usuario
            
            if facund10s:
                print(f"\n✅ Usuario {USERNAME} encontrado en búsqueda:")
                print(json.dumps(facund10s, indent=2, ensure_ascii=False))
                return facund10s
            else:
                print(f"\n❌ Usuario {USERNAME} NO encontrado en búsqueda")
                return None
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"🚨 Error: {e}")
        return None

def test_perfil_publico():
    """Probar endpoint de perfil público"""
    print(f"\n🔍 Probando endpoint de perfil público para {USERNAME}...")
    url = f"{BACKEND_URL}/usuarios/perfil-publico/{USERNAME}"
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Perfil encontrado:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        elif response.status_code == 404:
            print("❌ Usuario no encontrado")
            print(f"📄 Response: {response.text}")
            return None
        else:
            print(f"⚠️ Error {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"🚨 Error: {e}")
        return None

def test_otros_endpoints():
    """Probar otros endpoints relacionados"""
    print(f"\n🔍 Probando otros endpoints...")
    
    # Probar endpoint alternativo
    url1 = f"{BACKEND_URL}/usuarios/@{USERNAME}/perfil"
    print(f"📡 GET {url1}")
    try:
        response = requests.get(url1, timeout=10)
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Endpoint alternativo funciona")
        else:
            print(f"❌ Endpoint alternativo: {response.text}")
    except Exception as e:
        print(f"🚨 Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print(f"🔍 DEBUGGING USUARIO: {USERNAME}")
    print("=" * 60)
    
    # Test 1: Búsqueda
    usuario_busqueda = test_buscar_usuario()
    
    # Test 2: Perfil público
    usuario_perfil = test_perfil_publico()
    
    # Test 3: Otros endpoints
    test_otros_endpoints()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN:")
    print(f"  Búsqueda: {'✅ Encontrado' if usuario_busqueda else '❌ No encontrado'}")
    print(f"  Perfil:   {'✅ Encontrado' if usuario_perfil else '❌ No encontrado'}")
    
    if usuario_busqueda and not usuario_perfil:
        print("\n🐛 PROBLEMA CONFIRMADO:")
        print("  El usuario existe en búsqueda pero no en perfil público")
        print("  Posibles causas:")
        print("  - Diferencia en las queries SQL")
        print("  - Problema con el JOIN en perfil público")
        print("  - Usuario sin perfil completo")
    print("=" * 60)