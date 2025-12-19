"""
Servicio para confirmación de parejas en torneos
Sistema híbrido: código + notificación push
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import secrets
import string

from ..models.torneo_models import TorneoPareja, Torneo, EstadoPareja
from ..models.playt_models import Usuario, PerfilUsuario


class TorneoConfirmacionService:
    """Servicio para gestión de confirmaciones de pareja"""
    
    EXPIRACION_HORAS = 48  # Tiempo para confirmar
    
    @staticmethod
    def generar_codigo() -> str:
        """Genera un código único de 6 caracteres alfanuméricos"""
        caracteres = string.ascii_uppercase + string.digits
        # Evitar caracteres confusos: 0, O, I, 1, L
        caracteres = caracteres.replace('0', '').replace('O', '').replace('I', '').replace('1', '').replace('L', '')
        return ''.join(secrets.choice(caracteres) for _ in range(6))
    
    @staticmethod
    def crear_inscripcion_pendiente(
        db: Session,
        torneo_id: int,
        jugador1_id: int,
        jugador2_id: int,
        categoria_id: Optional[int],
        creador_id: int,
        observaciones: Optional[str] = None
    ) -> dict:
        """
        Crea una inscripción pendiente de confirmación
        
        Returns:
            dict con pareja_id, codigo_confirmacion, fecha_expiracion
        """
        # Verificar torneo
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            raise ValueError("Torneo no encontrado")
        
        # Verificar jugadores
        j1 = db.query(Usuario).filter(Usuario.id_usuario == jugador1_id).first()
        j2 = db.query(Usuario).filter(Usuario.id_usuario == jugador2_id).first()
        if not j1 or not j2:
            raise ValueError("Uno o ambos jugadores no existen")
        
        if jugador1_id == jugador2_id:
            raise ValueError("Los jugadores deben ser diferentes")
        
        # Verificar que no estén ya inscritos
        parejas_existentes = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == torneo_id,
            TorneoPareja.estado.notin_(['baja', 'rechazada', 'expirada'])
        ).all()
        
        for p in parejas_existentes:
            if jugador1_id in [p.jugador1_id, p.jugador2_id]:
                raise ValueError("Ya estás inscrito en este torneo")
            if jugador2_id in [p.jugador1_id, p.jugador2_id]:
                raise ValueError("Tu compañero ya está inscrito en este torneo")
        
        # Generar código único
        codigo = TorneoConfirmacionService.generar_codigo()
        while db.query(TorneoPareja).filter(
            TorneoPareja.codigo_confirmacion == codigo
        ).first():
            codigo = TorneoConfirmacionService.generar_codigo()
        
        # Determinar quién es jugador1 y jugador2 (el creador siempre es jugador1)
        if creador_id == jugador2_id:
            jugador1_id, jugador2_id = jugador2_id, jugador1_id
        
        # Crear pareja pendiente
        fecha_expiracion = datetime.now() + timedelta(hours=TorneoConfirmacionService.EXPIRACION_HORAS)
        
        pareja = TorneoPareja(
            torneo_id=torneo_id,
            categoria_id=categoria_id,
            jugador1_id=jugador1_id,
            jugador2_id=jugador2_id,
            estado='pendiente',
            codigo_confirmacion=codigo,
            confirmado_jugador1=True,
            confirmado_jugador2=False,
            fecha_expiracion=fecha_expiracion,
            creado_por_id=creador_id,
            observaciones=observaciones
        )
        
        db.add(pareja)
        db.commit()
        db.refresh(pareja)
        
        # Enviar notificación al compañero
        TorneoConfirmacionService._enviar_notificacion_invitacion(
            db, pareja, torneo, jugador2_id
        )
        
        return {
            'pareja_id': pareja.id,
            'codigo_confirmacion': codigo,
            'fecha_expiracion': fecha_expiracion.isoformat(),
            'mensaje': f'Comparte el código {codigo} con tu compañero para confirmar la inscripción'
        }
    
    @staticmethod
    def confirmar_por_codigo(
        db: Session,
        codigo: str,
        user_id: int
    ) -> TorneoPareja:
        """
        Confirma una inscripción usando el código
        """
        pareja = db.query(TorneoPareja).filter(
            TorneoPareja.codigo_confirmacion == codigo.upper()
        ).first()
        
        if not pareja:
            raise ValueError("Código inválido")
        
        if pareja.estado != 'pendiente':
            raise ValueError("Esta inscripción ya fue procesada")
        
        if pareja.fecha_expiracion and pareja.fecha_expiracion < datetime.now():
            pareja.estado = 'expirada'
            db.commit()
            raise ValueError("El código ha expirado")
        
        # Verificar que el usuario es el jugador2 (el que debe confirmar)
        if user_id != pareja.jugador2_id:
            raise ValueError("Este código no es para ti")
        
        # Confirmar
        pareja.confirmado_jugador2 = True
        pareja.estado = 'inscripta'
        pareja.codigo_confirmacion = None  # Limpiar código usado
        
        db.commit()
        db.refresh(pareja)
        
        # Notificar al creador que fue confirmado
        TorneoConfirmacionService._enviar_notificacion_confirmacion(db, pareja)
        
        return pareja
    
    @staticmethod
    def rechazar_invitacion(
        db: Session,
        pareja_id: int,
        user_id: int,
        motivo: Optional[str] = None
    ) -> bool:
        """
        Rechaza una invitación de pareja
        """
        pareja = db.query(TorneoPareja).filter(TorneoPareja.id == pareja_id).first()
        
        if not pareja:
            raise ValueError("Inscripción no encontrada")
        
        if user_id != pareja.jugador2_id:
            raise ValueError("No tienes permisos para rechazar esta invitación")
        
        if pareja.estado != 'pendiente':
            raise ValueError("Esta inscripción ya fue procesada")
        
        pareja.estado = 'rechazada'
        pareja.observaciones = f"{pareja.observaciones or ''}\nRechazada: {motivo or 'Sin motivo'}"
        
        db.commit()
        
        # Notificar al creador
        TorneoConfirmacionService._enviar_notificacion_rechazo(db, pareja, motivo)
        
        return True
    
    @staticmethod
    def obtener_invitaciones_pendientes(
        db: Session,
        user_id: int
    ) -> list:
        """
        Obtiene las invitaciones pendientes para un usuario
        """
        parejas = db.query(TorneoPareja).filter(
            TorneoPareja.jugador2_id == user_id,
            TorneoPareja.estado == 'pendiente',
            TorneoPareja.confirmado_jugador2 == False
        ).all()
        
        resultado = []
        for p in parejas:
            # Verificar si expiró
            if p.fecha_expiracion and p.fecha_expiracion < datetime.now():
                p.estado = 'expirada'
                db.commit()
                continue
            
            # Obtener info del torneo y compañero
            torneo = db.query(Torneo).filter(Torneo.id == p.torneo_id).first()
            perfil_companero = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == p.jugador1_id
            ).first()
            
            resultado.append({
                'pareja_id': p.id,
                'torneo_id': p.torneo_id,
                'torneo_nombre': torneo.nombre if torneo else 'Torneo',
                'companero_id': p.jugador1_id,
                'companero_nombre': f"{perfil_companero.nombre} {perfil_companero.apellido}" if perfil_companero else 'Jugador',
                'fecha_expiracion': p.fecha_expiracion.isoformat() if p.fecha_expiracion else None,
                'codigo': p.codigo_confirmacion
            })
        
        return resultado
    
    @staticmethod
    def _enviar_notificacion_invitacion(
        db: Session,
        pareja: TorneoPareja,
        torneo: Torneo,
        destinatario_id: int
    ):
        """Envía notificación push de invitación"""
        try:
            from .notification_service import NotificationService
            
            perfil_creador = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == pareja.creado_por_id
            ).first()
            nombre_creador = f"{perfil_creador.nombre}" if perfil_creador else "Alguien"
            
            NotificationService.enviar_notificacion(
                db=db,
                user_id=destinatario_id,
                titulo="🎾 Invitación a torneo",
                mensaje=f"{nombre_creador} te invitó a jugar en {torneo.nombre}. Código: {pareja.codigo_confirmacion}",
                data={
                    'tipo': 'invitacion_torneo',
                    'pareja_id': pareja.id,
                    'torneo_id': torneo.id,
                    'codigo': pareja.codigo_confirmacion
                }
            )
        except Exception as e:
            print(f"Error enviando notificación: {e}")
    
    @staticmethod
    def _enviar_notificacion_confirmacion(db: Session, pareja: TorneoPareja):
        """Notifica al creador que el compañero confirmó"""
        try:
            from .notification_service import NotificationService
            
            perfil_companero = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == pareja.jugador2_id
            ).first()
            nombre_companero = f"{perfil_companero.nombre}" if perfil_companero else "Tu compañero"
            
            torneo = db.query(Torneo).filter(Torneo.id == pareja.torneo_id).first()
            
            NotificationService.enviar_notificacion(
                db=db,
                user_id=pareja.creado_por_id,
                titulo="✅ Pareja confirmada",
                mensaje=f"{nombre_companero} confirmó la inscripción en {torneo.nombre if torneo else 'el torneo'}",
                data={
                    'tipo': 'pareja_confirmada',
                    'pareja_id': pareja.id,
                    'torneo_id': pareja.torneo_id
                }
            )
        except Exception as e:
            print(f"Error enviando notificación: {e}")
    
    @staticmethod
    def _enviar_notificacion_rechazo(
        db: Session,
        pareja: TorneoPareja,
        motivo: Optional[str]
    ):
        """Notifica al creador que el compañero rechazó"""
        try:
            from .notification_service import NotificationService
            
            perfil_companero = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == pareja.jugador2_id
            ).first()
            nombre_companero = f"{perfil_companero.nombre}" if perfil_companero else "Tu compañero"
            
            torneo = db.query(Torneo).filter(Torneo.id == pareja.torneo_id).first()
            
            NotificationService.enviar_notificacion(
                db=db,
                user_id=pareja.creado_por_id,
                titulo="❌ Invitación rechazada",
                mensaje=f"{nombre_companero} rechazó jugar en {torneo.nombre if torneo else 'el torneo'}",
                data={
                    'tipo': 'pareja_rechazada',
                    'pareja_id': pareja.id,
                    'torneo_id': pareja.torneo_id
                }
            )
        except Exception as e:
            print(f"Error enviando notificación: {e}")
