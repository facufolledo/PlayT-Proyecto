"""
Servicio para gestión de inscripciones en torneos
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models.torneo_models import (
    Torneo, TorneoPareja, EstadoTorneo, EstadoPareja, TorneoHistorialCambios
)
from ..models.driveplus_models import Usuario
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
        # Verificar que el torneo existe
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            raise ValueError("Torneo no encontrado")
        
        # Verificar permisos según estado del torneo
        from .torneo_service import TorneoService
        es_organizador = TorneoService.es_organizador_torneo(db, torneo_id, inscriptor_id)
        
        # Si no está en inscripción, solo el organizador puede agregar parejas
        if torneo.estado != EstadoTorneo.INSCRIPCION:
            if not es_organizador:
                raise ValueError("El torneo no está en período de inscripción")
            # Organizador puede agregar parejas de último momento
        
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
        
        # Obtener nombres de los jugadores para mensajes de error
        from ..models.driveplus_models import PerfilUsuario
        perfil1 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja_data.jugador1_id).first()
        perfil2 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja_data.jugador2_id).first()
        nombre1 = f"{perfil1.nombre} {perfil1.apellido}" if perfil1 else f"Jugador {pareja_data.jugador1_id}"
        nombre2 = f"{perfil2.nombre} {perfil2.apellido}" if perfil2 else f"Jugador {pareja_data.jugador2_id}"
        
        for pareja in parejas_existentes:
            if pareja_data.jugador1_id in [pareja.jugador1_id, pareja.jugador2_id]:
                raise ValueError(f"{nombre1} ya está inscrito en este torneo")
            if pareja_data.jugador2_id in [pareja.jugador1_id, pareja.jugador2_id]:
                raise ValueError(f"{nombre2} ya está inscrito en este torneo")
        
        # Verificar categoría si se especifica
        categoria_id = getattr(pareja_data, 'categoria_id', None)
        if categoria_id:
            from ..models.torneo_models import TorneoCategoria
            categoria = db.query(TorneoCategoria).filter(
                TorneoCategoria.id == categoria_id,
                TorneoCategoria.torneo_id == torneo_id
            ).first()
            if not categoria:
                raise ValueError("Categoría no encontrada en este torneo")
            
            # Verificar que no exceda el máximo de parejas
            parejas_en_categoria = db.query(TorneoPareja).filter(
                TorneoPareja.categoria_id == categoria_id,
                TorneoPareja.estado != EstadoPareja.BAJA
            ).count()
            if parejas_en_categoria >= categoria.max_parejas:
                raise ValueError(f"La categoría {categoria.nombre} ya tiene el máximo de parejas ({categoria.max_parejas})")
        
        # Crear pareja
        pareja = TorneoPareja(
            torneo_id=torneo_id,
            categoria_id=categoria_id,
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
        
        # Si el torneo ya tiene playoffs generados, regenerarlos para incluir la nueva pareja
        if torneo.estado in [EstadoTorneo.FASE_GRUPOS, EstadoTorneo.FASE_ELIMINACION]:
            TorneoInscripcionService._actualizar_playoffs_si_necesario(db, torneo_id, inscriptor_id)
        
        return pareja
    
    @staticmethod
    def _actualizar_playoffs_si_necesario(db: Session, torneo_id: int, user_id: int) -> bool:
        """
        Regenera playoffs si hay parejas nuevas que no están incluidas
        
        Returns:
            True si se regeneraron los playoffs
        """
        from ..models.driveplus_models import Partido
        from ..services.torneo_playoff_service import TorneoPlayoffService
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # Verificar si hay partidos de playoffs
            partidos_playoffs = db.query(Partido).filter(
                Partido.id_torneo == torneo_id,
                Partido.fase != 'zona',
                Partido.fase.isnot(None)
            ).all()
            
            if not partidos_playoffs:
                return False
            
            # Verificar si hay partidos de playoffs ya jugados
            partidos_jugados = [p for p in partidos_playoffs if p.estado == 'confirmado']
            
            if partidos_jugados:
                # No regenerar si ya hay partidos jugados
                logger.info(f"No se regeneran playoffs del torneo {torneo_id}: hay partidos ya jugados")
                return False
            
            # Regenerar playoffs
            logger.info(f"Regenerando playoffs del torneo {torneo_id} por nueva pareja")
            TorneoPlayoffService.generar_playoffs(
                db=db,
                torneo_id=torneo_id,
                user_id=user_id,
                clasificados_por_zona=2
            )
            return True
        except Exception as e:
            logger.error(f"Error actualizando playoffs: {e}")
            return False
    
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
        
        if pareja_data.categoria_id is not None:
            # Verificar que la categoría existe y pertenece al torneo
            from ..models.torneo_models import TorneoCategoria
            categoria = db.query(TorneoCategoria).filter(
                TorneoCategoria.id == pareja_data.categoria_id,
                TorneoCategoria.torneo_id == pareja.torneo_id
            ).first()
            if not categoria:
                raise ValueError("La categoría no existe o no pertenece a este torneo")
            pareja.categoria_id = pareja_data.categoria_id
        
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
