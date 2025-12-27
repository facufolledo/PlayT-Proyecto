"""
Controller base de torneos - CRUD y operaciones básicas
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ...database.config import get_db
from ...services.torneo_service import TorneoService
from ...schemas.torneo_schemas import TorneoCreate, TorneoUpdate, TorneoResponse, EstadisticasTorneoResponse
from ...auth.auth_utils import get_current_user
from ...models.playt_models import Usuario
from ...utils.exceptions import NotFoundError, AuthorizationError, BusinessError
from ...utils.logger import get_logger

logger = get_logger("torneo")
router = APIRouter()


@router.post("/", response_model=TorneoResponse, status_code=status.HTTP_201_CREATED)
def crear_torneo(
    torneo_data: TorneoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crea un nuevo torneo"""
    try:
        logger.info(f"Usuario {current_user.id_usuario} creando torneo: {torneo_data.nombre}")
        torneo = TorneoService.crear_torneo(db, torneo_data, current_user.id_usuario)
        logger.info(f"Torneo {torneo.id} creado exitosamente")
        return torneo
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/mis-torneos")
def obtener_mis_torneos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene los torneos donde el usuario está inscripto"""
    from sqlalchemy import or_
    from ...models.torneo_models import Torneo, TorneoPareja
    
    parejas = db.query(TorneoPareja).filter(
        or_(
            TorneoPareja.jugador1_id == current_user.id_usuario,
            TorneoPareja.jugador2_id == current_user.id_usuario
        )
    ).all()
    
    if not parejas:
        return {"torneos": []}
    
    torneo_ids = list(set([p.torneo_id for p in parejas]))
    torneos = db.query(Torneo).filter(Torneo.id.in_(torneo_ids)).all()
    
    parejas_por_torneo = {
        p.torneo_id: {
            "pareja_id": p.id,
            "estado_inscripcion": p.estado.value if hasattr(p.estado, 'value') else str(p.estado),
            "es_jugador1": p.jugador1_id == current_user.id_usuario
        }
        for p in parejas
    }
    
    resultado = []
    for torneo in torneos:
        info_pareja = parejas_por_torneo.get(torneo.id, {})
        resultado.append({
            "id": torneo.id,
            "nombre": torneo.nombre,
            "descripcion": torneo.descripcion,
            "tipo": torneo.tipo.value if hasattr(torneo.tipo, 'value') else str(torneo.tipo),
            "categoria": torneo.categoria,
            "estado": torneo.estado.value if hasattr(torneo.estado, 'value') else str(torneo.estado),
            "fecha_inicio": torneo.fecha_inicio.isoformat() if torneo.fecha_inicio else None,
            "fecha_fin": torneo.fecha_fin.isoformat() if torneo.fecha_fin else None,
            "lugar": torneo.lugar,
            "pareja_id": info_pareja.get("pareja_id"),
            "estado_inscripcion": info_pareja.get("estado_inscripcion"),
            "es_jugador1": info_pareja.get("es_jugador1", False)
        })
    
    return {"torneos": resultado}


@router.get("/mis-invitaciones")
def obtener_mis_invitaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene las invitaciones pendientes del usuario"""
    from ...services.torneo_confirmacion_service import TorneoConfirmacionService
    
    invitaciones = TorneoConfirmacionService.obtener_invitaciones_pendientes(
        db=db, user_id=current_user.id_usuario
    )
    return {"invitaciones": invitaciones}


