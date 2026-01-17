"""
Servicio de tareas programadas para mantenimiento automático
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from ..database.config import SessionLocal
from ..models.driveplus_models import Usuario, Categoria
from ..services.categoria_service import actualizar_categoria_usuario
from ..controllers.categoria_maintenance_controller import ejecutar_correccion_categorias

logger = logging.getLogger(__name__)

class ScheduledTasksService:
    """Servicio para ejecutar tareas programadas"""
    
    def __init__(self):
        self.running = False
        self.last_categoria_check: Optional[datetime] = None
    
    async def start_scheduler(self):
        """Inicia el programador de tareas (NO BLOQUEANTE)"""
        if self.running:
            return
        
        self.running = True
        logger.info("🕐 Iniciando programador de tareas automáticas")
        
        # CORREGIDO: No ejecutar bucle infinito aquí
        # Solo marcar como iniciado y programar primera ejecución
        try:
            # Ejecutar primera verificación inmediata (sin bloquear)
            import asyncio
            asyncio.create_task(self._background_scheduler())
            logger.info("✅ Programador de tareas iniciado en background")
        except Exception as e:
            logger.error(f"Error iniciando programador: {e}")
    
    async def _background_scheduler(self):
        """Bucle de tareas en background (separado del startup)"""
        while self.running:
            try:
                await self.check_and_run_tasks()
                # Esperar 1 hora antes de la siguiente verificación
                await asyncio.sleep(3600)  # 3600 segundos = 1 hora
            except Exception as e:
                logger.error(f"Error en programador de tareas: {e}")
                await asyncio.sleep(300)  # Esperar 5 minutos si hay error
    
    def stop_scheduler(self):
        """Detiene el programador de tareas"""
        self.running = False
        logger.info("🛑 Deteniendo programador de tareas automáticas")
    
    async def check_and_run_tasks(self):
        """Verifica y ejecuta las tareas que correspondan"""
        now = datetime.now()
        
        # Verificar categorías cada 6 horas
        if self.should_run_categoria_check(now):
            await self.run_categoria_maintenance()
            self.last_categoria_check = now
    
    def should_run_categoria_check(self, now: datetime) -> bool:
        """Determina si debe ejecutar la verificación de categorías"""
        if self.last_categoria_check is None:
            return True
        
        # Ejecutar cada 6 horas
        return now - self.last_categoria_check >= timedelta(hours=6)
    
    async def run_categoria_maintenance(self):
        """Ejecuta el mantenimiento de categorías"""
        logger.info("🔧 Iniciando mantenimiento automático de categorías")
        
        db = SessionLocal()
        try:
            resultado = await ejecutar_correccion_categorias(db)
            
            if resultado['usuarios_corregidos'] > 0:
                logger.info(
                    f"✅ Mantenimiento completado: {resultado['usuarios_corregidos']} "
                    f"usuarios corregidos, {resultado['errores']} errores"
                )
            else:
                logger.info("✅ Mantenimiento completado: No se requirieron correcciones")
                
        except Exception as e:
            logger.error(f"❌ Error en mantenimiento de categorías: {e}")
        finally:
            db.close()

# Instancia global del servicio
scheduler_service = ScheduledTasksService()

async def start_background_tasks():
    """Función para iniciar las tareas en background"""
    await scheduler_service.start_scheduler()

def stop_background_tasks():
    """Función para detener las tareas en background"""
    scheduler_service.stop_scheduler()

# Función manual para forzar verificación
async def force_categoria_check():
    """Fuerza una verificación inmediata de categorías"""
    logger.info("🔧 Forzando verificación manual de categorías")
    await scheduler_service.run_categoria_maintenance()