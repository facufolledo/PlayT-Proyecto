"""
Servicio para gestión de playoffs (fase de eliminación) en torneos
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import math

from ..models.torneo_models import (
    Torneo, TorneoZona, TorneoPareja,
    EstadoTorneo
)
from ..models.playt_models import Usuario, Partido


class TorneoPlayoffService:
    """Servicio para gestión de playoffs en torneos"""
    
    @staticmethod
    def generar_playoffs(
        db: Session,
        torneo_id: int,
        user_id: int,
        clasificados_por_zona: int = 2
    ) -> List[Partido]:
        """
        Genera el cuadro de playoffs automáticamente
        
        Args:
            db: Sesión de base de datos
            torneo_id: ID del torneo
            user_id: ID del usuario que ejecuta (debe ser organizador)
            clasificados_por_zona: Número de clasificados por zona (default: 2)
            
        Returns:
            Lista de partidos de playoffs generados
            
        Raises:
            ValueError: Si hay errores de validación
        """
        # Verificar que el torneo existe y el usuario es organizador
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            raise ValueError("Torneo no encontrado")
        
        if not TorneoPlayoffService._es_organizador(db, torneo_id, user_id):
            raise ValueError("No tienes permisos para generar playoffs en este torneo")
        
        # Verificar que el torneo está en un estado válido para generar playoffs
        # Permitimos FASE_ELIMINACION para poder regenerar playoffs si es necesario
        estados_validos = [
            EstadoTorneo.FASE_GRUPOS, 
            EstadoTorneo.ARMANDO_ZONAS, 
            EstadoTorneo.INSCRIPCION,
            EstadoTorneo.FASE_ELIMINACION
        ]
        if torneo.estado not in estados_validos:
            raise ValueError(f"No se pueden generar playoffs en estado {torneo.estado}. Estados válidos: inscripcion, armando_zonas, fase_grupos, fase_eliminacion")
        
        # Obtener clasificados de cada zona
        clasificados = TorneoPlayoffService._obtener_clasificados(
            db, torneo_id, clasificados_por_zona
        )
        
        if len(clasificados) < 2:
            raise ValueError("Se necesitan al menos 2 clasificados para generar playoffs")
        
        # Eliminar partidos de playoff existentes si los hay
        db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase != 'zona'
        ).delete()
        db.commit()
        
        # Generar bracket según número de clasificados
        partidos = TorneoPlayoffService._generar_bracket(
            db, torneo_id, clasificados, user_id
        )
        
        # Cambiar estado del torneo
        torneo.estado = EstadoTorneo.FASE_ELIMINACION
        db.commit()
        
        return partidos
    
    @staticmethod
    def _obtener_clasificados(
        db: Session,
        torneo_id: int,
        clasificados_por_zona: int
    ) -> List[Dict]:
        """
        Obtiene los clasificados de cada zona ordenados por posición
        
        Returns:
            Lista de diccionarios con info de clasificados:
            [
                {
                    'pareja_id': int,
                    'zona_id': int,
                    'zona_nombre': str,
                    'posicion': int,
                    'puntos': int,
                    'rating_promedio': float
                },
                ...
            ]
        """
        from ..services.torneo_zona_service import TorneoZonaService
        from ..models.torneo_models import TorneoZonaPareja
        
        zonas = db.query(TorneoZona).filter(
            TorneoZona.torneo_id == torneo_id
        ).order_by(TorneoZona.numero_orden).all()
        
        clasificados = []
        
        # Si no hay zonas, obtener parejas directamente
        if not zonas:
            parejas = db.query(TorneoPareja).filter(
                TorneoPareja.torneo_id == torneo_id,
                TorneoPareja.estado.in_(['inscripta', 'confirmada'])
            ).all()
            
            for i, pareja in enumerate(parejas):
                clasificados.append({
                    'pareja_id': pareja.id,
                    'zona_id': None,
                    'zona_nombre': 'Sin zona',
                    'posicion': i + 1,
                    'puntos': 0,
                    'rating_promedio': 1200
                })
            return clasificados
        
        for zona in zonas:
            try:
                # Obtener tabla de posiciones de la zona
                resultado = TorneoZonaService.obtener_tabla_posiciones(db, zona.id)
                tabla = resultado.get('tabla', [])
                
                # Tomar los primeros N clasificados
                for i, posicion in enumerate(tabla[:clasificados_por_zona]):
                    clasificados.append({
                        'pareja_id': posicion['pareja_id'],
                        'zona_id': zona.id,
                        'zona_nombre': zona.nombre,
                        'posicion': i + 1,  # 1 = primero, 2 = segundo
                        'puntos': posicion.get('puntos', 0),
                        'rating_promedio': posicion.get('rating_promedio', 1200)
                    })
            except Exception as e:
                # Si falla obtener tabla, obtener parejas de la zona directamente
                parejas_zona = db.query(TorneoPareja).join(
                    TorneoZonaPareja,
                    TorneoZonaPareja.pareja_id == TorneoPareja.id
                ).filter(
                    TorneoZonaPareja.zona_id == zona.id
                ).all()
                
                for i, pareja in enumerate(parejas_zona[:clasificados_por_zona]):
                    clasificados.append({
                        'pareja_id': pareja.id,
                        'zona_id': zona.id,
                        'zona_nombre': zona.nombre,
                        'posicion': i + 1,
                        'puntos': 0,
                        'rating_promedio': 1200
                    })
        
        return clasificados
    
    @staticmethod
    def _generar_bracket(
        db: Session,
        torneo_id: int,
        clasificados: List[Dict],
        user_id: int = None
    ) -> List[Partido]:
        """
        Genera el bracket de eliminación directa
        
        Lógica de emparejamiento:
        - Los primeros de cada zona se enfrentan a los segundos de otras zonas
        - Se intenta evitar que parejas de la misma zona se enfrenten en primera ronda
        - Se usa sistema de seeds para balancear el cuadro
        """
        num_clasificados = len(clasificados)
        
        # Calcular potencia de 2 más cercana (para el bracket)
        potencia = 2 ** math.ceil(math.log2(num_clasificados))
        
        # Asignar seeds
        clasificados_con_seed = TorneoPlayoffService._asignar_seeds(clasificados)
        
        # Generar emparejamientos de primera ronda
        partidos = []
        
        if potencia == num_clasificados:
            # Bracket perfecto (potencia de 2)
            partidos = TorneoPlayoffService._generar_bracket_perfecto(
                db, torneo_id, clasificados_con_seed, user_id
            )
        else:
            # Bracket con byes
            partidos = TorneoPlayoffService._generar_bracket_con_byes(
                db, torneo_id, clasificados_con_seed, potencia, user_id
            )
        
        return partidos
    
    @staticmethod
    def _asignar_seeds(clasificados: List[Dict]) -> List[Dict]:
        """
        Asigna seeds a los clasificados
        
        Lógica:
        1. Primeros de zona tienen seeds más altos
        2. Dentro de cada posición, se ordenan por puntos y rating
        """
        # Separar primeros y segundos
        primeros = [c for c in clasificados if c['posicion'] == 1]
        segundos = [c for c in clasificados if c['posicion'] == 2]
        
        # Ordenar cada grupo por puntos y rating
        primeros.sort(key=lambda x: (x['puntos'], x['rating_promedio']), reverse=True)
        segundos.sort(key=lambda x: (x['puntos'], x['rating_promedio']), reverse=True)
        
        # Asignar seeds
        clasificados_con_seed = []
        seed = 1
        
        for c in primeros:
            c['seed'] = seed
            clasificados_con_seed.append(c)
            seed += 1
        
        for c in segundos:
            c['seed'] = seed
            clasificados_con_seed.append(c)
            seed += 1
        
        return clasificados_con_seed
    
    @staticmethod
    def _generar_bracket_perfecto(
        db: Session,
        torneo_id: int,
        clasificados: List[Dict],
        user_id: int = None
    ) -> List[Partido]:
        """
        Genera bracket perfecto (número de clasificados es potencia de 2)
        
        Emparejamientos típicos:
        - 4 clasificados: 1vs4, 2vs3 (semis directas)
        - 8 clasificados: 1vs8, 4vs5, 2vs7, 3vs6 (cuartos)
        - 16 clasificados: 1vs16, 8vs9, 4vs13, 5vs12, 2vs15, 7vs10, 3vs14, 6vs11 (16avos)
        """
        num_clasificados = len(clasificados)
        clasificados_dict = {c['seed']: c for c in clasificados}
        
        # Determinar fase inicial
        if num_clasificados == 2:
            fase = 'final'
        elif num_clasificados == 4:
            fase = 'semis'
        elif num_clasificados == 8:
            fase = '4tos'
        elif num_clasificados == 16:
            fase = '16avos'
        else:
            fase = '8vos'
        
        # Generar emparejamientos
        partidos = []
        emparejamientos = TorneoPlayoffService._calcular_emparejamientos(num_clasificados)
        
        for i, (seed1, seed2) in enumerate(emparejamientos):
            c1 = clasificados_dict[seed1]
            c2 = clasificados_dict[seed2]
            
            partido = Partido(
                id_torneo=torneo_id,
                pareja1_id=c1['pareja_id'],
                pareja2_id=c2['pareja_id'],
                fase=fase,
                numero_partido=i + 1,
                estado='pendiente',
                fecha=datetime.now(),
                id_creador=user_id,
                tipo='torneo'
            )
            db.add(partido)
            partidos.append(partido)
        
        db.commit()
        return partidos
    
    @staticmethod
    def _generar_bracket_con_byes(
        db: Session,
        torneo_id: int,
        clasificados: List[Dict],
        potencia: int,
        user_id: int = None
    ) -> List[Partido]:
        """
        Genera bracket con byes (número de clasificados no es potencia de 2)
        
        Los mejores seeds reciben byes y pasan directamente a la siguiente ronda
        """
        num_clasificados = len(clasificados)
        num_byes = potencia - num_clasificados
        
        # Los primeros N seeds reciben bye
        clasificados_con_bye = clasificados[:num_byes]
        clasificados_sin_bye = clasificados[num_byes:]
        
        # Determinar fase inicial
        if potencia == 4:
            fase_inicial = 'semis'
            fase_con_bye = 'final'
        elif potencia == 8:
            fase_inicial = '4tos'
            fase_con_bye = 'semis'
        elif potencia == 16:
            fase_inicial = '8vos'
            fase_con_bye = '4tos'
        else:
            fase_inicial = '16avos'
            fase_con_bye = '8vos'
        
        # Generar partidos de primera ronda (sin byes)
        partidos = []
        num_partidos_primera_ronda = len(clasificados_sin_bye) // 2
        
        for i in range(num_partidos_primera_ronda):
            c1 = clasificados_sin_bye[i * 2]
            c2 = clasificados_sin_bye[i * 2 + 1]
            
            partido = Partido(
                id_torneo=torneo_id,
                pareja1_id=c1['pareja_id'],
                pareja2_id=c2['pareja_id'],
                fase=fase_inicial,
                numero_partido=i + 1,
                estado='pendiente',
                fecha=datetime.now(),
                id_creador=user_id,
                tipo='torneo'
            )
            db.add(partido)
            partidos.append(partido)
        
        # Generar partidos de siguiente ronda con byes (TBD vs clasificado con bye)
        for i, c_bye in enumerate(clasificados_con_bye):
            partido = Partido(
                id_torneo=torneo_id,
                pareja1_id=None,  # TBD - ganador de partido anterior
                pareja2_id=c_bye['pareja_id'],
                fase=fase_con_bye,
                numero_partido=num_partidos_primera_ronda + i + 1,
                estado='pendiente',
                fecha=datetime.now(),
                id_creador=user_id,
                tipo='torneo'
            )
            db.add(partido)
            partidos.append(partido)
        
        db.commit()
        return partidos
    
    @staticmethod
    def _calcular_emparejamientos(num_clasificados: int) -> List[Tuple[int, int]]:
        """
        Calcula emparejamientos estándar de bracket
        
        Returns:
            Lista de tuplas (seed1, seed2)
        """
        if num_clasificados == 2:
            return [(1, 2)]
        elif num_clasificados == 4:
            return [(1, 4), (2, 3)]
        elif num_clasificados == 8:
            return [(1, 8), (4, 5), (2, 7), (3, 6)]
        elif num_clasificados == 16:
            return [
                (1, 16), (8, 9), (4, 13), (5, 12),
                (2, 15), (7, 10), (3, 14), (6, 11)
            ]
        else:
            # Para otros números, generar emparejamientos simples
            emparejamientos = []
            for i in range(num_clasificados // 2):
                emparejamientos.append((i + 1, num_clasificados - i))
            return emparejamientos
    
    @staticmethod
    def listar_partidos_playoffs(
        db: Session,
        torneo_id: int
    ) -> Dict[str, List[Partido]]:
        """
        Lista todos los partidos de playoffs agrupados por fase
        
        Returns:
            Diccionario con partidos por fase:
            {
                '16avos': [...],
                '8vos': [...],
                '4tos': [...],
                'semis': [...],
                'final': [...]
            }
        """
        partidos = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase != 'zona'
        ).order_by(Partido.numero_partido).all()
        
        # Agrupar por fase
        partidos_por_fase = {
            '16avos': [],
            '8vos': [],
            '4tos': [],
            'semis': [],
            'final': []
        }
        
        for partido in partidos:
            if partido.fase == '16avos':
                partidos_por_fase['16avos'].append(partido)
            elif partido.fase == '8vos':
                partidos_por_fase['8vos'].append(partido)
            elif partido.fase == '4tos':
                partidos_por_fase['4tos'].append(partido)
            elif partido.fase == 'semis':
                partidos_por_fase['semis'].append(partido)
            elif partido.fase == 'final':
                partidos_por_fase['final'].append(partido)
        
        return partidos_por_fase
    
    @staticmethod
    def avanzar_ganador(
        db: Session,
        partido_id: int,
        pareja_ganadora_id: int
    ) -> Optional[Partido]:
        """
        Avanza al ganador de un partido a la siguiente ronda
        
        Args:
            db: Sesión de base de datos
            partido_id: ID del partido finalizado
            pareja_ganadora_id: ID de la pareja ganadora
            
        Returns:
            Partido de siguiente ronda actualizado, o None si es la final
        """
        partido = db.query(Partido).filter(
            Partido.id_partido == partido_id
        ).first()
        
        if not partido:
            raise ValueError("Partido no encontrado")
        
        if partido.estado != 'finalizado':
            raise ValueError("El partido debe estar finalizado para avanzar al ganador")
        
        # Si es la final, no hay siguiente ronda
        if partido.fase == 'final':
            # Marcar torneo como finalizado
            torneo = db.query(Torneo).filter(Torneo.id == partido.torneo_id).first()
            if torneo:
                torneo.estado = EstadoTorneo.FINALIZADO
                db.commit()
            return None
        
        # Determinar siguiente fase
        siguiente_fase = TorneoPlayoffService._obtener_siguiente_fase(partido.fase)
        
        # Buscar partido de siguiente ronda
        # Lógica: el ganador del partido N va al partido (N+1)//2 de la siguiente fase
        numero_siguiente = (partido.numero_partido + 1) // 2
        
        partido_siguiente = db.query(Partido).filter(
            Partido.id_torneo == partido.id_torneo,
            Partido.fase == siguiente_fase,
            Partido.numero_partido == numero_siguiente
        ).first()
        
        if partido_siguiente:
            # Asignar ganador a la posición correspondiente
            if partido.numero_partido % 2 == 1:
                # Partido impar -> pareja1
                partido_siguiente.pareja1_id = pareja_ganadora_id
            else:
                # Partido par -> pareja2
                partido_siguiente.pareja2_id = pareja_ganadora_id
            
            db.commit()
            return partido_siguiente
        
        return None
    
    @staticmethod
    def _obtener_siguiente_fase(fase_actual: str) -> str:
        """Obtiene la siguiente fase del torneo"""
        if fase_actual == '16avos':
            return '8vos'
        elif fase_actual == '8vos':
            return '4tos'
        elif fase_actual == '4tos':
            return 'semis'
        elif fase_actual == 'semis':
            return 'final'
        else:
            return 'final'
    
    @staticmethod
    def _es_organizador(db: Session, torneo_id: int, user_id: int) -> bool:
        """Verifica si un usuario es organizador de un torneo"""
        from ..models.torneo_models import TorneoOrganizador
        
        # Verificar si es el creador del torneo
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if torneo and torneo.creado_por == user_id:
            return True
        
        # Verificar si está en la tabla de organizadores
        try:
            org = db.query(TorneoOrganizador).filter(
                TorneoOrganizador.torneo_id == torneo_id,
                TorneoOrganizador.user_id == user_id
            ).first()
            return org is not None
        except Exception:
            return False
