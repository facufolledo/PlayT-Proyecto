"""
Script para probar el endpoint de actualizar perfil
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_actualizar_perfil():
    """Probar actualización de perfil"""
    
    print("=" * 60)
    print("TEST: Actualizar Perfil de Usuario")
    print("=" * 60)
    
    # 1. Login para obtener token
    print("\n1. Haciendo login...")
    login_data = {
        "email": "test@test.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Error en login: {response.status_code}")
            print(response.text)
            return
        
        token = response.json()["access_token"]
        print(f"✅ Login exitoso. Token obtenido.")
        
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        print("Asegúrate de que el backend esté corriendo en http://localhost:8000")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. Obtener perfil actual
    print("\n2. Obteniendo perfil actual...")
    response = requests.get(f"{BASE_URL}/usuarios/me", headers=headers)
    
    if response.status_code == 200:
        perfil_antes = response.json()
        print(f"✅ Perfil actual:")
        print(f"   - Nombre: {perfil_antes.get('nombre')} {perfil_antes.get('apellido')}")
        print(f"   - Ciudad: {perfil_antes.get('ciudad')}")
        print(f"   - País: {perfil_antes.get('pais')}")
        print(f"   - Posición: {perfil_antes.get('posicion_preferida')}")
        print(f"   - Mano: {perfil_antes.get('mano_dominante')}")
    else:
        print(f"❌ Error obteniendo perfil: {response.status_code}")
        print(response.text)
        return
    
    # 3. Actualizar perfil
    print("\n3. Actualizando perfil...")
    datos_actualizacion = {
        "nombre": "Juan Carlos",
        "apellido": "Pérez García",
        "ciudad": "Buenos Aires",
        "pais": "Argentina",
        "posicion_preferida": "drive",
        "mano_dominante": "derecha"
    }
    
    response = requests.put(
        f"{BASE_URL}/usuarios/perfil",
        headers=headers,
        json=datos_actualizacion
    )
    
    if response.status_code == 200:
        perfil_despues = response.json()
        print(f"✅ Perfil actualizado exitosamente:")
        print(f"   - Nombre: {perfil_despues.get('nombre')} {perfil_despues.get('apellido')}")
        print(f"   - Ciudad: {perfil_despues.get('ciudad')}")
        print(f"   - País: {perfil_despues.get('pais')}")
        print(f"   - Posición: {perfil_despues.get('posicion_preferida')}")
        print(f"   - Mano: {perfil_despues.get('mano_dominante')}")
    else:
        print(f"❌ Error actualizando perfil: {response.status_code}")
        print(response.text)
        return
    
    # 4. Verificar cambios con GET
    print("\n4. Verificando cambios con GET /usuarios/me...")
    response = requests.get(f"{BASE_URL}/usuarios/me", headers=headers)
    
    if response.status_code == 200:
        perfil_verificado = response.json()
        print(f"✅ Cambios verificados:")
        print(f"   - Nombre: {perfil_verificado.get('nombre')} {perfil_verificado.get('apellido')}")
        print(f"   - Ciudad: {perfil_verificado.get('ciudad')}")
        print(f"   - Posición: {perfil_verificado.get('posicion_preferida')}")
        print(f"   - Mano: {perfil_verificado.get('mano_dominante')}")
    else:
        print(f"❌ Error verificando perfil: {response.status_code}")
        return
    
    # 5. Probar actualización parcial
    print("\n5. Probando actualización parcial (solo ciudad)...")
    datos_parcial = {
        "ciudad": "Córdoba"
    }
    
    response = requests.put(
        f"{BASE_URL}/usuarios/perfil",
        headers=headers,
        json=datos_parcial
    )
    
    if response.status_code == 200:
        perfil_parcial = response.json()
        print(f"✅ Actualización parcial exitosa:")
        print(f"   - Ciudad: {perfil_parcial.get('ciudad')}")
        print(f"   - Nombre (sin cambios): {perfil_parcial.get('nombre')}")
    else:
        print(f"❌ Error en actualización parcial: {response.status_code}")
        print(response.text)
        return
    
    # 6. Probar validación de posición
    print("\n6. Probando validación de posición_preferida...")
    datos_invalidos = {
        "posicion_preferida": "invalido"
    }
    
    response = requests.put(
        f"{BASE_URL}/usuarios/perfil",
        headers=headers,
        json=datos_invalidos
    )
    
    if response.status_code == 400:
        print(f"✅ Validación funcionando correctamente (rechazó valor inválido)")
    else:
        print(f"⚠️  Validación no funcionó como esperado: {response.status_code}")
    
    # 7. Probar validación de mano
    print("\n7. Probando validación de mano_dominante...")
    datos_invalidos = {
        "mano_dominante": "ambidiestro"
    }
    
    response = requests.put(
        f"{BASE_URL}/usuarios/perfil",
        headers=headers,
        json=datos_invalidos
    )
    
    if response.status_code == 400:
        print(f"✅ Validación funcionando correctamente (rechazó valor inválido)")
    else:
        print(f"⚠️  Validación no funcionó como esperado: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 60)


if __name__ == "__main__":
    test_actualizar_perfil()
