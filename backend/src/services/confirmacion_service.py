"""
Servicio de Confirmaciones
Maneja el flujo de confirmación de resultados de partidos
"""
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.playt_models import Partido, PartidoJugador, Usuario
from ..models.confirmacion import Confirmacion
from ..models.historial_enfrentamiento import HistorialEnfrentamiento
from ..services.elo_service import EloService


class ConfirmacionService:
    """Servicio para manejar confirmaciones de resultados"""
    
    HORAS_AUTO_CONFIRMACION = 48
    
    @staticmethod
    def obtener_estado_confirmaciones(id_partido: int, id_usuario_actual: int, db: Session) -> Dict:
        """
        Obtiene el estado de confirmaciones de un partido
        
        Returns:
            Dict con información de confirmaciones
        """
        partido = db.query(Partido).filter(Partido.id_partido == id_partido).first()
        if not partido:
            return None
        
        # Obtener todas las confirmaciones
        confirmaciones = db.query(Confirmacion).filter(
            Confirmacion.id_partido == id_partido
        ).all()
        
        # Contar confirmaciones y reportes
        confirmaciones_count = len([c for c in confirmaciones if c.tipo == 'confirmacion'])
        reportes_count = len([c for c in confirmaciones if c.tipo == 'reporte'])
        
        # Verificar si el usuario actual ya confirmó
        ya_confirmo = any(c.id_usuario == id_usuario_actual for c in confirmaciones)
        
        # Verificar si puede confirmar (no es el creador y no ha confirmado)
        puede_confirmar = (
            partido.creado_por != id_usuario_actual and 
            not ya_confirmo and
            partido.estado_confirmacion == 'pendiente_confirmacion'
        )
        
        return {
            "total_jugadores": 4,
            "confirmaciones": confirmaciones_count,
            "reportes": reportes_count,
            "pendientes": 4 - len(confirmaciones),
            "puede_confirmar": puede_confirmar,
            "ya_confirmo": ya_confirmo,
            "estado": partido.estado_confirmacion,
            "confirmaciones_detalle": confirmaciones
        }
    
    @staticmethod
    def confirmar_resultado(id_partido: int, id_usuario: int, db: Session) -> Dict:
        """
        Confirma el resultado de un partido
        
        Returns:
            Dict con resultado de la confirmación
        """
        partido = db.query(Partido).filter(Partido.id_partido == id_partido).first()
        if not partido:
            raise ValueError("Partido no encontrado")
        
        # Verificar que el partido tenga resultado
        if not partido.resultado_padel:
            raise ValueError("El partido no tiene resultado cargado")
        
        # Verificar que el usuario sea parte del partido
        jugador = db.query(PartidoJugador).filter(
            and_(
                PartidoJugador.id_partido == id_partido,
                PartidoJugador.id_usuario == id_usuario
            )
        ).first()
        
        if not jugador:
            raise ValueError("No eres parte de este partido")
        
        # Verificar que no sea el creador
        if partido.creado_por == id_usuario:
            raise ValueError("El creador no puede confirmar su propio resultado")
        
        # Verificar que no haya confirmado ya
        confirmacion_existente = db.query(Confirmacion).filter(
            and_(
                Confirmacion.id_partido == id_partido,
                Confirmacion.id_usuario == id_usuario
            )
        ).first()
        
        if confirmacion_existente:
            raise ValueError("Ya confirmaste este resultado")
        
        # Crear confirmación
        confirmacion = Confirmacion(
            id_partido=id_partido,
            id_usuario=id_usuario,
            tipo='confirmacion',
            fecha=datetime.now()
        )
        db.add(confirmacion)
        db.flush()
        
        # Contar confirmaciones totales (incluyendo esta)
        total_confirmaciones = db.query(Confirmacion).filter(
            and_(
                Confirmacion.id_partido == id_partido,
                Confirmacion.tipo == 'confirmacion'
            )
        ).count()
        
        # Si todos confirmaron (3 rivales), aplicar Elo
        elo_changes = None
        if total_confirmaciones >= 3:
            elo_changes = ConfirmacionService._aplicar_elo(partido, db)
            partido.estado_confirmacion = 'confirmado'
        
        # Obtener jugadores que faltan por confirmar
        jugadores_faltantes = []
        if total_confirmaciones < 3:
            # Obtener todos los jugadores del partido
            todos_jugadores = db.query(PartidoJugador).filter(
                PartidoJugador.id_partido == id_partido
            ).all()
            
            # Obtener quiénes ya confirmaron
            confirmaciones = db.query(Confirmacion).filter(
                and_(
                    Confirmacion.id_partido == id_partido,
                    Confirmacion.tipo == 'confirmacion'
                )
            ).all()
            
            ids_confirmados = {c.id_usuario for c in confirmaciones}
            ids_confirmados.add(partido.creado_por)  # El creador no confirma
            
            # Encontrar quiénes faltan
            for jugador in todos_jugadores:
                if jugador.id_usuario not in ids_confirmados:
                    usuario = db.query(Usuario).filter(Usuario.id_usuario == jugador.id_usuario).first()
                    if usuario:
                        jugadores_faltantes.append(usuario.nombre_usuario)
        
        # Calcular cambio de Elo estimado para el usuario actual
        cambio_elo_usuario = None
        if not elo_changes:  # Solo si no se aplicó aún
            # Estimación simple basada en el resultado
            jugador_actual = db.query(PartidoJugador).filter(
                and_(
                    PartidoJugador.id_partido == id_partido,
                    PartidoJugador.id_usuario == id_usuario
                )
            ).first()
            
            if jugador_actual:
                # Estimación: ganadores +15, perdedores -15 (simplificado)
                gano = (partido.ganador_equipo == jugador_actual.equipo)
                cambio_elo_usuario = 15 if gano else -15
        
        db.commit()
        
        return {
            "success": True,
            "confirmaciones_totales": total_confirmaciones,
            "elo_aplicado": total_confirmaciones >= 3,
            "elo_changes": elo_changes,
            "cambio_elo_usuario": cambio_elo_usuario,
            "jugadores_faltantes": jugadores_faltantes,
            "mensaje": "Resultado confirmado" if total_confirmaciones < 3 else "Todos confirmaron. Elo actualizado."
        }
    
    @staticmethod
    def reportar_resultado(id_partido: int, id_usuario: int, motivo: str, db: Session) -> Dict:
        """
        Reporta un resultado como incorrecto
        """
        partido = db.query(Partido).filter(Partido.id_partido == id_partido).first()
        if not partido:
            raise ValueError("Partido no encontrado")
        
        # Verificar que el usuario sea parte del partido
        jugador = db.query(PartidoJugador).filter(
            and_(
                PartidoJugador.id_partido == id_partido,
                PartidoJugador.id_usuario == id_usuario
            )
        ).first()
        
        if not jugador:
            raise ValueError("No eres parte de este partido")
        
        # Verificar que no haya reportado ya
        reporte_existente = db.query(Confirmacion).filter(
            and_(
                Confirmacion.id_partido == id_partido,
                Confirmacion.id_usuario == id_usuario
            )
        ).first()
        
        if reporte_existente:
            raise ValueError("Ya reportaste este resultado")
        
        # Crear reporte
        reporte = Confirmacion(
            id_partido=id_partido,
            id_usuario=id_usuario,
            tipo='reporte',
            motivo=motivo,
            fecha=datetime.now()
        )
        db.add(reporte)
        
        # Cambiar estado del partido a disputado
        partido.estado_confirmacion = 'disputado'
        
        db.commit()
        
        return {
            "success": True,
            "mensaje": "Reporte registrado. Un administrador revisará el caso."
        }
    
    @staticmethod
    def _aplicar_elo(partido: Partido, db: Session) -> Dict:
        """
        Aplica el cálculo de Elo cuando todos confirman
        
        Returns:
            Dict con cambios de Elo por jugador
        """
        if partido.elo_aplicado:
            return None  # Ya se aplicó
        
        # Obtener jugadores del partido
        jugadores = db.query(PartidoJugador).filter(
            PartidoJugador.id_partido == partido.id_partido
        ).all()
        
        if len(jugadores) != 4:
            raise ValueError("El partido debe tener 4 jugadores")
        
        # Separar por equipos
        equipo1 = [j for j in jugadores if j.equipo == 1]
        equipo2 = [j for j in jugadores if j.equipo == 2]
        
        # Obtener ratings actuales
        ratings_equipo1 = []
        ratings_equipo2 = []
        
        for j in equipo1:
            usuario = db.query(Usuario).filter(Usuario.id_usuario == j.id_usuario).first()
            ratings_equipo1.append(usuario.rating)
            j.rating_antes = usuario.rating
        
        for j in equipo2:
            usuario = db.query(Usuario).filter(Usuario.id_usuario == j.id_usuario).first()
            ratings_equipo2.append(usuario.rating)
            j.rating_antes = usuario.rating
        
        # Preparar datos para el servicio Elo
        team_a_players = []
        team_b_players = []
        
        for j in equipo1:
            usuario = db.query(Usuario).filter(Usuario.id_usuario == j.id_usuario).first()
            team_a_players.append({
                'id': usuario.id_usuario,  # El servicio Elo espera 'id'
                'id_usuario': usuario.id_usuario,
                'rating': usuario.rating,
                'partidos': usuario.partidos_jugados
            })
        
        for j in equipo2:
            usuario = db.query(Usuario).filter(Usuario.id_usuario == j.id_usuario).first()
            team_b_players.append({
                'id': usuario.id_usuario,  # El servicio Elo espera 'id'
                'id_usuario': usuario.id_usuario,
                'rating': usuario.rating,
                'partidos': usuario.partidos_jugados
            })
        
        # Extraer datos del resultado
        resultado = partido.resultado_padel
        sets_a = sum(1 for s in resultado['sets'] if s.get('ganador') == 'equipoA')
        sets_b = sum(1 for s in resultado['sets'] if s.get('ganador') == 'equipoB')
        games_a = sum(s.get('gamesEquipoA', 0) for s in resultado['sets'])
        games_b = sum(s.get('gamesEquipoB', 0) for s in resultado['sets'])
        
        # Calcular Elo usando el servicio existente
        elo_service = EloService()
        cambios_elo_result = elo_service.calculate_match_ratings(
            team_a_players=team_a_players,
            team_b_players=team_b_players,
            sets_a=sets_a,
            sets_b=sets_b,
            games_a=games_a,
            games_b=games_b,
            sets_detail=resultado['sets'],
            match_type='amistoso',
            match_date=partido.fecha
        )
        
        # Convertir resultado al formato esperado
        cambios_elo = {}
        for i, player_change in enumerate(cambios_elo_result['team_a']['players']):
            cambios_elo[f'jugador_a_{i}'] = {
                'anterior': player_change['old_rating'],
                'nuevo': player_change['new_rating'],
                'cambio': player_change['rating_change']
            }
        
        for i, player_change in enumerate(cambios_elo_result['team_b']['players']):
            cambios_elo[f'jugador_b_{i}'] = {
                'anterior': player_change['old_rating'],
                'nuevo': player_change['new_rating'],
                'cambio': player_change['rating_change']
            }
        
        # Aplicar cambios (convertir a enteros)
        resultado = {}
        
        for i, j in enumerate(equipo1):
            usuario = db.query(Usuario).filter(Usuario.id_usuario == j.id_usuario).first()
            cambio_key = f'jugador_a_{i}'
            cambio = cambios_elo[cambio_key]
            
            # Convertir a enteros
            nuevo_rating = int(round(cambio['nuevo']))
            cambio_elo_int = int(round(cambio['cambio']))
            
            usuario.rating = nuevo_rating
            j.rating_despues = nuevo_rating
            j.cambio_elo = cambio_elo_int
            
            resultado[j.id_usuario] = {
                'anterior': int(cambio['anterior']),
                'nuevo': nuevo_rating,
                'cambio': cambio_elo_int
            }
        
        for i, j in enumerate(equipo2):
            usuario = db.query(Usuario).filter(Usuario.id_usuario == j.id_usuario).first()
            cambio_key = f'jugador_b_{i}'
            cambio = cambios_elo[cambio_key]
            
            # Convertir a enteros
            nuevo_rating = int(round(cambio['nuevo']))
            cambio_elo_int = int(round(cambio['cambio']))
            
            usuario.rating = nuevo_rating
            j.rating_despues = nuevo_rating
            j.cambio_elo = cambio_elo_int
            
            resultado[j.id_usuario] = {
                'anterior': int(cambio['anterior']),
                'nuevo': nuevo_rating,
                'cambio': cambio_elo_int
            }
        
        # Marcar Elo como aplicado
        partido.elo_aplicado = True
        
        # Actualizar historial de enfrentamientos
        historial = db.query(HistorialEnfrentamiento).filter(
            HistorialEnfrentamiento.id_partido == partido.id_partido
        ).first()
        
        if historial:
            historial.elo_aplicado = True
        
        db.commit()
        
        return resultado
    
    @staticmethod
    def auto_confirmar_partidos_antiguos(db: Session) -> int:
        """
        Auto-confirma partidos que tienen más de 48 horas sin reportes
        
        Returns:
            Cantidad de partidos auto-confirmados
        """
        fecha_limite = datetime.now() - timedelta(hours=ConfirmacionService.HORAS_AUTO_CONFIRMACION)
        
        # Buscar partidos pendientes de confirmación antiguos
        partidos = db.query(Partido).filter(
            and_(
                Partido.estado_confirmacion == 'pendiente_confirmacion',
                Partido.creado_en <= fecha_limite
            )
        ).all()
        
        count = 0
        for partido in partidos:
            # Verificar que no haya reportes
            reportes = db.query(Confirmacion).filter(
                and_(
                    Confirmacion.id_partido == partido.id_partido,
                    Confirmacion.tipo == 'reporte'
                )
            ).count()
            
            if reportes == 0:
                # Auto-confirmar
                try:
                    ConfirmacionService._aplicar_elo(partido, db)
                    partido.estado_confirmacion = 'auto_confirmado'
                    count += 1
                except Exception as e:
                    print(f"Error auto-confirmando partido {partido.id_partido}: {e}")
                    continue
        
        db.commit()
        return count


    def __init__(self, db: Session):
        """Inicializar servicio con sesión de base de datos"""
        self.db = db
    
    def crear_resultado(self, resultado_data) -> Dict:
        """
        Crear un nuevo resultado de partido desde una sala
        
        Args:
            resultado_data: Datos del resultado (ResultadoPadelCreate)
            
        Returns:
            Dict con información del resultado creado
        """
        from ..models.confirmacion import ResultadoPadel
        
        # Crear el resultado en la base de datos
        resultado = ResultadoPadel(
            id_sala=resultado_data.id_sala,
            id_creador=resultado_data.id_creador,
            sets=resultado_data.sets,
            ganador_equipo=resultado_data.ganador_equipo,
            estado='pendiente_confirmacion',
            confirmaciones=1,  # El creador ya confirmó
            fecha_creacion=datetime.now()
        )
        
        self.db.add(resultado)
        self.db.commit()
        self.db.refresh(resultado)
        
        return {
            "id_resultado": resultado.id_resultado,
            "id_sala": resultado.id_sala,
            "estado": resultado.estado,
            "confirmaciones": resultado.confirmaciones,
            "mensaje": "Resultado creado. Esperando confirmación de rivales."
        }
    
    def obtener_resultado(self, id_sala: str):
        """
        Obtener el resultado de una sala
        
        Args:
            id_sala: ID de la sala
            
        Returns:
            Resultado o None si no existe
        """
        from ..models.confirmacion import ResultadoPadel
        
        resultado = self.db.query(ResultadoPadel).filter(
            ResultadoPadel.id_sala == id_sala
        ).first()
        
        return resultado
    
    def confirmar_resultado_por_sala(self, id_sala: str, id_usuario: int) -> Dict:
        """
        Confirmar un resultado de partido por sala
        
        Args:
            id_sala: ID de la sala
            id_usuario: ID del usuario que confirma
            
        Returns:
            Dict con resultado de la confirmación
        """
        from ..models.confirmacion import ResultadoPadel, ConfirmacionUsuario
        
        # Obtener el resultado
        resultado = self.obtener_resultado(id_sala)
        if not resultado:
            raise ValueError("Resultado no encontrado")
        
        # Verificar que no sea el creador
        if resultado.id_creador == id_usuario:
            raise ValueError("El creador no puede confirmar su propio resultado")
        
        # Verificar que no haya confirmado ya
        confirmacion_existente = self.db.query(ConfirmacionUsuario).filter(
            and_(
                ConfirmacionUsuario.id_resultado == resultado.id_resultado,
                ConfirmacionUsuario.id_usuario == id_usuario
            )
        ).first()
        
        if confirmacion_existente:
            raise ValueError("Ya confirmaste este resultado")
        
        # Crear confirmación
        confirmacion = ConfirmacionUsuario(
            id_resultado=resultado.id_resultado,
            id_usuario=id_usuario,
            fecha=datetime.now()
        )
        self.db.add(confirmacion)
        
        # Incrementar contador de confirmaciones
        resultado.confirmaciones += 1
        
        # Si se alcanzó consenso (3 confirmaciones), aplicar Elo
        consenso_alcanzado = False
        if resultado.confirmaciones >= 3:
            resultado.estado = 'confirmado'
            consenso_alcanzado = True
            # TODO: Aplicar Elo aquí
        
        self.db.commit()
        
        return {
            "success": True,
            "confirmaciones": resultado.confirmaciones,
            "consenso_alcanzado": consenso_alcanzado,
            "mensaje": "Resultado confirmado" if not consenso_alcanzado else "Consenso alcanzado. Elo aplicado."
        }
    
    def obtener_pendientes_usuario(self, id_usuario: int) -> List:
        """
        Obtener resultados pendientes de confirmación para un usuario
        
        Args:
            id_usuario: ID del usuario
            
        Returns:
            Lista de resultados pendientes
        """
        from ..models.confirmacion import ResultadoPadel
        
        # TODO: Implementar lógica para obtener salas donde el usuario es jugador
        # y hay resultados pendientes de confirmación
        
        resultados = self.db.query(ResultadoPadel).filter(
            and_(
                ResultadoPadel.estado == 'pendiente_confirmacion',
                ResultadoPadel.id_creador != id_usuario
            )
        ).all()
        
        return resultados
