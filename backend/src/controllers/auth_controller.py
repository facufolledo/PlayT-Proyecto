from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta
import os

from ..database.config import get_db
from ..models.playt_models import Usuario, PerfilUsuario, Categoria
from ..schemas.auth import UserLogin, UserRegister, Token, UserResponse
from ..auth.jwt_handler import JWTHandler

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# OAuth2 scheme para tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario"""
    
    # Verificar si el email ya existe
    existing_user = db.query(Usuario).filter(Usuario.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Verificar si el nombre de usuario ya existe
    existing_username = db.query(Usuario).filter(Usuario.nombre_usuario == user_data.nombre_usuario).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso"
        )
    
    try:
        # Crear hash de la contraseña
        hashed_password = JWTHandler.get_password_hash(user_data.password)
        
        # Determinar rating inicial basado en la categoría
        rating_inicial = 1000  # Rating por defecto
        
        if user_data.id_categoria_inicial:
            # Buscar la categoría para obtener el rating inicial
            categoria = db.query(Categoria).filter(Categoria.id_categoria == user_data.id_categoria_inicial).first()
            if categoria:
                # Calcular rating promedio de la categoría
                if categoria.rating_min is not None and categoria.rating_max is not None:
                    rating_inicial = (categoria.rating_min + categoria.rating_max) // 2
                elif categoria.rating_min is not None:
                    # Para categorías como "Libre" (1500+)
                    rating_inicial = categoria.rating_min + 50
                elif categoria.rating_max is not None:
                    # Para categorías como "8va" (0-899)
                    rating_inicial = categoria.rating_max - 50
                else:
                    rating_inicial = 1000  # Fallback
        
        # Crear usuario
        db_user = Usuario(
            nombre_usuario=user_data.nombre_usuario,
            email=user_data.email,
            password_hash=hashed_password,
            rating=rating_inicial,  # Rating basado en categoría
            partidos_jugados=0,
            id_categoria=user_data.id_categoria_inicial,  # Asignar categoría inicial
            sexo=user_data.sexo  # Agregar campo sexo
        )
        
        db.add(db_user)
        db.flush()  # Para obtener el ID del usuario
        
        # Crear perfil de usuario
        db_perfil = PerfilUsuario(
            id_usuario=db_user.id_usuario,
            nombre=user_data.nombre,
            apellido=user_data.apellido,
            ciudad=user_data.ciudad,
            pais=user_data.pais,
            id_categoria_inicial=user_data.id_categoria_inicial  # Guardar categoría inicial
        )
        
        db.add(db_perfil)
        db.commit()
        db.refresh(db_user)
        
        # Retornar usuario creado
        return UserResponse(
            id_usuario=db_user.id_usuario,
            nombre_usuario=db_user.nombre_usuario,
            email=db_user.email,
            nombre=db_perfil.nombre,
            apellido=db_perfil.apellido,
            sexo=db_user.sexo,
            ciudad=db_perfil.ciudad,
            pais=db_perfil.pais,
            rating=db_user.rating,
            partidos_jugados=db_user.partidos_jugados,
            id_categoria=db_user.id_categoria
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Iniciar sesión (OAuth2 Password Flow).
    Swagger mandará form-data con fields: username, password.
    Usamos 'username' como email o nombre de usuario para autenticar.
    """
    # Buscar usuario por email o nombre de usuario
    user = db.query(Usuario).filter(
        (Usuario.email == form_data.username) | (Usuario.nombre_usuario == form_data.username)
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/nombre de usuario o contraseña incorrectos"
        )

    # Verificar contraseña
    if not JWTHandler.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )

    # Crear token
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
    access_token = JWTHandler.create_access_token(
        data={"sub": str(user.id_usuario), "email": user.email},
        expires_delta=access_token_expires
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds())
    )

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Obtener usuario actual desde el token"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = JWTHandler.verify_token(token)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    user = db.query(Usuario).filter(Usuario.id_usuario == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user

@router.get("/categorias")
async def get_categorias(db: Session = Depends(get_db)):
    """Obtener todas las categorías disponibles para el registro"""
    categorias = db.query(Categoria).order_by(Categoria.id_categoria.asc()).all()
    return [
        {
            "id_categoria": cat.id_categoria,
            "nombre": cat.nombre,
            "descripcion": cat.descripcion,
            "rating_min": cat.rating_min,
            "rating_max": cat.rating_max
        }
        for cat in categorias
    ]

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obtener información del usuario actual"""
    
    # Obtener perfil del usuario
    perfil = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == current_user.id_usuario).first()
    
    if not perfil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de usuario no encontrado"
        )
    
    return UserResponse(
        id_usuario=current_user.id_usuario,
        nombre_usuario=current_user.nombre_usuario,
        email=current_user.email,
        nombre=perfil.nombre,
        apellido=perfil.apellido,
        ciudad=perfil.ciudad,
        pais=perfil.pais,
        rating=current_user.rating,
        partidos_jugados=current_user.partidos_jugados,
        id_categoria=current_user.id_categoria
    )
