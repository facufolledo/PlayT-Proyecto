from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from typing import List

from ..database.config import get_db
from ..models.playt_models import Categoria, Usuario
from ..schemas.categoria import CategoriaResponse, JugadoresPorCategoriaResponse, JugadorCategoriaResponse

router = APIRouter(prefix="/categorias", tags=["Categorías"])

@router.get("/", response_model=List[CategoriaResponse])
async def get_categorias(sexo: str = "masculino", db: Session = Depends(get_db)):
    """Obtener todas las categorías filtradas por sexo"""
    categorias = db.query(Categoria).filter(Categoria.sexo == sexo).order_by(Categoria.rating_min.asc()).all()
    return categorias

@router.get("/{categoria_id}", response_model=CategoriaResponse)
async def get_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Obtener una categoría específica"""
    categoria = db.query(Categoria).filter(Categoria.id_categoria == categoria_id).first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    
    return categoria

   

@router.get("/usuario/{usuario_id}/categoria", response_model=CategoriaResponse)
async def get_categoria_por_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtener la categoría de un jugador específico por su ID"""
    usuario = db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Buscar la categoría que contenga el rating y sea del mismo sexo
    categoria = db.query(Categoria).filter(
        Categoria.sexo == usuario.sexo &
        (Categoria.rating_min.is_(None) | (Categoria.rating_min <= usuario.rating)) &
        (Categoria.rating_max.is_(None) | (Categoria.rating_max >= usuario.rating))
    ).order_by(Categoria.rating_min.desc()).first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se pudo determinar la categoría del usuario"
        )
    
    return categoria

@router.get("/ranking/global", response_model=List[dict])
async def get_ranking_global(db: Session = Depends(get_db), limit: int = 100):
    """Obtener ranking global de jugadores"""
    jugadores = db.query(
        Usuario.id_usuario,
        Usuario.nombre_usuario,
        Usuario.rating,
        Usuario.partidos_jugados
    ).order_by(Usuario.rating.desc()).limit(limit).all()
    
    ranking = []
    for i, jugador in enumerate(jugadores, 1):
        ranking.append({
            "posicion": i,
            "id_usuario": jugador.id_usuario,
            "nombre_usuario": jugador.nombre_usuario,
            "rating": jugador.rating,
            "partidos_jugados": jugador.partidos_jugados
        })
    
    return ranking

@router.get("/{categoria_id}/jugadores", response_model=JugadoresPorCategoriaResponse)
async def get_jugadores_por_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Obtener todos los jugadores de una categoría específica"""
    # Verificar que la categoría existe
    categoria = db.query(Categoria).filter(Categoria.id_categoria == categoria_id).first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )
    
    # Obtener jugadores que pertenecen a esta categoría y sean del mismo sexo
    # Si la categoría tiene rating_min y rating_max definidos, buscar por rango
    if categoria.rating_min is not None and categoria.rating_max is not None:
        jugadores = db.query(Usuario).filter(
            Usuario.rating >= categoria.rating_min,
            Usuario.rating <= categoria.rating_max,
            Usuario.sexo == categoria.sexo
        ).order_by(Usuario.rating.desc()).all()
    elif categoria.rating_min is not None:
        # Solo rating mínimo definido
        jugadores = db.query(Usuario).filter(
            Usuario.rating >= categoria.rating_min,
            Usuario.sexo == categoria.sexo
        ).order_by(Usuario.rating.desc()).all()
    elif categoria.rating_max is not None:
        # Solo rating máximo definido
        jugadores = db.query(Usuario).filter(
            Usuario.rating <= categoria.rating_max,
            Usuario.sexo == categoria.sexo
        ).order_by(Usuario.rating.desc()).all()
    else:
        # Si no hay rangos definidos, buscar por id_categoria directo
        jugadores = db.query(Usuario).filter(
            Usuario.id_categoria == categoria_id
        ).order_by(Usuario.rating.desc()).all()
    
    # Convertir a la respuesta esperada
    jugadores_response = []
    for jugador in jugadores:
        jugadores_response.append(JugadorCategoriaResponse(
            id_usuario=jugador.id_usuario,
            nombre_usuario=jugador.nombre_usuario,
            rating=jugador.rating,
            partidos_jugados=jugador.partidos_jugados
        ))
    
    return JugadoresPorCategoriaResponse(
        categoria=categoria,
        jugadores=jugadores_response,
        total_jugadores=len(jugadores_response)
    )
