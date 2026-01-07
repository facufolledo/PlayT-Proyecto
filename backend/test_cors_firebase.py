"""
Script de prueba para verificar CORS y Firebase Auth
Ejecutar con: python test_cors_firebase.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_cors():
    """Probar que CORS funciona correctamente"""
    print("🧪 Probando CORS...")
    try:
        response = requests.get(f"{BASE_URL}/api/test-cors")
        if response.status_code == 200:
            print("✅ CORS funciona correctamente")
            print(f"   Respuesta: {response.json()}")
            return True
        else:
            print(f"❌ Error en CORS: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al conectar con el servidor: {e}")
        print("   ¿Está el servidor corriendo en http://localhost:8000?")
        return False

def test_health():
    """Probar endpoint de health"""
    print("\n🧪 Probando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check OK")
            print(f"   Respuesta: {response.json()}")
            return True
        else:
            print(f"❌ Error en health: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_firebase_debug():
    """Probar endpoint de debug de Firebase"""
    print("\n🧪 Probando Firebase debug...")
    try:
        response = requests.get(f"{BASE_URL}/debug/firebase")
        if response.status_code == 200:
            data = response.json()
            print("✅ Firebase debug OK")
            print(f"   Firebase disponible: {data.get('firebase_available')}")
            print(f"   Credentials JSON env: {data.get('credentials_json_env')}")
            print(f"   Credentials path env: {data.get('credentials_path_env')}")
            return True
        else:
            print(f"❌ Error en Firebase debug: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_categorias():
    """Probar endpoint de categorías (no requiere auth)"""
    print("\n🧪 Probando categorías...")
    try:
        response = requests.get(f"{BASE_URL}/auth/categorias")
        if response.status_code == 200:
            categorias = response.json()
            print(f"✅ Categorías OK - {len(categorias)} categorías encontradas")
            for cat in categorias[:3]:  # Mostrar solo las primeras 3
                print(f"   - {cat.get('nombre')}: {cat.get('rating_min')}-{cat.get('rating_max')}")
            return True
        else:
            print(f"❌ Error en categorías: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE BACKEND - Drive+ API")
    print("=" * 60)
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("CORS", test_cors()))
    results.append(("Firebase Debug", test_firebase_debug()))
    results.append(("Categorías", test_categorias()))
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\n🎯 Resultado: {total_passed}/{total_tests} pruebas pasaron")
    
    if total_passed == total_tests:
        print("\n✅ ¡Todos los tests pasaron! El backend está funcionando correctamente.")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisa los errores arriba.")
        print("\n💡 Sugerencias:")
        print("   1. Verifica que el servidor esté corriendo: uvicorn main:app --reload")
        print("   2. Verifica que esté en http://localhost:8000")
        print("   3. Revisa las variables de entorno en .env")
        print("   4. Verifica que Firebase esté configurado correctamente")
