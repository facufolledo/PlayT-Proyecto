"""
Configuración centralizada de logging para PlayT.
"""
import logging
import sys
import os
from datetime import datetime


def setup_logging():
    """Configurar logging para toda la aplicación"""
    
    # Nivel según entorno
    is_production = os.getenv("ENVIRONMENT", "development") == "production"
    log_level = logging.INFO if is_production else logging.DEBUG
    
    # Formato
    if is_production:
        # Formato JSON-like para producción (mejor para log aggregators)
        format_str = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    else:
        # Formato legible para desarrollo
        format_str = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    
    # Configurar root logger
    logging.basicConfig(
        level=log_level,
        format=format_str,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Silenciar loggers ruidosos
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Logger principal de la app
    logger = logging.getLogger("playt")
    logger.setLevel(log_level)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Obtener logger para un módulo específico"""
    return logging.getLogger(f"playt.{name}")


# Loggers pre-configurados para módulos comunes
class Loggers:
    """Acceso rápido a loggers por dominio"""
    
    @staticmethod
    def elo() -> logging.Logger:
        return get_logger("elo")
    
    @staticmethod
    def torneo() -> logging.Logger:
        return get_logger("torneo")
    
    @staticmethod
    def sala() -> logging.Logger:
        return get_logger("sala")
    
    @staticmethod
    def auth() -> logging.Logger:
        return get_logger("auth")
    
    @staticmethod
    def anti_trampa() -> logging.Logger:
        return get_logger("anti_trampa")
    
    @staticmethod
    def db() -> logging.Logger:
        return get_logger("db")
