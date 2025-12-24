"""
Script de diagnóstico para el error de inscripción en torneos
Ejecutar: python test_inscripcion_debug.py
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuración
API_URL = os.getenv("API_URL", "http://localhost:8000")
# Para producción: API_URL = "https://playt-backend.onrender.com"

def test_firebase_status():
    """Verificar estado de Firebase en el backend"""
    print("\n🔥 1. Verificando estado de Firebase...")
    try:
        response = requests.get(f"{API_URL}/debug/firebase")
        data = response.json()
        print(f"   Firebase disponible: {data.get('firebase_available')}")
        print(f"   Credentials JSON: {data.get('credentials_json_env')}")
        print(f"   Credentials Path: {data.get('credentials_path_env')}")
        return data.get('firebase_available', False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_endpoint_exists():
    """Verificar que el endpoint existe"""
    print("\n📍 2. Verificando endpoint de inscripción...")
    try:
        # Hacer OPTIONS para ver si el endpoint existe
        response = requests.options(f"{API_URL}/torneos/1/inscribir")
        print(f"   Status: {response.status_code}")
        print(f"   Allow: {response.headers.get('Allow', 'No especificado')}")
        
        # Intentar POST sin auth para ver el error
        response = requests.post(f"{API_URL}/torneos/1/inscribir", json={})
        print(f"   POST sin auth: {response.status_code}")
        if response.status_code == 403:
            print("   ✅ Endpoint existe (requiere autenticación)")
            return True
        elif response.status_code == 401:
            print("   ✅ Endpoint existe (requiere autenticación)")
            return True
        elif response.status_code == 405:
            print("   ❌ Method Not Allowed - El endpoint puede no existir")
            return False
        elif response.status_code == 422:
            print("   ✅ Endpoint existe (error de validación esperado)")
            return True
        else:
            print(f"   ⚠️ Respuesta inesperada: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_with_token(token: str, torneo_id: int = 1):
    """Probar inscripción con un token"""
    print(f"\n🔐 3. Probando con token...")
    print(f"   Token (primeros 50 chars): {token[:50]}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Primero verificar el token
    print("\n   Verificando token con endpoint de usuario...")
    try:
        response = requests.get(f"{API_URL}/usuarios/me", headers=headers)
        print(f"   Status /usuarios/me: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Usuario: {user_data.get('email', 'N/A')}")
            print(f"   ✅ ID: {user_data.get('id_usuario', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Ahora probar inscripción
    print(f"\n   Probando inscripción en torneo {torneo_id}...")
    data = {
        "jugador1_id": user_data.get('id_usuario', 1),
        "jugador2_id": 2,  # Cambiar por un ID válido
        "nombre_pareja": "Test Pareja"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/torneos/{torneo_id}/inscribir",
            headers=headers,
            json=data
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
        
        if response.status_code == 201:
            print("   ✅ Inscripción exitosa!")
            return True
        elif response.status_code == 400:
            print("   ⚠️ Error de validación (pero el endpoint funciona)")
            return True
        elif response.status_code == 401:
            print("   ❌ Token inválido")
            return False
        elif response.status_code == 405:
            print("   ❌ Method Not Allowed")
            return False
        else:
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE INSCRIPCIÓN EN TORNEOS")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    
    # Test 1: Firebase
    firebase_ok = test_firebase_status()
    
    # Test 2: Endpoint
    endpoint_ok = test_endpoint_exists()
    
    # Test 3: Con token (si se proporciona)
    if len(sys.argv) > 1:
        token = sys.argv[1]
        torneo_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        test_with_token(token, torneo_id)
    else:
        print("\n💡 Para probar con token, ejecuta:")
        print("   python test_inscripcion_debug.py <TOKEN> [TORNEO_ID]")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN")
    print("=" * 60)
    print(f"   Firebase inicializado: {'✅' if firebase_ok else '❌'}")
    print(f"   Endpoint disponible: {'✅' if endpoint_ok else '❌'}")
    
    if not firebase_ok:
        print("\n⚠️ SOLUCIÓN: Configurar FIREBASE_CREDENTIALS_JSON o FIREBASE_SERVICE_ACCOUNT")
        print("   en las variables de entorno del backend (Render)")
    
    if not endpoint_ok:
        print("\n⚠️ SOLUCIÓN: Verificar que el router de torneos esté registrado en main.py")

if __name__ == "__main__":
    main()
