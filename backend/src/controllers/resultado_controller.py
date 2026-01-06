from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database.config import get_db
from ..models.Drive+_models import Usuario
from ..schemas.resultado_padel import ResultadoPadelCreate, ResultadoPadelResponse, ConfirmacionRequest
from ..services.confirmacion_service import ConfirmacionService
from ..services.anti_trampa_service import AntiTrampaService
from ..auth.auth_utils import get_current_user

router = APIRouter(prefix="/resultados", tags=["Resultados"])

@router.post("/", response_model=ResultadoPadelResponse, status_code=status.HTTP_201_CREATED)
async def crear_resultado(
    resultado: ResultadoPadelCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo resultado de partido.
    Solo el creador puede cargar el resultado inicial.
    """
    try:
        # Verificar que el usuario sea el creador
        if resultado.id_creador != current_user.id_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el creador puede cargar el resultado"
            )
        
        # Crear el resultado usando el servicio
        confirmacion_service = ConfirmacionService(db)
        resultado_creado = confirmacion_service.crear_resultado(resultado)
        
        return resultado_creado
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear resultado: {str(e)}"
        )


@router.post("/{id_sala}/confirmar", response_model=dict)
async def confirmar_resultado(
    id_sala: str,
    confirmacion: ConfirmacionRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Confirmar un resultado de partido.
    Los rivales deben confirmar el resultado para que sea oficial.
    """
    try:
        # Obtener la sala y su partido
        from ..models.sala import Sala
        from ..models.Drive+_models import Partido
        sala = db.query(Sala).filter(Sala.id_sala == id_sala).first()
        
        if not sala or not sala.id_partido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sala o partido no encontrado"
            )
        
        # Obtener el partido
        partido = db.query(Partido).filter(Partido.id_partido == sala.id_partido).first()
        
        if not partido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partido no encontrado"
            )
        
        # Verificar que el usuario no sea el creador
        if partido.creado_por == current_user.id_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El creador no puede confirmar su propio resultado"
            )
        
        # Confirmar el resultado usando el método estático
        resultado_confirmado = ConfirmacionService.confirmar_resultado(
            id_partido=partido.id_partido,
            id_usuario=confirmacion.id_usuario,
            db=db
        )
        
        # Devolver toda la información del servicio
        return {
            "success": resultado_confirmado.get('success', True),
            "message": resultado_confirmado.get('mensaje', 'Resultado confirmado'),
            "confirmaciones_totales": resultado_confirmado.get('confirmaciones_totales', 0),
            "elo_aplicado": resultado_confirmado.get('elo_aplicado', False),
            "elo_changes": resultado_confirmado.get('elo_changes'),
            "cambio_elo_usuario": resultado_confirmado.get('cambio_elo_usuario'),
            "jugadores_faltantes": resultado_confirmado.get('jugadores_faltantes', [])
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al confirmar resultado: {str(e)}"
        )


@router.get("/{id_sala}/estado", response_model=dict)
async def obtener_estado_confirmaciones(
    id_sala: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener el estado de confirmaciones de un partido.
    """
    try:
        # Obtener la sala y su partido
        from ..models.sala import Sala
        from ..models.Drive+_models import Partido
        sala = db.query(Sala).filter(Sala.id_sala == id_sala).first()
        
        if not sala or not sala.id_partido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sala o partido no encontrado"
            )
        
        # Obtener el estado de confirmaciones
        estado = ConfirmacionService.obtener_estado_confirmaciones(
            id_partido=sala.id_partido,
            id_usuario_actual=current_user.id_usuario,
            db=db
        )
        
        if not estado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Partido no encontrado"
            )
        
        return estado
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estado: {str(e)}"
        )


@router.get("/{id_sala}", response_model=ResultadoPadelResponse)
async def obtener_resultado(
    id_sala: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener el resultado de un partido específico.
    """
    try:
        confirmacion_service = ConfirmacionService(db)
        resultado = confirmacion_service.obtener_resultado(id_sala)
        
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resultado no encontrado"
            )
        
        return resultado
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resultado: {str(e)}"
        )


@router.get("/pendientes/{id_usuario}", response_model=List[ResultadoPadelResponse])
async def obtener_confirmaciones_pendientes(
    id_usuario: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los resultados pendientes de confirmación para un usuario.
    """
    try:
        # Verificar que el usuario solo pueda ver sus propias confirmaciones
        if id_usuario != current_user.id_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes ver confirmaciones de otros usuarios"
            )
        
        confirmacion_service = ConfirmacionService(db)
        resultados_pendientes = confirmacion_service.obtener_pendientes_usuario(id_usuario)
        
        return resultados_pendientes
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener confirmaciones pendientes: {str(e)}"
        )


@router.get("/anti-trampa/{id_sala}", response_model=dict)
async def verificar_anti_trampa(
    id_sala: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verificar el estado del sistema anti-trampa para un partido.
    """
    try:
        anti_trampa_service = AntiTrampaService(db)
        info = anti_trampa_service.obtener_info_enfrentamiento(id_sala)
        
        return info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar anti-trampa: {str(e)}"
        )
