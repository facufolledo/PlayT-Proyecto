from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class PartidoBase(BaseModel):
    """Esquema base para partido"""
    fecha: datetime
    id_club: Optional[int] = None

class PartidoCreate(PartidoBase):
    """Esquema para crear partido"""
    jugadores: List[int]  # Lista de IDs de usuarios
    equipos: List[int]    # Lista de equipos (1 o 2) para cada jugador

class PartidoUpdate(BaseModel):
    """Esquema para actualizar partido"""
    fecha: Optional[datetime] = None
    estado: Optional[str] = None
    id_club: Optional[int] = None

class PartidoResponse(PartidoBase):
    """Esquema para respuesta de partido"""
    id_partido: int
    estado: str
    id_creador: int
    creado_en: datetime
    jugadores: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True

class ResultadoBase(BaseModel):
    """Esquema base para resultado"""
    sets_eq1: int
    sets_eq2: int
    detalle_sets: List[Dict[str, Any]]  # JSON con detalles de cada set

class ResultadoCreate(ResultadoBase):
    """Esquema para crear resultado"""
    desenlace: Optional[str] = "normal"

class ResultadoResponse(ResultadoBase):
    """Esquema para respuesta de resultado"""
    id_partido: int
    id_reportador: int
    confirmado: bool
    desenlace: str
    creado_en: datetime
    
    class Config:
        from_attributes = True

class HistorialRatingResponse(BaseModel):
    """Esquema para historial de rating"""
    rating_antes: int
    delta: int
    rating_despues: int
    
    class Config:
        from_attributes = True

class PartidoCompleto(PartidoResponse):
    """Esquema para partido completo con resultado"""
    resultado: Optional[ResultadoResponse] = None
    club: Optional[Dict[str, Any]] = None
    creador: Dict[str, Any] = {}
    historial_rating: Optional[HistorialRatingResponse] = None
