"""
Servicio de Notificaciones Push
Maneja el envío de notificaciones push a través de Firebase Cloud Messaging
"""
from typing import List, Dict
import firebase_admin
from firebase_admin import messaging
from sqlalchemy.orm import Session
from ..models.playt_models import Usuario


class NotificationService:
    """Servicio para enviar notificaciones push"""
    
    @staticmethod
    def enviar_notificacion_elo_actualizado(
        usuarios: List[int],
        cambios_elo: Dict[int, Dict],
        db: Session
    ) -> Dict:
        """
        Envía notificaciones push a los jugadores cuando el Elo se actualiza
        
        Args:
            usuarios: Lista de IDs de usuarios
            cambios_elo: Dict con cambios de Elo por usuario {id_usuario: {cambio, nuevo, anterior}}
            db: Sesión de base de datos
            
        Returns:
            Dict con resultado del envío
        """
        try:
            mensajes_enviados = 0
            errores = []
            
            for id_usuario in usuarios:
                # Obtener usuario y su FCM token
                usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
                
                if not usuario or not hasattr(usuario, 'fcm_token') or not usuario.fcm_token:
                    continue
                
                # Obtener cambio de Elo del usuario
                cambio_info = cambios_elo.get(id_usuario, {})
                cambio = cambio_info.get('cambio', 0)
                nuevo_rating = cambio_info.get('nuevo', 0)
                
                # Determinar título y mensaje según si ganó o perdió
                if cambio > 0:
                    titulo = "¡Felicitaciones! 🎉"
                    cuerpo = f"Tu rating subió {cambio} puntos. Nuevo rating: {nuevo_rating}"
                    icono = "🎉"
                else:
                    titulo = "Partido finalizado"
                    cuerpo = f"Tu rating cambió {cambio} puntos. Nuevo rating: {nuevo_rating}"
                    icono = "📊"
                
                # Crear mensaje de notificación
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=titulo,
                        body=cuerpo,
                    ),
                    data={
                        'tipo': 'elo_actualizado',
                        'cambio_elo': str(cambio),
                        'nuevo_rating': str(nuevo_rating),
                        'icono': icono
                    },
                    token=usuario.fcm_token
                )
                
                try:
                    # Enviar notificación
                    response = messaging.send(message)
                    mensajes_enviados += 1
                except Exception as e:
                    errores.append(f"Error enviando a {usuario.nombre_usuario}: {str(e)}")
            
            return {
                "success": True,
                "mensajes_enviados": mensajes_enviados,
                "errores": errores
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def enviar_notificacion_resultado_pendiente(
        id_usuario: int,
        nombre_sala: str,
        db: Session
    ) -> Dict:
        """
        Envía notificación cuando hay un resultado pendiente de confirmación
        
        Args:
            id_usuario: ID del usuario
            nombre_sala: Nombre de la sala
            db: Sesión de base de datos
            
        Returns:
            Dict con resultado del envío
        """
        try:
            usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
            
            if not usuario or not hasattr(usuario, 'fcm_token') or not usuario.fcm_token:
                return {"success": False, "error": "Usuario sin token FCM"}
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title="Resultado pendiente de confirmación",
                    body=f"Hay un resultado en '{nombre_sala}' esperando tu confirmación",
                ),
                data={
                    'tipo': 'resultado_pendiente',
                    'nombre_sala': nombre_sala
                },
                token=usuario.fcm_token
            )
            
            response = messaging.send(message)
            
            return {
                "success": True,
                "message_id": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
