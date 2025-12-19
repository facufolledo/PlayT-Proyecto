from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SalaCreate(BaseModel):
    """Esquema para crear una sala"""
    nombre: str
    fecha: datetime
    max_jugadores: int = 4

class SalaResponse(BaseModel):
    """Esquema para respuesta de sala"""
    id_sala: str
    nombre: str
    fecha: datetime
    estado: str  # "esperando", "en_juego", "finalizada"
    codigo_invitacion: str
    id_creador: int
    jugadores_actuales: int
    max_jugadores: int
    creado_en: datetime
    
    class Config:
        from_attributes = True

class SalaJoin(BaseModel):
    """Esquema para unirse a una sala"""
    codigo_invitacion: str

class SalaCompleta(SalaResponse):
    """Esquema para sala completa con jugadores"""
    jugadores: List[dict] = []
    equipos: Optional[dict] = None
    resultado: Optional[dict] = None
    estado_confirmacion: Optional[str] = None
    cambios_elo: Optional[List[dict]] = None
    elo_aplicado: Optional[bool] = False
    usuarios_confirmados: Optional[List[int]] = []  # IDs de usuarios que ya confirmaron