@router.get("/")
def listar_torneos(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = None,
    categoria: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todos los torneos con filtros opcionales"""
    from ...models.torneo_models import TorneoPareja
    
    torneos = TorneoService.listar_torneos(db, skip, limit, estado, categoria)
    
    resultado = []
    for torneo in torneos:
        parejas_count = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == torneo.id,
            TorneoPareja.estado.in_(['inscripta', 'confirmada'])
        ).count()
        
        resultado.append({
            "id": torneo.id,
            "nombre": torneo.nombre,
            "descripcion": torneo.descripcion,
            "tipo": torneo.tipo.value if hasattr(torneo.tipo, 'value') else str(torneo.tipo),
            "categoria": torneo.categoria,
            "genero": torneo.genero or 'masculino',
            "estado": torneo.estado.value if hasattr(torneo.estado, 'value') else str(torneo.estado),
            "fecha_inicio": torneo.fecha_inicio.isoformat() if torneo.fecha_inicio else None,
            "fecha_fin": torneo.fecha_fin.isoformat() if torneo.fecha_fin else None,
            "lugar": torneo.lugar,
            "reglas_json": torneo.reglas_json,
            "creado_por": torneo.creado_por,
            "created_at": torneo.created_at.isoformat() if torneo.created_at else None,
            "parejas_inscritas": parejas_count,
        })
    
    return resultado


@router.get("/{torneo_id}")
def obtener_torneo(torneo_id: int, db: Session = Depends(get_db)):
    """Obtiene un torneo por ID"""
    from ...models.torneo_models import TorneoPareja
    
    torneo = TorneoService.obtener_torneo(db, torneo_id)
    if not torneo:
        raise HTTPException(status_code=404, detail="Torneo no encontrado")
    
    parejas_count = db.query(TorneoPareja).filter(
        TorneoPareja.torneo_id == torneo.id,
        TorneoPareja.estado.in_(['inscripta', 'confirmada'])
    ).count()
    
    return {
        "id": torneo.id,
        "nombre": torneo.nombre,
        "descripcion": torneo.descripcion,
        "tipo": torneo.tipo.value if hasattr(torneo.tipo, 'value') else str(torneo.tipo),
        "categoria": torneo.categoria,
        "genero": torneo.genero or 'masculino',
        "estado": torneo.estado.value if hasattr(torneo.estado, 'value') else str(torneo.estado),
        "fecha_inicio": torneo.fecha_inicio.isoformat() if torneo.fecha_inicio else None,
        "fecha_fin": torneo.fecha_fin.isoformat() if torneo.fecha_fin else None,
        "lugar": torneo.lugar,
        "reglas_json": torneo.reglas_json,
        "creado_por": torneo.creado_por,
        "created_at": torneo.created_at.isoformat() if torneo.created_at else None,
        "parejas_inscritas": parejas_count,
    }


@router.put("/{torneo_id}", response_model=TorneoResponse)
def actualizar_torneo(
    torneo_id: int,
    torneo_data: TorneoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualiza un torneo (solo organizadores)"""
    try:
        torneo = TorneoService.actualizar_torneo(db, torneo_id, torneo_data, current_user.id_usuario)
        return torneo
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{torneo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_torneo(
    torneo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Elimina un torneo (solo owner, solo en inscripción)"""
    try:
        TorneoService.eliminar_torneo(db, torneo_id, current_user.id_usuario)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{torneo_id}/estado")
def cambiar_estado(
    torneo_id: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Cambia el estado de un torneo"""
    try:
        logger.info(f"Cambiando estado de torneo {torneo_id} a {nuevo_estado}")
        torneo = TorneoService.cambiar_estado(db, torneo_id, nuevo_estado, current_user.id_usuario)
        return torneo
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{torneo_id}/estadisticas", response_model=EstadisticasTorneoResponse)
def obtener_estadisticas(torneo_id: int, db: Session = Depends(get_db)):
    """Obtiene estadísticas generales del torneo"""
    from ...models.torneo_models import TorneoPareja, TorneoZona
    from ...models.playt_models import Partido
    
    torneo = TorneoService.obtener_torneo(db, torneo_id)
    if not torneo:
        raise HTTPException(status_code=404, detail="Torneo no encontrado")
    
    total_parejas = db.query(TorneoPareja).filter(
        TorneoPareja.torneo_id == torneo_id,
        TorneoPareja.estado == "confirmada"
    ).count()
    
    total_partidos = db.query(Partido).filter(Partido.id_torneo == torneo_id).count()
    partidos_jugados = db.query(Partido).filter(
        Partido.id_torneo == torneo_id,
        Partido.estado == "finalizado"
    ).count()
    
    zonas = db.query(TorneoZona).filter(TorneoZona.torneo_id == torneo_id).count()
    
    return EstadisticasTorneoResponse(
        torneo_id=torneo_id,
        total_parejas=total_parejas,
        total_partidos=total_partidos,
        partidos_jugados=partidos_jugados,
        partidos_pendientes=total_partidos - partidos_jugados,
        zonas=zonas,
        fase_actual=torneo.estado
    )


# ============ ORGANIZADORES ============

@router.post("/{torneo_id}/organizadores")
def agregar_organizador(
    torneo_id: int,
    nuevo_organizador_id: int,
    rol: str = "colaborador",
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Agrega un organizador al torneo (solo owner)"""
    try:
        organizador = TorneoService.agregar_organizador(
            db, torneo_id, nuevo_organizador_id, current_user.id_usuario, rol
        )
        return {"message": "Organizador agregado", "organizador_id": organizador.id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{torneo_id}/organizadores/{organizador_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_organizador(
    torneo_id: int,
    organizador_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Remueve un organizador (solo owner, no puede remover al owner)"""
    try:
        TorneoService.remover_organizador(db, torneo_id, organizador_id, current_user.id_usuario)
        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{torneo_id}/organizadores")
def listar_organizadores(torneo_id: int, db: Session = Depends(get_db)):
    """Lista todos los organizadores de un torneo"""
    return TorneoService.listar_organizadores(db, torneo_id)
