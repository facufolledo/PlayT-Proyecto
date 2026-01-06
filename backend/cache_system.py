# Sistema de caché para el backend

import redis
import json
import asyncio
from typing import Any, Optional, Union
from datetime import datetime, timedelta
import hashlib

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 300  # 5 minutos por defecto
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generar clave de caché consistente"""
        if not kwargs:
            return prefix
        
        # Ordenar parámetros para consistencia
        sorted_params = sorted(kwargs.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        
        return f"{prefix}:{params_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtener valor del caché"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Guardar valor en caché"""
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)  # default=str para datetime
            return self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Eliminar clave del caché"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Eliminar claves que coincidan con patrón"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            return 0

# Instancia global
cache = CacheManager()

# Decorador para cachear funciones
def cached(prefix: str, ttl: Optional[int] = None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generar clave de caché
            cache_key = cache._generate_key(prefix, **kwargs)
            
            # Intentar obtener del caché
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Ejemplos de uso en endpoints

@cached("rankings:general", ttl=300)  # 5 minutos
async def get_ranking_general_cached(limit: int = 100, offset: int = 0, sexo: Optional[str] = None):
    """Ranking general con caché"""
    # Tu lógica actual de ranking
    pass

@cached("torneo:details", ttl=600)  # 10 minutos
async def get_torneo_details_cached(torneo_id: int):
    """Detalles de torneo con caché"""
    # Tu lógica actual de torneo
    pass

@cached("user:profile", ttl=1800)  # 30 minutos
async def get_user_profile_cached(user_id: int):
    """Perfil de usuario con caché"""
    # Tu lógica actual de perfil
    pass

# Funciones para invalidar caché específico
async def invalidate_ranking_cache():
    """Invalidar caché de rankings cuando hay cambios"""
    await cache.delete_pattern("rankings:*")

async def invalidate_torneo_cache(torneo_id: int):
    """Invalidar caché de torneo específico"""
    await cache.delete_pattern(f"torneo:*:{torneo_id}:*")

async def invalidate_user_cache(user_id: int):
    """Invalidar caché de usuario específico"""
    await cache.delete_pattern(f"user:*:{user_id}:*")
