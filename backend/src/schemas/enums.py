"""
Enums para estados y tipos en Drive+.
Usar en lugar de strings para mejor tipado y validación.
"""
from enum import Enum


class EstadoPartido(str, Enum):
    """Estados posibles de un partido"""
    pendiente = "pendiente"
    en_curso = "en_curso"
    reportado = "reportado"
    confirmado = "confirmado"
    finalizado = "finalizado"
    cancelado = "cancelado"


class EstadoConfirmacion(str, Enum):
    """Estados de confirmación de resultado"""
    pendiente_confirmacion = "pendiente_confirmacion"
    confirmado = "confirmado"
    disputado = "disputado"
    auto_confirmado = "auto_confirmado"


class EstadoSala(str, Enum):
    """Estados de una sala"""
    esperando = "esperando"
    completa = "completa"
    en_juego = "en_juego"
    finalizada = "finalizada"
    cancelada = "cancelada"


class EstadoTorneo(str, Enum):
    """Estados de un torneo"""
    borrador = "borrador"
    inscripcion = "inscripcion"
    inscripcion_cerrada = "inscripcion_cerrada"
    fase_grupos = "fase_grupos"
    playoffs = "playoffs"
    finalizado = "finalizado"
    cancelado = "cancelado"


class FaseTorneo(str, Enum):
    """Fases de un torneo"""
    grupos = "grupos"
    octavos = "octavos"
    cuartos = "cuartos"
    semifinal = "semifinal"
    final = "final"
    tercer_puesto = "tercer_puesto"


class EstadoInscripcion(str, Enum):
    """Estados de inscripción a torneo"""
    pendiente = "pendiente"
    confirmada = "confirmada"
    rechazada = "rechazada"
    cancelada = "cancelada"


class TipoConfirmacion(str, Enum):
    """Tipos de confirmación"""
    confirmacion = "confirmacion"
    reporte = "reporte"


class Sexo(str, Enum):
    """Sexo del jugador"""
    masculino = "M"
    femenino = "F"
    mixto = "mixto"


class TipoPartido(str, Enum):
    """Tipos de partido"""
    amistoso = "amistoso"
    torneo = "torneo"
    ranking = "ranking"


class CategoriaNivel(str, Enum):
    """Niveles de categoría"""
    principiante = "principiante"
    intermedio = "intermedio"
    avanzado = "avanzado"
    profesional = "profesional"
