from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from ..database.config import Base


class HistorialEnfrentamiento(Base):
    """Modelo de Historial de Enfrentamientos - Sistema Anti-Trampa"""
    __tablename__ = "historial_enfrentamientos"
    
    id_historial = Column(BigInteger, primary_key=True, index=True)
    id_partido = Column(BigInteger, ForeignKey("partidos.id_partido", ondelete="CASCADE"), nullable=False)
    fecha = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Los 4 jugadores (ordenados por ID)
    jugador1_id = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    jugador2_id = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    jugador3_id = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    jugador4_id = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    
    # Hashes de todas las combinaciones de 3 jugadores
    hash_trio_1 = Column(String(64), nullable=False, index=True)  # jugadores 1,2,3
    hash_trio_2 = Column(String(64), nullable=False, index=True)  # jugadores 1,2,4
    hash_trio_3 = Column(String(64), nullable=False, index=True)  # jugadores 1,3,4
    hash_trio_4 = Column(String(64), nullable=False, index=True)  # jugadores 2,3,4
    
    tipo_partido = Column(String(20), nullable=False)
    elo_aplicado = Column(Boolean, default=False)
    
    # Relaciones
    partido = relationship("Partido")
    jugador1 = relationship("Usuario", foreign_keys=[jugador1_id])
    jugador2 = relationship("Usuario", foreign_keys=[jugador2_id])
    jugador3 = relationship("Usuario", foreign_keys=[jugador3_id])
    jugador4 = relationship("Usuario", foreign_keys=[jugador4_id])
    
    __table_args__ = (
        CheckConstraint(
            """jugador1_id != jugador2_id AND 
               jugador1_id != jugador3_id AND 
               jugador1_id != jugador4_id AND
               jugador2_id != jugador3_id AND 
               jugador2_id != jugador4_id AND 
               jugador3_id != jugador4_id""",
            name='chk_jugadores_diferentes'
        ),
        {'comment': 'Tracking de enfrentamientos para sistema anti-trampa (máx 2 partidos/semana por trío)'}
    )
