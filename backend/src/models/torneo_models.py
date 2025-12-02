"""
Modelos SQLAlchemy para el sistema de torneos
"""
from sqlalchemy import Column, BigInteger, String, Text, Enum, Date, DateTime, Boolean, Integer, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.playt_models import Base
import enum


class EstadoTorneo(str, enum.Enum):
    INSCRIPCION = "inscripcion"
    ARMANDO_ZONAS = "armando_zonas"
    FASE_GRUPOS = "fase_grupos"
    FASE_ELIMINACION = "fase_eliminacion"
    FINALIZADO = "finalizado"


class TipoTorneo(str, enum.Enum):
    CLASICO = "clasico"


class RolOrganizador(str, enum.Enum):
    OWNER = "owner"
    COLABORADOR = "colaborador"


class EstadoPareja(str, enum.Enum):
    INSCRIPTA = "inscripta"
    CONFIRMADA = "confirmada"
    BAJA = "baja"


class FasePartido(str, enum.Enum):
    ZONA = "zona"
    DIECISEISAVOS = "16avos"
    OCTAVOS = "8vos"
    CUARTOS = "4tos"
    SEMIS = "semis"
    FINAL = "final"


class EstadoPartido(str, enum.Enum):
    PENDIENTE = "pendiente"
    EN_JUEGO = "en_juego"
    FINALIZADO = "finalizado"
    WO = "w_o"
    CANCELADO = "cancelado"


class OrigenPartido(str, enum.Enum):
    AUTO = "auto"
    MANUAL = "manual"


class OrganizadorAutorizado(Base):
    __tablename__ = "organizadores_autorizados"
    
    user_id = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True)
    autorizado_por = Column(BigInteger, ForeignKey("usuarios.id_usuario"))
    fecha_autorizacion = Column(DateTime, server_default=func.current_timestamp())
    activo = Column(Boolean, default=True)
    
    # Relationships - Comentados temporalmente
    # usuario = relationship("Usuario", foreign_keys=[user_id])
    # autorizador = relationship("Usuario", foreign_keys=[autorizado_por])


class GeneroTorneo(str, enum.Enum):
    MASCULINO = "masculino"
    FEMENINO = "femenino"
    MIXTO = "mixto"


class Torneo(Base):
    __tablename__ = "torneos"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    tipo = Column(String(20), default="clasico")  # Cambiado de Enum a String
    categoria = Column(String(50), nullable=False)
    genero = Column(String(20), default="masculino")  # masculino, femenino, mixto
    estado = Column(String(30), default="inscripcion")  # Cambiado de Enum a String
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    lugar = Column(String(255))
    reglas_json = Column(JSON, comment="Configuración: puntos por victoria, sets, etc.")
    creado_por = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships - Comentados temporalmente para evitar problemas de imports circulares
    # Se pueden agregar después si es necesario
    # organizadores = relationship("TorneoOrganizador", back_populates="torneo")
    # parejas = relationship("TorneoPareja", back_populates="torneo")
    # zonas = relationship("TorneoZona", back_populates="torneo")
    # canchas = relationship("TorneoCancha", back_populates="torneo")
    
    __table_args__ = (
        Index('idx_torneos_estado', 'estado'),
        Index('idx_torneos_fecha_inicio', 'fecha_inicio'),
        Index('idx_torneos_categoria', 'categoria'),
    )


class TorneoOrganizador(Base):
    __tablename__ = "torneos_organizadores"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    torneo_id = Column(BigInteger, ForeignKey("torneos.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    rol = Column(String(20), default="colaborador")  # Cambiado de Enum a String
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relationships - Comentados temporalmente
    # torneo = relationship("Torneo", back_populates="organizadores")
    # usuario = relationship("Usuario")


class TorneoPareja(Base):
    __tablename__ = "torneos_parejas"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    torneo_id = Column(BigInteger, ForeignKey("torneos.id", ondelete="CASCADE"), nullable=False)
    jugador1_id = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=False)
    jugador2_id = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=False)
    estado = Column(String(20), default="inscripta")  # Cambiado de Enum a String
    categoria_asignada = Column(String(50))
    observaciones = Column(Text)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships - Comentados temporalmente
    # torneo = relationship("Torneo", back_populates="parejas")
    # jugador1 = relationship("Usuario", foreign_keys=[jugador1_id])
    # jugador2 = relationship("Usuario", foreign_keys=[jugador2_id])
    # zona_asignacion = relationship("TorneoZonaPareja", back_populates="pareja", uselist=False)
    
    __table_args__ = (
        Index('idx_torneos_parejas_torneo', 'torneo_id'),
        Index('idx_torneos_parejas_estado', 'estado'),
        Index('idx_torneos_parejas_jugadores', 'jugador1_id', 'jugador2_id'),
    )


