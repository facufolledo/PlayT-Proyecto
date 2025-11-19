"""
WebSocket Controller para actualizaciones en tiempo real de salas
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import logging

from ..database.config import get_db
from ..models.sala import Sala
from ..websocket.connection_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/salas/{sala_id}")
async def websocket_sala_endpoint(
    websocket: WebSocket,
    sala_id: int,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint para actualizaciones en tiempo real de una sala
    
    Eventos que se envían:
    - jugador_unido: Cuando un jugador se une
    - equipos_asignados: Cuando se asignan los equipos
    - partido_iniciado: Cuando inicia el partido
    - marcador_actualizado: Cuando cambia el marcador
    - resultado_reportado: Cuando se reporta el resultado
    - resultado_confirmado: Cuando se confirma el resultado
    """
    sala_id_str = str(sala_id)
    
    # Verificar que la sala existe
    sala = db.query(Sala).filter(Sala.id_sala == sala_id).first()
    if not sala:
        await websocket.close(code=4004, reason="Sala no encontrada")
        return
    
    # Conectar el cliente
    await manager.connect(websocket, sala_id_str)
    
    try:
        # Enviar estado inicial de la sala
        await manager.send_personal_message({
            "type": "connected",
            "message": f"Conectado a sala {sala_id}",
            "sala_id": sala_id
        }, websocket)
        
        # Mantener la conexión abierta y escuchar mensajes
        while True:
            # Recibir mensajes del cliente (opcional, para ping/pong)
            data = await websocket.receive_text()
            
            # Responder a ping
            if data == "ping":
                await manager.send_personal_message({
                    "type": "pong"
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, sala_id_str)
        logger.info(f"Cliente desconectado de sala {sala_id}")
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        manager.disconnect(websocket, sala_id_str)
