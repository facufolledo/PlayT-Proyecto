"""
Controller de inscripciones a torneos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from pydantic import BaseModel

from ...database.config import get_db
from ...schemas.torneo_schemas import ParejaInscripcion
from ...auth.auth_utils import get_current_user
from ...models.playt_models import Usuario, PerfilUsuario
from ...models.torneo_models import TorneoPareja, TorneoCategoria, Torneo
from ...utils.logger import get_logger

logger = get_logger("torneo.inscripcion")
router = APIRouter()


class CategoriaCreateBody(BaseModel):
    nombre: str
    genero: str = "masculino"
    max_parejas: int = 16
    orden: int = 0


# ============ CATEGORÍAS ============

@router.post("/{torneo_id}/categorias", status_code=status.HTTP_201_CREATED)
def crear_categoria(
    torneo_id: int,
    categoria_data: CategoriaCreateBody,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crea una nueva categoría en el torneo"""
    from ...services.torneo_zona_service import TorneoZonaService
    
    if not TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario):
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    categoria = TorneoCategoria(
        torneo_id=torneo_id,
        nombre=categoria_data.nombre,
        genero=categoria_data.genero,
        max_parejas=categoria_data.max_parejas,
        orden=categoria_data.orden
    )
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    
    return {
        "id": categoria.id,
        "torneo_id": categoria.torneo_id,
        "nombre": categoria.nombre,
        "genero": categoria.genero,
        "max_parejas": categoria.max_parejas,
        "estado": categoria.estado,
        "orden": categoria.orden,
        "parejas_inscritas": 0
    }


@router.get("/{torneo_id}/categorias")
def listar_categorias(torneo_id: int, db: Session = Depends(get_db)):
    """Lista todas las categorías del torneo"""
    categorias = db.query(TorneoCategoria).filter(
        TorneoCategoria.torneo_id == torneo_id
    ).order_by(TorneoCategoria.orden).all()
    
    resultado = []
    for cat in categorias:
        parejas_count = db.query(TorneoPareja).filter(
            TorneoPareja.categoria_id == cat.id,
            TorneoPareja.estado.in_(['inscripta', 'confirmada'])
        ).count()
        
        resultado.append({
            "id": cat.id,
            "torneo_id": cat.torneo_id,
            "nombre": cat.nombre,
            "genero": cat.genero,
            "max_parejas": cat.max_parejas,
            "estado": cat.estado,
            "orden": cat.orden,
            "parejas_inscritas": parejas_count
        })
    
    return resultado


