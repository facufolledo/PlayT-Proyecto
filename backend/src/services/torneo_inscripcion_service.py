"""
Servicio para gestión de inscripciones en torneos
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models.torneo_models import (
    Torneo, TorneoPareja, EstadoTorneo, EstadoPareja, TorneoHistorialCambios
)
from ..models.playt_models import Usuario
from ..schemas.torneo_schemas import ParejaInscripcion, ParejaUpdate


class TorneoInscripcionService:
    """Servicio para operaciones de inscripción en torneos"""
    
    @staticmethod
    def inscribir_pareja(
        db: Session,
        torneo_id: int,
        pareja_data: ParejaInscripcion,
        inscriptor_id: int
    ) -> TorneoPareja:
        """
        Inscribe una pareja en un torneo
        
        Args:
            db: Sesión de base de datos
            torneo_id: ID del torneo
            pareja_data: Datos de la pareja
            inscriptor_id: ID del usuario que inscribe
            
        Returns:
            TorneoPareja creada
            
        Raises:
            ValueError: Si hay algún error de validación
        """
        # Verificar que el torneo existe y está en inscripción
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            raise ValueError("Torneo no encontrado")
        
        if torneo.estado != EstadoTorneo.INSCRIPCION:
            raise ValueError("El torneo no está en período de inscripción")
        
        # Verificar que los jugadores existen
        jugador1 = db.query(Usuario).filter(Usuario.id_usuario == pareja_data.jugador1_id).first()
        jugador2 = db.query(Usuario).filter(Usuario.id_usuario == pareja_data.jugador2_id).first()
        
        if not jugador1 or not jugador2:
            raise ValueError("Uno o ambos jugadores no existen")
        
        # Verificar que los jugadores son diferentes
        if pareja_data.jugador1_id == pareja_data.jugador2_id:
            raise ValueError("Los jugadores deben ser diferentes")
        
        # Verificar que ninguno de los jugadores ya está inscrito en este torneo
        parejas_existentes = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == torneo_id,
            TorneoPareja.estado != EstadoPareja.BAJA
        ).all()
        
        for pareja in parejas_existentes:
            if pareja_data.jugador1_id in [pareja.jugador1_id, pareja.jugador2_id]:
                raise ValueError(f"El jugador {pareja_data.jugador1_id} ya está inscrito en este torneo")
            if pareja_data.jugador2_id in [pareja.jugador1_id, pareja.jugador2_id]:
                raise ValueError(f"El jugador {pareja_data.jugador2_id} ya está inscrito en este torneo")
        
        # Crear pareja
        pareja = TorneoPareja(
            torneo_id=torneo_id,
            jugador1_id=pareja_data.jugador1_id,
            jugador2_id=pareja_data.jugador2_id,
            estado=EstadoPareja.INSCRIPTA,
            observaciones=pareja_data.observaciones
        )
        
        db.add(pareja)
        db.flush()
        
        # Registrar en historial
        historial = TorneoHistorialCambios(
            torneo_id=torneo_id,
            tipo_cambio='pareja_inscrita',
            descripcion=f"Pareja inscrita: Jugador {pareja_data.jugador1_id} y Jugador {pareja_data.jugador2_id}",
            realizado_por=inscriptor_id,
            datos_json={
                'pareja_id': pareja.id,
                'jugador1_id': pareja_data.jugador1_id,
                'jugador2_id': pareja_data.jugador2_id
            }
        )
        db.add(historial)
        
        db.commit()
        db.refresh(pareja)
        
        return pareja
    
    @staticmethod
    def listar_parejas(
        db: Session,
        torneo_id: int,
        estado: Optional[str] = None
    ) -> List[TorneoPareja]:
        """
        Lista parejas inscritas en un torneo
        
        Args:
            db: Sesión de base de datos
            torneo_id: ID del torneo
            estado: Filtrar por estado (opcional)
            
        Returns:
            Lista de parejas
        """
        query = db.query(TorneoPareja).filter(TorneoPareja.torneo_id == torneo_id)
        
        if estado:
            query = query.filter(TorneoPareja.estado == estado)
        
        return query.all()
    
    @staticmethod
    def confirmar_pareja(
        db: Session,
        pareja_id: int,
        user_id: int
    ) -> TorneoPareja:
        """
        Confirma una pareja inscrita (solo organizadores)
        
        Args:
            db: Sesión de base de datos
            pareja_id: ID de la pareja
            user_id: ID del organizador
            
        Returns:
            Pareja confirmada
            
        Raises:
            ValueError: Si no tiene permisos o la pareja no existe
        """
        pareja = db.query(TorneoPareja).filter(TorneoPareja.id == pareja_id).first()
        if not pareja:
            raise ValueError("Pareja no encontrada")
        
        # Verificar que es organizador
        from .torneo_service import TorneoService
        if not TorneoService.es_organizador_torneo(db, pareja.torneo_id, user_id):
            raise ValueError("No tienes permisos para confirmar parejas")
        
        if pareja.estado != EstadoPareja.INSCRIPTA:
            raise ValueError("La pareja no está en estado inscripta")
        
        pareja.estado = EstadoPareja.CONFIRMADA
        
        # Registrar en historial
        historial = TorneoHistorialCambios(
            torneo_id=pareja.torneo_id,
            tipo_cambio='pareja_inscrita',
            descripcion=f"Pareja {pareja_id} confirmada",
            realizado_por=user_id,
            datos_json={'pareja_id': pareja_id}
        )
        db.add(historial)
        
        db.commit()
        db.refresh(pareja)
        
        return pareja
    
    @staticmethod
    def rechazar_pareja(
        db: Session,
        pareja_id: int,
        user_id: int,
        motivo: Optional[str] = None
    ) -> bool:
        """
        Rechaza/elimina una pareja inscrita (solo organizadores)
        
        Args:
            db: Sesión de base de datos
            pareja_id: ID de la pareja
            user_id: ID del organizador
            motivo: Motivo del rechazo
            
        Returns:
            True si se rechazó correctamente
            
        Raises:
            ValueError: Si no tiene permisos o la pareja no existe
        """
        pareja = db.query(TorneoPareja).filter(TorneoPareja.id == pareja_id).first()
        if not pareja:
            raise ValueError("Pareja no encontrada")
        
        # Verificar que es organizador
        from .torneo_service import TorneoService
        if not TorneoService.es_organizador_torneo(db, pareja.torneo_id, user_id):
            raise ValueError("No tienes permisos para rechazar parejas")
        
        # Registrar en historial antes de eliminar
        historial = TorneoHistorialCambios(
            torneo_id=pareja.torneo_id,
            tipo_cambio='pareja_baja',
            descripcion=f"Pareja {pareja_id} rechazada. Motivo: {motivo or 'No especificado'}",
            realizado_por=user_id,
            datos_json={
                'pareja_id': pareja_id,
                'jugador1_id': pareja.jugador1_id,
                'jugador2_id': pareja.jugador2_id,
                'motivo': motivo
            }
        )
        db.add(historial)
        
        db.delete(pareja)
        db.commit()
        
        return True
    
    @staticmethod
    def dar_baja_pareja(
        db: Session,
        pareja_id: int,
        user_id: int,
        motivo: Optional[str] = None
    ) -> TorneoPareja:
        """
        Da de baja una pareja (puede ser el jugador o el organizador)
        
        Args:
            db: Sesión de base de datos
            pareja_id: ID de la pareja
            user_id: ID del usuario
            motivo: Motivo de la baja
            
        Returns:
            Pareja dada de baja
            
        Raises:
            ValueError: Si no tiene permisos o la pareja no existe
        """
        pareja = db.query(TorneoPareja).filter(TorneoPareja.id == pareja_id).first()
        if not pareja:
            raise ValueError("Pareja no encontrada")
        
        # Verificar permisos: debe ser uno de los jugadores o un organizador
        from .torneo_service import TorneoService
        es_jugador = user_id in [pareja.jugador1_id, pareja.jugador2_id]
        es_organizador = TorneoService.es_organizador_torneo(db, pareja.torneo_id, user_id)
        
        if not es_jugador and not es_organizador:
            raise ValueError("No tienes permisos para dar de baja esta pareja")
        
        # Verificar que el torneo no haya comenzado
        torneo = db.query(Torneo).filter(Torneo.id == pareja.torneo_id).first()
        if torneo.estado not in [EstadoTorneo.INSCRIPCION, EstadoTorneo.ARMANDO_ZONAS]:
            raise ValueError("No se puede dar de baja una pareja después de que el torneo comenzó")
        
        pareja.estado = EstadoPareja.BAJA
        pareja.observaciones = f"{pareja.observaciones or ''}\nBaja: {motivo or 'No especificado'}"
        
        # Registrar en historial
        historial = TorneoHistorialCambios(
            torneo_id=pareja.torneo_id,
            tipo_cambio='pareja_baja',
            descripcion=f"Pareja {pareja_id} dada de baja. Motivo: {motivo or 'No especificado'}",
            realizado_por=user_id,
            datos_json={
                'pareja_id': pareja_id,
                'motivo': motivo
            }
        )
        db.add(historial)
        
        db.commit()
        db.refresh(pareja)
        
        return pareja
    
    @staticmethod
    def reemplazar_jugador(
        db: Session,
        pareja_id: int,
        jugador_saliente_id: int,
        jugador_entrante_id: int,
        user_id: int
    ) -> TorneoPareja:
        """
        Reemplaza un jugador en una pareja
        
        Args:
            db: Sesión de base de datos
            pareja_id: ID de la pareja
            jugador_saliente_id: ID del jugador que sale
            jugador_entrante_id: ID del jugador que entra
            user_id: ID del organizador
            
        Returns:
            Pareja actualizada
            
        Raises:
            ValueError: Si hay algún error de validación
        """
        pareja = db.query(TorneoPareja).filter(TorneoPareja.id == pareja_id).first()
        if not pareja:
            raise ValueError("Pareja no encontrada")
        
        # Verificar que es organizador
        from .torneo_service import TorneoService
        if not TorneoService.es_organizador_torneo(db, pareja.torneo_id, user_id):
            raise ValueError("No tienes permisos para reemplazar jugadores")
        
        # Verificar que el jugador saliente está en la pareja
        if jugador_saliente_id not in [pareja.jugador1_id, pareja.jugador2_id]:
            raise ValueError("El jugador saliente no pertenece a esta pareja")
        
        # Verificar que el jugador entrante existe
        jugador_entrante = db.query(Usuario).filter(Usuario.id_usuario == jugador_entrante_id).first()
        if not jugador_entrante:
            raise ValueError("El jugador entrante no existe")
        
        # Verificar que el jugador entrante no está ya inscrito
        parejas_existentes = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == pareja.torneo_id,
            TorneoPareja.estado != EstadoPareja.BAJA,
            TorneoPareja.id != pareja_id
        ).all()
        
        for p in parejas_existentes:
            if jugador_entrante_id in [p.jugador1_id, p.jugador2_id]:
                raise ValueError("El jugador entrante ya está inscrito en este torneo")
        
        # Reemplazar jugador
        if pareja.jugador1_id == jugador_saliente_id:
            pareja.jugador1_id = jugador_entrante_id
        else:
            pareja.jugador2_id = jugador_entrante_id
        
        # Registrar en historial
        historial = TorneoHistorialCambios(
            torneo_id=pareja.torneo_id,
            tipo_cambio='jugador_reemplazado',
            descripcion=f"Jugador {jugador_saliente_id} reemplazado por {jugador_entrante_id} en pareja {pareja_id}",
            realizado_por=user_id,
            datos_json={
                'pareja_id': pareja_id,
                'jugador_saliente_id': jugador_saliente_id,
                'jugador_entrante_id': jugador_entrante_id
            }
        )
        db.add(historial)
        
        db.commit()
        db.refresh(pareja)
        
        return pareja
    
    @staticmethod
    def actualizar_pareja(
        db: Session,
        pareja_id: int,
        pareja_data: ParejaUpdate,
        user_id: int
    ) -> TorneoPareja:
        """
        Actualiza datos de una pareja
        
        Args:
            db: Sesión de base de datos
            pareja_id: ID de la pareja
            pareja_data: Datos a actualizar
            user_id: ID del organizador
            
        Returns:
            Pareja actualizada
            
        Raises:
            ValueError: Si no tiene permisos o la pareja no existe
        """
        pareja = db.query(TorneoPareja).filter(TorneoPareja.id == pareja_id).first()
        if not pareja:
            raise ValueError("Pareja no encontrada")
        
        # Verificar que es organizador
        from .torneo_service import TorneoService
        if not TorneoService.es_organizador_torneo(db, pareja.torneo_id, user_id):
            raise ValueError("No tienes permisos para actualizar parejas")
        
        # Actualizar campos
        if pareja_data.estado is not None:
            pareja.estado = pareja_data.estado
        
        if pareja_data.categoria_asignada is not None:
            pareja.categoria_asignada = pareja_data.categoria_asignada
        
        if pareja_data.observaciones is not None:
            pareja.observaciones = pareja_data.observaciones
        
        db.commit()
        db.refresh(pareja)
        
        return pareja
    
    @staticmethod
    def obtener_pareja(db: Session, pareja_id: int) -> Optional[TorneoPareja]:
        """Obtiene una pareja por ID"""
        return db.query(TorneoPareja).filter(TorneoPareja.id == pareja_id).first()
    
    @staticmethod
    def contar_parejas_confirmadas(db: Session, torneo_id: int) -> int:
        """Cuenta las parejas confirmadas en un torneo"""
        return db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == torneo_id,
            TorneoPareja.estado == EstadoPareja.CONFIRMADA
        ).count()
