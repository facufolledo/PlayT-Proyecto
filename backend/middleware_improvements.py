# Middleware mejorado para rate limiting y monitoreo

from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, Deque
import json

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.calls: Dict[str, Deque[float]] = defaultdict(deque)
    
    async def dispatch(self, request: Request, call_next):
        # Obtener IP del cliente
        client_ip = request.client.host
        
        # Limpiar llamadas antiguas (más de 1 minuto)
        now = time.time()
        minute_ago = now - 60
        
        while self.calls[client_ip] and self.calls[client_ip][0] < minute_ago:
            self.calls[client_ip].popleft()
        
        # Verificar límite
        if len(self.calls[client_ip]) >= self.calls_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later.",
                headers={"Retry-After": "60"}
            )
        
        # Registrar llamada actual
        self.calls[client_ip].append(now)
        
        # Continuar con la request
        response = await call_next(request)
        
        # Agregar headers de rate limit
        response.headers["X-RateLimit-Limit"] = str(self.calls_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.calls_per_minute - len(self.calls[client_ip]))
        )
        response.headers["X-RateLimit-Reset"] = str(int(now + 60))
        
        return response

class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.request_times: Deque[Dict] = deque(maxlen=1000)  # Últimas 1000 requests
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Ejecutar request
        response = await call_next(request)
        
        # Calcular tiempo de respuesta
        process_time = time.time() - start_time
        
        # Registrar métricas
        metrics = {
            "timestamp": start_time,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time,
            "user_agent": request.headers.get("user-agent", ""),
            "ip": request.client.host
        }
        
        self.request_times.append(metrics)
        
        # Agregar header de tiempo de respuesta
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log requests lentas (>2 segundos)
        if process_time > 2.0:
            print(f"SLOW REQUEST: {request.method} {request.url} took {process_time:.2f}s")
        
        return response
    
    def get_metrics(self):
        """Obtener métricas de performance"""
        if not self.request_times:
            return {}
        
        times = [req["process_time"] for req in self.request_times]
        
        return {
            "total_requests": len(self.request_times),
            "avg_response_time": sum(times) / len(times),
            "min_response_time": min(times),
            "max_response_time": max(times),
            "slow_requests": len([t for t in times if t > 2.0]),
            "recent_requests": list(self.request_times)[-10:]  # Últimas 10
        }

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Agregar headers de seguridad
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # CSP para desarrollo (ajustar para producción)
        if request.url.hostname in ["localhost", "127.0.0.1"]:
            response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval'"
        
        return response

# Endpoint para métricas (solo para admins)
from fastapi import APIRouter, Depends

metrics_router = APIRouter(prefix="/metrics", tags=["metrics"])

@metrics_router.get("/performance")
async def get_performance_metrics(current_user = Depends(get_current_admin_user)):
    """Obtener métricas de performance (solo admins)"""
    # Acceder al middleware desde la app
    # performance_middleware = app.user_middleware[1]  # Ajustar índice según orden
    # return performance_middleware.get_metrics()
    
    # Por ahora, datos simulados
    return {
        "total_requests": 1500,
        "avg_response_time": 0.25,
        "min_response_time": 0.05,
        "max_response_time": 3.2,
        "slow_requests": 12
    }

@metrics_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

# Función helper para verificar admin
def get_current_admin_user():
    """Verificar que el usuario actual es admin"""
    # Implementar lógica de verificación de admin
    pass
