from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.config import Base


class Confirmacion(Base):
    """Modelo de Confirmación de Resultados"""
    __tablename__ = "confirmaciones"
    
    id_confirmacion = Column(BigInteger, primary_key=True, index=True)
    id_partido = Column(BigInteger, ForeignKey("partidos.id_partido", ondelete="CASCADE"), nullable=False)
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'confirmacion' o 'reporte'
    motivo = Column(Text, nullable=True)  # Solo para reportes
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    partido = relationship("Partido", back_populates="confirmaciones")
    usuario = relationship("Usuario")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("tipo IN ('confirmacion', 'reporte')", name='chk_tipo_confirmacion'),
        {'comment': 'Registro de confirmaciones y reportes de resultados de partidos amistosos'}
    )



class ResultadoPadel(Base):
    """Modelo de Resultado de Pádel"""
    __tablename__ = "resultados_padel"
    
    id_resultado = Column(BigInteger, primary_key=True, index=True)
    id_sala = Column(String(50), nullable=False, index=True)
    id_creador = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    sets = Column(Text, nullable=False)  # JSON con los sets
    ganador_equipo = Column(String(10), nullable=False)  # 'equipo1' o 'equipo2'
    estado = Column(String(30), nullable=False, default='pendiente_confirmacion')
    confirmaciones = Column(BigInteger, default=1)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    creador = relationship("Usuario")
    confirmaciones_usuarios = relationship("ConfirmacionUsuario", back_populates="resultado")
    
    __table_args__ = (
        CheckConstraint("estado IN ('pendiente_confirmacion', 'confirmado', 'rechazado')", name='chk_estado_resultado'),
        CheckConstraint("ganador_equipo IN ('equipo1', 'equipo2')", name='chk_ganador_equipo'),
        {'comment': 'Resultados de partidos de pádel con sistema de confirmación'}
    )


class ConfirmacionUsuario(Base):
    """Modelo de Confirmación de Usuario"""
    __tablename__ = "confirmaciones_usuarios"
    
    id_confirmacion = Column(BigInteger, primary_key=True, index=True)
    id_resultado = Column(BigInteger, ForeignKey("resultados_padel.id_resultado", ondelete="CASCADE"), nullable=False)
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    resultado = relationship("ResultadoPadel", back_populates="confirmaciones_usuarios")
    usuario = relationship("Usuario")
    
    __table_args__ = (
        {'comment': 'Confirmaciones de usuarios para resultados de pádel'}
    )
