# Mejoras para el endpoint de búsqueda de usuarios

from fastapi import APIRouter, Depends, Query
from typing import List, Optional
import asyncio

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.get("/buscar")
async def buscar_usuarios_mejorado(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    limit: int = Query(5, ge=1, le=20, description="Límite de resultados"),
    exclude_ids: Optional[str] = Query(None, description="IDs a excluir separados por coma"),
    include_rating: bool = Query(True, description="Incluir rating en respuesta"),
    current_user = Depends(get_current_user)
):
    """
    Búsqueda mejorada de usuarios con filtros adicionales
    """
    try:
        # Parsear IDs a excluir
        excluded_ids = []
        if exclude_ids:
            excluded_ids = [int(id.strip()) for id in exclude_ids.split(",") if id.strip().isdigit()]
        
        # Búsqueda en base de datos con filtros
        query = """
        SELECT 
            u.id_usuario,
            u.nombre,
            u.apellido,
            u.nombre_usuario,
            u.email,
            CASE WHEN %s THEN COALESCE(r.rating, 1200) ELSE NULL END as rating,
            u.sexo,
            u.fecha_nacimiento
        FROM usuarios u
        LEFT JOIN rankings r ON u.id_usuario = r.id_usuario
        WHERE 
            (u.nombre ILIKE %s OR u.apellido ILIKE %s OR u.nombre_usuario ILIKE %s)
            AND u.id_usuario != %s
            AND (%s = '' OR u.id_usuario NOT IN %s)
            AND u.activo = true
        ORDER BY 
            -- Priorizar matches exactos
            CASE 
                WHEN u.nombre_usuario ILIKE %s THEN 1
                WHEN u.nombre ILIKE %s OR u.apellido ILIKE %s THEN 2
                ELSE 3
            END,
            -- Luego por rating (si está disponible)
            COALESCE(r.rating, 1200) DESC
        LIMIT %s
        """
        
        search_term = f"%{q}%"
        exact_term = f"{q}%"
        
        params = [
            include_rating,  # Para el CASE WHEN del rating
            search_term, search_term, search_term,  # Para las búsquedas ILIKE
            current_user.id_usuario,  # Excluir usuario actual
            len(excluded_ids) == 0,  # Condición para excluded_ids
            tuple(excluded_ids) if excluded_ids else (0,),  # Lista de IDs excluidos
            exact_term,  # Para priorización exacta
            exact_term, exact_term,  # Para priorización de nombre/apellido
            limit
        ]
        
        # Ejecutar query (ajustar según tu conexión a BD)
        # results = await database.fetch_all(query, params)
        
        # Por ahora, simulación de respuesta
        results = [
            {
                "id_usuario": 1,
                "nombre": "Juan",
                "apellido": "Pérez",
                "nombre_usuario": "juanp",
                "rating": 1350 if include_rating else None,
                "sexo": "M"
            }
        ]
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")

@router.get("/buscar/sugerencias")
async def obtener_sugerencias(
    current_user = Depends(get_current_user)
):
    """
    Obtener sugerencias de usuarios para inscripciones
    Basado en rating similar, ubicación, historial, etc.
    """
    try:
        # Lógica para sugerir usuarios compatibles
        # - Rating similar (+/- 200 puntos)
        # - Misma ciudad/región
        # - Han jugado juntos antes
        # - Disponibilidad similar
        
        query = """
        SELECT DISTINCT
            u.id_usuario,
            u.nombre,
            u.apellido,
            u.nombre_usuario,
            COALESCE(r.rating, 1200) as rating,
            u.sexo,
            ABS(COALESCE(r.rating, 1200) - COALESCE(ur.rating, 1200)) as rating_diff
        FROM usuarios u
        LEFT JOIN rankings r ON u.id_usuario = r.id_usuario
        LEFT JOIN rankings ur ON ur.id_usuario = %s
        WHERE 
            u.id_usuario != %s
            AND u.activo = true
            AND ABS(COALESCE(r.rating, 1200) - COALESCE(ur.rating, 1200)) <= 200
        ORDER BY rating_diff ASC, r.rating DESC
        LIMIT 10
        """
        
        # results = await database.fetch_all(query, [current_user.id_usuario, current_user.id_usuario])
        
        # Simulación
        results = []
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo sugerencias: {str(e)}")
