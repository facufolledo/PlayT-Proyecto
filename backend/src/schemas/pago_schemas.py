"""
Schemas para sistema de pagos en torneos
"""
from pydantic import BaseModel
from typing import Optional

class SubirComprobanteRequest(BaseModel):
    """Request para subir comprobante de pago"""
    comprobante_url: str
    
class VerificarPagoRequest(BaseModel):
    """Request para verificar/rechazar pago"""
    aprobado: bool
    motivo_rechazo: Optional[str] = None

class CambiarCompaneroRequest(BaseModel):
    """Request para cambiar de compañero"""
    nuevo_jugador2_id: int
    motivo: Optional[str] = None

class ActualizarDisponibilidadRequest(BaseModel):
    """Request para actualizar disponibilidad horaria"""
    disponibilidad_horaria: dict  # JSON con formato: {"lunes": ["08:00-10:00"], ...}

class DatosPagoResponse(BaseModel):
    """Response con datos de pago del torneo"""
    requiere_pago: bool
    monto_inscripcion: Optional[float] = None
    alias_cbu_cvu: Optional[str] = None
    titular_cuenta: Optional[str] = None
    banco: Optional[str] = None

class EstadoPagoResponse(BaseModel):
    """Response con estado de pago de una pareja"""
    pareja_id: int
    pago_estado: str
    pago_monto: Optional[float] = None
    pago_comprobante_url: Optional[str] = None
    pago_fecha_acreditacion: Optional[str] = None
    motivo_rechazo_pago: Optional[str] = None
