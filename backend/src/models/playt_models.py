from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Float, Text, ForeignKey, BigInteger, SmallInteger, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database.config import Base

class Usuario(Base):
    """Modelo de Usuario basado en tu tabla 'usuarios'"""
    __tablename__ = "usuarios"
    
    id_usuario = Column(BigInteger, primary_key=True, index=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    rating = Column(Integer, default=1200)
    partidos_jugados = Column(Integer, default=0)
    id_categoria = Column(BigInteger, ForeignKey("categorias.id_categoria"), nullable=True)
    avatar_url = Column(Text, nullable=True)
    sexo = Column(String(10), nullable=True)
    fcm_token = Column(String(255), nullable=True)
    puede_crear_torneos = Column(Boolean, default=False)
    es_administrador = Column(Boolean, default=False)
    
    # Relaciones
    historial_rating = relationship("HistorialRating", back_populates="usuario")
    checkpoints_categoria = relationship("CategoriaCheckpoint")
    perfil = relationship("PerfilUsuario", back_populates="usuario", uselist=False)
    partidos_creados = relationship("Partido", back_populates="creador", foreign_keys="Partido.id_creador")
    partidos_jugados_rel = relationship("PartidoJugador", back_populates="usuario")

class PerfilUsuario(Base):
    """Modelo de Perfil de Usuario basado en tu tabla 'perfil_usuarios'"""
    __tablename__ = "perfil_usuarios"
    
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario"), primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    ciudad = Column(String(100), nullable=True)
    pais = Column(String(100), nullable=True)
    url_avatar = Column(Text, nullable=True)
    id_categoria_inicial = Column(BigInteger, ForeignKey("categorias.id_categoria"), nullable=True)
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Campos adicionales para perfil completo
    dni = Column(String(20), nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    telefono = Column(String(20), nullable=True)
    mano_habil = Column(String(10), nullable=True)  # 'derecha' o 'zurda'
    posicion_preferida = Column(String(15), nullable=True)  # 'drive', 'reves', 'indiferente'
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="perfil")
    categoria_inicial = relationship("Categoria")

class Categoria(Base):
    """Modelo de Categoría basado en tu tabla 'categorias'"""
    __tablename__ = "categorias"
    
    id_categoria = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(20), nullable=False)
    descripcion = Column(String(255), nullable=True)
    rating_min = Column(Integer, nullable=True)
    rating_max = Column(Integer, nullable=True)
    sexo = Column(String(10), default="masculino", nullable=False)  # "masculino" o "femenino"
    
    # Índice único compuesto para nombre + sexo
    __table_args__ = (
        {'extend_existing': True}
    )

class Club(Base):
    """Modelo de Club basado en tu tabla 'clubes'"""
    __tablename__ = "clubes"
    
    id_club = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    ciudad = Column(String(100), nullable=True)
    pais = Column(String(10), nullable=True)
    
    # Relaciones
    partidos = relationship("Partido", back_populates="club")

class Partido(Base):
    """Modelo de Partido basado en tu tabla 'partidos'"""
    __tablename__ = "partidos"
    
    id_partido = Column(BigInteger, primary_key=True, index=True)
    id_club = Column(BigInteger, ForeignKey("clubes.id_club"), nullable=True)
    fecha = Column(DateTime(timezone=True), nullable=False)
    estado = Column(String(12), default="pendiente", nullable=False)
    id_creador = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Nuevos campos para sistema de marcador
    tipo = Column(String(20), default="amistoso", nullable=False)  # amistoso, torneo, ranking
    id_torneo = Column(BigInteger, nullable=True)  # ForeignKey a torneos cuando exista
    id_sala = Column(BigInteger, ForeignKey("salas.id_sala"), nullable=True)
    resultado_padel = Column(JSON, nullable=True)  # Resultado completo en formato JSON
    estado_confirmacion = Column(String(30), default="sin_resultado", nullable=False)
    ganador_equipo = Column(SmallInteger, nullable=True)  # 1 o 2
    elo_aplicado = Column(Boolean, default=False, nullable=False)
    creado_por = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=True)
    
    # Relaciones
    club = relationship("Club", back_populates="partidos")
    creador = relationship("Usuario", back_populates="partidos_creados", foreign_keys=[id_creador])
    jugadores = relationship("PartidoJugador", back_populates="partido")
    resultado = relationship("ResultadoPartido", back_populates="partido", uselist=False)
    historial_rating = relationship("HistorialRating", back_populates="partido")
    eventos = relationship("EventoPartido", back_populates="partido")
    confirmaciones = relationship("Confirmacion", back_populates="partido")

