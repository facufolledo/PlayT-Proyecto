# Sistema de notificaciones para el backend

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

router = APIRouter(prefix="/notifications", tags=["notifications"])

class NotificationCreate(BaseModel):
    user_id: int
    type: str  # 'tournament', 'match', 'system', 'partner_request'
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    priority: str = "normal"  # 'low', 'normal', 'high', 'urgent'

class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]]
    priority: str
    read: bool
    created_at: datetime

@router.get("/")
async def get_user_notifications(
    unread_only: bool = False,
    limit: int = 20,
    offset: int = 0,
    current_user = Depends(get_current_user)
) -> List[NotificationResponse]:
    """Obtener notificaciones del usuario"""
    try:
        query = """
        SELECT 
            id, type, title, message, data, priority, read, created_at
        FROM notifications 
        WHERE user_id = %s
        """
        params = [current_user.id_usuario]
        
        if unread_only:
            query += " AND read = false"
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        # results = await database.fetch_all(query, params)
        
        # Simulación
        results = [
            {
                "id": 1,
                "type": "tournament",
                "title": "Nuevo torneo disponible",
                "message": "Se ha creado un torneo en tu categoría",
                "data": {"tournament_id": 123},
                "priority": "normal",
                "read": False,
                "created_at": datetime.now()
            }
        ]
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo notificaciones: {str(e)}")

@router.post("/")
async def create_notification(
    notification: NotificationCreate,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_admin_user)  # Solo admins pueden crear notificaciones
):
    """Crear nueva notificación"""
    try:
        # Insertar en base de datos
        query = """
        INSERT INTO notifications (user_id, type, title, message, data, priority, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        # notification_id = await database.fetch_val(query, [
        #     notification.user_id,
        #     notification.type,
        #     notification.title,
        #     notification.message,
        #     json.dumps(notification.data) if notification.data else None,
        #     notification.priority,
        #     datetime.now()
        # ])
        
        notification_id = 1  # Simulación
        
        # Enviar notificación en tiempo real (WebSocket, Push, etc.)
        background_tasks.add_task(
            send_real_time_notification,
            notification.user_id,
            {
                "id": notification_id,
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "data": notification.data,
                "priority": notification.priority
            }
        )
        
        return {"id": notification_id, "status": "created"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando notificación: {str(e)}")

@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user = Depends(get_current_user)
):
    """Marcar notificación como leída"""
    try:
        query = """
        UPDATE notifications 
        SET read = true, read_at = %s
        WHERE id = %s AND user_id = %s
        """
        
        # await database.execute(query, [datetime.now(), notification_id, current_user.id_usuario])
        
        return {"status": "marked_as_read"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marcando notificación: {str(e)}")

@router.patch("/read-all")
async def mark_all_notifications_read(
    current_user = Depends(get_current_user)
):
    """Marcar todas las notificaciones como leídas"""
    try:
        query = """
        UPDATE notifications 
        SET read = true, read_at = %s
        WHERE user_id = %s AND read = false
        """
        
        # count = await database.execute(query, [datetime.now(), current_user.id_usuario])
        count = 5  # Simulación
        
        return {"status": "all_marked_as_read", "count": count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marcando notificaciones: {str(e)}")

@router.get("/unread-count")
async def get_unread_count(
    current_user = Depends(get_current_user)
):
    """Obtener cantidad de notificaciones no leídas"""
    try:
        query = """
        SELECT COUNT(*) as count
        FROM notifications 
        WHERE user_id = %s AND read = false
        """
        
        # result = await database.fetch_one(query, [current_user.id_usuario])
        # count = result["count"] if result else 0
        
        count = 3  # Simulación
        
        return {"unread_count": count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo contador: {str(e)}")

# Funciones helper para notificaciones automáticas

async def send_real_time_notification(user_id: int, notification_data: Dict):
    """Enviar notificación en tiempo real (WebSocket, etc.)"""
    # Implementar WebSocket o Push notification
    print(f"Sending real-time notification to user {user_id}: {notification_data}")

async def notify_tournament_created(tournament_id: int, category: str):
    """Notificar a usuarios de una categoría sobre nuevo torneo"""
    # Obtener usuarios de la categoría
    # Crear notificaciones para cada uno
    pass

async def notify_match_result(match_id: int, winner_ids: List[int], loser_ids: List[int]):
    """Notificar resultado de partido"""
    # Crear notificaciones para ganadores y perdedores
    pass

async def notify_partner_request(from_user_id: int, to_user_id: int, tournament_id: int):
    """Notificar solicitud de pareja"""
    notification = NotificationCreate(
        user_id=to_user_id,
        type="partner_request",
        title="Solicitud de pareja",
        message=f"Te han invitado a formar pareja para un torneo",
        data={
            "from_user_id": from_user_id,
            "tournament_id": tournament_id,
            "action_required": True
        },
        priority="high"
    )
    
    # Crear notificación
    # await create_notification(notification, BackgroundTasks(), admin_user)