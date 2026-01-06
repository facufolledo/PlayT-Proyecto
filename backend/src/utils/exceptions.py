"""
Excepciones personalizadas para Drive+.
Permiten manejo consistente de errores en toda la aplicación.
"""
from typing import Optional, Any


class Drive+Exception(Exception):
    """Excepción base para todas las excepciones de Drive+"""
    
    def __init__(self, message: str, code: str = "Drive+_ERROR", details: Optional[Any] = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


# ============ Errores de Negocio (400) ============

class BusinessError(Drive+Exception):
    """Error de lógica de negocio - HTTP 400"""
    pass


class ValidationError(BusinessError):
    """Error de validación de datos"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, code="VALIDATION_ERROR", details={"field": field})


class DuplicateError(BusinessError):
    """Recurso duplicado"""
    
    def __init__(self, message: str = "El recurso ya existe"):
        super().__init__(message, code="DUPLICATE_ERROR")


class InvalidStateError(BusinessError):
    """Estado inválido para la operación"""
    
    def __init__(self, message: str, current_state: Optional[str] = None):
        super().__init__(message, code="INVALID_STATE", details={"current_state": current_state})


class LimitExceededError(BusinessError):
    """Límite excedido (anti-trampa, inscripciones, etc.)"""
    
    def __init__(self, message: str, limit: Optional[int] = None):
        super().__init__(message, code="LIMIT_EXCEEDED", details={"limit": limit})


# ============ Errores de Autenticación (401) ============

class AuthenticationError(Drive+Exception):
    """Error de autenticación - HTTP 401"""
    
    def __init__(self, message: str = "No autenticado"):
        super().__init__(message, code="AUTH_ERROR")


class TokenExpiredError(AuthenticationError):
    """Token expirado"""
    
    def __init__(self):
        super().__init__("Token expirado")
        self.code = "TOKEN_EXPIRED"


class InvalidTokenError(AuthenticationError):
    """Token inválido"""
    
    def __init__(self):
        super().__init__("Token inválido")
        self.code = "INVALID_TOKEN"


# ============ Errores de Autorización (403) ============

class AuthorizationError(Drive+Exception):
    """Error de autorización - HTTP 403"""
    
    def __init__(self, message: str = "No tienes permiso para esta acción"):
        super().__init__(message, code="FORBIDDEN")


class NotOwnerError(AuthorizationError):
    """No es el dueño del recurso"""
    
    def __init__(self, resource: str = "recurso"):
        super().__init__(f"No eres el dueño de este {resource}")
        self.code = "NOT_OWNER"


class NotParticipantError(AuthorizationError):
    """No es participante"""
    
    def __init__(self, message: str = "No eres participante"):
        super().__init__(message)
        self.code = "NOT_PARTICIPANT"


# ============ Errores de Recurso (404) ============

class NotFoundError(Drive+Exception):
    """Recurso no encontrado - HTTP 404"""
    
    def __init__(self, resource: str = "Recurso", id: Optional[Any] = None):
        message = f"{resource} no encontrado"
        if id:
            message = f"{resource} con ID {id} no encontrado"
        super().__init__(message, code="NOT_FOUND", details={"resource": resource, "id": id})


class UserNotFoundError(NotFoundError):
    """Usuario no encontrado"""
    
    def __init__(self, user_id: Optional[int] = None):
        super().__init__("Usuario", user_id)


class PartidoNotFoundError(NotFoundError):
    """Partido no encontrado"""
    
    def __init__(self, partido_id: Optional[int] = None):
        super().__init__("Partido", partido_id)


class SalaNotFoundError(NotFoundError):
    """Sala no encontrada"""
    
    def __init__(self, sala_id: Optional[str] = None):
        super().__init__("Sala", sala_id)


class TorneoNotFoundError(NotFoundError):
    """Torneo no encontrado"""
    
    def __init__(self, torneo_id: Optional[int] = None):
        super().__init__("Torneo", torneo_id)


# ============ Errores de Conflicto (409) ============

class ConflictError(Drive+Exception):
    """Conflicto con el estado actual - HTTP 409"""
    
    def __init__(self, message: str):
        super().__init__(message, code="CONFLICT")


class AlreadyConfirmedError(ConflictError):
    """Ya confirmado"""
    
    def __init__(self):
        super().__init__("Ya confirmaste este resultado")
        self.code = "ALREADY_CONFIRMED"


class AlreadyInscribedError(ConflictError):
    """Ya inscrito"""
    
    def __init__(self):
        super().__init__("Ya estás inscrito en este torneo")
        self.code = "ALREADY_INSCRIBED"


# ============ Mapeo a HTTP Status Codes ============

def get_http_status(exception: Drive+Exception) -> int:
    """Obtener código HTTP para una excepción"""
    if isinstance(exception, NotFoundError):
        return 404
    elif isinstance(exception, AuthorizationError):
        return 403
    elif isinstance(exception, AuthenticationError):
        return 401
    elif isinstance(exception, ConflictError):
        return 409
    elif isinstance(exception, BusinessError):
        return 400
    else:
        return 500
