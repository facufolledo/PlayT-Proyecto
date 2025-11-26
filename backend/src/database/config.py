from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos PostgreSQL (Neon)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+pg8000://neondb_owner:npg_i2uqcNEZbk4M@ep-dawn-frost-ac67h4ke-pooler.sa-east-1.aws.neon.tech/neondb")

# Crear engine de SQLAlchemy para PostgreSQL
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # Aumentado de 10 a 20
    max_overflow=40,  # Aumentado de 20 a 40
    pool_pre_ping=True,
    pool_recycle=1800,  # Reciclar conexiones cada 30 minutos
    pool_timeout=10,  # Timeout de 10 segundos
    echo=False  # Desactivar logs SQL para mejor rendimiento
)

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
