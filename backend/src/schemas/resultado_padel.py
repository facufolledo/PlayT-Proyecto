"""
Schemas para el sistema de resultados de pádel
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime


class SetSchema(BaseModel):
    """Schema para un set de pádel (normal o supertiebreak)"""
    gamesEquipoA: int = Field(..., ge=0, le=99, description="Games/Puntos del equipo A")
    gamesEquipoB: int = Field(..., ge=0, le=99, description="Games/Puntos del equipo B")
    ganador: Optional[Literal["equipoA", "equipoB"]] = None
    completado: bool = False
    esSuperTiebreak: bool = False  # Indica si es supertiebreak (a 10 puntos)
    
    @validator('gamesEquipoA', 'gamesEquipoB')
    def validar_games(cls, v):
        if v < 0 or v > 99:
            raise ValueError("Los games/puntos deben estar entre 0 y 99")
        return v


class SuperTiebreakSchema(BaseModel):
    """Schema para supertiebreak"""
    puntosEquipoA: int = Field(..., ge=0, description="Puntos del equipo A")
    puntosEquipoB: int = Field(..., ge=0, description="Puntos del equipo B")
    ganador: Optional[Literal["equipoA", "equipoB"]] = None
    completado: bool = False
    
    @validator('puntosEquipoA', 'puntosEquipoB')
    def validar_puntos(cls, v):
        if v < 0:
            raise ValueError("Los puntos no pueden ser negativos")
        return v


class ResultadoPadelSchema(BaseModel):
    """Schema completo para resultado de partido de pádel"""
    formato: Literal["best_of_3", "best_of_5"] = "best_of_3"
    sets: List[SetSchema] = Field(..., min_items=2, max_items=5)
    supertiebreak: Optional[SuperTiebreakSchema] = None
    ganador: Literal["equipoA", "equipoB"]
    completado: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "formato": "best_of_3",
                "sets": [
                    {
                        "gamesEquipoA": 6,
                        "gamesEquipoB": 4,
                        "ganador": "equipoA",
                        "completado": True
                    },
                    {
                        "gamesEquipoA": 4,
                        "gamesEquipoB": 6,
                        "ganador": "equipoB",
                        "completado": True
                    }
                ],
                "supertiebreak": {
                    "puntosEquipoA": 10,
                    "puntosEquipoB": 8,
                    "ganador": "equipoA",
                    "completado": True
                },
                "ganador": "equipoA",
                "completado": True
            }
        }


class CargarResultadoRequest(BaseModel):
    """Request para cargar resultado de partido"""
    resultado: ResultadoPadelSchema


class ConfirmacionCreate(BaseModel):
    """Request para confirmar resultado"""
    pass  # No necesita body, el usuario viene del token


class ConfirmacionRequest(BaseModel):
    """Request para confirmar resultado con ID de usuario"""
    id_usuario: int = Field(..., description="ID del usuario que confirma")


class ResultadoPadelCreate(BaseModel):
    """Schema para crear un resultado de pádel"""
    id_sala: str = Field(..., description="ID de la sala")
    id_creador: int = Field(..., description="ID del usuario creador")
    sets: List[dict] = Field(..., min_items=2, max_items=3, description="Sets del partido")
    ganador_equipo: Literal["equipo1", "equipo2"] = Field(..., description="Equipo ganador")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_sala": "abc123",
                "id_creador": 1,
                "sets": [
                    {"equipo1": 6, "equipo2": 4},
                    {"equipo1": 4, "equipo2": 6},
                    {"equipo1": 10, "equipo2": 8}
                ],
                "ganador_equipo": "equipo1"
            }
        }


class ResultadoPadelResponse(BaseModel):
    """Response de resultado de pádel"""
    id_resultado: int
    id_sala: str
    id_creador: int
    sets: List[dict]
    ganador_equipo: str
    estado: str
    confirmaciones: int
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


class ReporteCreate(BaseModel):
    """Request para reportar resultado"""
    motivo: str = Field(..., min_length=10, max_length=500, description="Motivo del reporte")


class ConfirmacionResponse(BaseModel):
    """Response de confirmación"""
    id_confirmacion: int
    id_partido: int
    id_usuario: int
    tipo: Literal["confirmacion", "reporte"]
    motivo: Optional[str] = None
    fecha: datetime
    
    class Config:
        from_attributes = True


class EstadoConfirmacionResponse(BaseModel):
    """Estado de confirmaciones de un partido"""
    total_jugadores: int = 4
    confirmaciones: int
    reportes: int
    pendientes: int
    puede_confirmar: bool
    ya_confirmo: bool
    estado: Literal["sin_resultado", "pendiente_confirmacion", "confirmado", "disputado", "auto_confirmado"]
    confirmaciones_detalle: List[ConfirmacionResponse] = []


class PartidoConResultadoResponse(BaseModel):
    """Response de partido con resultado completo"""
    id_partido: int
    fecha: datetime
    tipo: str
    resultado_padel: Optional[ResultadoPadelSchema] = None
    estado_confirmacion: str
    ganador_equipo: Optional[int] = None
    elo_aplicado: bool
    jugadores: List[dict] = []
    estado_confirmaciones: Optional[EstadoConfirmacionResponse] = None
    
    class Config:
        from_attributes = True


class VerificacionAntiTrampaResponse(BaseModel):
    """Response de verificación anti-trampa"""
    puede_jugar: bool
    partidos_jugados: int
    limite: int = 2
    combinacion_bloqueada: Optional[str] = None
    jugadores_bloqueados: Optional[List[str]] = None
    proxima_disponibilidad: Optional[datetime] = None
    mensaje: str
