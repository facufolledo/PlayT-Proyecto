from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta

from ..database.config import get_db
from ..models.playt_models import Usuario, PerfilUsuario, Categoria
from ..schemas.ranking import RankingResponse, TopWeeklyResponse
from ..auth.auth_utils import get_current_user

router = APIRouter(prefix="/ranking", tags=["Ranking"])

@router.get("/", response_model=List[RankingResponse])
async def get_ranking(
    limit: int = Query(100, description="Número de jugadores a retornar"),
    offset: int = Query(0, description="Número de jugadores a saltar"),
    sexo: Optional[str] = Query(None, description="Filtrar por sexo: M o F"),
    db: Session = Depends(get_db)
):
    """Obtener el ranking general de jugadores"""
    
    try:
        from ..models.playt_models import PartidoJugador, ResultadoPartido, Partido
        from sqlalchemy import case
        
        # Subquery para calcular partidos ganados de forma eficiente
        partidos_ganados_subq = (
            db.query(
                PartidoJugador.id_usuario,
                func.count(PartidoJugador.id_partido).label("partidos_ganados")
            )
            .join(ResultadoPartido, PartidoJugador.id_partido == ResultadoPartido.id_partido)
            .join(Partido, PartidoJugador.id_partido == Partido.id_partido)
            .filter(
                Partido.estado == "finalizado",
                ResultadoPartido.confirmado == True,
                # Equipo 1 gana si sets_eq1 > sets_eq2, Equipo 2 gana si sets_eq2 > sets_eq1
                (
                    ((PartidoJugador.equipo == 1) & (ResultadoPartido.sets_eq1 > ResultadoPartido.sets_eq2)) |
                    ((PartidoJugador.equipo == 2) & (ResultadoPartido.sets_eq2 > ResultadoPartido.sets_eq1))
                )
            )
            .group_by(PartidoJugador.id_usuario)
            .subquery()
        )
        
        # Query principal con JOIN a la subquery
        query = (
            db.query(
                Usuario.id_usuario,
                Usuario.nombre_usuario,
                Usuario.rating,
                Usuario.partidos_jugados,
                Usuario.sexo,
                PerfilUsuario.nombre,
                PerfilUsuario.apellido,
                PerfilUsuario.ciudad,
                PerfilUsuario.pais,
                PerfilUsuario.url_avatar,
                Categoria.nombre.label("categoria_nombre"),
                func.coalesce(partidos_ganados_subq.c.partidos_ganados, 0).label("partidos_ganados")
            )
            .join(PerfilUsuario, Usuario.id_usuario == PerfilUsuario.id_usuario, isouter=True)
            .join(Categoria, Usuario.id_categoria == Categoria.id_categoria, isouter=True)
            .join(partidos_ganados_subq, Usuario.id_usuario == partidos_ganados_subq.c.id_usuario, isouter=True)
        )
        
        # Filtrar por sexo si se especifica
        if sexo:
            # Aceptar tanto 'M'/'F' como 'masculino'/'femenino'
            if sexo in ['M', 'masculino']:
                query = query.filter(Usuario.sexo.in_(['M', 'masculino']))
            elif sexo in ['F', 'femenino']:
                query = query.filter(Usuario.sexo.in_(['F', 'femenino']))
        
        # Ordenar y paginar
        usuarios = query.order_by(desc(Usuario.rating)).offset(offset).limit(limit).all()
        
        # Formatear respuesta
        ranking = []
        for i, usuario in enumerate(usuarios):
            ranking.append(RankingResponse(
                posicion=offset + i + 1,
                id_usuario=usuario.id_usuario,
                nombre_usuario=usuario.nombre_usuario,
                nombre=usuario.nombre or "",
                apellido=usuario.apellido or "",
                ciudad=usuario.ciudad or "",
                pais=usuario.pais or "",
                rating=usuario.rating,
                partidos_jugados=usuario.partidos_jugados,
                partidos_ganados=usuario.partidos_ganados,
                categoria=getattr(usuario, "categoria_nombre", None),
                sexo=usuario.sexo,
                imagen_url=usuario.url_avatar or None
            ))
        
        return ranking
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el ranking: {str(e)}"
        )

