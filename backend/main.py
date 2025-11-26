import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
from sqlalchemy import text

# Cargar variables de entorno
load_dotenv()

# Imports del proyecto
from src.database.config import engine
from src.controllers.auth_controller import router as auth_router
from src.controllers.usuario_controller import router as usuario_router
from src.controllers.categoria_controller import router as categoria_router
from src.controllers.partido_controller import router as partido_router
from src.controllers.ranking_controller import router as ranking_router
from src.controllers.estadisticas_controller import router as estadisticas_router
from src.controllers.sala_controller import router as sala_router
from src.controllers.resultado_controller import router as resultado_router


# ---- Lifespan (startup/shutdown) ----
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Iniciando PlayT API...")
    try:
        with engine.connect() as conn:
            # En SQLAlchemy 2.x, usar text() o exec_driver_sql()
            conn.execute(text("SELECT 1"))
        print("✅ Conexión a base de datos exitosa")
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
    
    # Inicializar Firebase Admin
    try:
        from src.auth.firebase_handler import FirebaseHandler
        if FirebaseHandler.initialize():
            print("✅ Firebase Admin inicializado correctamente")
        else:
            print("⚠️ Firebase Admin no pudo inicializarse")
    except Exception as e:
        print(f"❌ Error al inicializar Firebase Admin: {e}")

    yield  # <- aquí la app queda levantada

    # Shutdown
    print("🛑 Cerrando PlayT API...")


# ---- Crear app ----
app = FastAPI(
    title=os.getenv("APP_NAME", "PlayT API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="API para el sistema de pádel PlayT con ranking Elo",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,  # 👈 reemplaza on_event
)

# ---- CORS (json.loads en vez de eval) ----
_default_origins = '["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "https://kioskito.click", "https://www.kioskito.click"]'
try:
    origins = json.loads(os.getenv("CORS_ORIGINS", _default_origins))
    if not isinstance(origins, list):
        raise ValueError("CORS_ORIGINS debe ser una lista JSON de strings.")
except Exception:
    origins = json.loads(_default_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Routers ----
app.include_router(auth_router)
app.include_router(usuario_router)
app.include_router(categoria_router)
app.include_router(sala_router)
app.include_router(resultado_router)
app.include_router(partido_router)
app.include_router(ranking_router)
app.include_router(estadisticas_router)

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
    return {"status": "healthy", "service": "PlayT API", "database": "connected"}

@app.get("/debug/firebase")
async def firebase_debug():
    """Endpoint de debug para verificar estado de Firebase"""
    from src.auth.firebase_handler import FirebaseHandler
    
    return {
        "firebase_available": FirebaseHandler._initialized,
        "credentials_path_env": os.getenv("FIREBASE_CREDENTIALS_PATH"),
        "credentials_json_env": "SET" if os.getenv("FIREBASE_CREDENTIALS_JSON") else "NOT SET",
        "credentials_path_exists": os.path.exists(os.getenv("FIREBASE_CREDENTIALS_PATH", "")) if os.getenv("FIREBASE_CREDENTIALS_PATH") else False,
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
        reload=debug,
        log_level="info",
    )
