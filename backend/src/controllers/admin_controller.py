"""
Controller para funcionalidades de administración
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta

from ..database.config import get_db
from ..models.driveplus_models import Usuario, Partido
from ..models.torneo_models import Torneo
from ..auth.auth_utils import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(current_user: Usuario = Depends(get_current_user)):
    """Verificar que el usuario sea administrador"""
    if not current_user.es_administrador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user


@router.get("/estadisticas")
async def obtener_estadisticas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin)
):
    """Obtiene estadísticas generales del sistema para el panel de admin"""
    
    # Total usuarios
    total_usuarios = db.query(func.count(Usuario.id_usuario)).scalar() or 0
    
    # Usuarios activos en el último mes (con partidos)
    hace_un_mes = datetime.now() - timedelta(days=30)
    usuarios_activos = db.execute(text("""
        SELECT COUNT(DISTINCT hr.id_usuario) 
        FROM historial_rating hr
        JOIN partidos p ON hr.id_partido = p.id_partido
        WHERE p.fecha >= :fecha OR p.creado_en >= :fecha
    """), {'fecha': hace_un_mes}).scalar() or 0
    
    # Total torneos
    total_torneos = db.query(func.count(Torneo.id)).scalar() or 0
    
    # Torneos activos (en_curso o inscripcion)
    torneos_activos = db.query(func.count(Torneo.id)).filter(
        Torneo.estado.in_(['inscripcion', 'en_curso'])
    ).scalar() or 0
    
    # Total partidos
    total_partidos = db.query(func.count(Partido.id_partido)).filter(
        Partido.estado.in_(['confirmado', 'finalizado'])
    ).scalar() or 0
    
    # Partidos de hoy
    hoy = datetime.now().date()
    partidos_hoy = db.execute(text("""
        SELECT COUNT(*) FROM partidos 
        WHERE DATE(fecha) = :hoy OR DATE(creado_en) = :hoy
    """), {'hoy': hoy}).scalar() or 0
    
    return {
        "total_usuarios": total_usuarios,
        "usuarios_activos_mes": usuarios_activos,
        "total_torneos": total_torneos,
        "torneos_activos": torneos_activos,
        "total_partidos": total_partidos,
        "partidos_hoy": partidos_hoy
    }