@router.get("/top-weekly", response_model=List[TopWeeklyResponse])
async def get_top_weekly(
    limit: int = Query(5, description="Número de jugadores a retornar"),
    db: Session = Depends(get_db)
):
    """Obtener los mejores jugadores de la semana actual"""
    
    try:
        # Calcular fecha de inicio de la semana actual
        fecha_actual = datetime.now()
        inicio_semana = fecha_actual - timedelta(days=fecha_actual.weekday())
        inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Obtener usuarios con mejor rating (simulando ranking semanal)
        usuarios = db.query(
            Usuario.id_usuario,
            Usuario.nombre_usuario,
            Usuario.email,
            Usuario.rating,
            Usuario.partidos_jugados,
            PerfilUsuario.nombre,
            PerfilUsuario.apellido,
            PerfilUsuario.ciudad,
            PerfilUsuario.pais,
            PerfilUsuario.url_avatar
        ).join(
            PerfilUsuario, Usuario.id_usuario == PerfilUsuario.id_usuario, isouter=True
        ).order_by(
            desc(Usuario.rating)
        ).limit(limit).all()
        
        # Datos de ejemplo para el ranking semanal (esto se puede reemplazar con datos reales)
        sample_data = [
            {
                'id': 1,
                'nombre': 'Alejandro Martín',
                'ciudad': 'Madrid',
                'puntos': 1850,
                'imagen_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
                'rating': 1850,
            },
            {
                'id': 2,
                'nombre': 'Isabel Garcia',
                'ciudad': 'Barcelona',
                'puntos': 1820,
                'imagen_url': 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face',
                'rating': 1820,
            },
            {
                'id': 3,
                'nombre': 'Miguel Rodriguez',
                'ciudad': 'Valencia',
                'puntos': 1790,
                'imagen_url': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
                'rating': 1790,
            },
            {
                'id': 4,
                'nombre': 'Carmen López',
                'ciudad': 'Sevilla',
                'puntos': 1760,
                'imagen_url': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
                'rating': 1760,
            },
            {
                'id': 5,
                'nombre': 'David Fernández',
                'ciudad': 'Madrid',
                'puntos': 1745,
                'imagen_url': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face',
                'rating': 1745,
            },
        ]
        
        # Formatear respuesta con datos de ejemplo
        top_weekly = []
        for i, data in enumerate(sample_data[:limit]):
            top_weekly.append(TopWeeklyResponse(
                id=data['id'],
                nombre=data['nombre'],
                ciudad=data['ciudad'],
                puntos=data['puntos'],
                imagen_url=data['imagen_url'],
                rating=data['rating']
            ))
        
        return top_weekly
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el ranking semanal: {str(e)}"
        )

@router.get("/historial/{user_id}")
async def get_historial_elo(
    user_id: int,
    limit: int = Query(20, description="Número de registros a retornar"),
    db: Session = Depends(get_db)
):
    """Obtener el historial de cambios de rating de un usuario"""
    
    try:
        # Verificar que el usuario existe
        usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Aquí se puede implementar la lógica para obtener el historial de rating
        # Por ahora retornamos datos de ejemplo
        historial = [
            {
                "fecha": "2024-09-01",
                "rating_anterior": 1427,
                "rating_nuevo": 1450,
                "cambio": 23,
                "partido_id": 1
            },
            {
                "fecha": "2024-08-29",
                "rating_anterior": 1439,
                "rating_nuevo": 1427,
                "cambio": -12,
                "partido_id": 2
            },
            {
                "fecha": "2024-08-27",
                "rating_anterior": 1421,
                "rating_nuevo": 1439,
                "cambio": 18,
                "partido_id": 3
            }
        ]
        
        return {
            "usuario_id": user_id,
            "historial": historial[:limit]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el historial: {str(e)}"
        )
