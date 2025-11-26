"""
Script para probar el endpoint de historial de partidos de usuario
"""
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

def test_historial_usuario():
    """Probar endpoint de historial de usuario"""
    
    # Primero hacer login para obtener token
    print("🔐 Haciendo login...")
    # Usar usuario existente - ajusta según tu base de datos
    login_response = requests.post(
        f"{API_URL}/auth/login",
        data={
            "username": "facundo",
            "password": "123456"  # Ajusta la contraseña según tu usuario
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    usuario_id = login_response.json()["usuario"]["id_usuario"]
    print(f"✅ Login exitoso. Usuario ID: {usuario_id}")
    
    # Obtener historial de partidos
    print(f"\n📊 Obteniendo historial de partidos...")
    headers = {"Authorization": f"Bearer {token}"}
    
    historial_response = requests.get(
        f"{API_URL}/partidos/usuario/{usuario_id}",
        headers=headers,
        params={"limit": 50}
    )
    
    if historial_response.status_code != 200:
        print(f"❌ Error obteniendo historial: {historial_response.status_code}")
        print(historial_response.text)
        return
    
    partidos = historial_response.json()
    print(f"✅ Historial obtenido: {len(partidos)} partidos")
    
    # Mostrar detalles de los primeros 3 partidos
    print("\n📋 Detalles de partidos:")
    for i, partido in enumerate(partidos[:3], 1):
        print(f"\n--- Partido {i} ---")
        print(f"ID: {partido['id_partido']}")
        print(f"Fecha: {partido['fecha']}")
        print(f"Estado: {partido['estado']}")
        
        if partido.get('jugadores'):
            print(f"Jugadores: {len(partido['jugadores'])}")
            for jugador in partido['jugadores']:
                print(f"  - {jugador.get('nombre', '')} {jugador.get('apellido', '')} (Equipo {jugador.get('equipo')})")
        
        if partido.get('resultado'):
            resultado = partido['resultado']
            print(f"Resultado: {resultado['sets_eq1']}-{resultado['sets_eq2']}")
            print(f"Detalle sets: {resultado.get('detalle_sets', [])}")
            print(f"Confirmado: {resultado['confirmado']}")
        
        if partido.get('historial_rating'):
            historial = partido['historial_rating']
            print(f"Rating antes: {historial['rating_antes']}")
            print(f"Delta: {historial['delta']:+d}")
            print(f"Rating después: {historial['rating_despues']}")
    
    # Guardar respuesta completa en archivo
    with open('historial_response.json', 'w', encoding='utf-8') as f:
        json.dump(partidos, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Respuesta completa guardada en historial_response.json")

if __name__ == "__main__":
    test_historial_usuario()
