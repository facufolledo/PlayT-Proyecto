"""
Test simple para verificar endpoints de torneos
"""
import requests
import json

def test_endpoints():
    # Probar diferentes puertos comunes
    puertos = [8000, 9308, 5000, 3000]
    
    for puerto in puertos:
        print(f"\n🔍 PROBANDO PUERTO {puerto}...")
        try:
            # Test básico de health
            response = requests.get(f"http://localhost:{puerto}/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ Backend encontrado en puerto {puerto}")
                
                # Probar endpoint de torneos
                print(f"📋 Probando /torneos...")
                torneos_response = requests.get(f"http://localhost:{puerto}/torneos", timeout=5)
                print(f"   Status: {torneos_response.status_code}")
                
                if torneos_response.status_code == 200:
                    data = torneos_response.json()
                    print(f"   Torneos encontrados: {len(data)}")
                    
                    # Buscar torneo 17
                    torneo_17 = None
                    for torneo in data:
                        if torneo.get('id') == 17:
                            torneo_17 = torneo
                            break
                    
                    if torneo_17:
                        print(f"   ✅ Torneo 17 encontrado:")
                        print(f"      Nombre: {torneo_17.get('nombre')}")
                        print(f"      Parejas: {torneo_17.get('parejas_inscritas', 'N/A')}")
                        print(f"      Estado: {torneo_17.get('estado')}")
                    else:
                        print(f"   ❌ Torneo 17 no encontrado en la lista")
                        if len(data) > 0:
                            print(f"   📄 Primer torneo: {data[0]}")
                else:
                    print(f"   ❌ Error: {torneos_response.text[:200]}")
                
                return puerto  # Encontrado, salir
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ No hay conexión en puerto {puerto}")
        except requests.exceptions.Timeout:
            print(f"   ⏱️ Timeout en puerto {puerto}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n❌ No se encontró el backend en ningún puerto")
    return None

if __name__ == "__main__":
    test_endpoints()