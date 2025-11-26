from pydantic import BaseModel
from typing import Optional

class RankingResponse(BaseModel):
    """Schema para respuesta del ranking general"""
    posicion: int
    id_usuario: int
    nombre_usuario: str
    nombre: Optional[str] = ""
    apellido: Optional[str] = ""
    ciudad: Optional[str] = ""
    pais: Optional[str] = ""
    rating: int
    partidos_jugados: int
    partidos_ganados: Optional[int] = 0
    categoria: Optional[str] = None
    sexo: Optional[str] = None
    imagen_url: Optional[str] = None

    class Config:
        from_attributes = True

class TopWeeklyResponse(BaseModel):
    """Schema para respuesta del ranking semanal"""
    id: int
    nombre: str
    ciudad: str
    puntos: int
    imagen_url: Optional[str] = None
    rating: int

    class Config:
        from_attributes = True

class EloHistoryResponse(BaseModel):
    """Schema para respuesta del historial de rating"""
    fecha: str
    rating_anterior: int
    rating_nuevo: int
    cambio: int
    partido_id: int

    class Config:
        from_attributes = True
