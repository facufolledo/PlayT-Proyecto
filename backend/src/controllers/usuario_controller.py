from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from ..database.config import get_db
from ..models.playt_models import Usuario, PerfilUsuario, Categoria
from ..schemas.auth import UserResponse
from ..auth.auth_utils import get_current_user
from ..auth.firebase_handler import FirebaseHandler

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
security = HTTPBearer()


class CompletarPerfilRequest(BaseModel):
    nombre: str
    apellido: str
    dni: str
    fecha_nacimiento: str  # formato: YYYY-MM-DD
    genero: str  # 'masculino' o 'femenino'
    categoria_inicial: str  # '8va', '7ma', '6ta', '5ta', '4ta', 'Libre'
    mano_habil: Optional[str] = None  # 'derecha' o 'zurda'
    posicion_preferida: Optional[str] = None  # 'drive', 'reves', 'indiferente'
    telefono: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None


@router.post("/completar-perfil", response_model=UserResponse)
async def completar_perfil(
    datos: CompletarPerfilRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Completar el perfil de un usuario que se registró con Firebase
    Si el usuario no existe, lo crea primero
    """
    try:
        # Verificar token de Firebase
        token = credentials.credentials
        firebase_payload = FirebaseHandler.verify_token(token)
        
        if not firebase_payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de Firebase inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        firebase_email = firebase_payload.get("firebase_email")
        email_verified = firebase_payload.get("email_verified", False)
        
        if not firebase_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de Firebase inválido: email no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verificar que el email esté verificado
        if not email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Debes verificar tu correo electrónico antes de continuar. Revisa tu bandeja de entrada.",
            )
        
        # Buscar o crear usuario
        current_user = db.query(Usuario).filter(Usuario.email == firebase_email).first()
        
        if not current_user:
            # Crear nuevo usuario
            # Generar nombre de usuario único basado en email
            email_base = firebase_email.split('@')[0]
            nombre_usuario = email_base
            contador = 1
            while db.query(Usuario).filter(Usuario.nombre_usuario == nombre_usuario).first():
                nombre_usuario = f"{email_base}{contador}"
                contador += 1
            
            current_user = Usuario(
                nombre_usuario=nombre_usuario,
                email=firebase_email,
                password_hash="",  # No se usa para usuarios de Firebase
                rating=1000,  # Se actualizará según categoría
                partidos_jugados=0
            )
            db.add(current_user)
            db.flush()  # Para obtener el ID
        # Mapear género a formato de base de datos
        sexo = 'M' if datos.genero == 'masculino' else 'F'
        
        # Buscar categoría por nombre
        categoria = db.query(Categoria).filter(Categoria.nombre == datos.categoria_inicial).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Categoría '{datos.categoria_inicial}' no encontrada"
            )
        
        # Calcular rating inicial basado en la categoría
        rating_inicial = 1000  # Rating por defecto
        if categoria.rating_min is not None and categoria.rating_max is not None:
            rating_inicial = (categoria.rating_min + categoria.rating_max) // 2
        elif categoria.rating_min is not None:
            rating_inicial = categoria.rating_min + 50
        elif categoria.rating_max is not None:
            rating_inicial = categoria.rating_max - 50
        
        # Actualizar usuario
        current_user.sexo = sexo
        current_user.id_categoria = categoria.id_categoria
        current_user.rating = rating_inicial
        
        # Buscar o crear perfil
        perfil = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == current_user.id_usuario).first()
        
        if perfil:
            # Actualizar perfil existente
            perfil.nombre = datos.nombre
            perfil.apellido = datos.apellido
            perfil.dni = datos.dni
            perfil.fecha_nacimiento = datetime.strptime(datos.fecha_nacimiento, '%Y-%m-%d').date()
            perfil.ciudad = datos.ciudad or perfil.ciudad
            perfil.pais = datos.pais or perfil.pais or "Argentina"
            perfil.telefono = datos.telefono
            perfil.id_categoria_inicial = categoria.id_categoria
            perfil.mano_habil = datos.mano_habil
            perfil.posicion_preferida = datos.posicion_preferida
        else:
            # Crear nuevo perfil
            perfil = PerfilUsuario(
                id_usuario=current_user.id_usuario,
                nombre=datos.nombre,
                apellido=datos.apellido,
                dni=datos.dni,
                fecha_nacimiento=datetime.strptime(datos.fecha_nacimiento, '%Y-%m-%d').date(),
                ciudad=datos.ciudad,
                pais=datos.pais or "Argentina",
                telefono=datos.telefono,
                id_categoria_inicial=categoria.id_categoria,
                mano_habil=datos.mano_habil,
                posicion_preferida=datos.posicion_preferida
            )
            db.add(perfil)
        
        db.commit()
        db.refresh(current_user)
        db.refresh(perfil)
        
        return UserResponse(
            id_usuario=current_user.id_usuario,
            nombre_usuario=current_user.nombre_usuario,
            email=current_user.email,
            nombre=perfil.nombre,
            apellido=perfil.apellido,
            sexo=current_user.sexo,
            ciudad=perfil.ciudad,
            pais=perfil.pais,
            rating=current_user.rating,
            partidos_jugados=current_user.partidos_jugados,
            id_categoria=current_user.id_categoria
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de fecha inválido: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al completar perfil: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_usuario_actual(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener información del usuario actual
    """
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
        sexo=current_user.sexo,
        ciudad=perfil.ciudad,
        pais=perfil.pais,
        rating=current_user.rating,
        partidos_jugados=current_user.partidos_jugados,
        id_categoria=current_user.id_categoria
    )


class FCMTokenRequest(BaseModel):
    fcm_token: str


@router.post("/fcm-token")
async def registrar_fcm_token(
    datos: FCMTokenRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registrar o actualizar el token FCM del usuario para notificaciones push
    """
    try:
        current_user.fcm_token = datos.fcm_token
        db.commit()
        
        return {
            "success": True,
            "message": "Token FCM registrado exitosamente"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar token FCM: {str(e)}"
        )
