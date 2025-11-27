from pydantic import BaseModel, EmailStr
from typing import Optional

class FirebaseAuthRequest(BaseModel):
    """Esquema para autenticación con Firebase"""
    firebase_token: str

class UserLogin(BaseModel):
    """Esquema para login de usuario"""
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    """Esquema para registro de usuario"""
    nombre_usuario: str
    email: EmailStr
    password: str
    nombre: str
    apellido: str
    sexo: str  # "masculino" o "femenino"
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    id_categoria_inicial: Optional[int] = None  

class Token(BaseModel):
    """Esquema para respuesta de token"""
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    """Esquema para datos del token"""
    id_usuario: Optional[int] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    """Esquema para respuesta de usuario"""
    id_usuario: int
    nombre_usuario: str
    email: str
    nombre: str
    apellido: str
    sexo: str
    ciudad: Optional[str]
    pais: Optional[str]
    rating: int
    partidos_jugados: int
    id_categoria: Optional[int]
    posicion_preferida: Optional[str] = None
    mano_dominante: Optional[str] = None
    foto_perfil: Optional[str] = None
    dni: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    telefono: Optional[str] = None
    
    class Config:
        from_attributes = True
