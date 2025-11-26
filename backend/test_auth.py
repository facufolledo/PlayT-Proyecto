#!/usr/bin/env python3
"""
Script para probar la autenticación sin iniciar el servidor completo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth.jwt_handler import JWTHandler
from passlib.context import CryptContext

def test_bcrypt():
    """Probar que bcrypt funciona correctamente"""
    print("🔐 Probando bcrypt...")
    
    try:
        # Crear contexto de contraseñas
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Probar hash y verificación
        password = "test_password_123"
        hashed = pwd_context.hash(password)
        print(f"✅ Hash generado: {hashed[:50]}...")
        
        # Verificar contraseña
        is_valid = pwd_context.verify(password, hashed)
        print(f"✅ Verificación: {'Correcta' if is_valid else 'Incorrecta'}")
        
        # Probar con JWT Handler
        jwt_hash = JWTHandler.get_password_hash(password)
        jwt_verify = JWTHandler.verify_password(password, jwt_hash)
        print(f"✅ JWT Handler: {'Funcionando' if jwt_verify else 'Error'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con bcrypt: {e}")
        return False

def test_jwt():
    """Probar que JWT funciona correctamente"""
    print("\n🎫 Probando JWT...")
    
    try:
        # Crear token
        data = {"sub": "123", "email": "test@example.com"}
        token = JWTHandler.create_access_token(data)
        print(f"✅ Token creado: {token[:50]}...")
        
        # Verificar token
        payload = JWTHandler.verify_token(token)
        print(f"✅ Token verificado: {payload}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error con JWT: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de autenticación...\n")
    
    bcrypt_ok = test_bcrypt()
    jwt_ok = test_jwt()
    
    if bcrypt_ok and jwt_ok:
        print("\n✅ Todas las pruebas pasaron! La autenticación debería funcionar.")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa las dependencias.")

