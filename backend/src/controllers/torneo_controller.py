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

@router.post("/{torneo_id}/inscribir", status_code=status.HTTP_201_CREATED)
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
        return _pareja_to_dict(db, pareja)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{torneo_id}/parejas")
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
    from ..models.playt_models import Usuario
    
    try:
        parejas = TorneoInscripcionService.listar_parejas(db, torneo_id, estado)
        
        # Construir respuesta con datos de jugadores
        from ..models.playt_models import PerfilUsuario
        
        resultado = []
        for pareja in parejas:
            # Obtener perfiles de jugadores
            perfil1 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja.jugador1_id).first()
            perfil2 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja.jugador2_id).first()
            
            jugador1_nombre = f"{perfil1.nombre} {perfil1.apellido}" if perfil1 else f"Usuario {pareja.jugador1_id}"
            jugador2_nombre = f"{perfil2.nombre} {perfil2.apellido}" if perfil2 else f"Usuario {pareja.jugador2_id}"
            
            resultado.append({
                "id": pareja.id,
                "id_pareja": pareja.id,  # Alias para compatibilidad
                "torneo_id": pareja.torneo_id,
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
    from ..models.playt_models import PerfilUsuario
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
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Genera zonas automáticamente y distribuye parejas
    
    Solo organizadores pueden generar zonas
    
    - **num_zonas**: Número de zonas (opcional, se calcula automáticamente)
    - **balancear_por_rating**: Si True, distribuye parejas por rating
    """
    from ..services.torneo_zona_service import TorneoZonaService
    
    try:
        user_id = current_user.id_usuario
        zonas = TorneoZonaService.generar_zonas_automaticas(
            db, torneo_id, user_id, num_zonas, balancear_por_rating
        )
        return {
            "message": "Zonas generadas exitosamente",
            "zonas": [{"id": z.id, "nombre": z.nombre, "numero": z.numero_orden} for z in zonas]
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
    from ..models.playt_models import PerfilUsuario
    
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
    from ..models.playt_models import PerfilUsuario
    
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
    db: Session = Depends(get_db)
):
    """
    Lista todos los partidos del torneo
    
    - **zona_id**: Filtrar por zona (opcional)
    """
    from ..models.playt_models import Partido
    
    try:
        query = db.query(Partido).filter(Partido.id_torneo == torneo_id)
        
        # Filtrar por zona si se especifica
        if zona_id is not None:
            query = query.filter(Partido.zona_id == zona_id)
        
        partidos = query.all()
        
        # Construir respuesta con nombres de parejas
        from ..models.playt_models import PerfilUsuario
        from ..models.torneo_models import TorneoPareja
        
        resultado = []
        for p in partidos:
            # Obtener información de las parejas
            pareja1 = db.query(TorneoPareja).filter(TorneoPareja.id == p.pareja1_id).first() if p.pareja1_id else None
            pareja2 = db.query(TorneoPareja).filter(TorneoPareja.id == p.pareja2_id).first() if p.pareja2_id else None
            
            pareja1_nombre = "TBD"
            pareja2_nombre = "TBD"
            
            if pareja1:
                perfil1_1 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja1.jugador1_id).first()
                perfil1_2 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja1.jugador2_id).first()
                nombre1_1 = f"{perfil1_1.nombre} {perfil1_1.apellido}" if perfil1_1 else f"Jugador {pareja1.jugador1_id}"
                nombre1_2 = f"{perfil1_2.nombre} {perfil1_2.apellido}" if perfil1_2 else f"Jugador {pareja1.jugador2_id}"
                pareja1_nombre = f"{nombre1_1} / {nombre1_2}"
            
            if pareja2:
                perfil2_1 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja2.jugador1_id).first()
                perfil2_2 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja2.jugador2_id).first()
                nombre2_1 = f"{perfil2_1.nombre} {perfil2_1.apellido}" if perfil2_1 else f"Jugador {pareja2.jugador1_id}"
                nombre2_2 = f"{perfil2_2.nombre} {perfil2_2.apellido}" if perfil2_2 else f"Jugador {pareja2.jugador2_id}"
                pareja2_nombre = f"{nombre2_1} / {nombre2_2}"
            
            resultado.append({
                "id_partido": p.id_partido,
                "pareja1_id": p.pareja1_id,
                "pareja2_id": p.pareja2_id,
                "pareja1_nombre": pareja1_nombre,
                "pareja2_nombre": pareja2_nombre,
                "zona_id": p.zona_id,
                "fase": p.fase,
                "estado": p.estado,
                "fecha_hora": p.fecha_hora.isoformat() if p.fecha_hora else None,
                "cancha_id": p.cancha_id,
                "ganador_pareja_id": p.ganador_pareja_id,
                "resultado_padel": p.resultado_padel
            })
        
        return {
            "total": len(resultado),
            "partidos": resultado
        }
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
    db: Session = Depends(get_db)
):
    """
    Lista todos los partidos de playoffs agrupados por fase
    
    Returns:
        Diccionario con partidos por fase:
        {
            '16avos': [...],
            '8vos': [...],
            '4tos': [...],
            'semis': [...],
            'final': [...]
        }
    """
    from ..services.torneo_playoff_service import TorneoPlayoffService
    from ..models.playt_models import PerfilUsuario
    from ..models.torneo_models import TorneoPareja
    
    try:
        partidos_por_fase = TorneoPlayoffService.listar_partidos_playoffs(db, torneo_id)
        
        # Agregar nombres de parejas a cada partido
        resultado = {}
        for fase, partidos in partidos_por_fase.items():
            resultado[fase] = []
            for p in partidos:
                # Obtener información de las parejas
                pareja1_nombre = None
                pareja2_nombre = None
                
                if p.pareja1_id:
                    pareja1 = db.query(TorneoPareja).filter(TorneoPareja.id == p.pareja1_id).first()
                    if pareja1:
                        perfil1_1 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja1.jugador1_id).first()
                        perfil1_2 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja1.jugador2_id).first()
                        nombre1_1 = f"{perfil1_1.nombre} {perfil1_1.apellido}" if perfil1_1 else f"Jugador {pareja1.jugador1_id}"
                        nombre1_2 = f"{perfil1_2.nombre} {perfil1_2.apellido}" if perfil1_2 else f"Jugador {pareja1.jugador2_id}"
                        pareja1_nombre = f"{nombre1_1} / {nombre1_2}"
                
                if p.pareja2_id:
                    pareja2 = db.query(TorneoPareja).filter(TorneoPareja.id == p.pareja2_id).first()
                    if pareja2:
                        perfil2_1 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja2.jugador1_id).first()
                        perfil2_2 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja2.jugador2_id).first()
                        nombre2_1 = f"{perfil2_1.nombre} {perfil2_1.apellido}" if perfil2_1 else f"Jugador {pareja2.jugador1_id}"
                        nombre2_2 = f"{perfil2_2.nombre} {perfil2_2.apellido}" if perfil2_2 else f"Jugador {pareja2.jugador2_id}"
                        pareja2_nombre = f"{nombre2_1} / {nombre2_2}"
                
                resultado[fase].append({
                    "id": p.id_partido,
                    "numero_partido": p.numero_partido,
                    "pareja1_id": p.pareja1_id,
                    "pareja2_id": p.pareja2_id,
                    "pareja1_nombre": pareja1_nombre,
                    "pareja2_nombre": pareja2_nombre,
                    "ganador_id": p.ganador_pareja_id,
                    "resultado": p.resultado_padel,
                    "fase": fase,
                    "estado": p.estado.value if hasattr(p.estado, 'value') else str(p.estado)
                })
        
        # Aplanar todos los partidos en una lista para el frontend
        todos_partidos = []
        for fase_key, partidos_fase in resultado.items():
            todos_partidos.extend(partidos_fase)
        
        return {
            "partidos": todos_partidos,
            "por_fase": resultado
        }
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
    
    Útil para mostrar el bracket completo
    """
    from ..models.torneo_models import FasePartido
    from ..models.playt_models import Partido, PerfilUsuario
    from ..models.torneo_models import TorneoPareja
    
    try:
        partidos = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase != FasePartido.ZONA.value
        ).order_by(Partido.numero_partido).all()
        
        resultado = []
        for p in partidos:
            # Obtener información de las parejas
            pareja1_nombre = None
            pareja2_nombre = None
            
            if p.pareja1_id:
                pareja1 = db.query(TorneoPareja).filter(TorneoPareja.id == p.pareja1_id).first()
                if pareja1:
                    perfil1_1 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja1.jugador1_id).first()
                    perfil1_2 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja1.jugador2_id).first()
                    nombre1_1 = f"{perfil1_1.nombre} {perfil1_1.apellido}" if perfil1_1 else f"Jugador {pareja1.jugador1_id}"
                    nombre1_2 = f"{perfil1_2.nombre} {perfil1_2.apellido}" if perfil1_2 else f"Jugador {pareja1.jugador2_id}"
                    pareja1_nombre = f"{nombre1_1} / {nombre1_2}"
            
            if p.pareja2_id:
                pareja2 = db.query(TorneoPareja).filter(TorneoPareja.id == p.pareja2_id).first()
                if pareja2:
                    perfil2_1 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja2.jugador1_id).first()
                    perfil2_2 = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == pareja2.jugador2_id).first()
                    nombre2_1 = f"{perfil2_1.nombre} {perfil2_1.apellido}" if perfil2_1 else f"Jugador {pareja2.jugador1_id}"
                    nombre2_2 = f"{perfil2_2.nombre} {perfil2_2.apellido}" if perfil2_2 else f"Jugador {pareja2.jugador2_id}"
                    pareja2_nombre = f"{nombre2_1} / {nombre2_2}"
            
            resultado.append({
                "id": p.id_partido,
                "numero_partido": p.numero_partido,
                "pareja1_id": p.pareja1_id,
                "pareja2_id": p.pareja2_id,
                "pareja1_nombre": pareja1_nombre,
                "pareja2_nombre": pareja2_nombre,
                "ganador_id": p.ganador_pareja_id,
                "resultado": p.resultado_padel,
                "fase": p.fase if p.fase else None,
                "estado": p.estado if p.estado else None
            })
        
        return {
            "total": len(resultado),
            "partidos": resultado
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================
# ENDPOINTS DE CANCHAS Y PROGRAMACIÓN
# ============================================

@router.post("/{torneo_id}/canchas")
def crear_cancha(
    torneo_id: int,
    nombre: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea una cancha para el torneo
    
    Solo organizadores pueden crear canchas
    """
    from ..models.torneo_models import TorneoCancha
    from ..services.torneo_zona_service import TorneoZonaService
    
    try:
        if not TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario):
            raise HTTPException(status_code=403, detail="No tienes permisos")
        
        cancha = TorneoCancha(
            torneo_id=torneo_id,
            nombre=nombre,
            activa=True
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
    
    resultado = []
    for s in slots:
        cancha = db.query(TorneoCancha).filter(TorneoCancha.id == s.cancha_id).first()
        resultado.append({
            "id": s.id,
            "cancha_id": s.cancha_id,
            "cancha_nombre": cancha.nombre if cancha else None,
            "fecha_hora_inicio": s.fecha_hora_inicio.isoformat() if s.fecha_hora_inicio else None,
            "fecha_hora_fin": s.fecha_hora_fin.isoformat() if s.fecha_hora_fin else None,
            "ocupado": s.ocupado,
            "partido_id": s.partido_id
        })
    
    return resultado


@router.post("/{torneo_id}/programar-partidos")
def programar_partidos_automatico(
    torneo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Programa automáticamente todos los partidos pendientes en los slots disponibles
    
    Considera:
    - Disponibilidad de slots
    - Bloqueos horarios de jugadores
    - Que una pareja no juegue dos partidos seguidos
    """
    from ..models.torneo_models import TorneoSlot, TorneoCancha, TorneoBloqueoJugador, TorneoPareja
    from ..models.playt_models import Partido
    from ..services.torneo_zona_service import TorneoZonaService
    from datetime import datetime, timedelta
    
    try:
        if not TorneoZonaService._es_organizador(db, torneo_id, current_user.id_usuario):
            raise HTTPException(status_code=403, detail="No tienes permisos")
        
        # Obtener partidos pendientes sin programar
        partidos = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.estado == 'pendiente',
            Partido.cancha_id == None
        ).all()
        
        if not partidos:
            return {"message": "No hay partidos pendientes para programar", "programados": 0}
        
        # Obtener slots disponibles ordenados por fecha
        slots = db.query(TorneoSlot).filter(
            TorneoSlot.torneo_id == torneo_id,
            TorneoSlot.ocupado == False
        ).order_by(TorneoSlot.fecha_hora_inicio).all()
        
        if not slots:
            raise HTTPException(status_code=400, detail="No hay slots disponibles. Crea slots primero.")
        
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
        
        # Tracking de último partido por pareja (para evitar partidos seguidos)
        ultimo_partido_pareja = {}
        
        partidos_programados = 0
        partidos_no_programados = []
        
        for partido in partidos:
            programado = False
            
            for slot in slots:
                if slot.ocupado:
                    continue
                
                # Verificar que las parejas no tengan bloqueo en ese horario
                pareja1 = db.query(TorneoPareja).filter(TorneoPareja.id == partido.pareja1_id).first()
                pareja2 = db.query(TorneoPareja).filter(TorneoPareja.id == partido.pareja2_id).first()
                
                if not pareja1 or not pareja2:
                    continue
                
                # Verificar bloqueos de los 4 jugadores
                jugadores = [pareja1.jugador1_id, pareja1.jugador2_id, pareja2.jugador1_id, pareja2.jugador2_id]
                tiene_bloqueo = False
                
                for jugador_id in jugadores:
                    if _jugador_tiene_bloqueo(bloqueos_por_jugador, jugador_id, slot):
                        tiene_bloqueo = True
                        break
                
                if tiene_bloqueo:
                    continue
                
                # Verificar que ninguna pareja jugó en el slot anterior
                slot_inicio = slot.fecha_hora_inicio
                for pareja_id in [partido.pareja1_id, partido.pareja2_id]:
                    if pareja_id in ultimo_partido_pareja:
                        ultimo_fin = ultimo_partido_pareja[pareja_id]
                        # Dar al menos 30 minutos de descanso
                        if slot_inicio < ultimo_fin + timedelta(minutes=30):
                            tiene_bloqueo = True
                            break
                
                if tiene_bloqueo:
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
                partidos_no_programados.append(partido.id_partido)
        
        db.commit()
        
        return {
            "message": f"Se programaron {partidos_programados} partidos",
            "programados": partidos_programados,
            "sin_programar": len(partidos_no_programados),
            "partidos_sin_slot": partidos_no_programados[:10]  # Mostrar solo los primeros 10
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
    from ..models.playt_models import Partido
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
