"""
Servicio Anti-Trampa
Verifica que no se abuse del sistema jugando repetidamente entre los mismos jugadores
"""
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.historial_enfrentamiento import HistorialEnfrentamiento
from ..models.driveplus_models import Usuario
from ..utils.logger import Loggers

logger = Loggers.anti_trampa()


class AntiTrampaService:
    """Servicio para prevenir abuso del sistema de Elo"""
    
    LIMITE_PARTIDOS_SEMANA = 2
    DIAS_VENTANA = 7
    
    @staticmethod
    def generar_hash_trio(jugador1_id: int, jugador2_id: int, jugador3_id: int) -> str:
        """
        Genera un hash MD5 único para un trío de jugadores
        Los IDs se ordenan para garantizar consistencia
        """
        trio_ordenado = sorted([jugador1_id, jugador2_id, jugador3_id])
        trio_str = f"{trio_ordenado[0]}-{trio_ordenado[1]}-{trio_ordenado[2]}"
        return hashlib.md5(trio_str.encode()).hexdigest()
    
    @staticmethod
    def generar_hashes_cuarteto(jugadores: List[int]) -> Dict[str, str]:
        """
        Genera los 4 hashes de tríos posibles de un cuarteto
        
        Args:
            jugadores: Lista de 4 IDs de jugadores
            
        Returns:
            Dict con los 4 hashes: hash_trio_1, hash_trio_2, hash_trio_3, hash_trio_4
        """
        if len(jugadores) != 4:
            raise ValueError("Se requieren exactamente 4 jugadores")
        
        # Ordenar jugadores para consistencia
        j = sorted(jugadores)
        
        return {
            "hash_trio_1": AntiTrampaService.generar_hash_trio(j[0], j[1], j[2]),
            "hash_trio_2": AntiTrampaService.generar_hash_trio(j[0], j[1], j[3]),
            "hash_trio_3": AntiTrampaService.generar_hash_trio(j[0], j[2], j[3]),
            "hash_trio_4": AntiTrampaService.generar_hash_trio(j[1], j[2], j[3])
        }
    
    @staticmethod
    def verificar_limite_partidos(jugadores_ids: List[int], db: Session) -> Dict:
        """
        Verifica si alguna combinación de 3 jugadores ya alcanzó el límite de partidos
        
        Args:
            jugadores_ids: Lista de 4 IDs de jugadores
            db: Sesión de base de datos
            
        Returns:
            Dict con:
                - puede_jugar: bool
                - partidos_jugados: int
                - combinacion_bloqueada: str (IDs de los 3 jugadores)
                - jugadores_bloqueados: List[str] (nombres)
                - proxima_disponibilidad: datetime
                - mensaje: str
        """
        if len(jugadores_ids) != 4:
            raise ValueError("Se requieren exactamente 4 jugadores")
        
        # Generar hashes de todos los tríos
        hashes = AntiTrampaService.generar_hashes_cuarteto(jugadores_ids)
        
        # Fecha límite (hace 7 días)
        fecha_limite = datetime.now() - timedelta(days=AntiTrampaService.DIAS_VENTANA)
        
        # Verificar cada trío
        jugadores_ordenados = sorted(jugadores_ids)
        trios = [
            (jugadores_ordenados[0], jugadores_ordenados[1], jugadores_ordenados[2]),
            (jugadores_ordenados[0], jugadores_ordenados[1], jugadores_ordenados[3]),
            (jugadores_ordenados[0], jugadores_ordenados[2], jugadores_ordenados[3]),
            (jugadores_ordenados[1], jugadores_ordenados[2], jugadores_ordenados[3])
        ]
        
        for i, (hash_key, hash_value) in enumerate(hashes.items()):
            # Contar partidos de este trío en los últimos 7 días
            count = db.query(HistorialEnfrentamiento).filter(
                or_(
                    HistorialEnfrentamiento.hash_trio_1 == hash_value,
                    HistorialEnfrentamiento.hash_trio_2 == hash_value,
                    HistorialEnfrentamiento.hash_trio_3 == hash_value,
                    HistorialEnfrentamiento.hash_trio_4 == hash_value
                ),
                HistorialEnfrentamiento.fecha >= fecha_limite
            ).count()
            
            if count >= AntiTrampaService.LIMITE_PARTIDOS_SEMANA:
                # Obtener nombres de los jugadores bloqueados
                trio_ids = trios[i]
                jugadores = db.query(Usuario).filter(
                    Usuario.id_usuario.in_(trio_ids)
                ).all()
                
                nombres = [j.nombre_usuario for j in jugadores]
                
                # Calcular próxima disponibilidad
                # Buscar el partido más antiguo de este trío
                partido_mas_antiguo = db.query(HistorialEnfrentamiento).filter(
                    or_(
                        HistorialEnfrentamiento.hash_trio_1 == hash_value,
                        HistorialEnfrentamiento.hash_trio_2 == hash_value,
                        HistorialEnfrentamiento.hash_trio_3 == hash_value,
                        HistorialEnfrentamiento.hash_trio_4 == hash_value
                    ),
                    HistorialEnfrentamiento.fecha >= fecha_limite
                ).order_by(HistorialEnfrentamiento.fecha.asc()).first()
                
                proxima_disponibilidad = None
                if partido_mas_antiguo:
                    proxima_disponibilidad = partido_mas_antiguo.fecha + timedelta(days=AntiTrampaService.DIAS_VENTANA)
                
                return {
                    "puede_jugar": False,
                    "partidos_jugados": count,
                    "limite": AntiTrampaService.LIMITE_PARTIDOS_SEMANA,
                    "combinacion_bloqueada": f"{trio_ids[0]}-{trio_ids[1]}-{trio_ids[2]}",
                    "jugadores_bloqueados": nombres,
                    "proxima_disponibilidad": proxima_disponibilidad,
                    "mensaje": f"Esta combinación de jugadores ({', '.join(nombres)}) ya jugó {count} partidos esta semana. Límite: {AntiTrampaService.LIMITE_PARTIDOS_SEMANA} partidos cada {AntiTrampaService.DIAS_VENTANA} días."
                }
        
        # Todo OK, pueden jugar
        return {
            "puede_jugar": True,
            "partidos_jugados": 0,
            "limite": AntiTrampaService.LIMITE_PARTIDOS_SEMANA,
            "combinacion_bloqueada": None,
            "jugadores_bloqueados": None,
            "proxima_disponibilidad": None,
            "mensaje": "OK - Pueden jugar"
        }
    
    @staticmethod
    def registrar_enfrentamiento(
        id_partido: int,
        jugadores_ids: List[int],
        tipo_partido: str,
        db: Session
    ) -> HistorialEnfrentamiento:
        """
        Registra un enfrentamiento en el historial para tracking anti-trampa
        
        Args:
            id_partido: ID del partido
            jugadores_ids: Lista de 4 IDs de jugadores
            tipo_partido: Tipo de partido (amistoso, torneo, etc)
            db: Sesión de base de datos
            
        Returns:
            HistorialEnfrentamiento creado
        """
        if len(jugadores_ids) != 4:
            raise ValueError("Se requieren exactamente 4 jugadores")
        
        # Ordenar jugadores
        jugadores_ordenados = sorted(jugadores_ids)
        
        # Generar hashes
        hashes = AntiTrampaService.generar_hashes_cuarteto(jugadores_ids)
        
        # Crear registro
        historial = HistorialEnfrentamiento(
            id_partido=id_partido,
            fecha=datetime.now(),
            jugador1_id=jugadores_ordenados[0],
            jugador2_id=jugadores_ordenados[1],
            jugador3_id=jugadores_ordenados[2],
            jugador4_id=jugadores_ordenados[3],
            hash_trio_1=hashes["hash_trio_1"],
            hash_trio_2=hashes["hash_trio_2"],
            hash_trio_3=hashes["hash_trio_3"],
            hash_trio_4=hashes["hash_trio_4"],
            tipo_partido=tipo_partido,
            elo_aplicado=False
        )
        
        db.add(historial)
        db.commit()
        db.refresh(historial)
        
        return historial
