"""
Controllers de Torneos - Divididos por responsabilidad
"""
from .torneo_base_controller import router as torneo_base_router
from .torneo_inscripcion_controller import router as torneo_inscripcion_router
from .torneo_zona_controller import router as torneo_zona_router
from .torneo_fixture_controller import router as torneo_fixture_router
from .torneo_resultado_controller import router as torneo_resultado_router
from .torneo_playoff_controller import router as torneo_playoff_router

# Router principal que agrupa todos
from fastapi import APIRouter

router = APIRouter(prefix="/torneos", tags=["Torneos"])

# Incluir sub-routers
router.include_router(torneo_base_router)
router.include_router(torneo_inscripcion_router)
router.include_router(torneo_zona_router)
router.include_router(torneo_fixture_router)
router.include_router(torneo_resultado_router)
router.include_router(torneo_playoff_router)
