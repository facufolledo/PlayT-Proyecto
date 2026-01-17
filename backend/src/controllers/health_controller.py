"""
Health Check y Monitoreo
Endpoints para verificar estado del sistema en producción
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database.config import get_db, get_pool_status
from ..utils.cache import cache

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    """Health check básico + inicio de tareas programadas"""
    try:
        # Iniciar tareas programadas si no están iniciadas
        from ..services.scheduled_tasks import scheduler_service
        if not scheduler_service.running:
            await scheduler_service.start_scheduler()
        
        return {
            "status": "ok",
            "scheduled_tasks": "running" if scheduler_service.running else "stopped"
        }
    except Exception as e:
        return {
            "status": "ok",
            "scheduled_tasks_error": str(e)
        }


@router.get("/db")
async def db_health(db: Session = Depends(get_db)):
    """Verificar conexión a base de datos"""
    try:
        db.execute(text("SELECT 1"))
        pool_status = get_pool_status()
        return {
            "status": "ok",
            "database": "connected",
            "pool": pool_status
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }


@router.get("/cache")
async def cache_health():
    """Ver estado del caché en memoria"""
    stats = cache.stats()
    return {
        "status": "ok",
        "cache": stats
    }


@router.post("/cache/clear")
async def clear_cache():
    """Limpiar todo el caché (usar con cuidado)"""
    cache.clear()
    return {"status": "ok", "message": "Cache cleared"}


@router.post("/cache/cleanup")
async def cleanup_cache():
    """Limpiar entries expirados del caché"""
    cache.cleanup_expired()
    return {"status": "ok", "message": "Expired entries cleaned"}
