"""
Servicio para generación de fixture en torneos
Considera disponibilidad horaria y balanceo por rating
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime, date, time, timedelta
from collections import defaultdict
import itertools

from ..models.torneo_models import (
    Torneo, TorneoZona, TorneoPareja, TorneoZonaPareja,
    TorneoBloqueoJugador, TorneoCancha, TorneoSlot
)
from ..models.playt_models import Usuario, Partido


class TorneoFixtureService:
    """Servicio para generación inteligente de fixture"""
    
    @staticmethod
    def generar_zonas_con_disponibilidad(
        db: Session,
        torneo_id: int,
        user_id: int,
        num_zonas: Optional[int] = None
    ) -> List[TorneoZona]:
        """
        Genera zonas considerando disponibilidad horaria como prioridad principal
        
        Algoritmo:
        1. Obtener parejas confirmadas
        2. Calcular disponibilidad horaria de cada pareja
        3. Agrupar parejas por compatibilidad horaria
        4. Dentro de cada grupo, balancear por rating
        5. Crear zonas con parejas compatibles
        """
        from ..services.torneo_zona_service import TorneoZonaService
        
        # Verificar permisos
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            raise ValueError("Torneo no encontrado")
        
        if not TorneoZonaService._es_organizador(db, torneo_id, user_id):
            raise ValueError("No tienes permisos para generar zonas")
        
        if torneo.estado != 'inscripcion':
            raise ValueError("Solo se pueden generar zonas cuando el torneo está en inscripción")
        
        # Obtener parejas confirmadas
        parejas = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == torneo_id,
            TorneoPareja.estado == 'confirmada'
        ).all()
        
        if len(parejas) < 4:
            raise ValueError("Se necesitan al menos 4 parejas confirmadas")
        
        # Calcular disponibilidad de cada pareja
        disponibilidad_parejas = TorneoFixtureService._calcular_disponibilidad_parejas(
            db, torneo, parejas
        )
        
        # Agrupar parejas por compatibilidad horaria
        grupos_compatibles = TorneoFixtureService._agrupar_por_compatibilidad(
            parejas, disponibilidad_parejas
        )
        
        # Calcular número óptimo de zonas si no se especificó
        if num_zonas is None:
            num_zonas = TorneoZonaService._calcular_num_zonas_optimo(len(parejas))
        
        # Validar número de zonas
        parejas_por_zona_min = len(parejas) // num_zonas
        if parejas_por_zona_min < 2:
            raise ValueError(f"Con {len(parejas)} parejas no se pueden crear {num_zonas} zonas (mínimo 2 parejas por zona)")
        
        # Eliminar zonas existentes
        db.query(TorneoZonaPareja).filter(
            TorneoZonaPareja.zona_id.in_(
                db.query(TorneoZona.id).filter(TorneoZona.torneo_id == torneo_id)
            )
        ).delete(synchronize_session=False)
        
        db.query(TorneoZona).filter(TorneoZona.torneo_id == torneo_id).delete()
        db.commit()
        
        # Crear zonas
        zonas = []
        for i in range(num_zonas):
            zona = TorneoZona(
                torneo_id=torneo_id,
                nombre=f"Zona {chr(65 + i)}",
                numero_orden=i + 1
            )
            db.add(zona)
            zonas.append(zona)
        
        db.flush()
        
        # Distribuir parejas priorizando compatibilidad horaria
        TorneoFixtureService._distribuir_parejas_inteligente(
            db, parejas, zonas, grupos_compatibles, disponibilidad_parejas
        )
        
        # Cambiar estado del torneo
        torneo.estado = 'armando_zonas'
        db.commit()
        
        return zonas
    
    @staticmethod
    def _calcular_disponibilidad_parejas(
        db: Session,
        torneo: Torneo,
        parejas: List[TorneoPareja]
    ) -> Dict[int, Set[Tuple[date, str, str]]]:
        """
        Calcula la disponibilidad horaria de cada pareja
        
        Returns:
            Dict con pareja_id -> Set de (fecha, hora_desde, hora_hasta) disponibles
        """
        disponibilidad = {}
        
        # Obtener rango de fechas del torneo
        fecha_inicio = torneo.fecha_inicio
        fecha_fin = torneo.fecha_fin
        
        for pareja in parejas:
            # Obtener bloqueos de ambos jugadores
            bloqueos_j1 = db.query(TorneoBloqueoJugador).filter(
                TorneoBloqueoJugador.torneo_id == torneo.id,
                TorneoBloqueoJugador.jugador_id == pareja.jugador1_id,
                TorneoBloqueoJugador.fecha >= fecha_inicio,
                TorneoBloqueoJugador.fecha <= fecha_fin
            ).all()
            
            bloqueos_j2 = db.query(TorneoBloqueoJugador).filter(
                TorneoBloqueoJugador.torneo_id == torneo.id,
                TorneoBloqueoJugador.jugador_id == pareja.jugador2_id,
                TorneoBloqueoJugador.fecha >= fecha_inicio,
                TorneoBloqueoJugador.fecha <= fecha_fin
            ).all()
            
            # Combinar bloqueos de ambos jugadores
            bloqueos_pareja = set()
            for bloqueo in bloqueos_j1 + bloqueos_j2:
                bloqueos_pareja.add((bloqueo.fecha, bloqueo.hora_desde, bloqueo.hora_hasta))
            
            disponibilidad[pareja.id] = bloqueos_pareja
        
        return disponibilidad
    
    @staticmethod
    def _agrupar_por_compatibilidad(
        parejas: List[TorneoPareja],
        disponibilidad: Dict[int, Set[Tuple[date, str, str]]]
    ) -> List[List[TorneoPareja]]:
        """
        Agrupa parejas que tienen compatibilidad horaria
        
        Dos parejas son compatibles si NO tienen bloqueos que se solapen
        """
        # Crear grafo de compatibilidad
        compatibilidad = defaultdict(set)
        
        for i, pareja1 in enumerate(parejas):
            for j, pareja2 in enumerate(parejas):
                if i >= j:
                    continue
                
                # Verificar si son compatibles
                if TorneoFixtureService._son_compatibles(
                    disponibilidad.get(pareja1.id, set()),
                    disponibilidad.get(pareja2.id, set())
                ):
                    compatibilidad[pareja1.id].add(pareja2.id)
                    compatibilidad[pareja2.id].add(pareja1.id)
        
        # Agrupar parejas usando algoritmo greedy
        grupos = []
        parejas_asignadas = set()
        
        for pareja in parejas:
            if pareja.id in parejas_asignadas:
                continue
            
            # Crear nuevo grupo
            grupo = [pareja]
            parejas_asignadas.add(pareja.id)
            
            # Agregar parejas compatibles con todas las del grupo
            for otra_pareja in parejas:
                if otra_pareja.id in parejas_asignadas:
                    continue
                
                # Verificar si es compatible con todas las del grupo
                compatible_con_todas = all(
                    otra_pareja.id in compatibilidad[p.id]
                    for p in grupo
                )
                
                if compatible_con_todas:
                    grupo.append(otra_pareja)
                    parejas_asignadas.add(otra_pareja.id)
            
            grupos.append(grupo)
        
        return grupos
    
    @staticmethod
    def _son_compatibles(
        bloqueos1: Set[Tuple[date, str, str]],
        bloqueos2: Set[Tuple[date, str, str]]
    ) -> bool:
        """
        Verifica si dos parejas son compatibles horariamente
        
        Son compatibles si NO tienen bloqueos que se solapen en la misma fecha
        """
        # Si alguna no tiene bloqueos, son compatibles
        if not bloqueos1 or not bloqueos2:
            return True
        
        # Verificar solapamiento
        for fecha1, desde1, hasta1 in bloqueos1:
            for fecha2, desde2, hasta2 in bloqueos2:
                # Si es la misma fecha
                if fecha1 == fecha2:
                    # Verificar si los horarios se solapan
                    if TorneoFixtureService._horarios_se_solapan(
                        desde1, hasta1, desde2, hasta2
                    ):
                        return False
        
        return True
    
    @staticmethod
    def _horarios_se_solapan(
        desde1, hasta1,
        desde2, hasta2
    ) -> bool:
        """Verifica si dos rangos horarios se solapan"""
        # Convertir a time objects si son strings
        def to_time(s):
            if isinstance(s, time):
                return s
            if isinstance(s, str):
                parts = s.split(':')
                return time(int(parts[0]), int(parts[1]))
            return s
        
        t1_desde = to_time(desde1)
        t1_hasta = to_time(hasta1)
        t2_desde = to_time(desde2)
        t2_hasta = to_time(hasta2)
        
        # Verificar solapamiento
        return not (t1_hasta <= t2_desde or t2_hasta <= t1_desde)
    
    @staticmethod
    def _distribuir_parejas_inteligente(
        db: Session,
        parejas: List[TorneoPareja],
        zonas: List[TorneoZona],
        grupos_compatibles: List[List[TorneoPareja]],
        disponibilidad: Dict[int, Set[Tuple[date, str, str]]]
    ):
        """
        Distribuye parejas en zonas priorizando compatibilidad horaria
        y balanceando por rating
        """
        # Calcular rating promedio de cada pareja
        parejas_con_rating = {}
        for pareja in parejas:
            jugador1 = db.query(Usuario).filter(Usuario.id_usuario == pareja.jugador1_id).first()
            jugador2 = db.query(Usuario).filter(Usuario.id_usuario == pareja.jugador2_id).first()
            
            rating1 = jugador1.rating if jugador1 and jugador1.rating else 1200
            rating2 = jugador2.rating if jugador2 and jugador2.rating else 1200
            rating_promedio = (rating1 + rating2) / 2
            
            parejas_con_rating[pareja.id] = rating_promedio
        
        # Ordenar grupos por tamaño (más grandes primero)
        grupos_compatibles.sort(key=lambda g: len(g), reverse=True)
        
        # Distribuir grupos en zonas
        zona_idx = 0
        for grupo in grupos_compatibles:
            # Ordenar parejas del grupo por rating
            grupo_ordenado = sorted(grupo, key=lambda p: parejas_con_rating[p.id], reverse=True)
            
            # Distribuir en serpiente dentro del grupo
            for i, pareja in enumerate(grupo_ordenado):
                zona_pareja = TorneoZonaPareja(
                    zona_id=zonas[zona_idx].id,
                    pareja_id=pareja.id
                )
                db.add(zona_pareja)
                
                # Siguiente zona
                zona_idx = (zona_idx + 1) % len(zonas)
    
    @staticmethod
    def generar_partidos_zona(
        db: Session,
        zona_id: int,
        user_id: int
    ) -> List[Partido]:
        """
        Genera todos los partidos de una zona (todos contra todos)
        
        En una zona de N parejas, se generan N*(N-1)/2 partidos
        """
        # Verificar zona
        zona = db.query(TorneoZona).filter(TorneoZona.id == zona_id).first()
        if not zona:
            raise ValueError("Zona no encontrada")
        
        # Verificar permisos
        from ..services.torneo_zona_service import TorneoZonaService
        if not TorneoZonaService._es_organizador(db, zona.torneo_id, user_id):
            raise ValueError("No tienes permisos para generar partidos")
        
        # Obtener parejas de la zona
        parejas = db.query(TorneoPareja).join(
            TorneoZonaPareja,
            TorneoZonaPareja.pareja_id == TorneoPareja.id
        ).filter(
            TorneoZonaPareja.zona_id == zona_id
        ).all()
        
        if len(parejas) < 2:
            raise ValueError("Se necesitan al menos 2 parejas en la zona")
        
        # Generar todas las combinaciones (todos contra todos)
        partidos = []
        for i, pareja1 in enumerate(parejas):
            for j, pareja2 in enumerate(parejas):
                if i >= j:
                    continue
                
                # Crear partido
                partido = Partido(
                    id_torneo=zona.torneo_id,
                    zona_id=zona_id,
                    categoria_id=zona.categoria_id,  # Heredar categoría de la zona
                    pareja1_id=pareja1.id,
                    pareja2_id=pareja2.id,
                    tipo='torneo',
                    fase='zona',
                    estado='pendiente',
                    fecha=datetime.now(),  # Fecha placeholder
                    id_creador=user_id,
                    origen='auto'
                )
                db.add(partido)
                partidos.append(partido)
        
        db.commit()
        
        return partidos
    
    @staticmethod
    def generar_fixture_completo(
        db: Session,
        torneo_id: int,
        user_id: int
    ) -> Dict[str, any]:
        """
        Genera el fixture completo del torneo (todos los partidos de todas las zonas)
        """
        # Verificar permisos
        from ..services.torneo_zona_service import TorneoZonaService
        if not TorneoZonaService._es_organizador(db, torneo_id, user_id):
            raise ValueError("No tienes permisos para generar fixture")
        
        # Obtener zonas
        zonas = db.query(TorneoZona).filter(
            TorneoZona.torneo_id == torneo_id
        ).all()
        
        if not zonas:
            raise ValueError("No hay zonas creadas. Primero genera las zonas.")
        
        # Generar partidos para cada zona
        total_partidos = 0
        partidos_por_zona = {}
        
        for zona in zonas:
            partidos = TorneoFixtureService.generar_partidos_zona(db, zona.id, user_id)
            partidos_por_zona[zona.nombre] = len(partidos)
            total_partidos += len(partidos)
        
        # Cambiar estado del torneo
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if torneo:
            torneo.estado = 'fase_grupos'
            db.commit()
        
        return {
            "total_partidos": total_partidos,
            "partidos_por_zona": partidos_por_zona,
            "zonas": len(zonas)
        }