class TorneoZona(Base):
    __tablename__ = "torneo_zonas"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    torneo_id = Column(BigInteger, ForeignKey("torneos.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(50), nullable=False, comment="Zona A, Zona B, etc.")
    numero_orden = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relationships - Comentados temporalmente
    # torneo = relationship("Torneo", back_populates="zonas")
    # parejas_asignadas = relationship("TorneoZonaPareja", back_populates="zona")
    # tabla_posiciones = relationship("TorneoTablaPosiciones", back_populates="zona")


class TorneoZonaPareja(Base):
    __tablename__ = "torneo_zona_parejas"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    zona_id = Column(BigInteger, ForeignKey("torneo_zonas.id", ondelete="CASCADE"), nullable=False)
    pareja_id = Column(BigInteger, ForeignKey("torneos_parejas.id", ondelete="CASCADE"), nullable=False)
    posicion_final = Column(Integer, comment="Posición final en la zona (1°, 2°, 3°)")
    clasificado = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relationships - Comentados temporalmente
    # zona = relationship("TorneoZona", back_populates="parejas_asignadas")
    # pareja = relationship("TorneoPareja", back_populates="zona_asignacion")


class TorneoCancha(Base):
    __tablename__ = "torneo_canchas"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    torneo_id = Column(BigInteger, ForeignKey("torneos.id", ondelete="CASCADE"), nullable=False)
    nombre = Column(String(100), nullable=False, comment="Cancha 1, Cancha Techada, etc.")
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relationships - Comentados temporalmente
    # torneo = relationship("Torneo", back_populates="canchas")
    # slots = relationship("TorneoSlot", back_populates="cancha")


class TorneoSlot(Base):
    __tablename__ = "torneo_slots"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    torneo_id = Column(BigInteger, ForeignKey("torneos.id", ondelete="CASCADE"), nullable=False)
    cancha_id = Column(BigInteger, ForeignKey("torneo_canchas.id", ondelete="CASCADE"), nullable=False)
    fecha_hora_inicio = Column(DateTime, nullable=False)
    fecha_hora_fin = Column(DateTime, nullable=False)
    ocupado = Column(Boolean, default=False)
    partido_id = Column(BigInteger, comment="Partido asignado a este slot")
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relationships - Comentados temporalmente
    # cancha = relationship("TorneoCancha", back_populates="slots")
    
    __table_args__ = (
        Index('idx_torneo_slots_torneo', 'torneo_id'),
        Index('idx_torneo_slots_cancha', 'cancha_id'),
        Index('idx_torneo_slots_fecha', 'fecha_hora_inicio'),
        Index('idx_torneo_slots_ocupado', 'ocupado'),
    )


class TorneoBloqueoJugador(Base):
    __tablename__ = "torneo_bloqueos_jugador"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    torneo_id = Column(BigInteger, ForeignKey("torneos.id", ondelete="CASCADE"), nullable=False)
    jugador_id = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_desde = Column(String(8), nullable=False)  # TIME en BD, pero usamos String para facilidad
    hora_hasta = Column(String(8), nullable=False)  # TIME en BD, pero usamos String para facilidad
    motivo = Column(String(255))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relationships - Comentados temporalmente
    # jugador = relationship("Usuario")
    
    __table_args__ = (
        Index('idx_torneo_bloqueos_jugador', 'jugador_id'),
        Index('idx_torneo_bloqueos_fecha', 'fecha'),
    )


# NOTA: Los partidos de torneo se guardan en la tabla 'partidos' existente
# Ver modelo Partido en playt_models.py
# Los sets se guardan en la tabla 'partido_sets'


class TorneoTablaPosiciones(Base):
    __tablename__ = "torneo_tabla_posiciones"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    zona_id = Column(BigInteger, ForeignKey("torneo_zonas.id", ondelete="CASCADE"), nullable=False)
    pareja_id = Column(BigInteger, ForeignKey("torneos_parejas.id", ondelete="CASCADE"), nullable=False)
    puntos = Column(Integer, default=0)
    partidos_jugados = Column(Integer, default=0)
    partidos_ganados = Column(Integer, default=0)
    partidos_perdidos = Column(Integer, default=0)
    sets_favor = Column(Integer, default=0)
    sets_contra = Column(Integer, default=0)
    games_favor = Column(Integer, default=0)
    games_contra = Column(Integer, default=0)
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships - Comentados temporalmente
    # zona = relationship("TorneoZona", back_populates="tabla_posiciones")
    # pareja = relationship("TorneoPareja")
    
    __table_args__ = (
        Index('idx_torneo_tabla_zona', 'zona_id'),
        Index('idx_torneo_tabla_puntos', 'puntos'),
    )


class TorneoHistorialCambios(Base):
    __tablename__ = "torneo_historial_cambios"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    torneo_id = Column(BigInteger, ForeignKey("torneos.id", ondelete="CASCADE"), nullable=False)
    tipo_cambio = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=False)
    realizado_por = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=False)
    datos_json = Column(JSON, comment="Datos adicionales del cambio")
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Relationships - Comentados temporalmente
    # torneo = relationship("Torneo")
    # usuario = relationship("Usuario")