class PartidoJugador(Base):
    """Modelo de Jugador por Partido basado en tu tabla 'partido_jugadores'"""
    __tablename__ = "partido_jugadores"
    
    id_partido = Column(BigInteger, ForeignKey("partidos.id_partido"), primary_key=True)
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario"), primary_key=True)
    equipo = Column(SmallInteger, nullable=False)  # 1 o 2
    
    # Nuevos campos para tracking de Elo
    rating_antes = Column(Integer, nullable=True)
    rating_despues = Column(Integer, nullable=True)
    cambio_elo = Column(Integer, nullable=True)
    
    # Relaciones
    partido = relationship("Partido", back_populates="jugadores")
    usuario = relationship("Usuario", back_populates="partidos_jugados_rel")

class ResultadoPartido(Base):
    """Modelo de Resultado de Partido basado en tu tabla 'resultados_partidos'"""
    __tablename__ = "resultados_partidos"
    
    id_partido = Column(BigInteger, ForeignKey("partidos.id_partido"), primary_key=True)
    id_reportador = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=False)
    sets_eq1 = Column(SmallInteger, nullable=False)
    sets_eq2 = Column(SmallInteger, nullable=False)
    detalle_sets = Column(JSON, nullable=False)  # JSON con detalles de cada set
    confirmado = Column(Boolean, default=False, nullable=False)
    desenlace = Column(String(10), default="normal", nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    partido = relationship("Partido", back_populates="resultado")
    reportador = relationship("Usuario")

class HistorialRating(Base):
    """Modelo de Historial de Rating basado en tu tabla 'historial_rating'"""
    __tablename__ = "historial_rating"
    
    id_historial = Column(BigInteger, primary_key=True, index=True)
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=False)
    id_partido = Column(BigInteger, ForeignKey("partidos.id_partido"), nullable=False)
    rating_antes = Column(Integer, nullable=False)
    delta = Column(Integer, nullable=False)
    rating_despues = Column(Integer, nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="historial_rating")
    partido = relationship("Partido", back_populates="historial_rating")

class EventoPartido(Base):
    """Modelo de Evento de Partido basado en tu tabla 'eventos_partido'"""
    __tablename__ = "eventos_partido"
    
    id_evento = Column(BigInteger, primary_key=True, index=True)
    id_partido = Column(BigInteger, ForeignKey("partidos.id_partido"), nullable=False)
    id_usuario_actor = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=True)
    tipo = Column(String(16), nullable=False)
    meta = Column(JSON, nullable=True)  # JSON con metadatos del evento
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    partido = relationship("Partido", back_populates="eventos")
    usuario_actor = relationship("Usuario")

class FlagSospechoso(Base):
    """Modelo de Flag Sospechoso basado en tu tabla 'flags_sospechosos'"""
    __tablename__ = "flags_sospechosos"
    
    id_flag = Column(BigInteger, primary_key=True, index=True)
    id_partido = Column(BigInteger, ForeignKey("partidos.id_partido"), nullable=False)
    motivo = Column(String(64), nullable=False)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    partido = relationship("Partido")


class CategoriaCheckpoint(Base):
    """Modelo de Checkpoint de Categoría para tracking de ascensos"""
    __tablename__ = "categoria_checkpoints"
    
    id_checkpoint = Column(BigInteger, primary_key=True, index=True)
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario"), nullable=False)
    categoria_anterior = Column(String(20), nullable=True)
    categoria_nueva = Column(String(20), nullable=False)
    rating_ascenso = Column(Integer, nullable=False)
    fecha_ascenso = Column(DateTime(timezone=True), server_default=func.now())
    id_partido_ascenso = Column(BigInteger, ForeignKey("partidos.id_partido"), nullable=True)
    partidos_inmunidad_restantes = Column(SmallInteger, default=0)
    
    # Relaciones
    usuario = relationship("Usuario", overlaps="checkpoints_categoria")
    partido_ascenso = relationship("Partido")