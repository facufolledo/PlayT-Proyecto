import requests
import json

# Test directo al endpoint
url = "http://localhost:8000/torneos/24"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"\nRespuesta completa:")
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    print(f"\n=== DATOS CLAVE ===")
    print(f"ID: {data.get('id_torneo') or data.get('id')}")
    print(f"Nombre: {data.get('nombre')}")
    print(f"Fecha Inicio: {data.get('fecha_inicio')}")
    print(f"Fecha Fin: {data.get('fecha_fin')}")
    print(f"Horarios: {data.get('horarios_disponibles')}")
    
except Exception as e:
    print(f"Error: {e}")
