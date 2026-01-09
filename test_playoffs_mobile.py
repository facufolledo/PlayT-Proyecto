#!/usr/bin/env python3
"""
Script de prueba para verificar que los playoffs funcionen correctamente en móviles
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
TORNEO_ID = 1  # Cambiar por un ID de torneo real

def test_playoffs_endpoints():
    """Prueba los endpoints de playoffs"""
    
    print("🧪 Probando endpoints de playoffs...")
    
    # 1. Probar obtener playoffs
    try:
        response = requests.get(f"{BASE_URL}/torneos/{TORNEO_ID}/playoffs")
        print(f"✅ GET /playoffs - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Partidos encontrados: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en GET /playoffs: {e}")
    
    # 2. Probar obtener bracket visual
    try:
        response = requests.get(f"{BASE_URL}/torneos/{TORNEO_ID}/playoffs/bracket")
        print(f"✅ GET /playoffs/bracket - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Bracket data: {type(data)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en GET /playoffs/bracket: {e}")
    
    # 3. Probar obtener clasificados
    try:
        response = requests.get(f"{BASE_URL}/torneos/{TORNEO_ID}/playoffs/clasificados")
        print(f"✅ GET /playoffs/clasificados - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Clasificados: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en GET /playoffs/clasificados: {e}")

def test_mobile_responsiveness():
    """Simula requests desde móvil"""
    
    print("\n📱 Probando responsividad móvil...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/torneos/{TORNEO_ID}/playoffs", headers=headers)
        print(f"✅ Mobile request - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Datos recibidos correctamente en móvil")
            
            # Verificar estructura de datos
            if isinstance(data, list):
                for partido in data[:3]:  # Solo los primeros 3
                    required_fields = ['id', 'fase', 'estado']
                    missing_fields = [field for field in required_fields if field not in partido]
                    if missing_fields:
                        print(f"   ⚠️ Campos faltantes en partido: {missing_fields}")
                    else:
                        print(f"   ✅ Partido {partido.get('id')} - Fase: {partido.get('fase')} - Estado: {partido.get('estado')}")
        else:
            print(f"   ❌ Error en móvil: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en mobile request: {e}")

def test_cors():
    """Prueba CORS para móviles"""
    
    print("\n🌐 Probando CORS...")
    
    # Simular preflight request
    headers = {
        'Origin': 'https://kioskito.click',
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    try:
        response = requests.options(f"{BASE_URL}/torneos/{TORNEO_ID}/playoffs", headers=headers)
        print(f"✅ CORS preflight - Status: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print(f"   CORS headers: {cors_headers}")
        
    except Exception as e:
        print(f"❌ Error en CORS test: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de playoffs para móviles...\n")
    
    test_playoffs_endpoints()
    test_mobile_responsiveness()
    test_cors()
    
    print("\n✅ Pruebas completadas!")
    print("\n💡 Recomendaciones para móviles:")
    print("   - Verificar que los datos se carguen correctamente")
    print("   - Probar la vista móvil optimizada en el frontend")
    print("   - Verificar que no hay errores de CORS")
    print("   - Probar en diferentes tamaños de pantalla")