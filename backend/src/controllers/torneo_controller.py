"""
Controller para endpoints de torneos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..database.config import get_db
from ..services.torneo_service import TorneoService
from ..services.torneo_inscripcion_service import TorneoInscripcionService
from ..schemas.torneo_schemas import (
    TorneoCreate, TorneoUpdate, TorneoResponse,
    EstadisticasTorneoResponse,
    ParejaInscripcion, ParejaUpdate, ParejaResponse
)
from ..auth.auth_utils import get_current_user
from ..models.driveplus_models import Usuario

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


@router.get("/")
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
    from ..models.torneo_models import TorneoPareja
    
    try:
        torneos = TorneoService.listar_torneos(db, skip, limit, estado, categoria)
        
        # Agregar conteo de parejas a cada torneo
        resultado = []
        for torneo in torneos:
            # Contar parejas inscritas
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
                "updated_at": torneo.updated_at.isoformat() if torneo.updated_at else None,
                "parejas_inscritas": parejas_count,
                "total_partidos": 0  # TODO: contar partidos
            })
        
        return resultado
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/mis-torneos")
def obtener_mis_torneos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene los torneos donde el usuario está inscripto (como jugador1 o jugador2)
    """
    from ..models.torneo_models import TorneoPareja, Torneo
    from sqlalchemy import or_
    
    try:
        # Buscar parejas donde el usuario participa
        parejas = db.query(TorneoPareja).filter(
            or_(
                TorneoPareja.jugador1_id == current_user.id_usuario,
                TorneoPareja.jugador2_id == current_user.id_usuario
            ),
            TorneoPareja.estado.in_(['inscripta', 'confirmada'])  # Removido 'pendiente' que no existe en el enum
        ).all()
        
        if not parejas:
            return {"torneos": []}
        
        # Obtener IDs únicos de torneos
        torneo_ids = list(set(p.torneo_id for p in parejas))
        
        # Obtener info de los torneos
        torneos = db.query(Torneo).filter(Torneo.id.in_(torneo_ids)).all()
        
        # Crear dict de parejas por torneo para incluir estado de inscripción
        parejas_por_torneo = {}
        for p in parejas:
            parejas_por_torneo[p.torneo_id] = {
                "pareja_id": p.id,
                "estado_inscripcion": p.estado.value if hasattr(p.estado, 'value') else str(p.estado),
                "categoria_id": p.categoria_id
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
                "genero": torneo.genero or 'masculino',
                "estado": torneo.estado.value if hasattr(torneo.estado, 'value') else str(torneo.estado),
                "fecha_inicio": torneo.fecha_inicio.isoformat() if torneo.fecha_inicio else None,
                "fecha_fin": torneo.fecha_fin.isoformat() if torneo.fecha_fin else None,
                "lugar": torneo.lugar,
                "mi_inscripcion": info_pareja
            })
        
        return {"torneos": resultado}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}")
