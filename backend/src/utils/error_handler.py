"""
Manejador centralizado de errores para FastAPI.
Convierte excepciones de PlayT a respuestas HTTP consistentes.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

from .exceptions import PlayTException, get_http_status

logger = logging.getLogger(__name__)


async def playt_exception_handler(request: Request, exc: PlayTException) -> JSONResponse:
    """Handler para excepciones de PlayT"""
    status_code = get_http_status(exc)
    
    # Log según severidad
    if status_code >= 500:
        logger.error(f"[{exc.code}] {exc.message}", exc_info=True)
    elif status_code >= 400:
        logger.warning(f"[{exc.code}] {exc.message}")
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handler para ValueError (compatibilidad con código existente)"""
    logger.warning(f"[VALIDATION] {str(exc)}")
    
    return JSONResponse(
        status_code=400,
        content={
            "error": True,
            "code": "VALIDATION_ERROR",
            "message": str(exc),
            "details": None
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler para excepciones no manejadas"""
    logger.error(f"[UNHANDLED] {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "code": "INTERNAL_ERROR",
            "message": "Error interno del servidor",
            "details": None
        }
    )


def register_exception_handlers(app):
    """Registrar todos los handlers de excepciones en la app FastAPI"""
    app.add_exception_handler(PlayTException, playt_exception_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    # No registrar generic para no ocultar errores en desarrollo
    # app.add_exception_handler(Exception, generic_exception_handler)
