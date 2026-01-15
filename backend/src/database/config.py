from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging para monitoreo
logger = logging.getLogger(__name__)

# Configuración de la base de datos PostgreSQL (Neon)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+pg8000://neondb_owner:npg_i2uqcNEZbk4M@ep-dawn-frost-ac67h4ke-pooler.sa-east-1.aws.neon.tech/neondb")

# Detectar si estamos en producción
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"

# Configuración optimizada para escalar a 1000+ usuarios
# En Render free/starter: pool_size bajo porque hay límite de conexiones
# En producción con DB dedicada: se puede subir
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))  # Conexiones permanentes
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))  # Conexiones extra bajo demanda

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_pre_ping=True,  # CRÍTICO: verifica conexión antes de usar
    pool_recycle=280,  # Reciclar cada 4.6 min (antes de que Railway cierre a los 5 min)
    pool_timeout=30,  # Timeout para obtener conexión del pool
    connect_args={
        "timeout": 10,  # Timeout de conexión inicial
        "tcp_keepalive": True,  # Mantener conexión viva
        "tcp_keepalive_idle": 120,  # Enviar keepalive cada 2 min
        "tcp_keepalive_interval": 30,  # Intervalo entre keepalives
        "tcp_keepalive_count": 5  # Reintentos antes de considerar muerta
    },
    echo=False
)

# Event listeners para monitoreo y debugging
@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log cuando se toma una conexión del pool"""
    if not IS_PRODUCTION:
        logger.debug("Conexión tomada del pool")

@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log cuando se devuelve una conexión al pool"""
    if not IS_PRODUCTION:
        logger.debug("Conexión devuelta al pool")

@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Log cuando se crea una nueva conexión"""
    logger.info("Nueva conexión a la base de datos establecida")

@event.listens_for(engine, "close")
def receive_close(dbapi_connection, connection_record):
    """Manejar cierre de conexión de forma silenciosa"""
    try:
        # Intentar cerrar normalmente
        pass
    except Exception as e:
        # Suprimir errores de BrokenPipe al cerrar
        if "Broken pipe" in str(e) or "network error" in str(e):
            logger.debug(f"Conexión ya cerrada por el servidor: {e}")
        else:
            logger.warning(f"Error al cerrar conexión: {e}")

# Crear sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """Función para obtener la sesión de la base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_pool_status():
    """Obtener estado del pool de conexiones (útil para monitoreo)"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "checked_in": pool.checkedin()
    }
