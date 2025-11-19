from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database.config import get_db
from ..models.sala import Sala, SalaJugador
from ..models.playt_models import Usuario, PerfilUsuario
from ..schemas.sala import SalaCreate, SalaResponse, SalaJoin, SalaCompleta
from ..auth.auth_utils import get_current_user
from ..websocket.connection_manager import manager

router = APIRouter(prefix="/salas", tags=["Salas"])

@router.post("/", response_model=SalaResponse)
async def crear_sala(
    sala_data: SalaCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear una nueva sala de juego"""
    try:
        # Generar código único
        codigo = Sala.generar_codigo()
        
        # Verificar que el código sea único
        while db.query(Sala).filter(Sala.codigo_invitacion == codigo).first():
            codigo = Sala.generar_codigo()
        
        # Crear sala
        db_sala = Sala(
            nombre=sala_data.nombre,
            codigo_invitacion=codigo,
            fecha=sala_data.fecha,
            estado="esperando",
            id_creador=current_user.id_usuario,
            max_jugadores=sala_data.max_jugadores
        )
        
        db.add(db_sala)
        db.flush()
        
        # Agregar al creador como primer jugador
        db_jugador = SalaJugador(
            id_sala=db_sala.id_sala,
            id_usuario=current_user.id_usuario,
            orden=1
        )
        db.add(db_jugador)
        
        db.commit()
        db.refresh(db_sala)
        
        return SalaResponse(
            id_sala=str(db_sala.id_sala),
            nombre=db_sala.nombre,
            fecha=db_sala.fecha,
            estado=db_sala.estado,
            codigo_invitacion=db_sala.codigo_invitacion,
            id_creador=db_sala.id_creador,
            jugadores_actuales=1,
            max_jugadores=db_sala.max_jugadores,
            creado_en=db_sala.creado_en
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear sala: {str(e)}"
        )

@router.post("/unirse", response_model=SalaCompleta)
async def unirse_sala(
    join_data: SalaJoin,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unirse a una sala con código de invitación"""
    
    # Buscar sala por código
    sala = db.query(Sala).filter(
        Sala.codigo_invitacion == join_data.codigo_invitacion.upper()
    ).first()
    
    if not sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala no encontrada"
        )
    
    # Verificar que la sala no esté llena
    jugadores_actuales = db.query(SalaJugador).filter(
        SalaJugador.id_sala == sala.id_sala
    ).count()
    
    if jugadores_actuales >= sala.max_jugadores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La sala está llena"
        )
    
    # Verificar que el usuario no esté ya en la sala
    ya_esta = db.query(SalaJugador).filter(
        SalaJugador.id_sala == sala.id_sala,
        SalaJugador.id_usuario == current_user.id_usuario
    ).first()
    
    if ya_esta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya estás en esta sala"
        )
    
    try:
        # Agregar jugador a la sala
        db_jugador = SalaJugador(
            id_sala=sala.id_sala,
            id_usuario=current_user.id_usuario,
            orden=jugadores_actuales + 1
        )
        db.add(db_jugador)
        db.commit()
        
        # Notificar a través de WebSocket
        await manager.notify_jugador_unido(str(sala.id_sala), {
            "id_usuario": current_user.id_usuario,
            "nombre_usuario": current_user.nombre_usuario,
            "jugadores_actuales": jugadores_actuales + 1
        })
        
        # Obtener información completa de la sala
        return await obtener_sala(sala.id_sala, current_user, db)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al unirse a la sala: {str(e)}"
        )

