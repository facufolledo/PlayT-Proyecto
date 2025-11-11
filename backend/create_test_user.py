#!/usr/bin/env python3
"""
Script para crear un usuario de prueba en la base de datos
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy.orm import Session
from src.database.config import get_db
from src.models.playt_models import Usuario, PerfilUsuario
from src.auth.jwt_handler import JWTHandler

def create_test_user():
    """Crear un usuario de prueba"""
    
    # Datos del usuario de prueba
    test_user_data = {
        "nombre_usuario": "testuser",
        "email": "test@example.com",
        "password": "test123",
        "nombre": "Usuario",
        "apellido": "Prueba",
        "ciudad": "Buenos Aires",
        "pais": "Argentina"
    }
    
    try:
        # Obtener sesión de base de datos
        db = next(get_db())
        
        # Verificar si el usuario ya existe
        existing_user = db.query(Usuario).filter(Usuario.email == test_user_data["email"]).first()
        if existing_user:
            print("✅ Usuario de prueba ya existe:")
            print(f"   Email: {existing_user.email}")
            print(f"   Nombre de usuario: {existing_user.nombre_usuario}")
            print(f"   Rating: {existing_user.rating}")
            return
        
        # Crear hash de la contraseña
        hashed_password = JWTHandler.get_password_hash(test_user_data["password"])
        
        # Crear usuario
        db_user = Usuario(
            nombre_usuario=test_user_data["nombre_usuario"],
            email=test_user_data["email"],
            password_hash=hashed_password,
            rating=1000,  # Rating inicial
            partidos_jugados=0,
            id_categoria=None  # Sin categoría inicial
        )
        
        db.add(db_user)
        db.flush()  # Para obtener el ID del usuario
        
        # Crear perfil de usuario
        db_perfil = PerfilUsuario(
            id_usuario=db_user.id_usuario,
            nombre=test_user_data["nombre"],
            apellido=test_user_data["apellido"],
            ciudad=test_user_data["ciudad"],
            pais=test_user_data["pais"],
            id_categoria_inicial=None
        )
        
        db.add(db_perfil)
        db.commit()
        db.refresh(db_user)
        
        print("✅ Usuario de prueba creado exitosamente:")
        print(f"   Email: {db_user.email}")
        print(f"   Nombre de usuario: {db_user.nombre_usuario}")
        print(f"   Contraseña: {test_user_data['password']}")
        print(f"   Rating inicial: {db_user.rating}")
        print("\n🔑 Credenciales para login:")
        print(f"   Email: {test_user_data['email']}")
        print(f"   Contraseña: {test_user_data['password']}")
        
    except Exception as e:
        print(f"❌ Error al crear usuario de prueba: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creando usuario de prueba...")
    create_test_user()

