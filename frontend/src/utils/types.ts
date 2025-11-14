export interface Jugador {
  id: string;
  nombre: string;
}

export interface Equipo {
  jugador1: Jugador;
  jugador2: Jugador;
  puntos: number;
  confirmado: boolean;
  confirmadoPor?: string; // ID del jugador que confirmó
  fechaConfirmacion?: string;
}

export interface Sala {
  id: string;
  nombre: string;
  fecha: string;
  estado: 'activa' | 'finalizada' | 'programada';
  equipoA: Equipo;
  equipoB: Equipo;
  ganador?: 'equipoA' | 'equipoB';
  torneoId?: string;
  creadoPor: string; // ID del usuario que creó la sala
  estadoConfirmacion: 'pendiente' | 'parcial' | 'confirmado' | 'disputado';
  resultadoFinal: boolean; // true cuando ambos equipos confirman
  motivoDisputa?: string;
  createdAt: string;
}

export interface Torneo {
  id: string;
  nombre: string;
  fechaInicio: string;
  fechaFin: string;
  categoria: string;
  formato: 'eliminacion-simple' | 'eliminacion-doble' | 'round-robin' | 'grupos' | 'por-puntos';
  genero: 'masculino' | 'femenino' | 'mixto';
  descripcion: string;
  estado: 'activo' | 'finalizado' | 'programado';
  salasIds: string[];
  participantes: number;
  ganadorId?: string;
  createdAt: string;
}

export interface Usuario {
  id: string;
  nombre: string;
  email: string;
  avatar?: string;
  rol: 'jugador' | 'admin';
  estadisticas: {
    partidosJugados: number;
    partidosGanados: number;
    torneosParticipados: number;
    torneosGanados: number;
  };
  createdAt: string;
}

export interface EstadisticasJugador {
  jugadorId: string;
  nombre: string;
  partidosJugados: number;
  partidosGanados: number;
  partidosPerdidos: number;
  puntosAFavor: number;
  puntosEnContra: number;
  porcentajeVictorias: number;
}
