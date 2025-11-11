from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Imports del proyecto
from src.database.config import engine  # NO importamos create_tables (no existe)
from src.controllers.auth_controller import router as auth_router
from src.controllers.categoria_controller import router as categoria_router
from src.controllers.partido_controller import router as partido_router

# Crear la app FastAPI
app = FastAPI(
    title=os.getenv("APP_NAME", "PlayT API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="API para el sistema de pádel PlayT con ranking Elo",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---- CORS seguro (json.loads en vez de eval) ----
default_origins_json = '["http://localhost:3000", "http://localhost:8080"]'
cors_env = os.getenv("CORS_ORIGINS", default_origins_json)

try:
    origins = json.loads(cors_env)
    if not isinstance(origins, list):
        raise ValueError("CORS_ORIGINS debe ser una lista JSON de strings.")
except Exception:
    # Fallback seguro si la variable está mal formada
    origins = json.loads(default_origins_json)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Routers ----
app.include_router(auth_router)
app.include_router(categoria_router)
app.include_router(partido_router)

# ---- Eventos ----
@app.on_event("startup")
async def startup_event():
    """Chequeo simple de conexión a la base al iniciar."""
    print("🚀 Iniciando PlayT API...")
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Conexión a base de datos exitosa")
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")

# ---- Endpoints básicos ----
@app.get("/")
async def root():
    return {
        "message": "¡Bienvenido a PlayT API! 🎾",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "status": "running",
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "PlayT API",
        "database": "connected",
    }

@app.get("/api/info")
async def api_info():
    return {
        "name": "PlayT API",
        "description": "Sistema de pádel con ranking Elo",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "features": [
            "Sistema de usuarios y autenticación",
            "Gestión de partidos de pádel",
            "Algoritmo Elo para rankings",
            "Historial de ratings",
            "Estadísticas de jugadores",
        ],
        "endpoints": {
            "documentation": "/docs",
            "health_check": "/health",
            "api_info": "/api/info",
        },
    }

# ---- Runner local ----
if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    print(f"🌐 Servidor iniciando en http://{host}:{port}")
    print(f"📚 Documentación:       http://{host}:{port}/docs")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,   # Recarga en caliente si DEBUG=True
        log_level="info",
    )
