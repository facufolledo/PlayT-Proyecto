"""
Controller de zonas de torneos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ...database.config import get_db
from ...auth.auth_utils import get_current_user
from ...models.playt_models import Usuario
from ...services.torneo_zona_service import TorneoZonaService
from ...utils.logger import get_logger

logger = get_logger("torneo.zona")
router = APIRouter()


@router.post("/{torneo_id}/zonas/generar")
def generar_zonas(
    torneo_id: int,
    num_zonas: int = 4,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Genera zonas automáticamente distribuyendo parejas"""
    try:
        logger.info(f"Generando {num_zonas} zonas para torneo {torneo_id}")
        resultado = TorneoZonaService.generar_zonas_automaticas(
            db, torneo_id, num_zonas, current_user.id_usuario, categoria_id
        )
        logger.info(f"Zonas generadas: {len(resultado.get('zonas', []))}")
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{torneo_id}/zonas")
def listar_zonas(
    torneo_id: int,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista todas las zonas del torneo"""
    return TorneoZonaService.obtener_zonas(db, torneo_id, categoria_id)


@router.get("/{torneo_id}/zonas/{zona_id}")
def obtener_zona(
    torneo_id: int,
    zona_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene detalle de una zona con tabla de posiciones"""
    zona = TorneoZonaService.obtener_zona_detalle(db, zona_id)
    if not zona:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    return zona


@router.get("/{torneo_id}/zonas/{zona_id}/tabla")
def obtener_tabla_posiciones(
    torneo_id: int,
    zona_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene la tabla de posiciones de una zona"""
    return TorneoZonaService.calcular_tabla_posiciones(db, zona_id)


@router.post("/{torneo_id}/zonas/{zona_id}/parejas/{pareja_id}")
def agregar_pareja_a_zona(
    torneo_id: int,
    zona_id: int,
    pareja_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Agrega una pareja a una zona manualmente"""
    try:
        resultado = TorneoZonaService.agregar_pareja_a_zona(
            db, zona_id, pareja_id, current_user.id_usuario
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{torneo_id}/zonas/{zona_id}/parejas/{pareja_id}")
def remover_pareja_de_zona(
    torneo_id: int,
    zona_id: int,
    pareja_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Remueve una pareja de una zona"""
    try:
        TorneoZonaService.remover_pareja_de_zona(
            db, zona_id, pareja_id, current_user.id_usuario
        )
        return {"message": "Pareja removida de la zona"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{torneo_id}/zonas/{zona_id}/mover-pareja")
def mover_pareja_entre_zonas(
    torneo_id: int,
    zona_id: int,
    pareja_id: int,
    zona_destino_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Mueve una pareja de una zona a otra"""
    try:
        resultado = TorneoZonaService.mover_pareja_entre_zonas(
            db, pareja_id, zona_id, zona_destino_id, current_user.id_usuario
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{torneo_id}/zonas/eliminar-todas")
def eliminar_todas_zonas(
    torneo_id: int,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Elimina todas las zonas (para regenerar)"""
    try:
        TorneoZonaService.eliminar_zonas(db, torneo_id, current_user.id_usuario, categoria_id)
        return {"message": "Zonas eliminadas"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
