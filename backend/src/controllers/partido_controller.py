from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database.config import get_db
from ..models.playt_models import Partido, PartidoJugador, ResultadoPartido, Usuario, Club, HistorialRating, PerfilUsuario, Categoria
from ..schemas.partido import PartidoCreate, PartidoResponse, PartidoCompleto, ResultadoCreate
from ..auth.auth_utils import get_current_user
from ..services.elo_service import EloService
from ..services.categoria_service import actualizar_categoria_usuario

router = APIRouter(prefix="/partidos", tags=["Partidos"])

@router.post("/", response_model=PartidoResponse)
async def crear_partido(
    partido_data: PartidoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear un nuevo partido"""
    
    # Verificar que el usuario esté en la lista de jugadores
    if current_user.id_usuario not in partido_data.jugadores:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El creador debe ser uno de los jugadores"
        )
    
    # Verificar que haya 4 jugadores
    if len(partido_data.jugadores) != 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe haber exactamente 4 jugadores"
        )
    
    # Verificar que los equipos sean válidos (1 o 2)
    if not all(equipo in [1, 2] for equipo in partido_data.equipos):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los equipos deben ser 1 o 2"
        )
    
    try:
        # Crear el partido
        db_partido = Partido(
            fecha=partido_data.fecha,
            estado="pendiente",
            id_creador=current_user.id_usuario,
            id_club=partido_data.id_club
        )
        
        db.add(db_partido)
        db.flush()  # Para obtener el ID del partido
        
        # Agregar jugadores al partido
        for i, jugador_id in enumerate(partido_data.jugadores):
            db_jugador = PartidoJugador(
                id_partido=db_partido.id_partido,
                id_usuario=jugador_id,
                equipo=partido_data.equipos[i]
            )
            db.add(db_jugador)
        
        db.commit()
        db.refresh(db_partido)
        
        # Retornar partido creado
        return PartidoResponse(
            id_partido=db_partido.id_partido,
            fecha=db_partido.fecha,
            estado=db_partido.estado,
            id_creador=db_partido.id_creador,
            creado_en=db_partido.creado_en,
            id_club=db_partido.id_club,
            jugadores=[]
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear partido: {str(e)}"
        )

@router.get("/", response_model=List[PartidoCompleto])
async def listar_partidos(
    estado: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Listar partidos con filtros opcionales"""
    
    query = db.query(Partido)
    
    if estado:
        query = query.filter(Partido.estado == estado)
    
    partidos = query.order_by(Partido.fecha.desc()).limit(limit).all()
    
    # Construir respuesta completa
    partidos_completos = []
    for partido in partidos:
        # Obtener jugadores
        jugadores = db.query(PartidoJugador).filter(
            PartidoJugador.id_partido == partido.id_partido
        ).all()
        
        # Obtener resultado si existe
        resultado = db.query(ResultadoPartido).filter(
            ResultadoPartido.id_partido == partido.id_partido
        ).first()
        
        # Obtener club si existe
        club = None
        if partido.id_club:
            club = db.query(Club).filter(Club.id_club == partido.id_club).first()
        
        # Obtener creador
        creador = db.query(Usuario).filter(Usuario.id_usuario == partido.id_creador).first()
        
        partidos_completos.append(PartidoCompleto(
            id_partido=partido.id_partido,
            fecha=partido.fecha,
            estado=partido.estado,
            id_creador=partido.id_creador,
            creado_en=partido.creado_en,
            id_club=partido.id_club,
            jugadores=[],
            resultado=resultado,
            club=club,
            creador={
                "id_usuario": creador.id_usuario,
                "nombre_usuario": creador.nombre_usuario
            } if creador else {}
        ))
    
    return partidos_completos

@router.get("/{partido_id}", response_model=PartidoCompleto)
async def obtener_partido(
    partido_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un partido específico con todos sus datos"""
    
    partido = db.query(Partido).filter(Partido.id_partido == partido_id).first()
    
    if not partido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partido no encontrado"
        )
    
    # Obtener jugadores
    jugadores = db.query(PartidoJugador).filter(
        PartidoJugador.id_partido == partido.id_partido
    ).all()
    
    # Obtener resultado si existe
    resultado = db.query(ResultadoPartido).filter(
        ResultadoPartido.id_partido == partido.id_partido
    ).first()
    
    # Obtener club si existe
    club = None
    if partido.id_club:
        club = db.query(Club).filter(Club.id_club == partido.id_club).first()
    
    # Obtener creador
    creador = db.query(Usuario).filter(Usuario.id_usuario == partido.id_creador).first()
    
    return PartidoCompleto(
        id_partido=partido.id_partido,
        fecha=partido.fecha,
        estado=partido.estado,
        id_creador=partido.id_creador,
        creado_en=partido.creado_en,
        id_club=partido.id_club,
        jugadores=[],
        resultado=resultado,
        club=club,
        creador={
            "id_usuario": creador.id_usuario,
            "nombre_usuario": creador.nombre_usuario
        } if creador else {}
    )

@router.post("/{partido_id}/resultado")
async def reportar_resultado(
    partido_id: int,
    resultado_data: ResultadoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reportar resultado de un partido (sin calcular Elo aún)"""
    
    # Verificar que el partido existe
    partido = db.query(Partido).filter(Partido.id_partido == partido_id).first()
    
    if not partido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partido no encontrado"
        )
    
    # Verificar que el partido esté en estado "pendiente"
    if partido.estado != "pendiente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden reportar resultados de partidos pendientes"
        )
    
    # Verificar que el usuario sea uno de los jugadores
    jugador_partido = db.query(PartidoJugador).filter(
        PartidoJugador.id_partido == partido_id,
        PartidoJugador.id_usuario == current_user.id_usuario
    ).first()
    
    if not jugador_partido:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los jugadores del partido pueden reportar resultados"
        )
    
    try:
        # Crear resultado
        db_resultado = ResultadoPartido(
            id_partido=partido_id,
            id_reportador=current_user.id_usuario,
            sets_eq1=resultado_data.sets_eq1,
            sets_eq2=resultado_data.sets_eq2,
            detalle_sets=resultado_data.detalle_sets,
            desenlace=resultado_data.desenlace
        )
        
        db.add(db_resultado)
        
        # Cambiar estado del partido a "reportado"
        partido.estado = "reportado"
        
        db.commit()
        
        return {
            "message": "Resultado reportado exitosamente. El equipo rival debe confirmarlo para calcular el ranking Elo.",
            "estado": "reportado",
            "resultado": {
                "sets_equipo1": resultado_data.sets_eq1,
                "sets_equipo2": resultado_data.sets_eq2,
                "desenlace": resultado_data.desenlace,
                "reportado_por": current_user.nombre_usuario
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al reportar resultado: {str(e)}"
        )
        
        return {
            "message": "Resultado reportado exitosamente y ranking Elo avanzado actualizado (estado: reportado)",
            "equipo1": {
                "sets": resultado_data.sets_eq1,
                "rating_antes": nuevos_ratings['team_a']['old_rating'],
                "rating_despues": nuevos_ratings['team_a']['new_rating'],
                "cambio": nuevos_ratings['team_a']['rating_change'],
                "jugadores": [
                    {
                        "rating_antes": player['old_rating'],
                        "rating_despues": player['new_rating'],
                        "cambio": player['rating_change']
                    }
                    for player in nuevos_ratings['team_a']['players']
                ]
            },
            "equipo2": {
                "sets": resultado_data.sets_eq2,
                "rating_antes": nuevos_ratings['team_b']['old_rating'],
                "rating_despues": nuevos_ratings['team_b']['new_rating'],
                "cambio": nuevos_ratings['team_b']['rating_change'],
                "jugadores": [
                    {
                        "rating_antes": player['old_rating'],
                        "rating_despues": player['new_rating'],
                        "cambio": player['rating_change']
                    }
                    for player in nuevos_ratings['team_b']['players']
                ]
            },
            "detalles_elo": {
                "expectativa_equipo1": nuevos_ratings['match_details']['expected_a'],
                "expectativa_equipo2": nuevos_ratings['match_details']['expected_b'],
                "puntuacion_real_equipo1": nuevos_ratings['match_details']['actual_score_a'],
                "puntuacion_real_equipo2": nuevos_ratings['match_details']['actual_score_b'],
                "multiplicador_sets": nuevos_ratings['match_details']['sets_multiplier'],
                "factor_k_equipo1": nuevos_ratings['match_details']['team_a_k'],
                "factor_k_equipo2": nuevos_ratings['match_details']['team_b_k'],
                "suavizador_equipo1": nuevos_ratings['match_details']['loss_softener_a'],
                "suavizador_equipo2": nuevos_ratings['match_details']['loss_softener_b'],
                "caps_equipo1": nuevos_ratings['match_details']['caps_a'],
                "caps_equipo2": nuevos_ratings['match_details']['caps_b']
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al reportar resultado: {str(e)}"
        )

@router.post("/{partido_id}/confirmar")
async def confirmar_resultado(
    partido_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirmar resultado reportado (sin calcular Elo aún)"""
    
    # Verificar que el partido existe
    partido = db.query(Partido).filter(Partido.id_partido == partido_id).first()
    
    if not partido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partido no encontrado"
        )
    
    # Verificar que el partido esté en estado "reportado"
    if partido.estado != "reportado":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden confirmar resultados de partidos reportados"
        )
    
    # Verificar que el usuario sea del equipo rival (no del que reportó)
    resultado = db.query(ResultadoPartido).filter(
        ResultadoPartido.id_partido == partido_id
    ).first()
    
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró resultado para este partido"
        )
    
    # Verificar que el usuario NO sea el que reportó el resultado
    if resultado.id_reportador == current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes confirmar tu propio resultado reportado"
        )
    
    # Verificar que el usuario sea uno de los jugadores del partido
    jugador_partido = db.query(PartidoJugador).filter(
        PartidoJugador.id_partido == partido_id,
        PartidoJugador.id_usuario == current_user.id_usuario
    ).first()
    
    if not jugador_partido:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los jugadores del partido pueden confirmar resultados"
        )
    
    try:
        # Solo cambiar estado del partido a "confirmado"
        partido.estado = "confirmado"
        
        db.commit()
        
        return {
            "message": "Resultado confirmado exitosamente. Ahora se puede calcular el ranking Elo.",
            "estado": "confirmado",
            "resultado": {
                "sets_equipo1": resultado.sets_eq1,
                "sets_equipo2": resultado.sets_eq2,
                "desenlace": resultado.desenlace,
                "confirmado_por": current_user.nombre_usuario
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al confirmar resultado: {str(e)}"
        )

@router.post("/{partido_id}/calcular-elo")
async def calcular_elo_partido(
    partido_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calcular ranking Elo para un partido confirmado"""
    
    # Verificar que el partido existe
    partido = db.query(Partido).filter(Partido.id_partido == partido_id).first()
    
    if not partido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partido no encontrado"
        )
    
    # Verificar que el partido esté en estado "confirmado"
    if partido.estado != "confirmado":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede calcular Elo para partidos confirmados"
        )
    
    # Verificar que el usuario sea uno de los jugadores del partido
    jugador_partido = db.query(PartidoJugador).filter(
        PartidoJugador.id_partido == partido_id,
        PartidoJugador.id_usuario == current_user.id_usuario
    ).first()
    
    if not jugador_partido:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los jugadores del partido pueden calcular Elo"
        )
    
    # Verificar que no se haya calculado Elo ya
    historial_existente = db.query(HistorialRating).filter(
        HistorialRating.id_partido == partido_id
    ).first()
    
    if historial_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ranking Elo ya fue calculado para este partido"
        )
    
    try:
        # Obtener resultado del partido
        resultado = db.query(ResultadoPartido).filter(
            ResultadoPartido.id_partido == partido_id
        ).first()
        
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró resultado para este partido"
            )
        
        # Obtener todos los jugadores del partido
        jugadores_partido = db.query(PartidoJugador).filter(
            PartidoJugador.id_partido == partido_id
        ).all()
        
        if len(jugadores_partido) != 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El partido debe tener exactamente 4 jugadores"
            )
        
        # Separar jugadores por equipos
        equipo1 = [j for j in jugadores_partido if j.equipo == 1]
        equipo2 = [j for j in jugadores_partido if j.equipo == 2]
        
        if len(equipo1) != 2 or len(equipo2) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cada equipo debe tener exactamente 2 jugadores"
            )
        
        # Obtener información de los jugadores
        jugadores_info = {}
        for jugador in jugadores_partido:
            usuario = db.query(Usuario).filter(Usuario.id_usuario == jugador.id_usuario).first()
            if usuario:
                jugadores_info[jugador.id_usuario] = {
                    'usuario': usuario,
                    'equipo': jugador.equipo
                }
        
        # CALCULAR RANKING ELO AVANZADO
        elo_service = EloService()
        
        # Preparar datos para el algoritmo Elo avanzado
        equipo1_players = [
            {
                "rating": jugadores_info[j.id_usuario]['usuario'].rating,
                "partidos": jugadores_info[j.id_usuario]['usuario'].partidos_jugados
            }
            for j in equipo1
        ]
        
        equipo2_players = [
            {
                "rating": jugadores_info[j.id_usuario]['usuario'].rating,
                "partidos": jugadores_info[j.id_usuario]['usuario'].partidos_jugados
            }
            for j in equipo2
        ]
        
        # Calcular games totales si están disponibles en detalle_sets
        games_equipo1 = 0
        games_equipo2 = 0
        
        if resultado.detalle_sets:
            for set_result in resultado.detalle_sets:
                if isinstance(set_result, str) and '-' in set_result:
                    try:
                        games1, games2 = map(int, set_result.split('-'))
                        games_equipo1 += games1
                        games_equipo2 += games2
                    except (ValueError, AttributeError):
                        pass  # Si no se puede parsear, usar 0
        
        # Calcular nuevos ratings usando el algoritmo Elo avanzado
        nuevos_ratings = elo_service.calculate_match_ratings(
            team_a_players=equipo1_players,
            team_b_players=equipo2_players,
            sets_a=resultado.sets_eq1,
            sets_b=resultado.sets_eq2,
            games_a=games_equipo1,
            games_b=games_equipo2,
            desenlace=resultado.desenlace
        )
        
        # Actualizar ratings de todos los jugadores
        for jugador in jugadores_partido:
            usuario = jugadores_info[jugador.id_usuario]['usuario']
            equipo = jugador.equipo  # Corregido: usar jugador.equipo directamente
            
            # Encontrar el índice del jugador en su equipo (0 o 1)
            equipo_jugadores = equipo1 if equipo == 1 else equipo2
            jugador_index = next(i for i, j in enumerate(equipo_jugadores) if j.id_usuario == jugador.id_usuario)
            
            # Obtener datos del nuevo rating
            if equipo == 1:
                player_data = nuevos_ratings['team_a']['players'][jugador_index]
            else:
                player_data = nuevos_ratings['team_b']['players'][jugador_index]
            
            rating_antes = usuario.rating
            rating_despues = player_data['new_rating']
            delta = player_data['rating_change']
            
            # Actualizar usuario
            usuario.rating = int(rating_despues)
            usuario.partidos_jugados += 1
            
            # Actualizar categoría según el nuevo rating
            actualizar_categoria_usuario(db, usuario)
            
            # Crear registro en historial de rating
            historial = HistorialRating(
                id_usuario=usuario.id_usuario,
                id_partido=partido_id,
                rating_antes=rating_antes,
                delta=int(delta),  # Convertir delta a entero
                rating_despues=int(rating_despues)
            )
            db.add(historial)
        
        db.commit()
        
        return {
            "message": "Ranking Elo avanzado calculado y aplicado exitosamente",
            "equipo1": {
                "sets": resultado.sets_eq1,
                "rating_antes": nuevos_ratings['team_a']['old_rating'],
                "rating_despues": nuevos_ratings['team_a']['new_rating'],
                "cambio": nuevos_ratings['team_a']['rating_change'],
                "jugadores": [
                    {
                        "rating_antes": player['old_rating'],
                        "rating_despues": player['new_rating'],
                        "cambio": player['rating_change']
                    }
                    for player in nuevos_ratings['team_a']['players']
                ]
            },
            "equipo2": {
                "sets": resultado.sets_eq2,
                "rating_antes": nuevos_ratings['team_b']['old_rating'],
                "rating_despues": nuevos_ratings['team_b']['new_rating'],
                "cambio": nuevos_ratings['team_b']['rating_change'],
                "jugadores": [
                    {
                        "rating_antes": player['old_rating'],
                        "rating_despues": player['new_rating'],
                        "cambio": player['rating_change']
                    }
                    for player in nuevos_ratings['team_b']['players']
                ]
            },
            "detalles_elo": {
                "expectativa_equipo1": nuevos_ratings['match_details']['expected_a'],
                "expectativa_equipo2": nuevos_ratings['match_details']['expected_b'],
                "puntuacion_real_equipo1": nuevos_ratings['match_details']['actual_score_a'],
                "puntuacion_real_equipo2": nuevos_ratings['match_details']['actual_score_b'],
                "multiplicador_sets": nuevos_ratings['match_details']['sets_multiplier'],
                "factor_k_equipo1": nuevos_ratings['match_details']['team_a_k'],
                "factor_k_equipo2": nuevos_ratings['match_details']['team_b_k'],
                "suavizador_equipo1": nuevos_ratings['match_details']['loss_softener_a'],
                "suavizador_equipo2": nuevos_ratings['match_details']['loss_softener_b'],
                "caps_equipo1": nuevos_ratings['match_details']['caps_a'],
                "caps_equipo2": nuevos_ratings['match_details']['caps_b']
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular Elo: {str(e)}"
        )

@router.get("/usuario/{usuario_id}", response_model=List[PartidoCompleto])
async def partidos_usuario(
    usuario_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Obtener partidos de un usuario específico"""
    
    # Verificar que el usuario existe
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Buscar partidos donde participa el usuario
    partidos_jugador = db.query(PartidoJugador).filter(
        PartidoJugador.id_usuario == usuario_id
    ).all()
    
    partido_ids = [pj.id_partido for pj in partidos_jugador]
    
    # Obtener los partidos
    partidos = db.query(Partido).filter(
        Partido.id_partido.in_(partido_ids)
    ).order_by(Partido.fecha.desc()).limit(limit).all()
    
    # Construir respuesta completa
    partidos_completos = []
    for partido in partidos:
        # Obtener jugadores del partido
        jugadores = db.query(PartidoJugador).filter(
            PartidoJugador.id_partido == partido.id_partido
        ).all()
        
        # Obtener información completa de los jugadores
        jugadores_info = []
        for jugador in jugadores:
            usuario_jugador = db.query(Usuario).filter(
                Usuario.id_usuario == jugador.id_usuario
            ).first()
            perfil_jugador = db.query(PerfilUsuario).filter(
                PerfilUsuario.id_usuario == jugador.id_usuario
            ).first()
            
            if usuario_jugador:
                jugadores_info.append({
                    "id_usuario": usuario_jugador.id_usuario,
                    "nombre_usuario": usuario_jugador.nombre_usuario,
                    "nombre": perfil_jugador.nombre if perfil_jugador else "",
                    "apellido": perfil_jugador.apellido if perfil_jugador else "",
                    "equipo": jugador.equipo,
                    "rating": usuario_jugador.rating
                })
        
        # Obtener resultado si existe
        resultado = db.query(ResultadoPartido).filter(
            ResultadoPartido.id_partido == partido.id_partido
        ).first()
        
        # Obtener historial de rating para el usuario actual
        historial_rating = db.query(HistorialRating).filter(
            HistorialRating.id_partido == partido.id_partido,
            HistorialRating.id_usuario == usuario_id
        ).first()
        
        # Obtener club si existe
        club = None
        if partido.id_club:
            club = db.query(Club).filter(Club.id_club == partido.id_club).first()
        
        # Obtener creador
        creador = db.query(Usuario).filter(Usuario.id_usuario == partido.id_creador).first()
        
        partidos_completos.append(PartidoCompleto(
            id_partido=partido.id_partido,
            fecha=partido.fecha,
            estado=partido.estado,
            id_creador=partido.id_creador,
            creado_en=partido.creado_en,
            id_club=partido.id_club,
            jugadores=jugadores_info,
            resultado=resultado,
            club=club,
            creador={
                "id_usuario": creador.id_usuario,
                "nombre_usuario": creador.nombre_usuario
            } if creador else {},
            historial_rating=historial_rating
        ))
    
    return partidos_completos
