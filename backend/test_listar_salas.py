import requests
import json

# URL del backend
BASE_URL = "http://localhost:8000"

# Token de autenticación (reemplazar con un token válido)
# Puedes obtenerlo haciendo login primero
TOKEN = "tu_token_aqui"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

try:
    print("🔍 Probando endpoint de listar salas...")
    response = requests.get(f"{BASE_URL}/salas/", headers=headers, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        salas = response.json()
        print(f"✅ Salas obtenidas: {len(salas)}")
        print(json.dumps(salas, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.text}")
        
except requests.exceptions.Timeout:
    print("⏱️ Timeout: El servidor no respondió a tiempo")
except requests.exceptions.ConnectionError:
    print("🔌 Error de conexión: No se pudo conectar al servidor")
except Exception as e:
    print(f"❌ Error inesperado: {str(e)}")
