# Guía de integración para el main.py del backend

"""
INSTRUCCIONES PARA INTEGRAR TODAS LAS MEJORAS EN TU main.py:

1. Instalar dependencias adicionales:
   pip install redis aioredis

2. Agregar imports al inicio de main.py:
"""

from middleware_improvements import (
    RateLimitMiddleware, 
    PerformanceMonitoringMiddleware, 
    SecurityHeadersMiddleware,
    metrics_router
)
from endpoints_logging import router as logging_router
from endpoints_search_improvements import router as search_router
from endpoints_notifications import router as notifications_router
from cache_system import cache

"""
3. Agregar middleware a tu app (DESPUÉS de crear la app FastAPI):
"""

# app = FastAPI(title="Drive+ API", version="1.0.0")

# Agregar middleware (el orden importa)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(PerformanceMonitoringMiddleware)
app.add_middleware(RateLimitMiddleware, calls_per_minute=120)  # 120 calls por minuto

"""
4. Incluir los nuevos routers:
"""

app.include_router(logging_router)
app.include_router(search_router)
app.include_router(notifications_router)
app.include_router(metrics_router)

"""
5. Agregar endpoint de health check mejorado:
"""

@app.get("/health")
async def enhanced_health_check():
    """Health check mejorado con más información"""
    try:
        # Verificar conexión a base de datos
        # db_status = await check_database_connection()
        
        # Verificar conexión a Redis (caché)
        cache_status = "ok"
        try:
            await cache.set("health_check", "ok", ttl=10)
            test_value = await cache.get("health_check")
            if test_value != "ok":
                cache_status = "error"
        except:
            cache_status = "error"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "database": "ok",  # db_status
                "cache": cache_status,
                "api": "ok"
            },
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

"""
6. Modificar tus endpoints existentes para usar caché:

ANTES:
@app.get("/rankings/general")
async def get_ranking_general(limit: int = 100, offset: int = 0):
    # Tu lógica actual
    pass

DESPUÉS:
"""

from cache_system import cached

@app.get("/rankings/general")
@cached("rankings:general", ttl=300)  # Caché por 5 minutos
async def get_ranking_general(limit: int = 100, offset: int = 0, sexo: Optional[str] = None):
    # Tu lógica actual (sin cambios)
    pass

"""
7. Invalidar caché cuando sea necesario:

Ejemplo: Después de actualizar un resultado de partido
"""

from cache_system import cache

async def actualizar_resultado_partido(partido_id: int, resultado: dict):
    # Tu lógica actual para actualizar resultado
    
    # Invalidar cachés relacionados
    await cache.delete_pattern("rankings:*")  # Limpiar rankings
    await cache.delete_pattern(f"torneo:*")   # Limpiar torneos
    await cache.delete_pattern("user:*")      # Limpiar perfiles de usuario

"""
8. Variables de entorno adicionales (.env):
"""

# Agregar a tu archivo .env:
REDIS_URL=redis://localhost:6379
RATE_LIMIT_PER_MINUTE=120
CACHE_DEFAULT_TTL=300
LOG_LEVEL=INFO

"""
9. Estructura de base de datos adicional:

Crear tabla para notificaciones:
"""

CREATE_NOTIFICATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    priority VARCHAR(20) DEFAULT 'normal',
    read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_notifications_user_id (user_id),
    INDEX idx_notifications_read (read),
    INDEX idx_notifications_created_at (created_at)
);
"""

"""
10. Ejemplo completo de main.py modificado:
"""

EXAMPLE_MAIN_PY = """
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

# Tus imports existentes
# ...

# Nuevos imports
from middleware_improvements import (
    RateLimitMiddleware, 
    PerformanceMonitoringMiddleware, 
    SecurityHeadersMiddleware,
    metrics_router
)
from endpoints_logging import router as logging_router
from endpoints_notifications import router as notifications_router
from cache_system import cache, cached

app = FastAPI(title="Drive+ API", version="1.0.0")

# CORS (tu configuración actual)
origins = [
    "http://localhost:3000",
    "http://localhost:5173", 
    "https://kioskito.click",
    "https://www.kioskito.click"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nuevos middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(PerformanceMonitoringMiddleware)
app.add_middleware(RateLimitMiddleware, calls_per_minute=120)

# Incluir routers
app.include_router(logging_router)
app.include_router(notifications_router)
app.include_router(metrics_router)

# Tus routers existentes
# app.include_router(torneos_router)
# app.include_router(usuarios_router)
# etc...

# Health check mejorado
@app.get("/health")
async def enhanced_health_check():
    # Código del health check de arriba
    pass

# Tus endpoints existentes con caché agregado
@app.get("/rankings/general")
@cached("rankings:general", ttl=300)
async def get_ranking_general(limit: int = 100, offset: int = 0, sexo: Optional[str] = None):
    # Tu lógica actual sin cambios
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

print("Guía de integración creada. Revisa los archivos generados y sigue las instrucciones.")
