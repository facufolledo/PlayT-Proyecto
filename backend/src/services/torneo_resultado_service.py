"""
Servicio para gestión de resultados en torneos
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from ..models.playt_models import Partido
from ..models.torneo_models import TorneoPareja, TorneoZona


class TorneoResultadoService:
    """Servicio para cargar y gestionar resultados de partidos de torneo"""
    
    @staticmethod
    def cargar_resultado(
        db: Session,
        partido_id: int,
        resultado_data: Dict,
        user_id: int
    ) -> Partido:
        """
        Carga el resultado de un partido de torneo
        
        Args:
            db: Sesión de base de datos
            partido_id: ID del partido
            resultado_data: Datos del resultado en formato JSON
            user_id: ID del usuario que carga el resultado
            
        Returns:
            Partido actualizado
        """
        # Obtener partido
        partido = db.query(Partido).filter(Partido.id_partido == partido_id).first()
        if not partido:
            raise ValueError("Partido no encontrado")
        
        # Verificar que sea partido de torneo
        if partido.tipo != 'torneo':
            raise ValueError("Este partido no es de torneo")
        
        # Verificar que el partido esté pendiente
        if partido.estado == 'confirmado':
            raise ValueError("El partido ya está confirmado")
        
        # Validar resultado
        TorneoResultadoService._validar_resultado(resultado_data)
        
        # Determinar ganador
        ganador_pareja_id = TorneoResultadoService._determinar_ganador(
            resultado_data, partido.pareja1_id, partido.pareja2_id
        )
        
        # Actualizar partido
        partido.resultado_padel = resultado_data
        partido.estado = 'confirmado'  # Usar 'confirmado' en lugar de 'finalizado'
        partido.ganador_pareja_id = ganador_pareja_id
        partido.elo_aplicado = False  # Se aplicará después si es necesario
        
        db.commit()
        db.refresh(partido)
        
        # Si es partido de playoffs, avanzar ganador a siguiente fase
        if partido.fase and partido.fase != 'zona':
            TorneoResultadoService._avanzar_ganador_playoff(db, partido, ganador_pareja_id)
        
        return partido
    
    @staticmethod
    def _avanzar_ganador_playoff(
        db: Session,
        partido: Partido,
        ganador_pareja_id: int
    ) -> Optional[Partido]:
        """
        Avanza al ganador de un partido de playoff a la siguiente ronda
        
        Args:
            db: Sesión de base de datos
            partido: Partido finalizado
            ganador_pareja_id: ID de la pareja ganadora
            
        Returns:
            Partido de siguiente ronda actualizado, o None si es la final
        """
        from ..models.torneo_models import Torneo, EstadoTorneo
        
        # Si es la final, marcar torneo como finalizado
        if partido.fase == 'final':
            torneo = db.query(Torneo).filter(Torneo.id == partido.id_torneo).first()
            if torneo:
                torneo.estado = EstadoTorneo.FINALIZADO
                db.commit()
            return None
        
        # Determinar siguiente fase
        fases_orden = ['16avos', '8vos', '4tos', 'semis', 'final']
        fase_actual = partido.fase
        if fase_actual == 'semifinal':
            fase_actual = 'semis'
        elif fase_actual == 'cuartos':
            fase_actual = '4tos'
            
        try:
            idx_actual = fases_orden.index(fase_actual)
            siguiente_fase = fases_orden[idx_actual + 1]
        except (ValueError, IndexError):
            return None
        
        # Buscar o crear partido de siguiente ronda
        # Lógica: el ganador del partido N va al partido (N+1)//2 de la siguiente fase
        numero_partido = partido.numero_partido or 1
        numero_siguiente = (numero_partido + 1) // 2
        
        partido_siguiente = db.query(Partido).filter(
            Partido.id_torneo == partido.id_torneo,
            Partido.fase == siguiente_fase,
            Partido.numero_partido == numero_siguiente
        ).first()
        
        # Si no existe el partido de siguiente fase, crearlo
        if not partido_siguiente:
            partido_siguiente = Partido(
                id_torneo=partido.id_torneo,
                fase=siguiente_fase,
                numero_partido=numero_siguiente,
                estado='pendiente',
                fecha=partido.fecha,
                id_creador=partido.id_creador,
                tipo='torneo'
            )
            db.add(partido_siguiente)
            db.flush()
        
        # Asignar ganador a la posición correspondiente
        if numero_partido % 2 == 1:
            # Partido impar -> pareja1
            partido_siguiente.pareja1_id = ganador_pareja_id
        else:
            # Partido par -> pareja2
            partido_siguiente.pareja2_id = ganador_pareja_id
        
        db.commit()
        return partido_siguiente
    
    @staticmethod
    def _validar_resultado(resultado: Dict) -> None:
        """
        Valida que el resultado sea válido según reglas de pádel
        
        Reglas:
        - Debe haber al menos 2 sets
        - Máximo 3 sets
        - Un equipo debe ganar al menos 2 sets
        - Cada set debe tener un ganador claro
        - Games válidos: 6-0, 6-1, 6-2, 6-3, 6-4, 7-5, 7-6 (tiebreak)
        """
        if 'sets' not in resultado:
            raise ValueError("El resultado debe incluir los sets")
        
        sets = resultado['sets']
        
        if len(sets) < 2:
            raise ValueError("Debe haber al menos 2 sets")
        
        if len(sets) > 3:
            raise ValueError("No puede haber más de 3 sets")
        
        # Contar sets ganados por cada equipo
        sets_equipo_a = 0
        sets_equipo_b = 0
        
        for i, set_data in enumerate(sets):
            if not set_data.get('completado'):
                raise ValueError(f"El set {i+1} no está completado")
            
            games_a = set_data.get('gamesEquipoA', 0)
            games_b = set_data.get('gamesEquipoB', 0)
            
            # Validar games
            if not TorneoResultadoService._validar_games(games_a, games_b):
                raise ValueError(f"Games inválidos en set {i+1}: {games_a}-{games_b}")
            
            # Contar ganador del set
            if set_data.get('ganador') == 'equipoA':
                sets_equipo_a += 1
            elif set_data.get('ganador') == 'equipoB':
                sets_equipo_b += 1
            else:
                raise ValueError(f"El set {i+1} debe tener un ganador")
        
        # Verificar que haya un ganador claro
        if sets_equipo_a < 2 and sets_equipo_b < 2:
            raise ValueError("Debe haber un ganador con al menos 2 sets")
        
        # Verificar que el ganador tenga 2 sets
        if max(sets_equipo_a, sets_equipo_b) < 2:
            raise ValueError("El ganador debe tener al menos 2 sets")
        
        # Si hay 3 sets, verificar que sea 2-1
        if len(sets) == 3:
            if not ((sets_equipo_a == 2 and sets_equipo_b == 1) or 
                    (sets_equipo_a == 1 and sets_equipo_b == 2)):
                raise ValueError("Con 3 sets, el resultado debe ser 2-1")
    
    @staticmethod
    def _validar_games(games_a: int, games_b: int) -> bool:
        """
        Valida que los games sean válidos según reglas de pádel
        
        Resultados válidos:
        - 6-0, 6-1, 6-2, 6-3, 6-4 (victoria normal)
        - 7-5 (victoria con ventaja)
        - 7-6 (victoria en tiebreak)
        """
        # Ordenar para facilitar validación
        mayor = max(games_a, games_b)
        menor = min(games_a, games_b)
        
        # Victoria 6-X (X <= 4)
        if mayor == 6 and menor <= 4:
            return True
        
        # Victoria 7-5
        if mayor == 7 and menor == 5:
            return True
        
        # Victoria 7-6 (tiebreak)
        if mayor == 7 and menor == 6:
            return True
        
        return False
    
    @staticmethod
    def _determinar_ganador(
        resultado: Dict,
        pareja1_id: int,
        pareja2_id: int
    ) -> int:
        """Determina qué pareja ganó el partido"""
        sets = resultado['sets']
        
        sets_equipo_a = sum(1 for s in sets if s.get('ganador') == 'equipoA')
        sets_equipo_b = sum(1 for s in sets if s.get('ganador') == 'equipoB')
        
        if sets_equipo_a > sets_equipo_b:
            return pareja1_id
        else:
            return pareja2_id
    
    @staticmethod
    def obtener_clasificados_zona(
        db: Session,
        zona_id: int,
        num_clasificados: int = 2
    ) -> List[Dict]:
        """
        Obtiene las parejas clasificadas de una zona
        
        Args:
            db: Sesión de base de datos
            zona_id: ID de la zona
            num_clasificados: Número de parejas que clasifican (default: 2)
            
        Returns:
            Lista de parejas clasificadas ordenadas por posición
        """
        from ..services.torneo_zona_service import TorneoZonaService
        
        # Obtener tabla de posiciones
        tabla = TorneoZonaService.obtener_tabla_posiciones(db, zona_id)
        
        # Tomar los primeros N clasificados
        clasificados = tabla['tabla'][:num_clasificados]
        
        return clasificados
    
    @staticmethod
    def verificar_zona_completa(db: Session, zona_id: int) -> bool:
        """
        Verifica si todos los partidos de una zona están finalizados
        
        Returns:
            True si todos los partidos están finalizados
        """
        # Contar partidos pendientes (no confirmados)
        partidos_pendientes = db.query(Partido).filter(
            Partido.zona_id == zona_id,
            Partido.estado != 'confirmado'
        ).count()
        
        return partidos_pendientes == 0
    
    @staticmethod
    def obtener_estadisticas_partido(
        db: Session,
        partido_id: int
    ) -> Dict:
        """
        Obtiene estadísticas detalladas de un partido
        
        Returns:
            Dict con estadísticas del partido
        """
        partido = db.query(Partido).filter(Partido.id_partido == partido_id).first()
        if not partido:
            raise ValueError("Partido no encontrado")
        
        if not partido.resultado_padel:
            return {
                "partido_id": partido_id,
                "estado": partido.estado,
                "tiene_resultado": False
            }
        
        resultado = partido.resultado_padel
        sets = resultado.get('sets', [])
        
        # Calcular estadísticas
        total_games_a = sum(s.get('gamesEquipoA', 0) for s in sets)
        total_games_b = sum(s.get('gamesEquipoB', 0) for s in sets)
        
        sets_a = sum(1 for s in sets if s.get('ganador') == 'equipoA')
        sets_b = sum(1 for s in sets if s.get('ganador') == 'equipoB')
        
        return {
            "partido_id": partido_id,
            "estado": partido.estado,
            "tiene_resultado": True,
            "pareja1_id": partido.pareja1_id,
            "pareja2_id": partido.pareja2_id,
            "ganador_pareja_id": partido.ganador_pareja_id,
            "sets": {
                "pareja1": sets_a,
                "pareja2": sets_b
            },
            "games": {
                "pareja1": total_games_a,
                "pareja2": total_games_b
            },
            "detalle_sets": sets
        }
    
    @staticmethod
    def corregir_resultado(
        db: Session,
        partido_id: int,
        nuevo_resultado: Dict,
        user_id: int
    ) -> Partido:
        """
        Corrige el resultado de un partido ya finalizado
        
        Solo organizadores pueden corregir resultados
        """
        partido = db.query(Partido).filter(Partido.id_partido == partido_id).first()
        if not partido:
            raise ValueError("Partido no encontrado")
        
        # Verificar permisos (debe ser organizador del torneo)
        from ..services.torneo_zona_service import TorneoZonaService
        if not TorneoZonaService._es_organizador(db, partido.id_torneo, user_id):
            raise ValueError("No tienes permisos para corregir este resultado")
        
        # Validar nuevo resultado
        TorneoResultadoService._validar_resultado(nuevo_resultado)
        
        # Determinar nuevo ganador
        ganador_pareja_id = TorneoResultadoService._determinar_ganador(
            nuevo_resultado, partido.pareja1_id, partido.pareja2_id
        )
        
        # Actualizar
        partido.resultado_padel = nuevo_resultado
        partido.ganador_pareja_id = ganador_pareja_id
        
        db.commit()
        db.refresh(partido)
        
        return partido
