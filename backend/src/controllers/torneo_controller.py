"""
Controller para endpoints de torneos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database.config import get_db
from ..services.torneo_service import TorneoService
from ..services.torneo_inscripcion_service import TorneoInscripcionService
from ..schemas.torneo_schemas import (
    TorneoCreate, TorneoUpdate, TorneoResponse,
    EstadisticasTorneoResponse,
    ParejaInscripcion, ParejaUpdate, ParejaResponse
)
from ..auth.auth_utils import get_current_user
from ..models.playt_models import Usuario

router = APIRouter(prefix="/torneos", tags=["Torneos"])


@router.post("/", response_model=TorneoResponse, status_code=status.HTTP_201_CREATED)
def crear_torneo(
    torneo_data: TorneoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea un nuevo torneo
    
    Solo usuarios autorizados pueden crear torneos
    """
    try:
        user_id = current_user.id_usuario
        torneo = TorneoService.crear_torneo(db, torneo_data, user_id)
        return torneo
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[TorneoResponse])
def listar_torneos(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    categoria: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos los torneos con filtros opcionales
    
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a devolver
    - **estado**: Filtrar por estado (inscripcion, fase_grupos, etc.)
    - **categoria**: Filtrar por categoría
    """
    try:
        torneos = TorneoService.listar_torneos(db, skip, limit, estado, categoria)
        return torneos
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}", response_model=TorneoResponse)
def obtener_torneo(
    torneo_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene un torneo por ID"""
    torneo = TorneoService.obtener_torneo(db, torneo_id)
    if not torneo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Torneo no encontrado")
    return torneo


@router.put("/{torneo_id}", response_model=TorneoResponse)
def actualizar_torneo(
    torneo_id: int,
    torneo_data: TorneoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza un torneo
    
    Solo organizadores del torneo pueden actualizarlo
    """
    try:
        user_id = current_user.id_usuario
        torneo = TorneoService.actualizar_torneo(db, torneo_id, torneo_data, user_id)
        return torneo
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{torneo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_torneo(
    torneo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Elimina un torneo
    
    Solo el owner puede eliminar el torneo
    Solo se puede eliminar si está en estado de inscripción
    """
    try:
        user_id = current_user.id_usuario
        TorneoService.eliminar_torneo(db, torneo_id, user_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{torneo_id}/organizadores")
def agregar_organizador(
    torneo_id: int,
    nuevo_organizador_id: int,
    rol: str = "colaborador",
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Agrega un organizador al torneo
    
    Solo el owner puede agregar organizadores
    """
    try:
        user_id = current_user.id_usuario
        organizador = TorneoService.agregar_organizador(
            db, torneo_id, nuevo_organizador_id, user_id, rol
        )
        return {"message": "Organizador agregado exitosamente", "organizador_id": organizador.id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{torneo_id}/organizadores/{organizador_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_organizador(
    torneo_id: int,
    organizador_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Remueve un organizador del torneo
    
    Solo el owner puede remover organizadores
    No se puede remover al owner
    """
    try:
        user_id = current_user.id_usuario
        TorneoService.remover_organizador(db, torneo_id, organizador_id, user_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}/organizadores")
def listar_organizadores(
    torneo_id: int,
    db: Session = Depends(get_db)
):
    """Lista todos los organizadores de un torneo"""
    try:
        organizadores = TorneoService.listar_organizadores(db, torneo_id)
        return organizadores
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{torneo_id}/estado")
def cambiar_estado(
    torneo_id: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cambia el estado de un torneo
    
    Transiciones válidas:
    - inscripcion -> armando_zonas
    - armando_zonas -> fase_grupos
    - fase_grupos -> fase_eliminacion
    - fase_eliminacion -> finalizado
    """
    try:
        user_id = current_user.id_usuario
        torneo = TorneoService.cambiar_estado(db, torneo_id, nuevo_estado, user_id)
        return torneo
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}/estadisticas", response_model=EstadisticasTorneoResponse)
def obtener_estadisticas(
    torneo_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene estadísticas generales del torneo"""
    from ..models.torneo_models import TorneoPareja, TorneoZona
    from ..models.playt_models import Partido
    
    torneo = TorneoService.obtener_torneo(db, torneo_id)
    if not torneo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Torneo no encontrado")
    
    # Contar parejas
    total_parejas = db.query(TorneoPareja).filter(
        TorneoPareja.torneo_id == torneo_id,
        TorneoPareja.estado == "confirmada"
    ).count()
    
    # Contar partidos
    total_partidos = db.query(Partido).filter(
        Partido.id_torneo == torneo_id
    ).count()
    
    partidos_jugados = db.query(Partido).filter(
        Partido.id_torneo == torneo_id,
        Partido.estado == "finalizado"
    ).count()
    
    partidos_pendientes = total_partidos - partidos_jugados
    
    # Contar zonas
    zonas = db.query(TorneoZona).filter(
        TorneoZona.torneo_id == torneo_id
    ).count()
    
    return EstadisticasTorneoResponse(
        torneo_id=torneo_id,
        total_parejas=total_parejas,
        total_partidos=total_partidos,
        partidos_jugados=partidos_jugados,
        partidos_pendientes=partidos_pendientes,
        zonas=zonas,
        fase_actual=torneo.estado
    )


# ============================================
# ENDPOINTS DE INSCRIPCIONES
# ============================================

@router.post("/{torneo_id}/inscribir", response_model=ParejaResponse, status_code=status.HTTP_201_CREATED)
def inscribir_pareja(
    torneo_id: int,
    pareja_data: ParejaInscripcion,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Inscribe una pareja en el torneo
    
    Cualquier jugador puede inscribirse mientras el torneo esté en período de inscripción
    """
    from ..services.torneo_inscripcion_service import TorneoInscripcionService
    
    try:
        user_id = current_user.id_usuario
        pareja = TorneoInscripcionService.inscribir_pareja(db, torneo_id, pareja_data, user_id)
        return pareja
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}/parejas", response_model=List[ParejaResponse])
def listar_parejas(
    torneo_id: int,
    estado: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todas las parejas inscritas en el torneo
    
    - **estado**: Filtrar por estado (inscripta, confirmada, baja)
    """
    from ..services.torneo_inscripcion_service import TorneoInscripcionService
    
    try:
        parejas = TorneoInscripcionService.listar_parejas(db, torneo_id, estado)
        return parejas
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{torneo_id}/parejas/{pareja_id}/confirmar", response_model=ParejaResponse)
def confirmar_pareja(
    torneo_id: int,
    pareja_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Confirma una pareja inscrita
    
    Solo organizadores pueden confirmar parejas
    """
    from ..services.torneo_inscripcion_service import TorneoInscripcionService
    
    try:
        user_id = current_user.id_usuario
        pareja = TorneoInscripcionService.confirmar_pareja(db, pareja_id, user_id)
        return pareja
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{torneo_id}/parejas/{pareja_id}/rechazar", status_code=status.HTTP_204_NO_CONTENT)
def rechazar_pareja(
    torneo_id: int,
    pareja_id: int,
    motivo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Rechaza/elimina una pareja inscrita
    
    Solo organizadores pueden rechazar parejas
    """
    from ..services.torneo_inscripcion_service import TorneoInscripcionService
    
    try:
        user_id = current_user.id_usuario
        TorneoInscripcionService.rechazar_pareja(db, pareja_id, user_id, motivo)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{torneo_id}/parejas/{pareja_id}/baja", response_model=ParejaResponse)
def dar_baja_pareja(
    torneo_id: int,
    pareja_id: int,
    motivo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Da de baja una pareja
    
    Puede ser realizado por uno de los jugadores o por un organizador
    """
    from ..services.torneo_inscripcion_service import TorneoInscripcionService
    
    try:
        user_id = current_user.id_usuario
        pareja = TorneoInscripcionService.dar_baja_pareja(db, pareja_id, user_id, motivo)
        return pareja
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{torneo_id}/parejas/{pareja_id}/reemplazar-jugador", response_model=ParejaResponse)
def reemplazar_jugador(
    torneo_id: int,
    pareja_id: int,
    jugador_saliente_id: int,
    jugador_entrante_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Reemplaza un jugador en una pareja
    
    Solo organizadores pueden reemplazar jugadores
    """
    from ..services.torneo_inscripcion_service import TorneoInscripcionService
    
    try:
        user_id = current_user.id_usuario
        pareja = TorneoInscripcionService.reemplazar_jugador(
            db, pareja_id, jugador_saliente_id, jugador_entrante_id, user_id
        )
        return pareja
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{torneo_id}/parejas/{pareja_id}", response_model=ParejaResponse)
def actualizar_pareja(
    torneo_id: int,
    pareja_id: int,
    pareja_data: ParejaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza datos de una pareja
    
    Solo organizadores pueden actualizar parejas
    """
    from ..services.torneo_inscripcion_service import TorneoInscripcionService
    
    try:
        user_id = current_user.id_usuario
        pareja = TorneoInscripcionService.actualizar_pareja(db, pareja_id, pareja_data, user_id)
        return pareja
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
