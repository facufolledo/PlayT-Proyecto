"""
Controller para recibir logs del cliente (frontend)
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/logs", tags=["Logs"])


class ClientLogRequest(BaseModel):
    level: str  # 'info', 'warn', 'error', 'debug'
    message: str
    context: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    userAgent: Optional[str] = None
    url: Optional[str] = None


class ErrorLogRequest(BaseModel):
    error: str
    stack: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    userAgent: Optional[str] = None
    url: Optional[str] = None
    userId: Optional[int] = None


@router.post("/client")
async def log_client(log: ClientLogRequest, request: Request):
    """
    Recibe logs del cliente para monitoreo
    En producción, estos logs podrían guardarse en un servicio de logging
    """
    # Por ahora solo logueamos en consola del servidor
    # En producción podrías enviar a CloudWatch, Datadog, etc.
    client_ip = request.client.host if request.client else "unknown"
    
    print(f"[CLIENT LOG] [{log.level.upper()}] {log.message}")
    if log.context:
        print(f"  Context: {log.context}")
    if log.url:
        print(f"  URL: {log.url}")
    print(f"  IP: {client_ip}")
    
    return {"status": "logged", "timestamp": datetime.now().isoformat()}


@router.post("/error")
async def log_error(error_log: ErrorLogRequest, request: Request):
    """
    Recibe errores del cliente para monitoreo
    """
    client_ip = request.client.host if request.client else "unknown"
    
    print(f"[CLIENT ERROR] {error_log.error}")
    if error_log.stack:
        print(f"  Stack: {error_log.stack[:500]}...")  # Limitar stack trace
    if error_log.context:
        print(f"  Context: {error_log.context}")
    if error_log.url:
        print(f"  URL: {error_log.url}")
    if error_log.userId:
        print(f"  User ID: {error_log.userId}")
    print(f"  IP: {client_ip}")
    
    return {"status": "error_logged", "timestamp": datetime.now().isoformat()}
