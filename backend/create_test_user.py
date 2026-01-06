#!/usr/bin/env python3
"""
Script para crear un usuario de prueba en la base de datos
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.database.config import get_db, SessionLocal
from src.models.Drive+_models import Usuario, PerfilUsuario, Categoria
from src.auth.jwt_handler import JWTHandler

def create_test_user():
    """Crear un usuario de prueba completo"""
    
    # Obtener sesión de base de datos
    db = SessionLocal()
    
    try:
        # Datos del usuario de prueba
        test_user_data = {
            "nombre_usuario": "demo",
            "email": "demo@driveplus.com",
            "password": "demo123",
            "nombre": "Demo",
            "apellido": "Usuario",
            "sexo": "masculino",
            "ciudad": "Buenos Aires",
            "pais": "Argentina"
        }
        
        # Verificar si el usuario ya existe
        existing_user = db.query(Usuario).filter(Usuario.email == test_user_data["email"]).first()
        if existing_user:
            print("✅ Usuario de prueba ya existe:")
            print(f"   Email: {existing_user.email}")
            print(f"   Nombre de usuario: {existing_user.nombre_usuario}")
            print(f"   Rating: {existing_user.rating}")
            print("\n🔑 Credenciales para login:")
            print(f"   Email: {test_user_data['email']}")
            print(f"   Contraseña: {test_user_data['password']}")
            print(f"   También puedes usar: {existing_user.nombre_usuario}")
            return
        
        # Buscar una categoría inicial (ej: 7ma)
        categoria = db.query(Categoria).filter(
            Categoria.nombre == "7ma",
            Categoria.sexo == test_user_data["sexo"]
        ).first()
        
        # Si no existe la categoría, buscar cualquier categoría masculina
        if not categoria:
            categoria = db.query(Categoria).filter(
                Categoria.sexo == test_user_data["sexo"]
            ).order_by(Categoria.id_categoria.asc()).first()
        
        id_categoria_inicial = categoria.id_categoria if categoria else None
        
        # Determinar rating inicial basado en la categoría
        rating_inicial = 1000  # Rating por defecto
        if categoria:
            if categoria.rating_min is not None and categoria.rating_max is not None:
                rating_inicial = (categoria.rating_min + categoria.rating_max) // 2
            elif categoria.rating_min is not None:
                rating_inicial = categoria.rating_min + 50
            elif categoria.rating_max is not None:
                rating_inicial = categoria.rating_max - 50
        
        # Crear hash de la contraseña
        hashed_password = JWTHandler.get_password_hash(test_user_data["password"])
        
        # Crear usuario
        db_user = Usuario(
            nombre_usuario=test_user_data["nombre_usuario"],
            email=test_user_data["email"],
            password_hash=hashed_password,
            rating=rating_inicial,
            partidos_jugados=0,
            id_categoria=id_categoria_inicial,
            sexo=test_user_data["sexo"]
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
            id_categoria_inicial=id_categoria_inicial
        )
        
        db.add(db_perfil)
        db.commit()
        db.refresh(db_user)
        
        print("✅ Usuario de prueba creado exitosamente!")
        print("\n📋 Datos del usuario:")
        print(f"   Nombre: {db_perfil.nombre} {db_perfil.apellido}")
        print(f"   Email: {db_user.email}")
        print(f"   Nombre de usuario: {db_user.nombre_usuario}")
        print(f"   Rating inicial: {db_user.rating}")
        print(f"   Categoría: {categoria.nombre if categoria else 'Sin categoría'}")
        print(f"   Sexo: {db_user.sexo}")
        print("\n🔑 Credenciales para login:")
        print(f"   Email: {test_user_data['email']}")
        print(f"   O nombre de usuario: {test_user_data['nombre_usuario']}")
        print(f"   Contraseña: {test_user_data['password']}")
        print("\n💡 Puedes usar cualquiera de estos dos en el campo 'username':")
        print(f"   - Email: {test_user_data['email']}")
        print(f"   - Username: {test_user_data['nombre_usuario']}")
        
    except Exception as e:
        print(f"❌ Error al crear usuario de prueba: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creando usuario de prueba...")
    print("=" * 50)
    create_test_user()
    print("=" * 50)
