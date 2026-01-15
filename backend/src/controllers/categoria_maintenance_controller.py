"""
Controlador para mantenimiento automático de categorías
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List

from ..database.config import get_db
from ..models.driveplus_models import Usuario, Categoria
from ..services.categoria_service import actualizar_categoria_usuario, obtener_categoria_por_rating
from ..auth.auth_utils import get_current_user

router = APIRouter(prefix="/admin/categorias", tags=["Admin - Categorías"])

@router.post("/verificar-y-corregir")
async def verificar_y_corregir_categorias(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verifica y corrige las categorías de todos los usuarios
    Solo disponible para administradores
    """
    # Verificar que el usuario sea administrador
    if not getattr(current_user, 'es_administrador', False):
        raise HTTPException(
            status_code=403, 
            detail="Solo los administradores pueden ejecutar esta acción"
        )
    
    try:
        resultado = await ejecutar_correccion_categorias(db)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al corregir categorías: {str(e)}"
        )

@router.get("/verificar")
async def verificar_categorias_sin_corregir(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Solo verifica qué usuarios tienen categorías incorrectas, sin corregir
    """
    if not getattr(current_user, 'es_administrador', False):
        raise HTTPException(
            status_code=403, 
            detail="Solo los administradores pueden ejecutar esta acción"
        )
    
    try:
        usuarios_incorrectos = []
        usuarios = db.query(Usuario).all()
        
        for usuario in usuarios:
            if not usuario.sexo:
                continue
                
            categoria_correcta = obtener_categoria_por_rating(
                db, usuario.rating or 1200, usuario.sexo
            )
            
            if categoria_correcta and usuario.id_categoria != categoria_correcta.id_categoria:
                categoria_actual = None
                if usuario.id_categoria:
                    categoria_actual = db.query(Categoria).filter(
                        Categoria.id_categoria == usuario.id_categoria
                    ).first()
                
                usuarios_incorrectos.append({
                    "id_usuario": usuario.id_usuario,
                    "nombre_usuario": usuario.nombre_usuario,
                    "rating": usuario.rating,
                    "categoria_actual": categoria_actual.nombre if categoria_actual else "Ninguna",
                    "categoria_correcta": categoria_correcta.nombre
                })
        
        return {
            "usuarios_con_categoria_incorrecta": len(usuarios_incorrectos),
            "detalles": usuarios_incorrectos
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al verificar categorías: {str(e)}"
        )

async def ejecutar_correccion_categorias(db: Session) -> Dict:
    """
    Función interna para ejecutar la corrección de categorías
    """
    usuarios_corregidos = []
    usuarios_sin_cambios = 0
    errores = []
    
    try:
        usuarios = db.query(Usuario).all()
        
        for usuario in usuarios:
            try:
                if not usuario.sexo:
                    errores.append(f"Usuario {usuario.nombre_usuario} no tiene sexo definido")
                    continue
                
                categoria_anterior_id = usuario.id_categoria
                categoria_anterior = None
                if categoria_anterior_id:
                    categoria_anterior = db.query(Categoria).filter(
                        Categoria.id_categoria == categoria_anterior_id
                    ).first()
                
                # Actualizar categoría
                categoria_nueva = actualizar_categoria_usuario(db, usuario)
                
                if categoria_nueva and categoria_anterior_id != categoria_nueva.id_categoria:
                    usuarios_corregidos.append({
                        "id_usuario": usuario.id_usuario,
                        "nombre_usuario": usuario.nombre_usuario,
                        "rating": usuario.rating,
                        "categoria_anterior": categoria_anterior.nombre if categoria_anterior else "Ninguna",
                        "categoria_nueva": categoria_nueva.nombre
                    })
                else:
                    usuarios_sin_cambios += 1
                    
            except Exception as e:
                errores.append(f"Error con usuario {usuario.nombre_usuario}: {str(e)}")
        
        # Confirmar cambios
        db.commit()
        
        return {
            "success": True,
            "usuarios_corregidos": len(usuarios_corregidos),
            "usuarios_sin_cambios": usuarios_sin_cambios,
            "errores": len(errores),
            "detalles_correcciones": usuarios_corregidos,
            "detalles_errores": errores
        }
        
    except Exception as e:
        db.rollback()
        raise e

@router.get("/estadisticas")
async def estadisticas_categorias(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Muestra estadísticas de distribución de usuarios por categoría
    """
    if not getattr(current_user, 'es_administrador', False):
        raise HTTPException(
            status_code=403, 
            detail="Solo los administradores pueden ver estas estadísticas"
        )
    
    try:
        # Obtener todas las categorías
        categorias = db.query(Categoria).order_by(
            Categoria.sexo, Categoria.rating_min.desc()
        ).all()
        
        estadisticas = []
        
        for categoria in categorias:
            # Contar usuarios en esta categoría
            usuarios_count = db.query(Usuario).filter(
                Usuario.id_categoria == categoria.id_categoria
            ).count()
            
            # Contar usuarios que DEBERÍAN estar en esta categoría por rating
            if categoria.rating_min is not None and categoria.rating_max is not None:
                usuarios_por_rating = db.query(Usuario).filter(
                    Usuario.rating >= categoria.rating_min,
                    Usuario.rating <= categoria.rating_max,
                    Usuario.sexo == categoria.sexo
                ).count()
            elif categoria.rating_min is not None:
                usuarios_por_rating = db.query(Usuario).filter(
                    Usuario.rating >= categoria.rating_min,
                    Usuario.sexo == categoria.sexo
                ).count()
            elif categoria.rating_max is not None:
                usuarios_por_rating = db.query(Usuario).filter(
                    Usuario.rating <= categoria.rating_max,
                    Usuario.sexo == categoria.sexo
                ).count()
            else:
                usuarios_por_rating = 0
            
            estadisticas.append({
                "categoria": categoria.nombre,
                "sexo": categoria.sexo,
                "rating_min": categoria.rating_min,
                "rating_max": categoria.rating_max,
                "usuarios_asignados": usuarios_count,
                "usuarios_por_rating": usuarios_por_rating,
                "diferencia": usuarios_por_rating - usuarios_count
            })
        
        return {
            "estadisticas": estadisticas,
            "total_usuarios_activos": db.query(Usuario).count()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )