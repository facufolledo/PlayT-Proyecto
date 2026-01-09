"""
Controller de playoffs de torneos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ...database.config import get_db
from ...auth.auth_utils import get_current_user
from ...models.driveplus_models import Usuario
from ...services.torneo_playoff_service import TorneoPlayoffService
from ...utils.logger import get_logger

logger = get_logger("torneo.playoff")
router = APIRouter()


@router.post("/{torneo_id}/generar-playoffs")
def generar_playoffs(
    torneo_id: int,
    clasificados_por_zona: int = 2,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Genera el bracket de playoffs basado en resultados de zonas"""
    try:
        logger.info(f"Generando playoffs para torneo {torneo_id}")
        resultado = TorneoPlayoffService.generar_playoffs(
            db, torneo_id, current_user.id_usuario, clasificados_por_zona
        )
        logger.info(f"Playoffs generados: {resultado}")
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{torneo_id}/playoffs")
def obtener_playoffs(
    torneo_id: int,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtiene el bracket de playoffs"""
    return TorneoPlayoffService.obtener_bracket(db, torneo_id, categoria_id)


@router.get("/{torneo_id}/playoffs/bracket")
def obtener_bracket_visual(
    torneo_id: int,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtiene el bracket en formato visual para frontend"""
    return TorneoPlayoffService.obtener_bracket_visual(db, torneo_id, categoria_id)


@router.post("/{torneo_id}/playoffs/avanzar")
def avanzar_ganador(
    torneo_id: int,
    partido_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Avanza al ganador de un partido a la siguiente ronda"""
    try:
        resultado = TorneoPlayoffService.avanzar_ganador(
            db, partido_id, current_user.id_usuario
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{torneo_id}/playoffs/clasificados")
def obtener_clasificados(
    torneo_id: int,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtiene las parejas clasificadas a playoffs"""
    return TorneoPlayoffService.obtener_clasificados(db, torneo_id, categoria_id)


@router.post("/{torneo_id}/playoffs/tercer-puesto")
def generar_partido_tercer_puesto(
    torneo_id: int,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Genera el partido por el tercer puesto"""
    try:
        resultado = TorneoPlayoffService.generar_tercer_puesto(
            db, torneo_id, current_user.id_usuario, categoria_id
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{torneo_id}/playoffs/eliminar")
def eliminar_playoffs(
    torneo_id: int,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Elimina los playoffs (para regenerar)"""
    try:
        TorneoPlayoffService.eliminar_playoffs(db, torneo_id, current_user.id_usuario, categoria_id)
        return {"message": "Playoffs eliminados"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{torneo_id}/podio")
def obtener_podio(
    torneo_id: int,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtiene el podio final del torneo"""
    return TorneoPlayoffService.obtener_podio(db, torneo_id, categoria_id)
