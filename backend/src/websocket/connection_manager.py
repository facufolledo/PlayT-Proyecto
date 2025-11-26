"""
WebSocket Connection Manager para actualizaciones en tiempo real
"""
from typing import Dict, List
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # Diccionario de salas activas: {sala_id: [websockets]}
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, sala_id: str):
        """Conectar un cliente a una sala específica"""
        await websocket.accept()
        
        if sala_id not in self.active_connections:
            self.active_connections[sala_id] = []
        
        self.active_connections[sala_id].append(websocket)
        logger.info(f"Cliente conectado a sala {sala_id}. Total: {len(self.active_connections[sala_id])}")

    def disconnect(self, websocket: WebSocket, sala_id: str):
        """Desconectar un cliente de una sala"""
        if sala_id in self.active_connections:
            if websocket in self.active_connections[sala_id]:
                self.active_connections[sala_id].remove(websocket)
                logger.info(f"Cliente desconectado de sala {sala_id}. Restantes: {len(self.active_connections[sala_id])}")
            
            # Limpiar sala si no hay conexiones
            if len(self.active_connections[sala_id]) == 0:
                del self.active_connections[sala_id]
                logger.info(f"Sala {sala_id} eliminada (sin conexiones)")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Enviar mensaje a un cliente específico"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error enviando mensaje personal: {e}")

    async def broadcast_to_sala(self, sala_id: str, message: dict):
        """Enviar mensaje a todos los clientes de una sala"""
        if sala_id not in self.active_connections:
            logger.warning(f"Intento de broadcast a sala inexistente: {sala_id}")
            return

        disconnected = []
        
        for connection in self.active_connections[sala_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error enviando mensaje a cliente: {e}")
                disconnected.append(connection)
        
        # Limpiar conexiones muertas
        for connection in disconnected:
            self.disconnect(connection, sala_id)

    async def notify_jugador_unido(self, sala_id: str, jugador_data: dict):
        """Notificar que un jugador se unió a la sala"""
        await self.broadcast_to_sala(sala_id, {
            "type": "jugador_unido",
            "data": jugador_data
        })

    async def notify_equipos_asignados(self, sala_id: str, equipos_data: dict):
        """Notificar que se asignaron los equipos"""
        await self.broadcast_to_sala(sala_id, {
            "type": "equipos_asignados",
            "data": equipos_data
        })

    async def notify_partido_iniciado(self, sala_id: str, partido_data: dict):
        """Notificar que el partido inició"""
        await self.broadcast_to_sala(sala_id, {
            "type": "partido_iniciado",
            "data": partido_data
        })

    async def notify_marcador_actualizado(self, sala_id: str, marcador_data: dict):
        """Notificar actualización del marcador"""
        await self.broadcast_to_sala(sala_id, {
            "type": "marcador_actualizado",
            "data": marcador_data
        })

    async def notify_resultado_reportado(self, sala_id: str, resultado_data: dict):
        """Notificar que se reportó el resultado"""
        await self.broadcast_to_sala(sala_id, {
            "type": "resultado_reportado",
            "data": resultado_data
        })

    async def notify_resultado_confirmado(self, sala_id: str, confirmacion_data: dict):
        """Notificar que se confirmó el resultado"""
        await self.broadcast_to_sala(sala_id, {
            "type": "resultado_confirmado",
            "data": confirmacion_data
        })


# Instancia global del manager
manager = ConnectionManager()
