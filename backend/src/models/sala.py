from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.config import Base
import secrets

class Sala(Base):
    """Modelo de Sala para partidos colaborativos"""
    __tablename__ = "salas"
    
    id_sala = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    codigo_invitacion = Column(String(10), unique=True, index=True, nullable=False)
    fecha = Column(DateTime(timezone=True), nullable=False)
    estado = Column(String(20), default="esperando", nullable=False)  # esperando, en_juego, finalizada
    id_creador = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=False)
    max_jugadores = Column(Integer, default=4, nullable=False)
    id_partido = Column(BigInteger, ForeignKey("partidos.id_partido"), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    creador = relationship("Usuario", foreign_keys=[id_creador])
    jugadores = relationship("SalaJugador", back_populates="sala")
    partido = relationship("Partido", foreign_keys=[id_partido])
    
    @staticmethod
    def generar_codigo():
        """Generar código de invitación único de 6 caracteres"""
        return secrets.token_urlsafe(6)[:6].upper()

class SalaJugador(Base):
    """Modelo de relación entre Sala y Jugadores"""
    __tablename__ = "sala_jugadores"
    
    id_sala = Column(BigInteger, ForeignKey("salas.id_sala"), primary_key=True)
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario"), primary_key=True)
    equipo = Column(Integer, nullable=True)  # 1 o 2, null si aún no se asigna
    orden = Column(Integer, nullable=False)  # Orden de llegada (1-4)
    unido_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    sala = relationship("Sala", back_populates="jugadores")
    usuario = relationship("Usuario")
