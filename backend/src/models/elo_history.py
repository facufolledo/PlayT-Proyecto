from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.config import Base

class EloHistory(Base):
    """Modelo para el historial de cambios en el rating Elo"""
    __tablename__ = "elo_history"
    
    # Campos básicos
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)  # Puede ser None si es cambio manual
    
    # Rating Elo
    elo_before = Column(Float, nullable=False)
    elo_after = Column(Float, nullable=False)
    elo_change = Column(Float, nullable=False)
    
    # Información del cambio
    reason = Column(String(100), default="match_result")  # match_result, manual_adjustment, etc.
    description = Column(Text, nullable=True)  # Descripción opcional del cambio
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="elo_history")
    match = relationship("Match")
    
    def __repr__(self):
        return f"<EloHistory(user_id={self.user_id}, elo_change={self.elo_change}, reason='{self.reason}')>"
    
    @property
    def is_positive_change(self):
        """Verificar si el cambio en el rating es positivo"""
        return self.elo_change > 0
    
    @property
    def change_magnitude(self):
        """Obtener la magnitud del cambio (valor absoluto)"""
        return abs(self.elo_change)
