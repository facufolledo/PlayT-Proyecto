from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.config import Base
import enum

class MatchStatus(enum.Enum):
    """Estados posibles de un partido"""
    PENDING = "pending"           # Partido creado, esperando confirmación
    CONFIRMED = "confirmed"       # Partido confirmado por ambos jugadores
    IN_PROGRESS = "in_progress"   # Partido en curso
    COMPLETED = "completed"       # Partido completado
    CANCELLED = "cancelled"       # Partido cancelado

class Match(Base):
    """Modelo de Partido de pádel"""
    __tablename__ = "matches"
    
    # Campos básicos
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=True)  # Título opcional del partido
    description = Column(Text, nullable=True)   # Descripción opcional
    
    # Jugadores
    player1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    player2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Estado del partido
    status = Column(Enum(MatchStatus), default=MatchStatus.PENDING, nullable=False)
    
    # Fecha y lugar
    match_date = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(200), nullable=True)  # Club o lugar del partido
    court_number = Column(String(20), nullable=True)  # Número de cancha
    
    # Resultados
    player1_sets_won = Column(Integer, default=0)  # Sets ganados por jugador 1
    player2_sets_won = Column(Integer, default=0)  # Sets ganados por jugador 2
    
    # Detalles de los sets
    set1_player1_score = Column(Integer, nullable=True)
    set1_player2_score = Column(Integer, nullable=True)
    set2_player1_score = Column(Integer, nullable=True)
    set2_player2_score = Column(Integer, nullable=True)
    set3_player1_score = Column(Integer, nullable=True)
    set3_player2_score = Column(Integer, nullable=True)
    
    # Confirmaciones
    player1_confirmed = Column(Boolean, default=False)
    player2_confirmed = Column(Boolean, default=False)
    
    # Rating Elo antes del partido
    player1_elo_before = Column(Float, nullable=True)
    player2_elo_before = Column(Float, nullable=True)
    
    # Rating Elo después del partido
    player1_elo_after = Column(Float, nullable=True)
    player2_elo_after = Column(Float, nullable=True)
    
    # Cambio en el rating Elo
    player1_elo_change = Column(Float, nullable=True)
    player2_elo_change = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    player1 = relationship("User", foreign_keys=[player1_id], back_populates="matches_as_player1")
    player2 = relationship("User", foreign_keys=[player2_id], back_populates="matches_as_player2")
    
    def __repr__(self):
        return f"<Match(id={self.id}, {self.player1.username} vs {self.player2.username}, status={self.status.value})>"
    
    @property
    def winner_id(self):
        """Obtener el ID del ganador del partido"""
        if self.status != MatchStatus.COMPLETED:
            return None
        
        if self.player1_sets_won > self.player2_sets_won:
            return self.player1_id
        elif self.player2_sets_won > self.player1_sets_won:
            return self.player2_id
        return None  # Empate
    
    @property
    def loser_id(self):
        """Obtener el ID del perdedor del partido"""
        if self.status != MatchStatus.COMPLETED:
            return None
        
        if self.player1_sets_won < self.player2_sets_won:
            return self.player1_id
        elif self.player2_sets_won < self.player1_sets_won:
            return self.player2_id
        return None  # Empate
    
    @property
    def is_confirmed(self):
        """Verificar si ambos jugadores confirmaron el partido"""
        return self.player1_confirmed and self.player2_confirmed
    
    @property
    def total_sets_played(self):
        """Calcular el total de sets jugados"""
        total = 0
        if self.set1_player1_score is not None:
            total += 1
        if self.set2_player1_score is not None:
            total += 1
        if self.set3_player1_score is not None:
            total += 1
        return total
    
    def get_set_score(self, set_number):
        """Obtener el score de un set específico"""
        if set_number == 1:
            return (self.set1_player1_score, self.set1_player2_score)
        elif set_number == 2:
            return (self.set2_player1_score, self.set2_player2_score)
        elif set_number == 3:
            return (self.set3_player1_score, self.set3_player2_score)
        return (None, None)
    
    def set_set_score(self, set_number, player1_score, player2_score):
        """Establecer el score de un set específico"""
        if set_number == 1:
            self.set1_player1_score = player1_score
            self.set1_player2_score = player2_score
        elif set_number == 2:
            self.set2_player1_score = player1_score
            self.set2_player2_score = player2_score
        elif set_number == 3:
            self.set3_player1_score = player1_score
            self.set3_player2_score = player2_score
        
        # Actualizar el conteo de sets ganados
        self._update_sets_won()
    
    def _update_sets_won(self):
        """Actualizar el conteo de sets ganados por cada jugador"""
        self.player1_sets_won = 0
        self.player2_sets_won = 0
        
        # Contar sets ganados
        sets = [
            (self.set1_player1_score, self.set1_player2_score),
            (self.set2_player1_score, self.set2_player2_score),
            (self.set3_player1_score, self.set3_player2_score)
        ]
        
        for player1_score, player2_score in sets:
            if player1_score is not None and player2_score is not None:
                if player1_score > player2_score:
                    self.player1_sets_won += 1
                elif player2_score > player1_score:
                    self.player2_sets_won += 1
