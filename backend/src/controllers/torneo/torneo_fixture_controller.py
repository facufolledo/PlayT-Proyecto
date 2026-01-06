"""
Controller de fixture de torneos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from ...database.config import get_db
from ...auth.auth_utils import get_current_user
from ...models.Drive+_models import Usuario
from ...services.torneo_fixture_service import TorneoFixtureService
from ...utils.logger import get_logger

logger = get_logger("torneo.fixture")
router = APIRouter()


class ProgramarPartidoBody(BaseModel):
    fecha: datetime
    cancha: Optional[str] = None


@router.post("/{torneo_id}/fixture/generar")
def generar_fixture(
    torneo_id: int,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Genera el fixture completo de fase de grupos"""
    try:
        logger.info(f"Generando fixture para torneo {torneo_id}")
        resultado = TorneoFixtureService.generar_fixture_fase_grupos(
            db, torneo_id, current_user.id_usuario, categoria_id
        )
        logger.info(f"Fixture generado: {resultado.get('total_partidos', 0)} partidos")
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{torneo_id}/fixture")
def obtener_fixture(
    torneo_id: int,
    zona_id: Optional[int] = None,
    jornada: Optional[int] = None,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtiene el fixture del torneo con filtros"""
    return TorneoFixtureService.obtener_fixture(db, torneo_id, zona_id, jornada, categoria_id)


@router.get("/{torneo_id}/fixture/jornadas")
def obtener_jornadas(
    torneo_id: int,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Obtiene resumen de jornadas"""
    return TorneoFixtureService.obtener_jornadas(db, torneo_id, categoria_id)


@router.patch("/{torneo_id}/partidos/{partido_id}/programar")
def programar_partido(
    torneo_id: int,
    partido_id: int,
    datos: ProgramarPartidoBody,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Programa fecha y cancha de un partido"""
    try:
        resultado = TorneoFixtureService.programar_partido(
            db, partido_id, datos.fecha, datos.cancha, current_user.id_usuario
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{torneo_id}/fixture/programar-jornada")
def programar_jornada_completa(
    torneo_id: int,
    jornada: int,
    fecha_inicio: datetime,
    intervalo_minutos: int = 90,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Programa todos los partidos de una jornada"""
    try:
        resultado = TorneoFixtureService.programar_jornada(
            db, torneo_id, jornada, fecha_inicio, intervalo_minutos,
            current_user.id_usuario, categoria_id
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{torneo_id}/fixture/eliminar")
def eliminar_fixture(
    torneo_id: int,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Elimina el fixture (para regenerar)"""
    try:
        TorneoFixtureService.eliminar_fixture(db, torneo_id, current_user.id_usuario, categoria_id)
        return {"message": "Fixture eliminado"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
