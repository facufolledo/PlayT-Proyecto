from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from .jwt_handler import JWTHandler
from .firebase_handler import FirebaseHandler
from ..database.config import get_db
from ..models.driveplus_models import Usuario

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Obtener usuario actual desde token JWT o Firebase token
    Soporta ambos sistemas de autenticación
    """
    
    token = credentials.credentials
    
    # Intentar primero con JWT tradicional
    payload = JWTHandler.verify_token(token)
    user_id = None
    
    if payload:
        # Es un token JWT tradicional
        user_id = payload.get("sub")
        if isinstance(user_id, str):
            try:
                user_id = int(user_id)
            except ValueError:
                user_id = None
    else:
        # Intentar con Firebase token
        firebase_payload = FirebaseHandler.verify_token(token)
        
        if firebase_payload:
            # Es un token de Firebase
            firebase_email = firebase_payload.get("firebase_email")
            
            if firebase_email:
                # Buscar usuario por email (Firebase)
                user = db.query(Usuario).filter(Usuario.email == firebase_email).first()
                if user:
                    return user
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Usuario no encontrado. Por favor, completa tu perfil primero.",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token de Firebase inválido: email no encontrado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    
    # Validación para tokens JWT tradicionales
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[Usuario]:
    """
    Obtener usuario actual de forma opcional (para endpoints públicos)
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