@router.get("/{sala_id}", response_model=SalaCompleta)
async def obtener_sala(
    sala_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener información completa de una sala"""
    
    sala = db.query(Sala).filter(Sala.id_sala == sala_id).first()
    
    if not sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala no encontrada"
        )
    
    # Obtener jugadores
    jugadores_sala = db.query(SalaJugador).filter(
        SalaJugador.id_sala == sala_id
    ).order_by(SalaJugador.orden).all()
    
    jugadores = []
    for sj in jugadores_sala:
        usuario = db.query(Usuario).filter(Usuario.id_usuario == sj.id_usuario).first()
        perfil = db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == sj.id_usuario).first()
        
        if usuario:
            jugadores.append({
                "id_usuario": usuario.id_usuario,
                "nombre_usuario": usuario.nombre_usuario,
                "nombre": perfil.nombre if perfil else "",
                "apellido": perfil.apellido if perfil else "",
                "rating": usuario.rating,
                "equipo": sj.equipo,
                "orden": sj.orden
            })
    
    return SalaCompleta(
        id_sala=str(sala.id_sala),
        nombre=sala.nombre,
        fecha=sala.fecha,
        estado=sala.estado,
        codigo_invitacion=sala.codigo_invitacion,
        id_creador=sala.id_creador,
        jugadores_actuales=len(jugadores),
        max_jugadores=sala.max_jugadores,
        creado_en=sala.creado_en,
        jugadores=jugadores
    )

@router.get("/", response_model=List[SalaCompleta])
async def listar_salas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar salas del usuario"""
    
    # Obtener salas donde el usuario participa
    salas_usuario = db.query(SalaJugador).filter(
        SalaJugador.id_usuario == current_user.id_usuario
    ).all()
    
    salas_ids = [sj.id_sala for sj in salas_usuario]
    
    salas = db.query(Sala).filter(Sala.id_sala.in_(salas_ids)).order_by(
        Sala.creado_en.desc()
    ).all()
    
    resultado = []
    for sala in salas:
        jugadores_count = db.query(SalaJugador).filter(
            SalaJugador.id_sala == sala.id_sala
        ).count()
        
        resultado.append(SalaCompleta(
            id_sala=str(sala.id_sala),
            nombre=sala.nombre,
            fecha=sala.fecha,
            estado=sala.estado,
            codigo_invitacion=sala.codigo_invitacion,
            id_creador=sala.id_creador,
            jugadores_actuales=jugadores_count,
            max_jugadores=sala.max_jugadores,
            creado_en=sala.creado_en,
            jugadores=[]
        ))
    
    return resultado

@router.post("/{sala_id}/asignar-equipos")
async def asignar_equipos(
    sala_id: int,
    equipos: dict,  # {"jugador_id": equipo_numero}
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Asignar equipos a los jugadores (solo creador)"""
    
    sala = db.query(Sala).filter(Sala.id_sala == sala_id).first()
    
    if not sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala no encontrada"
        )
    
    if sala.id_creador != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el creador puede asignar equipos"
        )
    
    try:
        # Actualizar equipos
        for jugador_id, equipo in equipos.items():
            db.query(SalaJugador).filter(
                SalaJugador.id_sala == sala_id,
                SalaJugador.id_usuario == int(jugador_id)
            ).update({"equipo": equipo})
        
        db.commit()
        
        # Notificar a través de WebSocket
        await manager.notify_equipos_asignados(str(sala_id), {
            "equipos": equipos,
            "sala_id": sala_id
        })
        
        return {"message": "Equipos asignados correctamente"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al asignar equipos: {str(e)}"
        )

@router.post("/{sala_id}/iniciar")
async def iniciar_partido(
    sala_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Iniciar el partido (solo creador, cuando haya 4 jugadores)"""
    
    sala = db.query(Sala).filter(Sala.id_sala == sala_id).first()
    
    if not sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala no encontrada"
        )
    
    if sala.id_creador != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el creador puede iniciar el partido"
        )
    
    # Verificar que haya 4 jugadores
    jugadores = db.query(SalaJugador).filter(
        SalaJugador.id_sala == sala_id
    ).all()
    
    if len(jugadores) != 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Se necesitan 4 jugadores. Actualmente hay {len(jugadores)}"
        )
    
    # Verificar que todos tengan equipo asignado
    sin_equipo = [j for j in jugadores if j.equipo is None]
    if sin_equipo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Todos los jugadores deben tener un equipo asignado"
        )
    
    try:
        # Crear el partido en la tabla de partidos
        from ..models.playt_models import Partido, PartidoJugador
        
        db_partido = Partido(
            fecha=sala.fecha,
            estado="activo",
            id_creador=sala.id_creador
        )
        db.add(db_partido)
        db.flush()
        
        # Agregar jugadores al partido
        for jugador in jugadores:
            db_partido_jugador = PartidoJugador(
                id_partido=db_partido.id_partido,
                id_usuario=jugador.id_usuario,
                equipo=jugador.equipo
            )
            db.add(db_partido_jugador)
        
        # Actualizar sala
        sala.estado = "en_juego"
        sala.id_partido = db_partido.id_partido
        
        db.commit()
        
        # Notificar a través de WebSocket
        await manager.notify_partido_iniciado(str(sala_id), {
            "id_partido": db_partido.id_partido,
            "sala_id": sala_id
        })
        
        return {
            "message": "Partido iniciado",
            "id_partido": db_partido.id_partido
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar partido: {str(e)}"
        )
