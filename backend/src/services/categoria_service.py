"""
Servicio para gestión de categorías
"""
from sqlalchemy.orm import Session
from typing import Optional
from ..models.driveplus_models import Categoria, Usuario


def actualizar_categoria_usuario(db: Session, usuario: Usuario) -> Optional[Categoria]:
    """
    Actualiza la categoría de un usuario según su rating actual
    
    Args:
        db: Sesión de base de datos
        usuario: Usuario a actualizar
        
    Returns:
        La nueva categoría asignada o None si no se encontró
    """
    # Buscar la categoría que corresponde al rating y sexo del usuario
    nueva_categoria = db.query(Categoria).filter(
        Categoria.sexo == usuario.sexo,
        (Categoria.rating_min.is_(None) | (Categoria.rating_min <= usuario.rating)),
        (Categoria.rating_max.is_(None) | (Categoria.rating_max >= usuario.rating))
    ).order_by(Categoria.rating_min.desc()).first()
    
    if nueva_categoria:
        usuario.id_categoria = nueva_categoria.id_categoria
        return nueva_categoria
    
    return None


def obtener_categoria_por_rating(db: Session, rating: int, sexo: str) -> Optional[Categoria]:
    """
    Obtiene la categoría que corresponde a un rating y sexo específicos
    
    Args:
        db: Sesión de base de datos
        rating: Rating del jugador
        sexo: Sexo del jugador ('M' o 'F')
        
    Returns:
        La categoría correspondiente o None si no se encontró
    """
    categoria = db.query(Categoria).filter(
        Categoria.sexo == sexo,
        (Categoria.rating_min.is_(None) | (Categoria.rating_min <= rating)),
        (Categoria.rating_max.is_(None) | (Categoria.rating_max >= rating))
    ).order_by(Categoria.rating_min.desc()).first()
    
    return categoria
