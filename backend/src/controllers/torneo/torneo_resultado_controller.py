"""
Controller de resultados de partidos de torneo
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from ...database.config import get_db
from ...auth.auth_utils import get_current_user
from ...models.playt_models import Usuario
from ...services.torneo_resultado_service import TorneoResultadoService
from ...utils.logger import get_logger

logger = get_logger("torneo.resultado")
router = APIRouter()


class SetScore(BaseModel):
    juegos_eq1: int
    juegos_eq2: int


class ResultadoTorneoBody(BaseModel):
    sets: List[SetScore]
    observaciones: Optional[str] = None


@router.post("/{torneo_id}/partidos/{partido_id}/resultado")
def cargar_resultado(
    torneo_id: int,
    partido_id: int,
    resultado: ResultadoTorneoBody,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Carga el resultado de un partido de torneo"""
    try:
        logger.info(f"Cargando resultado partido {partido_id} por usuario {current_user.id_usuario}")
        
        sets_data = [{"juegos_eq1": s.juegos_eq1, "juegos_eq2": s.juegos_eq2} for s in resultado.sets]
        
        result = TorneoResultadoService.cargar_resultado(
            db=db,
            partido_id=partido_id,
            sets=sets_data,
            user_id=current_user.id_usuario,
            observaciones=resultado.observaciones
        )
        
        logger.info(f"Resultado cargado: {result}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{torneo_id}/partidos/{partido_id}/confirmar")
def confirmar_resultado(
    torneo_id: int,
    partido_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Confirma el resultado de un partido"""
    try:
        result = TorneoResultadoService.confirmar_resultado(
            db=db,
            partido_id=partido_id,
            user_id=current_user.id_usuario
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{torneo_id}/partidos/{partido_id}/disputar")
def disputar_resultado(
    torneo_id: int,
    partido_id: int,
    motivo: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Disputa el resultado de un partido"""
    try:
        result = TorneoResultadoService.disputar_resultado(
            db=db,
            partido_id=partido_id,
            user_id=current_user.id_usuario,
            motivo=motivo
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{torneo_id}/partidos/{partido_id}")
def obtener_partido(
    torneo_id: int,
    partido_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene detalle de un partido"""
    partido = TorneoResultadoService.obtener_partido_detalle(db, partido_id)
    if not partido:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    return partido


@router.get("/{torneo_id}/partidos")
def listar_partidos(
    torneo_id: int,
    estado: Optional[str] = None,
    fase: Optional[str] = None,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista partidos del torneo con filtros"""
    return TorneoResultadoService.listar_partidos(
        db, torneo_id, estado, fase, categoria_id
    )


@router.post("/{torneo_id}/partidos/{partido_id}/walkover")
def asignar_walkover(
    torneo_id: int,
    partido_id: int,
    pareja_ganadora_id: int,
    motivo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Asigna walkover a un partido (solo organizadores)"""
    try:
        result = TorneoResultadoService.asignar_walkover(
            db=db,
            partido_id=partido_id,
            pareja_ganadora_id=pareja_ganadora_id,
            user_id=current_user.id_usuario,
            motivo=motivo
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
