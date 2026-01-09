"""
Servicio para gestión de playoffs (fase de eliminación) en torneos
Genera brackets dinámicos con BYEs automáticos
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime
import math

from ..models.torneo_models import (
    Torneo, TorneoZona, TorneoPareja, TorneoCategoria,
    EstadoTorneo
)
from ..models.driveplus_models import Partido


class TorneoPlayoffService:
    """Servicio para gestión de playoffs en torneos"""
    
    @staticmethod
    def _next_power_of_two(n: int) -> int:
        """Calcula la siguiente potencia de 2"""
        p = 1
        while p < n:
            p *= 2
        return p
    
    @staticmethod
    def generar_playoffs(
        db: Session,
        torneo_id: int,
        user_id: int,
        clasificados_por_zona: int = 2
    ) -> List[Partido]:
        """Genera playoffs para TODAS las categorías del torneo"""
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            raise ValueError("Torneo no encontrado")
        
        if not TorneoPlayoffService._es_organizador(db, torneo_id, user_id):
            raise ValueError("No tienes permisos para generar playoffs")
        
        # Obtener categorías del torneo
        categorias = db.query(TorneoCategoria).filter(
            TorneoCategoria.torneo_id == torneo_id
        ).all()
        
        todos_partidos = []
        
        if categorias:
            for categoria in categorias:
                partidos = TorneoPlayoffService._generar_playoffs_categoria(
                    db, torneo_id, user_id, categoria.id, clasificados_por_zona
                )
                todos_partidos.extend(partidos)
        else:
            partidos = TorneoPlayoffService._generar_playoffs_categoria(
                db, torneo_id, user_id, None, clasificados_por_zona
            )
            todos_partidos.extend(partidos)
        
        torneo.estado = EstadoTorneo.FASE_ELIMINACION
        db.commit()
        
        return todos_partidos
    
    @staticmethod
    def _generar_playoffs_categoria(
        db: Session,
        torneo_id: int,
        user_id: int,
        categoria_id: Optional[int],
        clasificados_por_zona: int
    ) -> List[Partido]:
        """Genera playoffs para una categoría específica"""
        # Eliminar playoffs existentes de esta categoría
        query_delete = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase.in_(['16avos', '8vos', '4tos', 'cuartos', 'semis', 'semifinal', 'final'])
        )
        if categoria_id:
            query_delete = query_delete.filter(Partido.categoria_id == categoria_id)
        else:
            query_delete = query_delete.filter(Partido.categoria_id.is_(None))
        query_delete.delete(synchronize_session=False)
        db.commit()
        
        # Obtener clasificados
        clasificados = TorneoPlayoffService._obtener_clasificados_categoria(
            db, torneo_id, categoria_id, clasificados_por_zona
        )
        
        if len(clasificados) < 2:
            return []
        
        # Generar bracket completo con BYEs explícitos
        partidos = TorneoPlayoffService._generar_bracket_con_byes(
            db, torneo_id, clasificados, user_id, categoria_id
        )
        
        return partidos
    
    @staticmethod
    def _obtener_clasificados_categoria(
        db: Session,
        torneo_id: int,
        categoria_id: Optional[int],
        clasificados_por_zona: int
    ) -> List[Dict]:
        """Obtiene los clasificados ordenados por posición y puntos"""
        from ..services.torneo_zona_service import TorneoZonaService
        from ..models.torneo_models import TorneoZonaPareja
        
        query_zonas = db.query(TorneoZona).filter(TorneoZona.torneo_id == torneo_id)
        if categoria_id:
            query_zonas = query_zonas.filter(TorneoZona.categoria_id == categoria_id)
        else:
            query_zonas = query_zonas.filter(TorneoZona.categoria_id.is_(None))
        
        zonas = query_zonas.order_by(TorneoZona.numero_orden).all()
        clasificados = []
        
        if not zonas:
            # Sin zonas, obtener parejas directamente
            query_parejas = db.query(TorneoPareja).filter(
                TorneoPareja.torneo_id == torneo_id,
                TorneoPareja.estado.in_(['inscripta', 'confirmada'])
            )
            if categoria_id:
                query_parejas = query_parejas.filter(TorneoPareja.categoria_id == categoria_id)
            
            parejas = query_parejas.all()
            for i, pareja in enumerate(parejas):
                clasificados.append({
                    'pareja_id': pareja.id,
                    'posicion': i + 1,
                    'puntos': 0,
                    'rating': 1200
                })
            return clasificados
        
        # Obtener clasificados de cada zona
        for zona in zonas:
            try:
                resultado = TorneoZonaService.obtener_tabla_posiciones(db, zona.id)
                tabla = resultado.get('tabla', [])
                
                for i, pos in enumerate(tabla[:clasificados_por_zona]):
                    clasificados.append({
                        'pareja_id': pos['pareja_id'],
                        'posicion': i + 1,
                        'puntos': pos.get('puntos', 0),
                        'rating': pos.get('rating_promedio', 1200),
                        'zona_nombre': zona.nombre
                    })
            except Exception:
                parejas_zona = db.query(TorneoPareja).join(
                    TorneoZonaPareja, TorneoZonaPareja.pareja_id == TorneoPareja.id
                ).filter(TorneoZonaPareja.zona_id == zona.id).all()
                
                for i, pareja in enumerate(parejas_zona[:clasificados_por_zona]):
                    clasificados.append({
                        'pareja_id': pareja.id,
                        'posicion': i + 1,
                        'puntos': 0,
                        'rating': 1200,
                        'zona_nombre': zona.nombre
                    })
        
        return clasificados

    
    @staticmethod
    def _generar_bracket_con_byes(
        db: Session,
        torneo_id: int,
        clasificados: List[Dict],
        user_id: int,
        categoria_id: Optional[int]
    ) -> List[Partido]:
        """
        Genera bracket completo con BYEs explícitos en la BD
        
        - Calcula potencia de 2 necesaria
        - Crea TODOS los partidos (incluyendo BYEs)
        - BYEs tienen pareja2_id = NULL y ganador ya seteado
        """
        num_clasificados = len(clasificados)
        bracket_size = TorneoPlayoffService._next_power_of_two(num_clasificados)
        
        # Limitar a 16
        if bracket_size > 16:
            bracket_size = 16
            clasificados = clasificados[:16]
            num_clasificados = 16
        
        num_byes = bracket_size - num_clasificados
        
        # Ordenar clasificados: primeros de zona primero, luego segundos, etc.
        # Dentro de cada grupo, ordenar por puntos y rating
        clasificados_ordenados = sorted(
            clasificados,
            key=lambda x: (-x['posicion'], -x['puntos'], -x['rating'])
        )
        # Invertir para que los mejores (posicion 1) queden primero
        clasificados_ordenados = sorted(
            clasificados,
            key=lambda x: (x['posicion'], -x['puntos'], -x['rating'])
        )
        
        # Asignar seeds
        for i, c in enumerate(clasificados_ordenados):
            c['seed'] = i + 1
        
        # Determinar fases
        fases = TorneoPlayoffService._determinar_fases(bracket_size)
        num_rondas = len(fases)
        
        # Generar emparejamientos de primera ronda (estándar de bracket)
        emparejamientos = TorneoPlayoffService._generar_emparejamientos(bracket_size)
        
        # Crear diccionario de clasificados por seed
        clasificados_dict = {c['seed']: c for c in clasificados_ordenados}
        
        partidos_creados = []
        # Estructura para trackear partidos por ronda y posición
        # partidos_ronda[ronda][posicion] = partido
        partidos_ronda: Dict[int, Dict[int, Partido]] = {i: {} for i in range(num_rondas)}
        
        # RONDA 1: Crear todos los partidos (normales y BYEs)
        fase_inicial = fases[0]
        
        for i, (seed1, seed2) in enumerate(emparejamientos):
            c1 = clasificados_dict.get(seed1)
            c2 = clasificados_dict.get(seed2)
            
            pareja1_id = c1['pareja_id'] if c1 else None
            pareja2_id = c2['pareja_id'] if c2 else None
            
            # Determinar si es BYE
            es_bye = (pareja1_id is not None and pareja2_id is None) or \
                     (pareja1_id is None and pareja2_id is not None)
            
            # Si es BYE, el ganador es la pareja que existe
            ganador_id = None
            estado = 'pendiente'
            if es_bye:
                ganador_id = pareja1_id or pareja2_id
                estado = 'bye'
            
            partido = Partido(
                id_torneo=torneo_id,
                categoria_id=categoria_id,
                pareja1_id=pareja1_id,
                pareja2_id=pareja2_id,
                ganador_pareja_id=ganador_id,
                fase=fase_inicial,
                numero_partido=i + 1,
                estado=estado,
                fecha=datetime.now(),
                id_creador=user_id,
                tipo='torneo'
            )
            db.add(partido)
            partidos_creados.append(partido)
            partidos_ronda[0][i + 1] = partido
        
        db.flush()
        
        # RONDAS SIGUIENTES: Crear partidos vacíos o con ganadores de BYE
        for ronda_idx in range(1, num_rondas):
            fase = fases[ronda_idx]
            partidos_ronda_anterior = partidos_ronda[ronda_idx - 1]
            num_partidos_ronda = bracket_size // (2 ** (ronda_idx + 1))
            
            for i in range(num_partidos_ronda):
                # Cada partido recibe ganadores de 2 partidos de la ronda anterior
                partido_origen_1 = partidos_ronda_anterior.get(i * 2 + 1)
                partido_origen_2 = partidos_ronda_anterior.get(i * 2 + 2)
                
                # Si el partido origen es BYE, ya sabemos el ganador
                pareja1_id = None
                pareja2_id = None
                
                if partido_origen_1 and partido_origen_1.estado == 'bye':
                    pareja1_id = partido_origen_1.ganador_pareja_id
                
                if partido_origen_2 and partido_origen_2.estado == 'bye':
                    pareja2_id = partido_origen_2.ganador_pareja_id
                
                partido = Partido(
                    id_torneo=torneo_id,
                    categoria_id=categoria_id,
                    pareja1_id=pareja1_id,
                    pareja2_id=pareja2_id,
                    fase=fase,
                    numero_partido=i + 1,
                    estado='pendiente',
                    fecha=datetime.now(),
                    id_creador=user_id,
                    tipo='torneo'
                )
                db.add(partido)
                partidos_creados.append(partido)
                partidos_ronda[ronda_idx][i + 1] = partido
        
        db.commit()
        return partidos_creados
    
    @staticmethod
    def _determinar_fases(bracket_size: int) -> List[str]:
        """Determina las fases según el tamaño del bracket"""
        if bracket_size == 2:
            return ['final']
        elif bracket_size == 4:
            return ['semis', 'final']
        elif bracket_size == 8:
            return ['4tos', 'semis', 'final']
        elif bracket_size == 16:
            return ['8vos', '4tos', 'semis', 'final']
        else:
            return ['16avos', '8vos', '4tos', 'semis', 'final']
    
    @staticmethod
    def _generar_emparejamientos(bracket_size: int) -> List[tuple]:
        """
        Genera emparejamientos estándar de bracket
        Seed 1 vs último, etc. para que los mejores se encuentren en la final
        """
        if bracket_size == 2:
            return [(1, 2)]
        elif bracket_size == 4:
            return [(1, 4), (2, 3)]
        elif bracket_size == 8:
            return [(1, 8), (4, 5), (2, 7), (3, 6)]
        elif bracket_size == 16:
            return [
                (1, 16), (8, 9), (4, 13), (5, 12),
                (2, 15), (7, 10), (3, 14), (6, 11)
            ]
        else:
            # Genérico
            emparejamientos = []
            for i in range(bracket_size // 2):
                emparejamientos.append((i + 1, bracket_size - i))
            return emparejamientos

    
    @staticmethod
    def listar_partidos_playoffs(
        db: Session,
        torneo_id: int,
        categoria_id: Optional[int] = None
    ) -> Dict[str, List[Partido]]:
        """Lista partidos de playoffs agrupados por fase"""
        query = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase.in_(['16avos', '8vos', '4tos', 'cuartos', 'semis', 'semifinal', 'final'])
        )
        
        if categoria_id:
            query = query.filter(Partido.categoria_id == categoria_id)
        
        partidos = query.order_by(Partido.numero_partido).all()
        
        partidos_por_fase = {
            '16avos': [],
            '8vos': [],
            '4tos': [],
            'semis': [],
            'final': []
        }
        
        for partido in partidos:
            fase = partido.fase
            if fase == 'cuartos':
                fase = '4tos'
            elif fase == 'semifinal':
                fase = 'semis'
            
            if fase in partidos_por_fase:
                partidos_por_fase[fase].append(partido)
        
        return partidos_por_fase
    
    @staticmethod
    def avanzar_ganador(
        db: Session,
        partido_id: int,
        pareja_ganadora_id: int
    ) -> Optional[Partido]:
        """Avanza al ganador de un partido a la siguiente ronda"""
        partido = db.query(Partido).filter(Partido.id_partido == partido_id).first()
        
        if not partido:
            raise ValueError("Partido no encontrado")
        
        if partido.fase == 'final':
            # Verificar si todas las finales terminaron
            torneo = db.query(Torneo).filter(Torneo.id == partido.id_torneo).first()
            if torneo:
                finales_pendientes = db.query(Partido).filter(
                    Partido.id_torneo == partido.id_torneo,
                    Partido.fase == 'final',
                    Partido.estado.notin_(['confirmado', 'bye'])
                ).count()
                
                if finales_pendientes == 0:
                    torneo.estado = EstadoTorneo.FINALIZADO
                    db.commit()
            return None
        
        # Determinar siguiente fase
        siguiente_fase = TorneoPlayoffService._obtener_siguiente_fase(partido.fase)
        numero_siguiente = (partido.numero_partido + 1) // 2
        
        partido_siguiente = db.query(Partido).filter(
            Partido.id_torneo == partido.id_torneo,
            Partido.fase == siguiente_fase,
            Partido.numero_partido == numero_siguiente,
            Partido.categoria_id == partido.categoria_id
        ).first()
        
        if partido_siguiente:
            if partido.numero_partido % 2 == 1:
                partido_siguiente.pareja1_id = pareja_ganadora_id
            else:
                partido_siguiente.pareja2_id = pareja_ganadora_id
            
            db.commit()
            return partido_siguiente
        
        return None
    
    @staticmethod
    def _obtener_siguiente_fase(fase_actual: str) -> str:
        """Obtiene la siguiente fase del torneo"""
        mapa = {
            '16avos': '8vos',
            '8vos': '4tos',
            '4tos': 'semis',
            'cuartos': 'semis',
            'semis': 'final',
            'semifinal': 'final'
        }
        return mapa.get(fase_actual, 'final')
    
    @staticmethod
    def obtener_bracket(
        db: Session,
        torneo_id: int,
        categoria_id: Optional[int] = None
    ) -> List[Dict]:
        """Obtiene el bracket de playoffs con información completa de parejas"""
        query = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase.in_(['16avos', '8vos', '4tos', 'cuartos', 'semis', 'semifinal', 'final'])
        )
        
        if categoria_id:
            query = query.filter(Partido.categoria_id == categoria_id)
        else:
            query = query.filter(Partido.categoria_id.is_(None))
        
        partidos = query.order_by(Partido.numero_partido).all()
        
        # Convertir a formato para frontend
        partidos_data = []
        for partido in partidos:
            # Obtener nombres de parejas
            pareja1_nombre = None
            pareja2_nombre = None
            
            if partido.pareja1_id:
                pareja1 = db.query(TorneoPareja).filter(TorneoPareja.id == partido.pareja1_id).first()
                if pareja1:
                    pareja1_nombre = pareja1.nombre_pareja
            
            if partido.pareja2_id:
                pareja2 = db.query(TorneoPareja).filter(TorneoPareja.id == partido.pareja2_id).first()
                if pareja2:
                    pareja2_nombre = pareja2.nombre_pareja
            
            partidos_data.append({
                'id': partido.id_partido,
                'pareja1_id': partido.pareja1_id,
                'pareja2_id': partido.pareja2_id,
                'pareja1_nombre': pareja1_nombre,
                'pareja2_nombre': pareja2_nombre,
                'ganador_id': partido.ganador_pareja_id,
                'resultado': partido.resultado,
                'fase': partido.fase,
                'estado': partido.estado,
                'numero_partido': partido.numero_partido,
                'categoria_id': partido.categoria_id
            })
        
        return partidos_data
    
    @staticmethod
    def obtener_bracket_visual(
        db: Session,
        torneo_id: int,
        categoria_id: Optional[int] = None
    ) -> Dict:
        """Obtiene el bracket en formato visual optimizado para frontend"""
        partidos = TorneoPlayoffService.obtener_bracket(db, torneo_id, categoria_id)
        
        # Agrupar por fase
        fases = {
            '16avos': [],
            '8vos': [],
            '4tos': [],
            'semis': [],
            'final': []
        }
        
        for partido in partidos:
            fase = partido['fase']
            if fase == 'cuartos':
                fase = '4tos'
            elif fase == 'semifinal':
                fase = 'semis'
            
            if fase in fases:
                fases[fase].append(partido)
        
        # Ordenar partidos dentro de cada fase
        for fase in fases:
            fases[fase].sort(key=lambda x: x.get('numero_partido', 0))
        
        return {
            'partidos': partidos,
            'fases': fases,
            'torneo_id': torneo_id,
            'categoria_id': categoria_id
        }
    
    @staticmethod
    def obtener_clasificados(
        db: Session,
        torneo_id: int,
        categoria_id: Optional[int] = None
    ) -> List[Dict]:
        """Obtiene las parejas clasificadas a playoffs"""
        return TorneoPlayoffService._obtener_clasificados_categoria(
            db, torneo_id, categoria_id, 2  # Por defecto 2 clasificados por zona
        )
    
    @staticmethod
    def generar_tercer_puesto(
        db: Session,
        torneo_id: int,
        user_id: int,
        categoria_id: Optional[int] = None
    ) -> Partido:
        """Genera el partido por el tercer puesto"""
        if not TorneoPlayoffService._es_organizador(db, torneo_id, user_id):
            raise ValueError("No tienes permisos para generar el partido por el tercer puesto")
        
        # Buscar semifinales
        query_semis = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase.in_(['semis', 'semifinal']),
            Partido.estado == 'confirmado'
        )
        
        if categoria_id:
            query_semis = query_semis.filter(Partido.categoria_id == categoria_id)
        else:
            query_semis = query_semis.filter(Partido.categoria_id.is_(None))
        
        semifinales = query_semis.all()
        
        if len(semifinales) != 2:
            raise ValueError("Se necesitan exactamente 2 semifinales finalizadas")
        
        # Obtener perdedores de semifinales
        perdedores = []
        for semi in semifinales:
            if semi.ganador_pareja_id == semi.pareja1_id:
                perdedores.append(semi.pareja2_id)
            else:
                perdedores.append(semi.pareja1_id)
        
        if len(perdedores) != 2 or None in perdedores:
            raise ValueError("No se pueden determinar los perdedores de semifinales")
        
        # Crear partido por el tercer puesto
        partido_tercer_puesto = Partido(
            id_torneo=torneo_id,
            categoria_id=categoria_id,
            pareja1_id=perdedores[0],
            pareja2_id=perdedores[1],
            fase='tercer_puesto',
            numero_partido=1,
            estado='pendiente',
            fecha=datetime.now(),
            id_creador=user_id,
            tipo='torneo'
        )
        
        db.add(partido_tercer_puesto)
        db.commit()
        
        return partido_tercer_puesto
    
    @staticmethod
    def eliminar_playoffs(
        db: Session,
        torneo_id: int,
        user_id: int,
        categoria_id: Optional[int] = None
    ):
        """Elimina los playoffs para regenerarlos"""
        if not TorneoPlayoffService._es_organizador(db, torneo_id, user_id):
            raise ValueError("No tienes permisos para eliminar playoffs")
        
        query_delete = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase.in_(['16avos', '8vos', '4tos', 'cuartos', 'semis', 'semifinal', 'final', 'tercer_puesto'])
        )
        
        if categoria_id:
            query_delete = query_delete.filter(Partido.categoria_id == categoria_id)
        else:
            query_delete = query_delete.filter(Partido.categoria_id.is_(None))
        
        query_delete.delete(synchronize_session=False)
        db.commit()
    
    @staticmethod
    def obtener_podio(
        db: Session,
        torneo_id: int,
        categoria_id: Optional[int] = None
    ) -> Dict:
        """Obtiene el podio final del torneo"""
        # Buscar final
        query_final = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase == 'final',
            Partido.estado == 'confirmado'
        )
        
        if categoria_id:
            query_final = query_final.filter(Partido.categoria_id == categoria_id)
        else:
            query_final = query_final.filter(Partido.categoria_id.is_(None))
        
        final = query_final.first()
        
        podio = {
            'primero': None,
            'segundo': None,
            'tercero': None
        }
        
        if final and final.ganador_pareja_id:
            # Campeón
            campeon_id = final.ganador_pareja_id
            subcampeon_id = final.pareja1_id if final.pareja2_id == campeon_id else final.pareja2_id
            
            campeon = db.query(TorneoPareja).filter(TorneoPareja.id == campeon_id).first()
            subcampeon = db.query(TorneoPareja).filter(TorneoPareja.id == subcampeon_id).first()
            
            if campeon:
                podio['primero'] = {
                    'pareja_id': campeon.id,
                    'nombre': campeon.nombre_pareja
                }
            
            if subcampeon:
                podio['segundo'] = {
                    'pareja_id': subcampeon.id,
                    'nombre': subcampeon.nombre_pareja
                }
            
            # Buscar tercer puesto
            query_tercero = db.query(Partido).filter(
                Partido.id_torneo == torneo_id,
                Partido.fase == 'tercer_puesto',
                Partido.estado == 'confirmado'
            )
            
            if categoria_id:
                query_tercero = query_tercero.filter(Partido.categoria_id == categoria_id)
            else:
                query_tercero = query_tercero.filter(Partido.categoria_id.is_(None))
            
            tercer_puesto = query_tercero.first()
            
            if tercer_puesto and tercer_puesto.ganador_pareja_id:
                tercero = db.query(TorneoPareja).filter(
                    TorneoPareja.id == tercer_puesto.ganador_pareja_id
                ).first()
                
                if tercero:
                    podio['tercero'] = {
                        'pareja_id': tercero.id,
                        'nombre': tercero.nombre_pareja
                    }
        
        return podio
    
    @staticmethod
    def _es_organizador(db: Session, torneo_id: int, user_id: int) -> bool:
        """Verifica si un usuario es organizador de un torneo"""
        from ..models.torneo_models import TorneoOrganizador
        
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if torneo and torneo.creado_por == user_id:
            return True
        
        try:
            org = db.query(TorneoOrganizador).filter(
                TorneoOrganizador.torneo_id == torneo_id,
                TorneoOrganizador.user_id == user_id
            ).first()
            return org is not None
        except Exception:
            return False
