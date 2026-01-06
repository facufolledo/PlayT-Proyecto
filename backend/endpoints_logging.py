# Endpoints necesarios para el sistema de logging del frontend

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

router = APIRouter(prefix="/logs", tags=["logging"])

class LogEntry(BaseModel):
    timestamp: str
    level: str  # DEBUG, INFO, WARN, ERROR
    message: str
    data: Optional[Dict[str, Any]] = None
    userId: Optional[str] = None
    sessionId: str
    url: str
    userAgent: str

class ClientLogsRequest(BaseModel):
    logs: List[LogEntry]
    sessionId: str

@router.post("/client")
async def receive_client_logs(
    request: ClientLogsRequest,
    current_user = Depends(get_current_user_optional)  # Opcional porque puede no estar logueado
):
    """
    Recibir logs del cliente para análisis y debugging
    """
    try:
        # Procesar logs (guardar en base de datos, enviar a servicio de logging, etc.)
        for log in request.logs:
            # Aquí puedes guardar en BD, enviar a CloudWatch, etc.
            print(f"[CLIENT LOG] {log.level}: {log.message}")
            
            # Si es un error crítico, podrías enviar notificación
            if log.level == "ERROR":
                # Enviar a sistema de alertas
                pass
        
        return {"status": "success", "processed": len(request.logs)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing logs: {str(e)}")

@router.post("/error")
async def receive_error_log(
    log: LogEntry,
    current_user = Depends(get_current_user_optional)
):
    """
    Recibir errores críticos del cliente inmediatamente
    """
    try:
        # Procesar error crítico
        print(f"[CRITICAL ERROR] {log.message}")
        
        # Aquí podrías:
        # - Guardar en tabla de errores críticos
        # - Enviar notificación a Slack/Discord
        # - Crear ticket automático
        
        return {"status": "error_logged"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging error: {str(e)}")

# Función helper que necesitas importar/crear
def get_current_user_optional():
    """
    Versión opcional de get_current_user que no falla si no hay token
    """
    # Implementar lógica similar a get_current_user pero que retorne None si no hay token
    pass