@router.delete("/{torneo_id}/categorias/{categoria_id}")
def eliminar_categoria(
    torneo_id: int,
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Elimina una categoría (solo si no tiene parejas)"""
    from ...services.torneo_zona_service import TorneoZonaService
    
    if not TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario):
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    parejas_count = db.query(TorneoPareja).filter(
        TorneoPareja.categoria_id == categoria_id
    ).count()
    
    if parejas_count > 0:
        raise HTTPException(status_code=400, detail=f"Hay {parejas_count} parejas inscritas")
    
    db.query(TorneoCategoria).filter(
        TorneoCategoria.id == categoria_id,
        TorneoCategoria.torneo_id == torneo_id
    ).delete()
    db.commit()
    
    return {"message": "Categoría eliminada"}


# ============ INSCRIPCIONES ============

@router.post("/{torneo_id}/inscribir", status_code=status.HTTP_201_CREATED)
def inscribir_pareja(
    torneo_id: int,
    pareja_data: ParejaInscripcion,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Inscribe una pareja (requiere confirmación del compañero)"""
    from ...services.torneo_confirmacion_service import TorneoConfirmacionService
    
    try:
        logger.info(f"Usuario {current_user.id_usuario} inscribiendo pareja en torneo {torneo_id}")
        resultado = TorneoConfirmacionService.crear_inscripcion_pendiente(
            db=db,
            torneo_id=torneo_id,
            jugador1_id=pareja_data.jugador1_id,
            jugador2_id=pareja_data.jugador2_id,
            categoria_id=getattr(pareja_data, 'categoria_id', None),
            creador_id=current_user.id_usuario,
            observaciones=pareja_data.observaciones
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/confirmar-pareja/{codigo}")
def confirmar_pareja_por_codigo(
    codigo: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Confirma una inscripción usando el código"""
    from ...services.torneo_confirmacion_service import TorneoConfirmacionService
    
    try:
        pareja = TorneoConfirmacionService.confirmar_por_codigo(
            db=db, codigo=codigo, user_id=current_user.id_usuario
        )
        return {
            "mensaje": "Inscripción confirmada",
            "pareja_id": pareja.id,
            "torneo_id": pareja.torneo_id
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/rechazar-invitacion/{pareja_id}")
def rechazar_invitacion(
    pareja_id: int,
    motivo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Rechaza una invitación de pareja"""
    from ...services.torneo_confirmacion_service import TorneoConfirmacionService
    
    try:
        TorneoConfirmacionService.rechazar_invitacion(
            db=db, pareja_id=pareja_id, user_id=current_user.id_usuario, motivo=motivo
        )
        return {"mensaje": "Invitación rechazada"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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


@router.get("/mis-torneos")
def obtener_mis_torneos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene los torneos donde el usuario está inscripto"""
    parejas = db.query(TorneoPareja).filter(
        or_(
            TorneoPareja.jugador1_id == current_user.id_usuario,
            TorneoPareja.jugador2_id == current_user.id_usuario
        ),
        TorneoPareja.estado.in_(['inscripta', 'confirmada'])  # Removido 'pendiente' que no existe en el enum
    ).all()
    
    if not parejas:
        return {"torneos": []}
    
    torneo_ids = list(set(p.torneo_id for p in parejas))
    torneos = db.query(Torneo).filter(Torneo.id.in_(torneo_ids)).all()
    
    parejas_por_torneo = {
        p.torneo_id: {
            "pareja_id": p.id,
            "estado_inscripcion": p.estado.value if hasattr(p.estado, 'value') else str(p.estado),
            "categoria_id": p.categoria_id
        }
        for p in parejas
    }
    
    resultado = []
    for torneo in torneos:
        info_pareja = parejas_por_torneo.get(torneo.id, {})
        resultado.append({
            "id": torneo.id,
            "nombre": torneo.nombre,
            "estado": torneo.estado.value if hasattr(torneo.estado, 'value') else str(torneo.estado),
            "fecha_inicio": torneo.fecha_inicio.isoformat() if torneo.fecha_inicio else None,
            "lugar": torneo.lugar,
            "mi_inscripcion": info_pareja
        })
    
    return {"torneos": resultado}


# ============ PAREJAS ============

@router.get("/{torneo_id}/parejas")
def listar_parejas(
    torneo_id: int,
    estado: Optional[str] = None,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista todas las parejas inscritas"""
    query = db.query(TorneoPareja).filter(TorneoPareja.torneo_id == torneo_id)
    
    if estado:
        query = query.filter(TorneoPareja.estado == estado)
    if categoria_id:
        query = query.filter(TorneoPareja.categoria_id == categoria_id)
    
    parejas = query.all()
    
    if not parejas:
        return []
    
    # Pre-cargar perfiles (optimización)
    jugadores_ids = set()
    categoria_ids = set()
    for p in parejas:
        jugadores_ids.add(p.jugador1_id)
        jugadores_ids.add(p.jugador2_id)
        if p.categoria_id:
            categoria_ids.add(p.categoria_id)
    
    perfiles = db.query(PerfilUsuario).filter(
        PerfilUsuario.id_usuario.in_(jugadores_ids)
    ).all()
    perfiles_dict = {p.id_usuario: p for p in perfiles}
    
    categorias = db.query(TorneoCategoria).filter(
        TorneoCategoria.id.in_(categoria_ids)
    ).all() if categoria_ids else []
    categorias_dict = {c.id: c for c in categorias}
    
    # También obtener usuarios para nombre_usuario
    usuarios = db.query(Usuario).filter(
        Usuario.id_usuario.in_(jugadores_ids)
    ).all()
    usuarios_dict = {u.id_usuario: u for u in usuarios}
    
    resultado = []
    for pareja in parejas:
        perfil1 = perfiles_dict.get(pareja.jugador1_id)
        perfil2 = perfiles_dict.get(pareja.jugador2_id)
        usuario1 = usuarios_dict.get(pareja.jugador1_id)
        usuario2 = usuarios_dict.get(pareja.jugador2_id)
        categoria = categorias_dict.get(pareja.categoria_id)
        
        j1_nombre = f"{perfil1.nombre} {perfil1.apellido}" if perfil1 else f"Usuario {pareja.jugador1_id}"
        j2_nombre = f"{perfil2.nombre} {perfil2.apellido}" if perfil2 else f"Usuario {pareja.jugador2_id}"
        
        resultado.append({
            "id": pareja.id,
            "torneo_id": pareja.torneo_id,
            "categoria_id": pareja.categoria_id,
            "categoria_nombre": categoria.nombre if categoria else None,
            "jugador1_id": pareja.jugador1_id,
            "jugador2_id": pareja.jugador2_id,
            "jugador1_nombre": j1_nombre,
            "jugador2_nombre": j2_nombre,
            "jugador1_username": usuario1.nombre_usuario if usuario1 else None,
            "jugador2_username": usuario2.nombre_usuario if usuario2 else None,
            "nombre_pareja": f"{j1_nombre} / {j2_nombre}",
            "estado": pareja.estado.value if hasattr(pareja.estado, 'value') else str(pareja.estado),
            "created_at": pareja.created_at.isoformat() if pareja.created_at else None
        })
    
    return resultado


@router.patch("/{torneo_id}/parejas/{pareja_id}/confirmar")
def confirmar_pareja(
    torneo_id: int,
    pareja_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Confirma una pareja (solo organizadores)"""
    from ...services.torneo_inscripcion_service import TorneoInscripcionService
    
    try:
        pareja = TorneoInscripcionService.confirmar_pareja(db, pareja_id, current_user.id_usuario)
        return {"message": "Pareja confirmada", "id": pareja.id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{torneo_id}/parejas/{pareja_id}/baja")
def dar_baja_pareja(
    torneo_id: int,
    pareja_id: int,
    motivo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Da de baja una pareja"""
    from ...services.torneo_inscripcion_service import TorneoInscripcionService
    
    try:
        pareja = TorneoInscripcionService.dar_baja_pareja(db, pareja_id, current_user.id_usuario, motivo)
        return {"message": "Pareja dada de baja", "id": pareja.id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
