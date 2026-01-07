"""
Sistema de caché en memoria para Drive+.
Optimizado para escalar a 1000+ usuarios sin necesidad de Redis.

Para datos que cambian poco y se consultan mucho:
- Rankings
- Estadísticas globales
- Listados de torneos activos
"""
from functools import wraps
from datetime import datetime, timedelta
from typing import Any, Callable, Optional
import threading
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """
    Caché en memoria thread-safe con TTL.
    Suficiente para 1000 usuarios. Para más, migrar a Redis.
    """
    
    def __init__(self):
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del caché si no expiró"""
        with self._lock:
            if key not in self._cache:
                return None
            
            value, expires_at = self._cache[key]
            if datetime.now() > expires_at:
                del self._cache[key]
                return None
            
            return value
    
    def set(self, key: str, value: Any, ttl_seconds: int = 60):
        """Guardar valor en caché con TTL"""
        with self._lock:
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            self._cache[key] = (value, expires_at)
    
    def delete(self, key: str):
        """Eliminar una key específica"""
        with self._lock:
            self._cache.pop(key, None)
    
    def delete_pattern(self, pattern: str):
        """Eliminar todas las keys que contengan el pattern"""
        with self._lock:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._cache[key]
    
    def clear(self):
        """Limpiar todo el caché"""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self):
        """Limpiar entries expirados (llamar periódicamente)"""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                k for k, (_, expires_at) in self._cache.items() 
                if now > expires_at
            ]
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"Cache cleanup: {len(expired_keys)} keys eliminadas")
    
    def stats(self) -> dict:
        """Estadísticas del caché"""
        with self._lock:
            return {
                "total_keys": len(self._cache),
                "keys": list(self._cache.keys())
            }


# Instancia global del caché
cache = SimpleCache()


# TTLs recomendados por tipo de dato
CACHE_TTL = {
    "ranking": 60,           # Rankings: 1 minuto
    "estadisticas": 120,     # Estadísticas globales: 2 minutos
    "torneos_activos": 30,   # Lista de torneos: 30 segundos
    "perfil_usuario": 300,   # Perfil de usuario: 5 minutos
    "default": 60
}


def cached(key_prefix: str, ttl_seconds: Optional[int] = None):
    """
    Decorador para cachear resultados de funciones.
    
    Uso:
        @cached("ranking", ttl_seconds=60)
        def get_ranking_global(db, categoria):
            ...
    
    La key se genera como: {prefix}:{args}
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar key única basada en argumentos (ignorando db session)
            cache_args = []
            for arg in args:
                if hasattr(arg, '__class__') and 'Session' in arg.__class__.__name__:
                    continue  # Ignorar session de DB
                cache_args.append(str(arg))
            
            for k, v in sorted(kwargs.items()):
                if k != 'db':
                    cache_args.append(f"{k}={v}")
            
            cache_key = f"{key_prefix}:{':'.join(cache_args)}"
            
            # Intentar obtener del caché
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value
            
            # Ejecutar función y cachear resultado
            logger.debug(f"Cache MISS: {cache_key}")
            result = func(*args, **kwargs)
            
            ttl = ttl_seconds or CACHE_TTL.get(key_prefix, CACHE_TTL["default"])
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_ranking_cache():
    """Invalidar caché de rankings (llamar después de guardar resultado)"""
    cache.delete_pattern("ranking")


def invalidate_torneo_cache(torneo_id: Optional[int] = None):
    """Invalidar caché de torneos"""
    if torneo_id:
        cache.delete_pattern(f"torneo:{torneo_id}")
    cache.delete_pattern("torneos_activos")


def invalidate_user_cache(user_id: int):
    """Invalidar caché de un usuario específico"""
    cache.delete_pattern(f"user:{user_id}")
