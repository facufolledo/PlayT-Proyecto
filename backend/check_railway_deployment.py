"""
Script para verificar si Railway ha desplegado los últimos cambios
"""
import requests
import time

def check_deployment():
    """Verificar estado del deployment"""
    url = "https://drive-plus-production.up.railway.app/health"
    
    print(f"\n{'='*80}")
    print(f"Verificando estado del backend en Railway...")
    print(f"{'='*80}\n")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend está ONLINE")
            print(f"\nDetalles:")
            print(f"  Status: {data.get('status', 'unknown')}")
            print(f"  Database: {data.get('database', 'unknown')}")
            
            # Verificar si el endpoint de perfil funciona
            print(f"\n{'='*80}")
            print("Probando endpoint de perfil...")
            print(f"{'='*80}\n")
            
            test_url = "https://drive-plus-production.up.railway.app/usuarios/perfil-publico/qezequiel96"
            test_response = requests.get(test_url, timeout=10)
            
            if test_response.status_code == 200:
                print("✅ Endpoint de perfil funciona correctamente")
                print("   Los cambios han sido desplegados exitosamente")
            elif test_response.status_code == 404:
                print("⚠️  Usuario no encontrado (404)")
                print("   Esto es normal si el usuario no existe")
            elif test_response.status_code == 500:
                print("❌ Error 500 - El backend aún tiene problemas")
                print("   Posibles causas:")
                print("   1. Railway aún está desplegando los cambios")
                print("   2. Hay un error en el código que no se detectó localmente")
                print("   3. Problema con la base de datos")
                print("\n   Esperando 30 segundos y reintentando...")
                time.sleep(30)
                return check_deployment()  # Reintentar
            else:
                print(f"⚠️  Status inesperado: {test_response.status_code}")
                
        else:
            print(f"⚠️  Backend respondió con status {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - El servidor no respondió")
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - No se pudo conectar")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    check_deployment()
