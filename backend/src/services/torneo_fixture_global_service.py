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
        user_id: int
    ) -> Dict:
        """
        Genera fixture completo para todas las zonas y categorías del torneo
        
        Args:
            db: Sesión de base de datos
            torneo_id: ID del torneo
            user_id: ID del usuario organizador
            
        Returns:
            Dict con partidos generados y estadísticas
        """
        # Verificar permisos
        torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
        if not torneo:
            raise ValueError("Torneo no encontrado")
        
        if torneo.creado_por != user_id:
            raise ValueError("No tienes permisos")
        
        # Obtener todas las zonas del torneo (todas las categorías)
        zonas = db.query(TorneoZona).filter(
            TorneoZona.torneo_id == torneo_id
        ).all()
        
        if not zonas:
            raise ValueError("No hay zonas creadas. Genera las zonas primero.")
        
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
            db, todos_partidos
        )
        
        # Generar slots de tiempo disponibles
        slots_disponibles = TorneoFixtureGlobalService._generar_slots_torneo(
            torneo, horarios_torneo
        )
        
        # Asignar horarios y canchas a los partidos
        partidos_programados = TorneoFixtureGlobalService._asignar_horarios_y_canchas(
            db,
            todos_partidos,
            parejas_disponibilidad,
            slots_disponibles,
            canchas,
            num_canchas
        )
        
        # Guardar partidos en la base de datos
        TorneoFixtureGlobalService._guardar_partidos(
            db, torneo_id, partidos_programados
        )
        
        return {
            "partidos_generados": len(partidos_programados),
            "zonas_procesadas": len(zonas),
            "canchas_utilizadas": num_canchas,
            "slots_utilizados": len(set(p['slot'] for p in partidos_programados)),
            "partidos": partidos_programados
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
        partidos: List[Dict]
    ) -> Dict[int, Set[Tuple[str, str]]]:
        """
        Obtiene disponibilidad horaria de todas las parejas
        
        Returns:
            Dict {pareja_id: set((dia, hora))}
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
            
            # Extraer slots de disponibilidad
            disp = pareja.disponibilidad_horaria or {}
            slots = set()
            
            # Si no tiene disponibilidad, asumimos disponible siempre (set vacío = sin restricciones)
            if not disp or not disp.get('franjas'):
                # Set vacío significa "disponible en cualquier horario del torneo"
                # Esto se manejará en _asignar_horarios_y_canchas
                disponibilidad[pareja_id] = set()
                continue
            
            # Procesar franjas específicas
            franjas = disp.get('franjas', [])
            for franja in franjas:
                dias = franja.get('dias', [])
                hora_inicio = franja.get('horaInicio', '08:00')
                hora_fin = franja.get('horaFin', '23:00')
                
                # Generar slots
                hora_actual = datetime.strptime(hora_inicio, '%H:%M')
                hora_limite = datetime.strptime(hora_fin, '%H:%M')
                
                for dia in dias:
                    h = hora_actual
                    while h < hora_limite:
                        slots.add((dia, h.strftime('%H:%M')))
                        h += timedelta(minutes=50)
            
            disponibilidad[pareja_id] = slots
        
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
            
            # Determinar si es semana o fin de semana
            tipo_dia = 'finDeSemana' if dia_semana in ['sabado', 'domingo'] else 'semana'
            
            # Obtener franjas horarias para este tipo de día
            franjas = horarios_torneo.get(tipo_dia, [])
            
            if not franjas:
                # Si no hay franjas definidas, usar horario por defecto
                franjas = [{'desde': '08:00', 'hasta': '23:00'}]
            
            # Generar slots para cada franja
            for franja in franjas:
                hora_desde = franja.get('desde', '08:00')
                hora_hasta = franja.get('hasta', '23:00')
                
                hora_actual = datetime.strptime(hora_desde, '%H:%M')
                hora_limite = datetime.strptime(hora_hasta, '%H:%M')
                
                while hora_actual < hora_limite:
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
        parejas_disponibilidad: Dict[int, Set],
        slots_disponibles: List[Tuple[str, str, str]],
        canchas: List[TorneoCancha],
        num_canchas: int
    ) -> List[Dict]:
        """
        Asigna horarios y canchas a los partidos considerando:
        - Disponibilidad de parejas
        - Máximo N partidos simultáneos (N = número de canchas)
        - No repetir cancha/horario
        
        Returns:
            Lista de partidos con slot y cancha asignados
        """
        partidos_programados = []
        
        # Mapa de ocupación: {(fecha, hora): [cancha_id, ...]}
        ocupacion = defaultdict(list)
        
        # Ordenar partidos por prioridad (ej: zonas con menos partidos primero)
        partidos_ordenados = sorted(partidos, key=lambda p: p['zona_id'])
        
        for partido in partidos_ordenados:
            pareja1_id = partido['pareja1_id']
            pareja2_id = partido['pareja2_id']
            
            # Obtener disponibilidad de ambas parejas
            disp1 = parejas_disponibilidad.get(pareja1_id, set())
            disp2 = parejas_disponibilidad.get(pareja2_id, set())
            
            # Slots compatibles para ambas parejas
            slots_compatibles = []
            for fecha, dia, hora in slots_disponibles:
                # Si alguna pareja no tiene restricciones (set vacío), está disponible siempre
                pareja1_disponible = len(disp1) == 0 or (dia, hora) in disp1
                pareja2_disponible = len(disp2) == 0 or (dia, hora) in disp2
                
                if pareja1_disponible and pareja2_disponible:
                    # Verificar si hay cancha disponible en este slot
                    canchas_ocupadas = ocupacion.get((fecha, hora), [])
                    if len(canchas_ocupadas) < num_canchas:
                        slots_compatibles.append((fecha, dia, hora))
            
            if not slots_compatibles:
                # Si no hay slots compatibles con disponibilidad específica,
                # usar cualquier slot del torneo (las zonas ya consideran compatibilidad)
                print(f"⚠️ Partido sin horarios compatibles específicos: Pareja {pareja1_id} vs {pareja2_id}")
                print(f"   Asignando primer slot disponible del torneo...")
                for fecha, dia, hora in slots_disponibles:
                    canchas_ocupadas = ocupacion.get((fecha, hora), [])
                    if len(canchas_ocupadas) < num_canchas:
                        slots_compatibles.append((fecha, dia, hora))
                        break
            
            if not slots_compatibles:
                # No hay slots disponibles en absoluto (todas las canchas ocupadas)
                print(f"❌ No se pudo programar partido: Pareja {pareja1_id} vs {pareja2_id} - Todas las canchas ocupadas")
                continue
            
            # Tomar el primer slot compatible
            fecha, dia, hora = slots_compatibles[0]
            
            # Asignar cancha disponible en ese slot
            canchas_ocupadas = ocupacion[(fecha, hora)]
            cancha_asignada = None
            
            for cancha in canchas:
                if cancha.id not in canchas_ocupadas:
                    cancha_asignada = cancha
                    break
            
            if not cancha_asignada:
                # No debería pasar, pero por seguridad
                cancha_asignada = canchas[0]
            
            # Marcar cancha como ocupada en este slot
            ocupacion[(fecha, hora)].append(cancha_asignada.id)
            
            # Agregar partido programado
            partidos_programados.append({
                **partido,
                "fecha": fecha,
                "hora": hora,
                "slot": f"{fecha} {hora}",
                "cancha_id": cancha_asignada.id,
                "cancha_nombre": cancha_asignada.nombre
            })
        
        return partidos_programados
    
    @staticmethod
    def _guardar_partidos(
        db: Session,
        torneo_id: int,
        partidos_programados: List[Dict]
    ):
        """Guarda los partidos programados en la base de datos"""
        # Eliminar partidos existentes de fase de grupos
        db.query(Partido).filter(
            Partido.id_torneo == torneo_id,
            Partido.fase == 'zona'
        ).delete()
        
        db.commit()
        
        # Crear nuevos partidos
        for i, partido_data in enumerate(partidos_programados):
            fecha_hora_str = f"{partido_data['fecha']} {partido_data['hora']}:00"
            fecha_hora = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M:%S')
            
            # Get tournament creator for id_creador
            torneo = db.query(Torneo).filter(Torneo.id == torneo_id).first()
            
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
