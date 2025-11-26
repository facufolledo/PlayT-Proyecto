"""
Script para probar el endpoint de iniciar partido
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"

def test_iniciar_partido():
    """Probar el flujo completo de iniciar un partido"""
    
    print("=" * 60)
    print("TEST: INICIAR PARTIDO")
    print("=" * 60)
    
    # 1. Login como usuario de prueba
    print("\n1. Login...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "nombre_usuario": "test_user",
            "password": "test123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login exitoso")
    
    # 2. Crear una sala
    print("\n2. Creando sala...")
    sala_response = requests.post(
        f"{BASE_URL}/salas/",
        headers=headers,
        json={
            "nombre": "Test Iniciar Partido",
            "fecha": "2024-01-20T10:00:00",
            "max_jugadores": 4
        }
    )
    
    if sala_response.status_code != 200:
        print(f"❌ Error al crear sala: {sala_response.status_code}")
        print(sala_response.text)
        return
    
    sala = sala_response.json()
    sala_id = sala["id_sala"]
    print(f"✅ Sala creada: {sala_id}")
    print(f"   Código: {sala['codigo_invitacion']}")
    
    # 3. Obtener información de la sala
    print(f"\n3. Obteniendo información de sala {sala_id}...")
    info_response = requests.get(
        f"{BASE_URL}/salas/{sala_id}",
        headers=headers
    )
    
    if info_response.status_code != 200:
        print(f"❌ Error al obtener sala: {info_response.status_code}")
        print(info_response.text)
        return
    
    sala_info = info_response.json()
    print(f"✅ Sala obtenida")
    print(f"   Jugadores actuales: {sala_info['jugadores_actuales']}/{sala_info['max_jugadores']}")
    print(f"   Estado: {sala_info['estado']}")
    
    # 4. Intentar iniciar partido (debería fallar - solo 1 jugador)
    print(f"\n4. Intentando iniciar partido con 1 jugador (debe fallar)...")
    iniciar_response = requests.post(
        f"{BASE_URL}/salas/{sala_id}/iniciar",
        headers=headers
    )
    
    if iniciar_response.status_code == 400:
        error = iniciar_response.json()
        print(f"✅ Error esperado: {error['detail']}")
    else:
        print(f"❌ Respuesta inesperada: {iniciar_response.status_code}")
        print(iniciar_response.text)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)
    print("\nNOTA: Para probar el inicio completo, necesitas:")
    print("  1. Agregar 3 jugadores más a la sala")
    print("  2. Asignar equipos a todos los jugadores")
    print("  3. Intentar iniciar el partido nuevamente")

if __name__ == "__main__":
    test_iniciar_partido()
