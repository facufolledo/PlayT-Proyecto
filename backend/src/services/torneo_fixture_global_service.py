"""
Servicio para gestión global de fixture considerando todas las categorías y canchas
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from ..models.torneo_models import (
    Torneo, TorneoZona, TorneoPareja, TorneoCancha, 
    TorneoCategoria
)
from ..models.driveplus_models import Partido


class TorneoFixtureGlobalService:
    """
    Servicio para generar fixture considerando:
    - Todas las categorías del torneo
    - Todas las canchas disponibles
    - Disponibilidad horaria de parejas
    - No más partidos simultáneos que canchas disponibles
    """
    
    DURACION_PARTIDO_MINUTOS = 50
    
    @staticmethod
    def generar_fixture_completo(
        db: Session,
        torneo_id: int,
        user_id: int,
        categoria_id: Optional[int] = None
    ) -> Dict:
        """
        Genera fixture completo para todas las zonas y categorías del torneo
        o solo para una categoría específica
        
        Args:
            db: Sesión de base de datos
            torneo_id: ID del torneo
            user_id: ID del usuario organizador
            categoria_id: (Opcional) ID de categoría específica
            
        Returns:
            Dict con partidos generados y estadísticas
        """
        # Verificar permisos
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            raise ValueError("Torneo no encontrado")
        
        if torneo.creado_por != user_id:
            raise ValueError("No tienes permisos")
        
        # Obtener zonas del torneo (filtrar por categoría si se especifica)
        query = db.query(TorneoZona).filter(TorneoZona.torneo_id == torneo_id)
        if categoria_id:
            query = query.filter(TorneoZona.categoria_id == categoria_id)
        
        zonas = query.all()
        
        if not zonas:
            mensaje = "No hay zonas creadas"
            if categoria_id:
                mensaje += f" para la categoría {categoria_id}"
            raise ValueError(mensaje + ". Genera las zonas primero.")
        
        # Obtener canchas disponibles
        canchas = db.query(TorneoCancha).filter(
            TorneoCancha.torneo_id == torneo_id,
            TorneoCancha.activa == True
        ).all()
        
        if not canchas:
            raise ValueError("No hay canchas configuradas")
        
        num_canchas = len(canchas)
        
        # Obtener horarios del torneo
        horarios_torneo = torneo.horarios_disponibles or {}
        
        # Generar todos los partidos de todas las zonas
        todos_partidos = []
        for zona in zonas:
            partidos_zona = TorneoFixtureGlobalService._generar_partidos_zona(
                db, zona
            )
            todos_partidos.extend(partidos_zona)
        
        # Obtener disponibilidad de todas las parejas involucradas
        parejas_disponibilidad = TorneoFixtureGlobalService._obtener_disponibilidad_parejas(
            db, todos_partidos, torneo
        )
        
        # Generar slots de tiempo disponibles
        slots_disponibles = TorneoFixtureGlobalService._generar_slots_torneo(
            torneo, horarios_torneo
        )
        
        # Asignar horarios y canchas a los partidos
        resultado_asignacion = TorneoFixtureGlobalService._asignar_horarios_y_canchas(
            db,
            todos_partidos,
            parejas_disponibilidad,
            slots_disponibles,
            canchas,
            num_canchas
        )
        
        partidos_programados = resultado_asignacion['partidos_programados']
        partidos_no_programados = resultado_asignacion['partidos_no_programados']
        
        # Guardar partidos en la base de datos
        TorneoFixtureGlobalService._guardar_partidos(
            db, torneo_id, partidos_programados, categoria_id
        )
        
        return {
            "partidos_generados": len(partidos_programados),
            "partidos_no_programados": len(partidos_no_programados),
            "zonas_procesadas": len(zonas),
            "canchas_utilizadas": num_canchas,
            "slots_utilizados": len(set(p['slot'] for p in partidos_programados)),
            "partidos": partidos_programados,
            "partidos_sin_programar": partidos_no_programados
        }
    
    @staticmethod
    def _generar_partidos_zona(
        db: Session,
        zona: TorneoZona
    ) -> List[Dict]:
        """
        Genera todos los partidos de una zona (round-robin)
        
        Returns:
            Lista de dicts con info de partidos
        """
        from ..models.torneo_models import TorneoZonaPareja
        
        # Obtener parejas de la zona
        parejas = db.query(TorneoPareja).join(
            TorneoZonaPareja,
            TorneoZonaPareja.pareja_id == TorneoPareja.id
        ).filter(
            TorneoZonaPareja.zona_id == zona.id
        ).all()
        
        if len(parejas) < 2:
            return []
        
        # Generar todos contra todos
        partidos = []
        for i in range(len(parejas)):
            for j in range(i + 1, len(parejas)):
                partidos.append({
                    "zona_id": zona.id,
                    "zona_nombre": zona.nombre,
                    "categoria_id": zona.categoria_id,
                    "pareja1_id": parejas[i].id,
                    "pareja2_id": parejas[j].id,
                    "pareja1": parejas[i],
                    "pareja2": parejas[j]
                })
        
        return partidos
    
    @staticmethod
    def _obtener_disponibilidad_parejas(
        db: Session,
        partidos: List[Dict],
        torneo: Torneo
    ) -> Dict[int, Dict]:
        """
        Obtiene restricciones horarias de todas las parejas
        
        NUEVA LÓGICA CON RESTRICCIONES:
        - Si una pareja especifica restricciones: NO puede jugar en esos días/horarios
        - Días/horarios NO especificados: disponibles (dentro de horarios del torneo)
        - Sin restricciones = disponible en todos los horarios del torneo
        
        Returns:
            Dict {pareja_id: {'restricciones': {dia: [(inicio, fin)]}}}
        """
        parejas_ids = set()
        for partido in partidos:
            parejas_ids.add(partido['pareja1_id'])
            parejas_ids.add(partido['pareja2_id'])
        
        disponibilidad = {}
        
        for pareja_id in parejas_ids:
            pareja = db.query(TorneoPareja).filter(TorneoPareja.id == pareja_id).first()
            if not pareja:
                continue
            
            disp_raw = pareja.disponibilidad_horaria or {}
            
            # Manejar diferentes formatos de disponibilidad_horaria
            # Formato 1: Lista directa de restricciones [{'dias': [...], 'horaInicio': ..., 'horaFin': ...}]
            # Formato 2: Diccionario con franjas {'franjas': [...]}
            # Formato 3: Vacío o None = sin restricciones
            
            franjas = []
            if isinstance(disp_raw, list):
                # Formato 1: lista directa
                franjas = disp_raw
            elif isinstance(disp_raw, dict):
                # Formato 2: diccionario con franjas
                franjas = disp_raw.get('franjas', [])
            
            # Si no tiene restricciones o está vacía, está disponible siempre
            if not franjas:
                disponibilidad[pareja_id] = {
                    'restricciones': {}  # Sin restricciones = disponible siempre
                }
                continue
            
            # Procesar franjas como RESTRICCIONES (horarios que NO puede jugar)
            restricciones = {}
            
            for franja in franjas:
                dias = franja.get('dias', [])
                hora_inicio = franja.get('horaInicio', '00:00')
                hora_fin = franja.get('horaFin', '23:59')
                
                # Convertir a minutos para facilitar comparación
                inicio_mins = int(hora_inicio.split(':')[0]) * 60 + int(hora_inicio.split(':')[1])
                fin_mins = int(hora_fin.split(':')[0]) * 60 + int(hora_fin.split(':')[1])
                
                for dia in dias:
                    if dia not in restricciones:
                        restricciones[dia] = []
                    restricciones[dia].append((inicio_mins, fin_mins))
            
            disponibilidad[pareja_id] = {
                'restricciones': restricciones
            }
        
        return disponibilidad
    
    @staticmethod
    def _generar_slots_torneo(
        torneo: Torneo,
        horarios_torneo: Dict
    ) -> List[Tuple[str, str, str]]:
        """
        Genera todos los slots de tiempo disponibles del torneo
        
        Returns:
            Lista de tuplas (fecha, dia_semana, hora)
        """
        slots = []
        
        fecha_inicio = torneo.fecha_inicio
        fecha_fin = torneo.fecha_fin
        
        # Iterar por cada día del torneo
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            dia_semana = TorneoFixtureGlobalService._obtener_dia_semana(fecha_actual)
            
            # Intentar obtener horarios específicos del día
            horarios_dia = None
            
            # Formato nuevo: horarios por día específico (viernes, sabado, domingo, etc.)
            if dia_semana in horarios_torneo:
                horarios_dia = horarios_torneo[dia_semana]
            # Formato viejo: horarios por tipo de día (semana, finDeSemana)
            else:
                tipo_dia = 'finDeSemana' if dia_semana in ['sabado', 'domingo'] else 'semana'
                franjas = horarios_torneo.get(tipo_dia, [])
                
                if not franjas:
                    # Si no hay franjas definidas, usar horario por defecto
                    franjas = [{'desde': '08:00', 'hasta': '23:00'}]
                
                # Generar slots para cada franja (formato viejo)
                for franja in franjas:
                    hora_desde = franja.get('desde', '08:00')
                    hora_hasta = franja.get('hasta', '23:00')
                    
                    hora_actual = datetime.strptime(hora_desde, '%H:%M')
                    hora_limite = datetime.strptime(hora_hasta, '%H:%M')
                    
                    # IMPORTANTE: Asegurar que no se generen slots que excedan el límite
                    # Restar 50 minutos del límite para que el partido termine antes del cierre
                    hora_limite_ajustada = hora_limite - timedelta(minutes=50)
                    
                    while hora_actual <= hora_limite_ajustada:
                        slots.append((
                            fecha_actual.strftime('%Y-%m-%d'),
                            dia_semana,
                            hora_actual.strftime('%H:%M')
                        ))
                        hora_actual += timedelta(minutes=50)
                
                fecha_actual += timedelta(days=1)
                continue
            
            # Formato nuevo: procesar horarios del día específico
            if horarios_dia and isinstance(horarios_dia, dict):
                hora_desde = horarios_dia.get('inicio') or horarios_dia.get('desde', '08:00')
                hora_hasta = horarios_dia.get('fin') or horarios_dia.get('hasta', '23:00')
                
                hora_actual = datetime.strptime(hora_desde, '%H:%M')
                hora_limite = datetime.strptime(hora_hasta, '%H:%M')
                
                # IMPORTANTE: Asegurar que no se generen slots que excedan el límite
                # Restar 50 minutos del límite para que el partido termine antes del cierre
                hora_limite_ajustada = hora_limite - timedelta(minutes=50)
                
                while hora_actual <= hora_limite_ajustada:
                    slots.append((
                        fecha_actual.strftime('%Y-%m-%d'),
                        dia_semana,
                        hora_actual.strftime('%H:%M')
                    ))
                    hora_actual += timedelta(minutes=50)
            
            fecha_actual += timedelta(days=1)
        
        return slots
    
    @staticmethod
    def _obtener_dia_semana(fecha: datetime.date) -> str:
        """Convierte fecha a nombre de día en español"""
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        return dias[fecha.weekday()]
    
    @staticmethod
    def _asignar_horarios_y_canchas(
        db: Session,
        partidos: List[Dict],
        parejas_disponibilidad: Dict[int, Dict],
        slots_disponibles: List[Tuple[str, str, str]],
        canchas: List[TorneoCancha],
        num_canchas: int
    ) -> Dict:
        """
        Asigna horarios y canchas a los partidos considerando:
        - Disponibilidad de parejas (RESPETADA ESTRICTAMENTE)
        - Mínimo 60 minutos entre partidos del mismo jugador
        - Máximo N partidos simultáneos (N = número de canchas)
        - No repetir cancha/horario
        
        Returns:
            Dict con partidos_programados y partidos_no_programados
        """
        partidos_programados = []
        partidos_no_programados = []
        
        # Mapa de ocupación: {(fecha, hora): [cancha_id, ...]}
        ocupacion_canchas = defaultdict(list)
        
        # Tracking de partidos por jugador: {jugador_id: [datetime, ...]}
        partidos_por_jugador = defaultdict(list)
        
        # Ordenar partidos por prioridad (ej: zonas con menos partidos primero)
        partidos_ordenados = sorted(partidos, key=lambda p: p['zona_id'])
        
        for partido in partidos_ordenados:
            pareja1_id = partido['pareja1_id']
            pareja2_id = partido['pareja2_id']
            
            # Obtener parejas para obtener jugadores
            pareja1 = db.query(TorneoPareja).filter(TorneoPareja.id == pareja1_id).first()
            pareja2 = db.query(TorneoPareja).filter(TorneoPareja.id == pareja2_id).first()
            
            if not pareja1 or not pareja2:
                continue
            
            # Lista de todos los jugadores involucrados
            jugadores = [pareja1.jugador1_id, pareja1.jugador2_id, pareja2.jugador1_id, pareja2.jugador2_id]
            
            # Obtener disponibilidad de ambas parejas
            disp1 = parejas_disponibilidad.get(pareja1_id, {'dias_restringidos': set(), 'rangos': {}})
            disp2 = parejas_disponibilidad.get(pareja2_id, {'dias_restringidos': set(), 'rangos': {}})
            
            # Buscar slot compatible
            slot_asignado = None
            cancha_asignada = None
            
            for fecha, dia, hora in slots_disponibles:
                # 1. VERIFICAR DISPONIBILIDAD HORARIA
                hora_mins = int(hora.split(':')[0]) * 60 + int(hora.split(':')[1])
                
                # Verificar pareja 1
                pareja1_disponible = TorneoFixtureGlobalService._verificar_disponibilidad_pareja(
                    dia, hora_mins, disp1
                )
                
                # Verificar pareja 2
                pareja2_disponible = TorneoFixtureGlobalService._verificar_disponibilidad_pareja(
                    dia, hora_mins, disp2
                )
                
                if not (pareja1_disponible and pareja2_disponible):
                    continue
                
                # 2. VERIFICAR TIEMPO MÍNIMO ENTRE PARTIDOS (60 MINUTOS)
                fecha_hora_slot = datetime.strptime(f"{fecha} {hora}", '%Y-%m-%d %H:%M')
                
                conflicto_tiempo = False
                for jugador_id in jugadores:
                    for fecha_hora_existente in partidos_por_jugador[jugador_id]:
                        diferencia_minutos = abs((fecha_hora_slot - fecha_hora_existente).total_seconds() / 60)
                        if diferencia_minutos < 60:  # Mínimo 60 minutos
                            conflicto_tiempo = True
                            break
                    if conflicto_tiempo:
                        break
                
                if conflicto_tiempo:
                    continue
                
                # 3. VERIFICAR CANCHA DISPONIBLE
                canchas_ocupadas = ocupacion_canchas[(fecha, hora)]
                cancha_libre = None
                
                for cancha in canchas:
                    if cancha.id not in canchas_ocupadas:
                        cancha_libre = cancha
                        break
                
                if not cancha_libre:
                    continue
                
                # ✅ SLOT VÁLIDO ENCONTRADO
                slot_asignado = (fecha, dia, hora)
                cancha_asignada = cancha_libre
                break
            
            if slot_asignado and cancha_asignada:
                # PROGRAMAR PARTIDO
                fecha, dia, hora = slot_asignado
                fecha_hora_slot = datetime.strptime(f"{fecha} {hora}", '%Y-%m-%d %H:%M')
                
                # Marcar ocupación de cancha
                ocupacion_canchas[(fecha, hora)].append(cancha_asignada.id)
                
                # Registrar partidos de jugadores
                for jugador_id in jugadores:
                    partidos_por_jugador[jugador_id].append(fecha_hora_slot)
                
                # Agregar partido programado
                partidos_programados.append({
                    **partido,
                    "fecha": fecha,
                    "hora": hora,
                    "slot": f"{fecha} {hora}",
                    "cancha_id": cancha_asignada.id,
                    "cancha_nombre": cancha_asignada.nombre
                })
                
            else:
                # NO SE PUDO PROGRAMAR - Agregar a lista de no programados
                # Obtener información detallada para el reporte
                
                # Obtener nombres de jugadores
                pareja1_nombres = "Pareja desconocida"
                pareja2_nombres = "Pareja desconocida"
                
                if pareja1:
                    from ..models.driveplus_models import Usuario
                    j1 = db.query(Usuario).filter(Usuario.id_usuario == pareja1.jugador1_id).first()
                    j2 = db.query(Usuario).filter(Usuario.id_usuario == pareja1.jugador2_id).first()
                    if j1 and j2:
                        pareja1_nombres = f"{j1.nombre_usuario} & {j2.nombre_usuario}"
                
                if pareja2:
                    from ..models.driveplus_models import Usuario
                    j1 = db.query(Usuario).filter(Usuario.id_usuario == pareja2.jugador1_id).first()
                    j2 = db.query(Usuario).filter(Usuario.id_usuario == pareja2.jugador2_id).first()
                    if j1 and j2:
                        pareja2_nombres = f"{j1.nombre_usuario} & {j2.nombre_usuario}"
                
                # Obtener información de la categoría
                categoria_info = "Categoría desconocida"
                if partido.get('categoria_id'):
                    categoria = db.query(TorneoCategoria).filter(TorneoCategoria.id == partido['categoria_id']).first()
                    if categoria:
                        genero_icon = "♂" if categoria.genero == "masculino" else "♀" if categoria.genero == "femenino" else "⚥"
                        categoria_info = f"{genero_icon} {categoria.nombre}"
                
                # Formatear restricciones para mostrar
                def formatear_disp(disp):
                    restricciones = disp.get('restricciones', {})
                    if not restricciones:
                        return "Sin restricciones (disponible en todos los horarios del torneo)"
                    
                    result = []
                    for dia, rangos in restricciones.items():
                        for inicio_mins, fin_mins in rangos:
                            inicio_str = f"{inicio_mins // 60:02d}:{inicio_mins % 60:02d}"
                            fin_str = f"{fin_mins // 60:02d}:{fin_mins % 60:02d}"
                            result.append(f"NO disponible {dia} {inicio_str}-{fin_str}")
                    return ", ".join(result)
                
                # Agregar a lista de no programados con detalles
                partidos_no_programados.append({
                    "zona_id": partido['zona_id'],
                    "zona_nombre": partido['zona_nombre'],
                    "categoria_id": partido['categoria_id'],
                    "categoria_nombre": categoria_info,
                    "pareja1_id": pareja1_id,
                    "pareja2_id": pareja2_id,
                    "pareja1_nombre": pareja1_nombres,
                    "pareja2_nombre": pareja2_nombres,
                    "motivo": "Sin horarios compatibles o conflicto de tiempo mínimo entre partidos",
                    "disponibilidad_pareja1": formatear_disp(disp1),
                    "disponibilidad_pareja2": formatear_disp(disp2)
                })
        
        return {
            "partidos_programados": partidos_programados,
            "partidos_no_programados": partidos_no_programados
        }
    
    @staticmethod
    def _verificar_disponibilidad_pareja(dia: str, hora_mins: int, disponibilidad: Dict) -> bool:
        """
        Verifica si una pareja está disponible en un día y hora específicos
        
        NUEVA LÓGICA CON RESTRICCIONES:
        - Si no tiene restricciones: disponible siempre (dentro de horarios del torneo)
        - Si tiene restricciones: verificar que NO esté en ninguna restricción
        - Si está en una restricción: NO disponible
        
        Args:
            dia: Día de la semana en español (lunes, martes, etc.)
            hora_mins: Hora en minutos desde medianoche
            disponibilidad: Dict con restricciones {dia: [(inicio, fin)]}
            
        Returns:
            bool: True si está disponible, False si está restringido
        """
        restricciones = disponibilidad.get('restricciones', {})
        
        # Sin restricciones = disponible siempre
        if not restricciones:
            return True
        
        # Verificar si el día tiene restricciones
        if dia not in restricciones:
            return True  # Día sin restricciones = disponible todo el día
        
        # Verificar si la hora está en alguna restricción
        rangos_restringidos = restricciones[dia]
        for inicio_mins, fin_mins in rangos_restringidos:
            # Si la hora del partido (incluyendo duración de 50 min) se solapa con la restricción
            if not (hora_mins + 50 <= inicio_mins or hora_mins >= fin_mins):
                return False  # Está en una restricción = NO disponible
        
        return True  # No está en ninguna restricción = disponible
    
    @staticmethod
    def _guardar_partidos(
        db: Session,
        torneo_id: int,
        partidos_programados: List[Dict],
        categoria_id: Optional[int] = None
    ):
        """
        Guarda los partidos programados en la base de datos
        
        Args:
            db: Sesión de base de datos
            torneo_id: ID del torneo
            partidos_programados: Lista de partidos a guardar
            categoria_id: (Opcional) Si se especifica, solo elimina partidos de esa categoría antes de guardar
        """
        # Eliminar partidos existentes de fase de grupos
        query = db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase == 'zona'
        )
        
        # Filtrar por categoría si se especifica
        if categoria_id:
            query = query.filter(Partido.categoria_id == categoria_id)
        
        query.delete()
        db.commit()
        
        # Crear nuevos partidos
        # Get tournament creator for id_creador
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        
        for i, partido_data in enumerate(partidos_programados):
            fecha_hora_str = f"{partido_data['fecha']} {partido_data['hora']}:00"
            # Crear datetime naive (sin timezone) para evitar conversiones UTC
            fecha_hora = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M:%S')
            
            partido = Partido(
                id_torneo=torneo_id,
                zona_id=partido_data['zona_id'],
                fase='zona',
                numero_partido=i + 1,
                pareja1_id=partido_data['pareja1_id'],
                pareja2_id=partido_data['pareja2_id'],
                cancha_id=partido_data['cancha_id'],
                fecha_hora=fecha_hora,
                fecha=fecha_hora,  # Also set fecha field
                estado='pendiente',
                tipo='torneo',
                id_creador=torneo.creado_por if torneo else 1,
                categoria_id=partido_data.get('categoria_id')
            )
            db.add(partido)
        
        db.commit()
