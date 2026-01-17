"""
Test simple y directo
"""
import requests

try:
    print("🔍 Probando health endpoint...")
    response = requests.get("http://127.0.0.1:8000/health", timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n🔍 Probando torneos endpoint...")
        torneos_response = requests.get("http://127.0.0.1:8000/torneos", timeout=30)
        print(f"Status: {torneos_response.status_code}")
        
        if torneos_response.status_code == 200:
            data = torneos_response.json()
            print(f"Torneos encontrados: {len(data)}")
            
            # Buscar torneo 17
            for torneo in data:
                if torneo.get('id') == 17:
                    print(f"\n✅ TORNEO 17 ENCONTRADO:")
                    print(f"   Nombre: {torneo.get('nombre')}")
                    print(f"   Parejas: {torneo.get('parejas_inscritas')}")
                    print(f"   Estado: {torneo.get('estado')}")
                    break
            else:
                print("❌ Torneo 17 no encontrado")
        else:
            print(f"Error: {torneos_response.text}")
    
except Exception as e:
    print(f"Error: {e}")