def obtener_torneo(
    torneo_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene un torneo por ID"""
    from ..models.torneo_models import TorneoPareja
    
    torneo = TorneoService.obtener_torneo(db, torneo_id)
    if not torneo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Torneo no encontrado")
    
    # Contar parejas inscritas
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
        "updated_at": torneo.updated_at.isoformat() if torneo.updated_at else None,
        "parejas_inscritas": parejas_count,
        "total_partidos": 0
    }


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
    from ..models.driveplus_models import Partido
    
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
# ENDPOINTS DE CATEGORÍAS
# ============================================

class CategoriaCreateBody(BaseModel):
    nombre: str
    genero: str = "masculino"
    max_parejas: int = 16
    orden: int = 0


@router.post("/{torneo_id}/categorias", status_code=status.HTTP_201_CREATED)
def crear_categoria(
    torneo_id: int,
    categoria_data: CategoriaCreateBody,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crea una nueva categoría en el torneo (8va, 6ta, 4ta, Libre, etc.)"""
    from ..models.torneo_models import TorneoCategoria
    from ..services.torneo_zona_service import TorneoZonaService
    
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{torneo_id}/categorias")
def listar_categorias(
    torneo_id: int,
    db: Session = Depends(get_db)
):
    """Lista todas las categorías del torneo con conteo de parejas"""
    from ..models.torneo_models import TorneoCategoria, TorneoPareja
    
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


@router.put("/{torneo_id}/categorias/{categoria_id}")
def actualizar_categoria(
    torneo_id: int,
    categoria_id: int,
    categoria_data: CategoriaCreateBody,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualiza una categoría del torneo"""
    from ..models.torneo_models import TorneoCategoria
    from ..services.torneo_zona_service import TorneoZonaService
    
    if not TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario):
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    categoria = db.query(TorneoCategoria).filter(
        TorneoCategoria.id == categoria_id,
        TorneoCategoria.torneo_id == torneo_id
    ).first()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    categoria.nombre = categoria_data.nombre
    categoria.genero = categoria_data.genero
    categoria.max_parejas = categoria_data.max_parejas
    categoria.orden = categoria_data.orden
    db.commit()
    
    return {"message": "Categoría actualizada", "id": categoria.id}


@router.delete("/{torneo_id}/categorias/{categoria_id}")
def eliminar_categoria(
    torneo_id: int,
    categoria_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Elimina una categoría (solo si no tiene parejas inscritas)"""
    from ..models.torneo_models import TorneoCategoria, TorneoPareja
    from ..services.torneo_zona_service import TorneoZonaService
    
    if not TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario):
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    # Verificar que no tenga parejas
    parejas_count = db.query(TorneoPareja).filter(
        TorneoPareja.categoria_id == categoria_id
    ).count()
    
    if parejas_count > 0:
        raise HTTPException(status_code=400, detail=f"No se puede eliminar: hay {parejas_count} parejas inscritas")
    
    db.query(TorneoCategoria).filter(
        TorneoCategoria.id == categoria_id,
        TorneoCategoria.torneo_id == torneo_id
    ).delete()
    db.commit()
    
    return {"message": "Categoría eliminada"}


# ============================================
# ENDPOINTS DE INSCRIPCIONES
# ============================================

@router.post("/{torneo_id}/inscribir", status_code=status.HTTP_201_CREATED)
def inscribir_pareja(
    torneo_id: int,
    pareja_data: ParejaInscripcion,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Inscribe una pareja en el torneo (requiere confirmación del compañero)
    
    Retorna un código que el compañero debe usar para confirmar.
    También se envía notificación push al compañero.
    """
    from ..services.torneo_confirmacion_service import TorneoConfirmacionService
    
    try:
        user_id = current_user.id_usuario
        resultado = TorneoConfirmacionService.crear_inscripcion_pendiente(
            db=db,
            torneo_id=torneo_id,
            jugador1_id=pareja_data.jugador1_id,
            jugador2_id=pareja_data.jugador2_id,
            categoria_id=getattr(pareja_data, 'categoria_id', None),
            creador_id=user_id,
            observaciones=pareja_data.observaciones
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/confirmar-pareja/{codigo}")
def confirmar_pareja_por_codigo(
    codigo: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Confirma una inscripción usando el código recibido
    """
    from ..services.torneo_confirmacion_service import TorneoConfirmacionService
    
    try:
        pareja = TorneoConfirmacionService.confirmar_por_codigo(
            db=db,
            codigo=codigo,
            user_id=current_user.id_usuario
        )
        return {
            "mensaje": "Inscripción confirmada exitosamente",
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
    """
    Rechaza una invitación de pareja
    """
    from ..services.torneo_confirmacion_service import TorneoConfirmacionService
    
    try:
        TorneoConfirmacionService.rechazar_invitacion(
            db=db,
            pareja_id=pareja_id,
            user_id=current_user.id_usuario,
            motivo=motivo
        )
        return {"mensaje": "Invitación rechazada"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/mis-invitaciones")
def obtener_mis_invitaciones(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene las invitaciones pendientes del usuario actual
    """
    try:
        # Simplificar temporalmente para debug
        from ..models.torneo_models import TorneoPareja, Torneo
        from ..models.driveplus_models import PerfilUsuario
        
        # Buscar parejas donde el usuario es jugador2 y está pendiente
        parejas = db.query(TorneoPareja).filter(
            TorneoPareja.jugador2_id == current_user.id_usuario,
            TorneoPareja.estado == 'pendiente'
        ).all()
        
        resultado = []
        for pareja in parejas:
            # Obtener info del torneo
            torneo = db.query(Torneo).filter(Torneo.id == pareja.torneo_id).first()
            
            # Obtener info del compañero (jugador1)
            perfil_companero = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == pareja.jugador1_id
            ).first()
            
            resultado.append({
                'pareja_id': pareja.id,
                'torneo_id': pareja.torneo_id,
                'torneo_nombre': torneo.nombre if torneo else 'Torneo',
                'companero_id': pareja.jugador1_id,
                'companero_nombre': f"{perfil_companero.nombre} {perfil_companero.apellido}" if perfil_companero else 'Jugador',
                'fecha_expiracion': getattr(pareja, 'fecha_expiracion', None),
                'codigo_confirmacion': getattr(pareja, 'codigo_confirmacion', None)
            })
        
        return {"invitaciones": resultado}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener invitaciones: {str(e)}"
        )


@router.get("/{torneo_id}/parejas")
def listar_parejas(
    torneo_id: int,
    estado: Optional[str] = None,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todas las parejas inscritas en el torneo
    
    - **estado**: Filtrar por estado (inscripta, confirmada, baja)
    - **categoria_id**: Filtrar por categoría (opcional)
    """
    from ..models.torneo_models import TorneoPareja, TorneoCategoria
    from ..models.driveplus_models import PerfilUsuario
    
    try:
        # Query optimizada
        query = db.query(TorneoPareja).filter(TorneoPareja.torneo_id == torneo_id)
        
        if estado:
            query = query.filter(TorneoPareja.estado == estado)
        
        if categoria_id:
            query = query.filter(TorneoPareja.categoria_id == categoria_id)
        
        parejas = query.all()
        
        if not parejas:
            return []
        
        # PRE-CARGAR perfiles y categorías (optimización)
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
        
        resultado = []
        for pareja in parejas:
            perfil1 = perfiles_dict.get(pareja.jugador1_id)
            perfil2 = perfiles_dict.get(pareja.jugador2_id)
            categoria = categorias_dict.get(pareja.categoria_id) if pareja.categoria_id else None
            
            jugador1_nombre = f"{perfil1.nombre} {perfil1.apellido}" if perfil1 else f"Usuario {pareja.jugador1_id}"
            jugador2_nombre = f"{perfil2.nombre} {perfil2.apellido}" if perfil2 else f"Usuario {pareja.jugador2_id}"
            
            resultado.append({
                "id": pareja.id,
                "id_pareja": pareja.id,
                "torneo_id": pareja.torneo_id,
                "categoria_id": pareja.categoria_id,
                "categoria_nombre": categoria.nombre if categoria else None,
                "categoria_genero": categoria.genero if categoria else None,
                "jugador1_id": pareja.jugador1_id,
                "jugador2_id": pareja.jugador2_id,
                "jugador1_nombre": jugador1_nombre,
                "jugador2_nombre": jugador2_nombre,
                "nombre_pareja": f"{jugador1_nombre} / {jugador2_nombre}",
                "estado": pareja.estado.value if hasattr(pareja.estado, 'value') else str(pareja.estado).replace('EstadoPareja.', '').lower(),
                "categoria_asignada": pareja.categoria_asignada,
                "created_at": pareja.created_at.isoformat() if pareja.created_at else None
            })
        
        return resultado
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def _pareja_to_dict(db: Session, pareja) -> dict:
    """Helper para convertir pareja a dict con nombres de jugadores"""
    from ..models.driveplus_models import PerfilUsuario
    perfil1 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja.jugador1_id).first()
    perfil2 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja.jugador2_id).first()
    jugador1_nombre = f"{perfil1.nombre} {perfil1.apellido}" if perfil1 else f"Usuario {pareja.jugador1_id}"
    jugador2_nombre = f"{perfil2.nombre} {perfil2.apellido}" if perfil2 else f"Usuario {pareja.jugador2_id}"
    return {
        "id": pareja.id,
        "id_pareja": pareja.id,
        "torneo_id": pareja.torneo_id,
        "jugador1_id": pareja.jugador1_id,
        "jugador2_id": pareja.jugador2_id,
        "jugador1_nombre": jugador1_nombre,
        "jugador2_nombre": jugador2_nombre,
        "nombre_pareja": f"{jugador1_nombre} / {jugador2_nombre}",
        "estado": pareja.estado.value if hasattr(pareja.estado, 'value') else str(pareja.estado),
        "categoria_asignada": pareja.categoria_asignada,
        "created_at": pareja.created_at.isoformat() if pareja.created_at else None
    }


@router.patch("/{torneo_id}/parejas/{pareja_id}/confirmar")
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
        return _pareja_to_dict(db, pareja)
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


@router.patch("/{torneo_id}/parejas/{pareja_id}/baja")
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
        return _pareja_to_dict(db, pareja)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{torneo_id}/parejas/{pareja_id}/reemplazar-jugador")
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
        return _pareja_to_dict(db, pareja)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{torneo_id}/parejas/{pareja_id}")
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
        return _pareja_to_dict(db, pareja)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# ENDPOINTS DE ZONAS
# ============================================

@router.post("/{torneo_id}/generar-zonas")
@router.post("/{torneo_id}/zonas/generar")  # Alias para compatibilidad con frontend
def generar_zonas(
    torneo_id: int,
    num_zonas: Optional[int] = None,
    balancear_por_rating: bool = True,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Genera zonas automáticamente y distribuye parejas
    
    Solo organizadores pueden generar zonas
    
    - **num_zonas**: Número de zonas (opcional, se calcula automáticamente)
    - **balancear_por_rating**: Si True, distribuye parejas por rating
    - **categoria_id**: ID de categoría (opcional, si se pasa genera solo para esa categoría)
    """
    from ..services.torneo_zona_service import TorneoZonaService
    
    try:
        user_id = current_user.id_usuario
        zonas = TorneoZonaService.generar_zonas_automaticas(
            db, torneo_id, user_id, num_zonas, balancear_por_rating, categoria_id
        )
        return {
            "message": "Zonas generadas exitosamente",
            "zonas": [{"id": z.id, "nombre": z.nombre, "numero": z.numero_orden, "categoria_id": z.categoria_id} for z in zonas]
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}/zonas")
def listar_zonas(
    torneo_id: int,
    db: Session = Depends(get_db)
):
    """Lista todas las zonas del torneo con sus parejas"""
    from ..services.torneo_zona_service import TorneoZonaService
    from ..models.driveplus_models import PerfilUsuario
    
    try:
        zonas = TorneoZonaService.listar_zonas(db, torneo_id)
        
        # Agregar nombres a cada pareja en cada zona
        for zona in zonas:
            if 'parejas' in zona:
                for pareja in zona['parejas']:
                    perfil1 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja['jugador1_id']).first()
                    perfil2 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja['jugador2_id']).first()
                    
                    nombre1 = f"{perfil1.nombre} {perfil1.apellido}" if perfil1 else f"Jugador {pareja['jugador1_id']}"
                    nombre2 = f"{perfil2.nombre} {perfil2.apellido}" if perfil2 else f"Jugador {pareja['jugador2_id']}"
                    
                    pareja['pareja_nombre'] = f"{nombre1} / {nombre2}"
        
        return zonas
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}/zonas/{zona_id}/tabla")
def obtener_tabla_zona(
    torneo_id: int,
    zona_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene la tabla de posiciones de una zona"""
    from ..services.torneo_zona_service import TorneoZonaService
    from ..models.driveplus_models import PerfilUsuario
    
    try:
        tabla = TorneoZonaService.obtener_tabla_posiciones(db, zona_id)
        
        # Agregar nombres de jugadores a cada pareja
        for item in tabla['tabla']:
            perfil1 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == item['jugador1_id']).first()
            perfil2 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == item['jugador2_id']).first()
            
            nombre1 = f"{perfil1.nombre} {perfil1.apellido}" if perfil1 else f"Jugador {item['jugador1_id']}"
            nombre2 = f"{perfil2.nombre} {perfil2.apellido}" if perfil2 else f"Jugador {item['jugador2_id']}"
            
            item['pareja_nombre'] = f"{nombre1} / {nombre2}"
        
        return tabla
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{torneo_id}/zonas/mover-pareja")
def mover_pareja(
    torneo_id: int,
    pareja_id: int,
    zona_destino_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Mueve una pareja de una zona a otra
    
    Solo organizadores pueden mover parejas
    """
    from ..services.torneo_zona_service import TorneoZonaService
    
    try:
        user_id = current_user.id_usuario
        result = TorneoZonaService.mover_pareja_entre_zonas(
            db, pareja_id, zona_destino_id, user_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# ENDPOINTS DE FIXTURE
# ============================================

@router.post("/{torneo_id}/generar-zonas-inteligente")
def generar_zonas_inteligente(
    torneo_id: int,
    num_zonas: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Genera zonas considerando disponibilidad horaria y balanceo por rating
    
    Prioridad 1: Compatibilidad horaria
    Prioridad 2: Balanceo por rating
    
    Solo organizadores pueden generar zonas
    """
    from ..services.torneo_fixture_service import TorneoFixtureService
    
    try:
        user_id = current_user.id_usuario
        zonas = TorneoFixtureService.generar_zonas_con_disponibilidad(
            db, torneo_id, user_id, num_zonas
        )
        return {
            "message": "Zonas generadas con criterio de disponibilidad horaria",
            "zonas": [{"id": z.id, "nombre": z.nombre, "numero": z.numero_orden} for z in zonas]
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{torneo_id}/generar-fixture")
def generar_fixture(
    torneo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Genera el fixture completo del torneo (todos los partidos de todas las zonas)
    
    Solo organizadores pueden generar fixture
    """
    from ..services.torneo_fixture_service import TorneoFixtureService
    
    try:
        user_id = current_user.id_usuario
        resultado = TorneoFixtureService.generar_fixture_completo(db, torneo_id, user_id)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}/partidos")
def listar_partidos_torneo(
    torneo_id: int,
    zona_id: Optional[int] = None,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos los partidos del torneo
    
    - **zona_id**: Filtrar por zona (opcional)
    - **categoria_id**: Filtrar por categoría (opcional)
    """
    from ..models.driveplus_models import Partido, PerfilUsuario
    from ..models.torneo_models import TorneoPareja
    
    try:
        query = db.query(Partido).filter(Partido.id_torneo == torneo_id)
        
        if zona_id is not None:
            query = query.filter(Partido.zona_id == zona_id)
        
        if categoria_id is not None:
            query = query.filter(Partido.categoria_id == categoria_id)
        
        partidos = query.all()
        
        if not partidos:
            return {"total": 0, "partidos": []}
        
        # PRE-CARGAR todas las parejas del torneo (optimización)
        parejas = db.query(TorneoPareja).filter(TorneoPareja.torneo_id == torneo_id).all()
        parejas_dict = {p.id: p for p in parejas}
        
        # PRE-CARGAR todos los perfiles de jugadores involucrados
        jugadores_ids = set()
        for p in parejas:
            jugadores_ids.add(p.jugador1_id)
            jugadores_ids.add(p.jugador2_id)
        
        perfiles = db.query(PerfilUsuario).filter(
            PerfilUsuario.id_usuario.in_(jugadores_ids)
        ).all() if jugadores_ids else []
        perfiles_dict = {p.id_usuario: p for p in perfiles}
        
        # Helper para obtener nombre de pareja
        def get_nombre_pareja(pareja_id):
            if not pareja_id:
                return "TBD"
            pareja = parejas_dict.get(pareja_id)
            if not pareja:
                return "TBD"
            p1 = perfiles_dict.get(pareja.jugador1_id)
            p2 = perfiles_dict.get(pareja.jugador2_id)
            n1 = f"{p1.nombre} {p1.apellido}" if p1 else f"Jugador {pareja.jugador1_id}"
            n2 = f"{p2.nombre} {p2.apellido}" if p2 else f"Jugador {pareja.jugador2_id}"
            return f"{n1} / {n2}"
        
        resultado = [
            {
                "id_partido": p.id_partido,
                "pareja1_id": p.pareja1_id,
                "pareja2_id": p.pareja2_id,
                "pareja1_nombre": get_nombre_pareja(p.pareja1_id),
                "pareja2_nombre": get_nombre_pareja(p.pareja2_id),
                "zona_id": p.zona_id,
                "categoria_id": getattr(p, 'categoria_id', None),
                "fase": p.fase,
                "estado": p.estado,
                "fecha_hora": p.fecha_hora.isoformat() if p.fecha_hora else None,
                "cancha_id": p.cancha_id,
                "ganador_pareja_id": p.ganador_pareja_id,
                "resultado_padel": p.resultado_padel
            }
            for p in partidos
        ]
        
        return {"total": len(resultado), "partidos": resultado}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# ENDPOINTS DE RESULTADOS
# ============================================

@router.post("/{torneo_id}/partidos/{partido_id}/resultado")
def cargar_resultado_partido(
    torneo_id: int,
    partido_id: int,
    resultado: dict,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Carga el resultado de un partido de torneo
    
    El resultado debe incluir:
    - sets: Lista de sets con gamesEquipoA, gamesEquipoB, ganador
    - Mínimo 2 sets, máximo 3
    - Un equipo debe ganar al menos 2 sets
    
    Solo organizadores pueden cargar resultados
    """
    from ..services.torneo_resultado_service import TorneoResultadoService
    
    try:
        user_id = current_user.id_usuario
        partido = TorneoResultadoService.cargar_resultado(
            db, partido_id, resultado, user_id
        )
        return {
            "message": "Resultado cargado exitosamente",
            "partido_id": partido.id_partido,
            "ganador_pareja_id": partido.ganador_pareja_id,
            "elo_aplicado": partido.elo_aplicado
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{torneo_id}/partidos/{partido_id}/resultado")
def corregir_resultado_partido(
    torneo_id: int,
    partido_id: int,
    resultado: dict,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Corrige el resultado de un partido ya finalizado
    
    Solo organizadores pueden corregir resultados
    """
    from ..services.torneo_resultado_service import TorneoResultadoService
    
    try:
        user_id = current_user.id_usuario
        partido = TorneoResultadoService.corregir_resultado(
            db, partido_id, resultado, user_id
        )
        return {
            "message": "Resultado corregido exitosamente",
            "partido_id": partido.id_partido,
            "ganador_pareja_id": partido.ganador_pareja_id
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}/partidos/{partido_id}/estadisticas")
def obtener_estadisticas_partido(
    torneo_id: int,
    partido_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene estadísticas detalladas de un partido"""
    from ..services.torneo_resultado_service import TorneoResultadoService
    
    try:
        estadisticas = TorneoResultadoService.obtener_estadisticas_partido(db, partido_id)
        return estadisticas
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}/zonas/{zona_id}/clasificados")
def obtener_clasificados_zona(
    torneo_id: int,
    zona_id: int,
    num_clasificados: int = 2,
    db: Session = Depends(get_db)
):
    """
    Obtiene las parejas clasificadas de una zona
    
    - **num_clasificados**: Número de parejas que clasifican (default: 2)
    """
    from ..services.torneo_resultado_service import TorneoResultadoService
    
    try:
        clasificados = TorneoResultadoService.obtener_clasificados_zona(
            db, zona_id, num_clasificados
        )
        return {
            "zona_id": zona_id,
            "num_clasificados": num_clasificados,
            "clasificados": clasificados
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}/zonas/{zona_id}/completa")
def verificar_zona_completa(
    torneo_id: int,
    zona_id: int,
    db: Session = Depends(get_db)
):
    """Verifica si todos los partidos de una zona están finalizados"""
    from ..services.torneo_resultado_service import TorneoResultadoService
    
    try:
        completa = TorneoResultadoService.verificar_zona_completa(db, zona_id)
        return {
            "zona_id": zona_id,
            "completa": completa
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# ENDPOINTS DE PLAYOFFS
# ============================================

@router.post("/{torneo_id}/generar-playoffs")
def generar_playoffs(
    torneo_id: int,
    clasificados_por_zona: int = 2,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Genera el cuadro de playoffs automáticamente
    
    Solo organizadores pueden generar playoffs
    El torneo debe estar en fase de grupos
    
    - **clasificados_por_zona**: Número de clasificados por zona (default: 2)
    """
    from ..services.torneo_playoff_service import TorneoPlayoffService
    
    try:
        user_id = current_user.id_usuario
        partidos = TorneoPlayoffService.generar_playoffs(
            db, torneo_id, user_id, clasificados_por_zona
        )
        return {
            "message": "Playoffs generados exitosamente",
            "total_partidos": len(partidos),
            "partidos": [
                {
                    "id": p.id_partido,
                    "fase": p.fase.value if hasattr(p.fase, 'value') else str(p.fase),
                    "numero_partido": p.numero_partido,
                    "pareja1_id": p.pareja1_id,
                    "pareja2_id": p.pareja2_id
                }
                for p in partidos
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}/playoffs")
def listar_partidos_playoffs(
    torneo_id: int,
    categoria_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos los partidos de playoffs agrupados por fase
    
    - **categoria_id**: Filtrar por categoría (opcional)
    """
    from ..services.torneo_playoff_service import TorneoPlayoffService
    from ..models.driveplus_models import PerfilUsuario
    from ..models.torneo_models import TorneoPareja
    
    try:
        partidos_por_fase = TorneoPlayoffService.listar_partidos_playoffs(db, torneo_id, categoria_id)
        
        # PRE-CARGAR todas las parejas y perfiles (optimización)
        parejas = db.query(TorneoPareja).filter(TorneoPareja.torneo_id == torneo_id).all()
        parejas_dict = {p.id: p for p in parejas}
        
        jugadores_ids = set()
        for p in parejas:
            jugadores_ids.add(p.jugador1_id)
            jugadores_ids.add(p.jugador2_id)
        
        perfiles = db.query(PerfilUsuario).filter(
            PerfilUsuario.id_usuario.in_(jugadores_ids)
        ).all() if jugadores_ids else []
        perfiles_dict = {p.id_usuario: p for p in perfiles}
        
        def get_nombre_pareja(pareja_id):
            if not pareja_id:
                return None
            pareja = parejas_dict.get(pareja_id)
            if not pareja:
                return None
            p1 = perfiles_dict.get(pareja.jugador1_id)
            p2 = perfiles_dict.get(pareja.jugador2_id)
            n1 = f"{p1.nombre} {p1.apellido}" if p1 else f"Jugador {pareja.jugador1_id}"
            n2 = f"{p2.nombre} {p2.apellido}" if p2 else f"Jugador {pareja.jugador2_id}"
            return f"{n1} / {n2}"
        
        resultado = {}
        for fase, partidos in partidos_por_fase.items():
            resultado[fase] = [
                {
                    "id": p.id_partido,
                    "numero_partido": p.numero_partido,
                    "pareja1_id": p.pareja1_id,
                    "pareja2_id": p.pareja2_id,
                    "pareja1_nombre": get_nombre_pareja(p.pareja1_id),
                    "pareja2_nombre": get_nombre_pareja(p.pareja2_id),
                    "ganador_id": p.ganador_pareja_id,
                    "resultado": p.resultado_padel,
                    "fase": fase,
                    "categoria_id": getattr(p, 'categoria_id', None),
                    "estado": p.estado.value if hasattr(p.estado, 'value') else str(p.estado)
                }
                for p in partidos
            ]
        
        todos_partidos = []
        for partidos_fase in resultado.values():
            todos_partidos.extend(partidos_fase)
        
        return {"partidos": todos_partidos, "por_fase": resultado}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}/playoffs/partidos")
def listar_todos_partidos_playoffs(
    torneo_id: int,
    db: Session = Depends(get_db)
):
    """
    Lista todos los partidos de playoffs en una sola lista (sin agrupar)
    """
    from ..models.torneo_models import FasePartido, TorneoPareja
    from ..models.driveplus_models import Partido, PerfilUsuario
    
    try:
        partidos = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase != FasePartido.ZONA.value
        ).order_by(Partido.numero_partido).all()
        
        if not partidos:
            return {"total": 0, "partidos": []}
        
        # PRE-CARGAR parejas y perfiles (optimización)
        parejas = db.query(TorneoPareja).filter(TorneoPareja.torneo_id == torneo_id).all()
        parejas_dict = {p.id: p for p in parejas}
        
        jugadores_ids = set()
        for p in parejas:
            jugadores_ids.add(p.jugador1_id)
            jugadores_ids.add(p.jugador2_id)
        
        perfiles = db.query(PerfilUsuario).filter(
            PerfilUsuario.id_usuario.in_(jugadores_ids)
        ).all() if jugadores_ids else []
        perfiles_dict = {p.id_usuario: p for p in perfiles}
        
        def get_nombre_pareja(pareja_id):
            if not pareja_id:
                return None
            pareja = parejas_dict.get(pareja_id)
            if not pareja:
                return None
            p1 = perfiles_dict.get(pareja.jugador1_id)
            p2 = perfiles_dict.get(pareja.jugador2_id)
            n1 = f"{p1.nombre} {p1.apellido}" if p1 else f"Jugador {pareja.jugador1_id}"
            n2 = f"{p2.nombre} {p2.apellido}" if p2 else f"Jugador {pareja.jugador2_id}"
            return f"{n1} / {n2}"
        
        resultado = [
            {
                "id": p.id_partido,
                "numero_partido": p.numero_partido,
                "pareja1_id": p.pareja1_id,
                "pareja2_id": p.pareja2_id,
                "pareja1_nombre": get_nombre_pareja(p.pareja1_id),
                "pareja2_nombre": get_nombre_pareja(p.pareja2_id),
                "ganador_id": p.ganador_pareja_id,
                "resultado": p.resultado_padel,
                "fase": p.fase,
                "categoria_id": getattr(p, 'categoria_id', None),
                "estado": p.estado
            }
            for p in partidos
        ]
        
        return {"total": len(resultado), "partidos": resultado}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# ENDPOINTS DE CANCHAS Y PROGRAMACIÓN
# ============================================

class CanchaCreate(BaseModel):
    nombre: str
    activa: bool = True

@router.post("/{torneo_id}/canchas")
def crear_cancha(
    torneo_id: int,
    cancha_data: CanchaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea una cancha para el torneo
    
    Solo organizadores pueden crear canchas
    
    Body:
    - nombre: Nombre de la cancha
    - activa: Si está activa (default: true)
    """
    from ..models.torneo_models import TorneoCancha
    from ..services.torneo_zona_service import TorneoZonaService
    
    try:
        if not TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario):
            raise HTTPException(status_code=403, detail="No tienes permisos")
        
        cancha = TorneoCancha(
            torneo_id=torneo_id,
            nombre=cancha_data.nombre,
            activa=cancha_data.activa
        )
        db.add(cancha)
        db.commit()
        db.refresh(cancha)
        
        return {
            "id": cancha.id,
            "torneo_id": cancha.torneo_id,
            "nombre": cancha.nombre,
            "activa": cancha.activa
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{torneo_id}/canchas")
def listar_canchas(
    torneo_id: int,
    db: Session = Depends(get_db)
):
    """Lista todas las canchas del torneo"""
    from ..models.torneo_models import TorneoCancha
    
    canchas = db.query(TorneoCancha).filter(
        TorneoCancha.torneo_id == torneo_id,
        TorneoCancha.activa == True
    ).all()
    
    return [
        {
            "id": c.id,
            "nombre": c.nombre,
            "activa": c.activa
        }
        for c in canchas
    ]


@router.delete("/{torneo_id}/canchas/{cancha_id}")
def eliminar_cancha(
    torneo_id: int,
    cancha_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Desactiva una cancha"""
    from ..models.torneo_models import TorneoCancha
    from ..services.torneo_zona_service import TorneoZonaService
    
    if not TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario):
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    cancha = db.query(TorneoCancha).filter(
        TorneoCancha.id == cancha_id,
        TorneoCancha.torneo_id == torneo_id
    ).first()
    
    if not cancha:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    
    cancha.activa = False
    db.commit()
    
    return {"message": "Cancha eliminada"}


@router.post("/{torneo_id}/slots")
def crear_slots(
    torneo_id: int,
    fecha: str,
    hora_inicio: str,
    hora_fin: str,
    duracion_minutos: int = 90,
    cancha_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea slots de horarios para un día
    
    - **fecha**: Fecha en formato YYYY-MM-DD
    - **hora_inicio**: Hora de inicio (ej: "09:00")
    - **hora_fin**: Hora de fin (ej: "21:00")
    - **duracion_minutos**: Duración de cada slot (default 90 min)
    - **cancha_ids**: Lista de canchas (opcional, si no se especifica usa todas)
    """
    from ..models.torneo_models import TorneoCancha, TorneoSlot
    from ..services.torneo_zona_service import TorneoZonaService
    from datetime import datetime, timedelta
    
    try:
        if not TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario):
            raise HTTPException(status_code=403, detail="No tienes permisos")
        
        # Parsear fecha y horas
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        hora_inicio_parts = hora_inicio.split(":")
        hora_fin_parts = hora_fin.split(":")
        
        hora_actual = datetime.combine(
            fecha_dt,
            datetime.strptime(hora_inicio, "%H:%M").time()
        )
        hora_limite = datetime.combine(
            fecha_dt,
            datetime.strptime(hora_fin, "%H:%M").time()
        )
        
        # Obtener canchas
        if cancha_ids:
            canchas = db.query(TorneoCancha).filter(
                TorneoCancha.id.in_(cancha_ids),
                TorneoCancha.torneo_id == torneo_id,
                TorneoCancha.activa == True
            ).all()
        else:
            canchas = db.query(TorneoCancha).filter(
                TorneoCancha.torneo_id == torneo_id,
                TorneoCancha.activa == True
            ).all()
        
        if not canchas:
            raise HTTPException(status_code=400, detail="No hay canchas disponibles")
        
        # Crear slots
        slots_creados = 0
        while hora_actual + timedelta(minutes=duracion_minutos) <= hora_limite:
            for cancha in canchas:
                # Verificar si ya existe el slot
                existe = db.query(TorneoSlot).filter(
                    TorneoSlot.torneo_id == torneo_id,
                    TorneoSlot.cancha_id == cancha.id,
                    TorneoSlot.fecha_hora_inicio == hora_actual
                ).first()
                
                if not existe:
                    slot = TorneoSlot(
                        torneo_id=torneo_id,
                        cancha_id=cancha.id,
                        fecha_hora_inicio=hora_actual,
                        fecha_hora_fin=hora_actual + timedelta(minutes=duracion_minutos),
                        ocupado=False
                    )
                    db.add(slot)
                    slots_creados += 1
            
            hora_actual += timedelta(minutes=duracion_minutos)
        
        db.commit()
        
        return {
            "message": f"Se crearon {slots_creados} slots",
            "fecha": fecha,
            "canchas": len(canchas),
            "slots_por_cancha": slots_creados // len(canchas) if canchas else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{torneo_id}/slots")
def listar_slots(
    torneo_id: int,
    fecha: Optional[str] = None,
    solo_disponibles: bool = False,
    db: Session = Depends(get_db)
):
    """
    Lista slots de horarios
    
    - **fecha**: Filtrar por fecha (YYYY-MM-DD)
    - **solo_disponibles**: Solo mostrar slots no ocupados
    """
    from ..models.torneo_models import TorneoSlot, TorneoCancha
    from datetime import datetime
    
    query = db.query(TorneoSlot).filter(TorneoSlot.torneo_id == torneo_id)
    
    if fecha:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        query = query.filter(
            TorneoSlot.fecha_hora_inicio >= datetime.combine(fecha_dt, datetime.min.time()),
            TorneoSlot.fecha_hora_inicio < datetime.combine(fecha_dt, datetime.max.time())
        )
    
    if solo_disponibles:
        query = query.filter(TorneoSlot.ocupado == False)
    
    slots = query.order_by(TorneoSlot.fecha_hora_inicio, TorneoSlot.cancha_id).all()
    
    # PRE-CARGAR todas las canchas de una vez (optimización)
    canchas = db.query(TorneoCancha).filter(TorneoCancha.torneo_id == torneo_id).all()
    canchas_dict = {c.id: c.nombre for c in canchas}
    
    resultado = [
        {
            "id": s.id,
            "cancha_id": s.cancha_id,
            "cancha_nombre": canchas_dict.get(s.cancha_id),
            "fecha_hora_inicio": s.fecha_hora_inicio.isoformat() if s.fecha_hora_inicio else None,
            "fecha_hora_fin": s.fecha_hora_fin.isoformat() if s.fecha_hora_fin else None,
            "ocupado": s.ocupado,
            "partido_id": s.partido_id
        }
        for s in slots
    ]
    
    return resultado


class ProgramacionParams(BaseModel):
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    duracion_partido_minutos: int = 90
    # Horarios para días de semana (Lun-Vie)
    hora_inicio_semana: Optional[str] = "17:00"
    hora_fin_semana: Optional[str] = "22:00"
    # Horarios para fin de semana (Sab-Dom)
    hora_inicio_finde: Optional[str] = "09:00"
    hora_fin_finde: Optional[str] = "21:00"


@router.delete("/{torneo_id}/limpiar-programacion")
def limpiar_programacion(
    torneo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Limpia toda la programación del torneo:
    - Elimina todos los slots
    - Desprograma todos los partidos (quita fecha_hora y cancha_id)
    
    Solo organizadores pueden limpiar la programación
    """
    from ..models.torneo_models import TorneoSlot
    from ..models.driveplus_models import Partido
    from ..services.torneo_zona_service import TorneoZonaService
    
    try:
        if not TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario):
            raise HTTPException(status_code=403, detail="No tienes permisos")
        
        # Contar antes de borrar
        slots_count = db.query(TorneoSlot).filter(TorneoSlot.torneo_id == torneo_id).count()
        
        # Desprogramar partidos (quitar fecha y cancha, pero no borrarlos)
        partidos_desprogramados = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.cancha_id != None
        ).update({
            "cancha_id": None,
            "fecha_hora": None
        }, synchronize_session=False)
        
        # Eliminar todos los slots
        db.query(TorneoSlot).filter(TorneoSlot.torneo_id == torneo_id).delete(synchronize_session=False)
        
        db.commit()
        
        return {
            "message": "Programación limpiada exitosamente",
            "slots_eliminados": slots_count,
            "partidos_desprogramados": partidos_desprogramados
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{torneo_id}/programar-partidos")
@router.post("/{torneo_id}/programar-automatico")  # Alias para compatibilidad con frontend
def programar_partidos_automatico(
    torneo_id: int,
    params: Optional[ProgramacionParams] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Programa automáticamente todos los partidos pendientes en los slots disponibles
    
    Considera:
    - Disponibilidad de slots
    - Bloqueos horarios de jugadores
    - Que una pareja no juegue dos partidos seguidos
    - Horarios diferentes para días de semana vs fin de semana
    
    Parámetros opcionales en body:
    - fecha_inicio: Fecha de inicio para crear slots
    - fecha_fin: Fecha de fin para crear slots
    - duracion_partido_minutos: Duración de cada partido (default: 90)
    - hora_inicio_semana/hora_fin_semana: Horarios Lun-Vie (default: 17:00-22:00)
    - hora_inicio_finde/hora_fin_finde: Horarios Sab-Dom (default: 09:00-21:00)
    """
    from ..models.torneo_models import TorneoSlot, TorneoCancha, TorneoBloqueoJugador, TorneoPareja
    from ..models.driveplus_models import Partido
    from ..services.torneo_zona_service import TorneoZonaService
    from datetime import datetime, timedelta
    
    # Extraer parámetros del body si existen
    fecha_inicio = params.fecha_inicio if params else None
    fecha_fin = params.fecha_fin if params else None
    duracion_minutos = params.duracion_partido_minutos if params else 90
    hora_inicio_semana = params.hora_inicio_semana if params else "17:00"
    hora_fin_semana = params.hora_fin_semana if params else "22:00"
    hora_inicio_finde = params.hora_inicio_finde if params else "09:00"
    hora_fin_finde = params.hora_fin_finde if params else "21:00"
    
    try:
        if not TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario):
            raise HTTPException(status_code=403, detail="No tienes permisos")
        
        # Si se proporcionan fechas, crear slots automáticamente
        if fecha_inicio and fecha_fin:
            canchas = db.query(TorneoCancha).filter(
                TorneoCancha.torneo_id == torneo_id,
                TorneoCancha.activa == True
            ).all()
            
            if not canchas:
                raise HTTPException(status_code=400, detail="No hay canchas configuradas. Crea canchas primero.")
            
            # Crear slots para cada día y cancha
            from datetime import datetime, time
            fecha_actual = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fecha_final = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            
            # Parsear horarios configurados
            def parse_hora(hora_str):
                parts = hora_str.split(":")
                return time(int(parts[0]), int(parts[1]))
            
            h_inicio_semana = parse_hora(hora_inicio_semana)
            h_fin_semana = parse_hora(hora_fin_semana)
            h_inicio_finde = parse_hora(hora_inicio_finde)
            h_fin_finde = parse_hora(hora_fin_finde)
            
            # Detectar si cruza medianoche (hora fin es 00:00 o menor que inicio)
            # En ese caso, 00:00 significa medianoche del día siguiente
            cruza_medianoche_semana = h_fin_semana <= h_inicio_semana
            cruza_medianoche_finde = h_fin_finde <= h_inicio_finde
            
            # PRE-CARGAR slots existentes para evitar queries individuales
            slots_existentes = db.query(TorneoSlot).filter(
                TorneoSlot.torneo_id == torneo_id
            ).all()
            slots_existentes_set = {
                (s.cancha_id, s.fecha_hora_inicio) for s in slots_existentes
            }
            
            slots_creados = 0
            nuevos_slots = []
            while fecha_actual <= fecha_final:
                # Determinar si es fin de semana (5=Sábado, 6=Domingo)
                dia_semana = fecha_actual.weekday()
                es_finde = dia_semana >= 5
                
                # Seleccionar horarios según el día
                if es_finde:
                    hora_inicio_dia = h_inicio_finde
                    hora_fin_dia = h_fin_finde
                    cruza_medianoche = cruza_medianoche_finde
                else:
                    hora_inicio_dia = h_inicio_semana
                    hora_fin_dia = h_fin_semana
                    cruza_medianoche = cruza_medianoche_semana
                
                # Generar slots dinámicamente según duración del partido
                hora_actual = datetime.combine(fecha_actual, hora_inicio_dia)
                
                # Si cruza medianoche, el límite es al día siguiente
                if cruza_medianoche:
                    hora_limite = datetime.combine(fecha_actual + timedelta(days=1), hora_fin_dia)
                else:
                    hora_limite = datetime.combine(fecha_actual, hora_fin_dia)
                
                while hora_actual + timedelta(minutes=duracion_minutos) <= hora_limite:
                    for cancha in canchas:
                        inicio = hora_actual
                        fin = hora_actual + timedelta(minutes=duracion_minutos)
                        
                        # Verificar en memoria si ya existe
                        if (cancha.id, inicio) not in slots_existentes_set:
                            nuevo_slot = TorneoSlot(
                                torneo_id=torneo_id,
                                cancha_id=cancha.id,
                                fecha_hora_inicio=inicio,
                                fecha_hora_fin=fin,
                                ocupado=False
                            )
                            nuevos_slots.append(nuevo_slot)
                            slots_creados += 1
                    
                    # Avanzar al siguiente slot
                    hora_actual += timedelta(minutes=duracion_minutos)
                
                fecha_actual += timedelta(days=1)
            
            # Insertar todos los slots de una vez
            if nuevos_slots:
                for slot in nuevos_slots:
                    db.add(slot)
                db.flush()
        
        # Obtener partidos pendientes sin programar
        partidos = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.estado == 'pendiente',
            Partido.cancha_id == None
        ).all()
        
        if not partidos:
            return {"message": "No hay partidos pendientes para programar", "programados": 0, "sin_programar": 0, "partidos_sin_slot_detalle": []}
        
        # Obtener slots disponibles ordenados por fecha
        slots = db.query(TorneoSlot).filter(
            TorneoSlot.torneo_id == torneo_id,
            TorneoSlot.ocupado == False
        ).order_by(TorneoSlot.fecha_hora_inicio).all()
        
        if not slots:
            raise HTTPException(status_code=400, detail="No hay slots disponibles. Verifica que los horarios de inicio sean menores a los de fin.")
        
        # Obtener bloqueos de jugadores
        bloqueos = db.query(TorneoBloqueoJugador).filter(
            TorneoBloqueoJugador.torneo_id == torneo_id
        ).all()
        
        # Crear diccionario de bloqueos por jugador
        bloqueos_por_jugador = {}
        for b in bloqueos:
            if b.jugador_id not in bloqueos_por_jugador:
                bloqueos_por_jugador[b.jugador_id] = []
            bloqueos_por_jugador[b.jugador_id].append({
                "fecha": b.fecha,
                "hora_desde": b.hora_desde,
                "hora_hasta": b.hora_hasta
            })
        
        # PRE-CARGAR todas las parejas del torneo (optimización)
        todas_parejas = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == torneo_id
        ).all()
        parejas_dict = {p.id: p for p in todas_parejas}
        
        # PRE-CARGAR todos los perfiles de usuarios involucrados (optimización)
        from ..models.driveplus_models import PerfilUsuario
        jugadores_ids = set()
        for p in todas_parejas:
            jugadores_ids.add(p.jugador1_id)
            jugadores_ids.add(p.jugador2_id)
        
        perfiles = db.query(PerfilUsuario).filter(
            PerfilUsuario.id_usuario.in_(jugadores_ids)
        ).all()
        perfiles_dict = {p.id_usuario: p for p in perfiles}
        
        # Helper para obtener nombres de parejas (usa cache)
        def obtener_nombre_pareja(pareja):
            if not pareja:
                return "Pareja desconocida"
            perfil1 = perfiles_dict.get(pareja.jugador1_id)
            perfil2 = perfiles_dict.get(pareja.jugador2_id)
            nombre1 = f"{perfil1.nombre} {perfil1.apellido}" if perfil1 else f"Jugador {pareja.jugador1_id}"
            nombre2 = f"{perfil2.nombre} {perfil2.apellido}" if perfil2 else f"Jugador {pareja.jugador2_id}"
            return f"{nombre1} / {nombre2}"
        
        # Tracking de último partido por pareja (para evitar partidos seguidos)
        ultimo_partido_pareja = {}
        
        partidos_programados = 0
        partidos_no_programados = []
        
        # Contador de partidos de playoffs sin parejas definidas
        partidos_playoffs_pendientes = 0
        
        for partido in partidos:
            programado = False
            razon_no_programado = "Sin slots disponibles"
            
            # Verificar si es un partido de playoffs sin parejas definidas aún
            if partido.pareja1_id is None or partido.pareja2_id is None:
                # Es un partido de playoffs esperando clasificados
                partidos_playoffs_pendientes += 1
                continue  # No intentar programar, es normal
            
            # Obtener parejas del cache
            pareja1 = parejas_dict.get(partido.pareja1_id)
            pareja2 = parejas_dict.get(partido.pareja2_id)
            
            if not pareja1 or not pareja2:
                # Esto sería un error de datos (pareja_id existe pero no se encuentra)
                partidos_no_programados.append({
                    "partido_id": partido.id_partido,
                    "pareja1_nombre": obtener_nombre_pareja(pareja1) if pareja1 else f"Pareja #{partido.pareja1_id}",
                    "pareja2_nombre": obtener_nombre_pareja(pareja2) if pareja2 else f"Pareja #{partido.pareja2_id}",
                    "razon": "Error: pareja no encontrada en base de datos"
                })
                continue
            
            for slot in slots:
                if slot.ocupado:
                    continue
                
                # Verificar bloqueos de los 4 jugadores
                jugadores = [pareja1.jugador1_id, pareja1.jugador2_id, pareja2.jugador1_id, pareja2.jugador2_id]
                tiene_bloqueo = False
                jugador_bloqueado = None
                
                for jugador_id in jugadores:
                    if _jugador_tiene_bloqueo(bloqueos_por_jugador, jugador_id, slot):
                        tiene_bloqueo = True
                        jugador_bloqueado = jugador_id
                        break
                
                if tiene_bloqueo:
                    razon_no_programado = f"Bloqueo horario de jugador"
                    continue
                
                # Verificar que ninguna pareja jugó en el slot anterior
                slot_inicio = slot.fecha_hora_inicio
                pareja_sin_descanso = None
                for pareja_id in [partido.pareja1_id, partido.pareja2_id]:
                    if pareja_id in ultimo_partido_pareja:
                        ultimo_fin = ultimo_partido_pareja[pareja_id]
                        # Dar al menos 30 minutos de descanso
                        if slot_inicio < ultimo_fin + timedelta(minutes=30):
                            tiene_bloqueo = True
                            pareja_sin_descanso = pareja_id
                            break
                
                if tiene_bloqueo:
                    razon_no_programado = "Pareja necesita descanso entre partidos"
                    continue
                
                # Asignar slot al partido
                partido.cancha_id = slot.cancha_id
                partido.fecha_hora = slot.fecha_hora_inicio
                slot.ocupado = True
                slot.partido_id = partido.id_partido
                
                # Actualizar tracking
                ultimo_partido_pareja[partido.pareja1_id] = slot.fecha_hora_fin
                ultimo_partido_pareja[partido.pareja2_id] = slot.fecha_hora_fin
                
                partidos_programados += 1
                programado = True
                break
            
            if not programado:
                partidos_no_programados.append({
                    "partido_id": partido.id_partido,
                    "pareja1_nombre": obtener_nombre_pareja(pareja1),
                    "pareja2_nombre": obtener_nombre_pareja(pareja2),
                    "razon": razon_no_programado
                })
        
        db.commit()
        
        # Construir mensaje
        mensaje = f"Se programaron {partidos_programados} partidos"
        if partidos_playoffs_pendientes > 0:
            mensaje += f" ({partidos_playoffs_pendientes} partidos de playoffs esperan clasificados)"
        
        return {
            "message": mensaje,
            "programados": partidos_programados,
            "sin_programar": len(partidos_no_programados),
            "playoffs_pendientes": partidos_playoffs_pendientes,
            "partidos_sin_slot": [p["partido_id"] for p in partidos_no_programados[:10]],
            "partidos_sin_slot_detalle": partidos_no_programados[:10]
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def _jugador_tiene_bloqueo(bloqueos_por_jugador, jugador_id, slot):
    """Verifica si un jugador tiene bloqueo en el horario del slot"""
    from datetime import datetime, time
    
    if jugador_id not in bloqueos_por_jugador:
        return False
    
    slot_fecha = slot.fecha_hora_inicio.date()
    slot_hora_inicio = slot.fecha_hora_inicio.time()
    slot_hora_fin = slot.fecha_hora_fin.time()
    
    for bloqueo in bloqueos_por_jugador[jugador_id]:
        if bloqueo["fecha"] != slot_fecha:
            continue
        
        # Parsear horas del bloqueo
        def parse_time(t):
            if isinstance(t, time):
                return t
            parts = t.split(":")
            return time(int(parts[0]), int(parts[1]))
        
        bloqueo_desde = parse_time(bloqueo["hora_desde"])
        bloqueo_hasta = parse_time(bloqueo["hora_hasta"])
        
        # Verificar solapamiento
        if not (slot_hora_fin <= bloqueo_desde or slot_hora_inicio >= bloqueo_hasta):
            return True
    
    return False


@router.post("/{torneo_id}/partidos/{partido_id}/reprogramar")
def reprogramar_partido(
    torneo_id: int,
    partido_id: int,
    slot_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Reprograma un partido a un slot específico
    """
    from ..models.torneo_models import TorneoSlot
    from ..models.driveplus_models import Partido
    from ..services.torneo_zona_service import TorneoZonaService
    
    try:
        if not TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario):
            raise HTTPException(status_code=403, detail="No tienes permisos")
        
        partido = db.query(Partido).filter(
            Partido.id_partido == partido_id,
            Partido.id_torneo == torneo_id
        ).first()
        
        if not partido:
            raise HTTPException(status_code=404, detail="Partido no encontrado")
        
        nuevo_slot = db.query(TorneoSlot).filter(
            TorneoSlot.id == slot_id,
            TorneoSlot.torneo_id == torneo_id
        ).first()
        
        if not nuevo_slot:
            raise HTTPException(status_code=404, detail="Slot no encontrado")
        
        if nuevo_slot.ocupado and nuevo_slot.partido_id != partido_id:
            raise HTTPException(status_code=400, detail="El slot ya está ocupado")
        
        # Liberar slot anterior si existe
        if partido.cancha_id:
            slot_anterior = db.query(TorneoSlot).filter(
                TorneoSlot.partido_id == partido_id
            ).first()
            if slot_anterior:
                slot_anterior.ocupado = False
                slot_anterior.partido_id = None
        
        # Asignar nuevo slot
        partido.cancha_id = nuevo_slot.cancha_id
        partido.fecha_hora = nuevo_slot.fecha_hora_inicio
        nuevo_slot.ocupado = True
        nuevo_slot.partido_id = partido_id
        
        db.commit()
        
        return {
            "message": "Partido reprogramado",
            "partido_id": partido_id,
            "nueva_fecha": nuevo_slot.fecha_hora_inicio.isoformat(),
            "cancha_id": nuevo_slot.cancha_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{torneo_id}/bloqueos")
def crear_bloqueo_jugador(
    torneo_id: int,
    jugador_id: int,
    fecha: str,
    hora_desde: str,
    hora_hasta: str,
    motivo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea un bloqueo horario para un jugador
    
    Puede ser creado por el propio jugador o por un organizador
    """
    from ..models.torneo_models import TorneoBloqueoJugador, TorneoPareja
    from ..services.torneo_zona_service import TorneoZonaService
    from datetime import datetime
    
    try:
        # Verificar que el usuario es el jugador o es organizador
        es_organizador = TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario)
        es_jugador = current_user.id_usuario == jugador_id
        
        if not es_organizador and not es_jugador:
            raise HTTPException(status_code=403, detail="No tienes permisos")
        
        # Verificar que el jugador está inscrito en el torneo
        pareja = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == torneo_id,
            (TorneoPareja.jugador1_id == jugador_id) | (TorneoPareja.jugador2_id == jugador_id)
        ).first()
        
        if not pareja:
            raise HTTPException(status_code=400, detail="El jugador no está inscrito en este torneo")
        
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d").date()
        
        bloqueo = TorneoBloqueoJugador(
            torneo_id=torneo_id,
            jugador_id=jugador_id,
            fecha=fecha_dt,
            hora_desde=hora_desde,
            hora_hasta=hora_hasta,
            motivo=motivo
        )
        db.add(bloqueo)
        db.commit()
        db.refresh(bloqueo)
        
        return {
            "id": bloqueo.id,
            "jugador_id": bloqueo.jugador_id,
            "fecha": fecha,
            "hora_desde": hora_desde,
            "hora_hasta": hora_hasta,
            "motivo": motivo
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{torneo_id}/bloqueos")
def listar_bloqueos(
    torneo_id: int,
    jugador_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista bloqueos horarios del torneo"""
    from ..models.torneo_models import TorneoBloqueoJugador
    
    query = db.query(TorneoBloqueoJugador).filter(
        TorneoBloqueoJugador.torneo_id == torneo_id
    )
    
    if jugador_id:
        query = query.filter(TorneoBloqueoJugador.jugador_id == jugador_id)
    
    bloqueos = query.order_by(TorneoBloqueoJugador.fecha, TorneoBloqueoJugador.hora_desde).all()
    
    return [
        {
            "id": b.id,
            "jugador_id": b.jugador_id,
            "fecha": b.fecha.isoformat() if b.fecha else None,
            "hora_desde": b.hora_desde,
            "hora_hasta": b.hora_hasta,
            "motivo": b.motivo
        }
        for b in bloqueos
    ]


@router.delete("/{torneo_id}/bloqueos/{bloqueo_id}")
def eliminar_bloqueo(
    torneo_id: int,
    bloqueo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Elimina un bloqueo horario"""
    from ..models.torneo_models import TorneoBloqueoJugador
    from ..services.torneo_zona_service import TorneoZonaService
    
    bloqueo = db.query(TorneoBloqueoJugador).filter(
        TorneoBloqueoJugador.id == bloqueo_id,
        TorneoBloqueoJugador.torneo_id == torneo_id
    ).first()
    
    if not bloqueo:
        raise HTTPException(status_code=404, detail="Bloqueo no encontrado")
    
    # Verificar permisos
    es_organizador = TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario)
    es_jugador = current_user.id_usuario == bloqueo.jugador_id
    
    if not es_organizador and not es_jugador:
        raise HTTPException(status_code=403, detail="No tienes permisos")
    
    db.delete(bloqueo)
    db.commit()
    
    return {"message": "Bloqueo eliminado"}
