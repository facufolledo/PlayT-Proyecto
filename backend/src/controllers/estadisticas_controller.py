from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..database.config import get_db
from ..models.Drive+_models import Usuario, PartidoJugador, ResultadoPartido, Partido
from ..auth.auth_utils import get_current_user

router = APIRouter(prefix="/estadisticas", tags=["Estadísticas"])

@router.get("/usuario")
async def get_estadisticas_usuario(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas del usuario actual"""
    
    try:
        # Contar partidos donde el usuario participó y tienen resultado (reportado o confirmado)
        # Un partido cuenta como "jugado" si tiene resultado reportado o confirmado
        partidos_completos = db.query(Partido).join(
            PartidoJugador, Partido.id_partido == PartidoJugador.id_partido
        ).filter(
            and_(
                PartidoJugador.id_usuario == current_user.id_usuario,
                Partido.estado.in_(["reportado", "confirmado"])
            )
        ).all()
        
        # También contar partidos que tienen resultado aunque el estado no sea reportado/confirmado
        # Esto cubre casos donde el estado puede ser diferente pero hay resultado
        partidos_con_resultado = db.query(Partido).join(
            PartidoJugador, Partido.id_partido == PartidoJugador.id_partido
        ).join(
            ResultadoPartido, Partido.id_partido == ResultadoPartido.id_partido
        ).filter(
            PartidoJugador.id_usuario == current_user.id_usuario
        ).all()
        
        # Combinar y deduplicar por id_partido
        todos_partidos = {p.id_partido: p for p in partidos_completos}
        for p in partidos_con_resultado:
            if p.id_partido not in todos_partidos:
                todos_partidos[p.id_partido] = p
        
        partidos_completos = list(todos_partidos.values())
        
        # Contar partidos ganados
        partidos_ganados = 0
        for partido in partidos_completos:
            # Obtener resultado del partido
            resultado = db.query(ResultadoPartido).filter(
                ResultadoPartido.id_partido == partido.id_partido
            ).first()
            
            if resultado:
                # Obtener el equipo del usuario
                partido_jugador = db.query(PartidoJugador).filter(
                    and_(
                        PartidoJugador.id_partido == partido.id_partido,
                        PartidoJugador.id_usuario == current_user.id_usuario
                    )
                ).first()
                
                if partido_jugador:
                    equipo_usuario = partido_jugador.equipo
                    # Verificar si el equipo del usuario ganó
                    # sets_eq1 son los sets del equipo 1, sets_eq2 son los sets del equipo 2
                    if (equipo_usuario == 1 and resultado.sets_eq1 > resultado.sets_eq2) or \
                       (equipo_usuario == 2 and resultado.sets_eq2 > resultado.sets_eq1):
                        partidos_ganados += 1
        
        partidos_jugados = len(partidos_completos)
        partidos_perdidos = partidos_jugados - partidos_ganados
        porcentaje_victoria = round((partidos_ganados / partidos_jugados * 100), 1) if partidos_jugados > 0 else 0
        
        # TODO: Contar torneos participados (cuando tengamos la tabla de torneos)
        torneos_participados = 0
        
        return {
            "id_usuario": current_user.id_usuario,
            "partidos_jugados": partidos_jugados,
            "partidos_ganados": partidos_ganados,
            "partidos_perdidos": partidos_perdidos,
            "porcentaje_victoria": porcentaje_victoria,
            "rating": current_user.rating,
            "torneos_participados": torneos_participados,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )

