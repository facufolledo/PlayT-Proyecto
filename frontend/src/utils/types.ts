export interface Jugador {
  id: string;
  nombre: string;
  rating?: number;
  esCreador?: boolean;
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
  estado: 'esperando' | 'activa' | 'en_juego' | 'finalizada' | 'programada';
  codigoInvitacion?: string;
  jugadores?: Jugador[];
  equiposAsignados?: boolean;
  equipoA: Equipo;
  equipoB: Equipo;
  sets?: any[]; // Set[] from padelTypes
  ganador?: 'equipoA' | 'equipoB';
  torneoId?: string;
  creadoPor: string;
  creador_id?: string | number; // ID del creador para comparación
  estadoConfirmacion?: 'sin_resultado' | 'pendiente_confirmacion' | 'confirmado' | 'disputado';
  resultado?: any; // ResultadoPartido from padelTypes
  resultadoFinal?: boolean;
  motivoDisputa?: string;
  formato?: 'best_of_3' | 'best_of_3_supertiebreak';
  cambiosElo?: Array<{
    id_usuario: number;
    rating_antes: number;
    rating_despues: number;
    cambio_elo: number;
  }>;
  eloAplicado?: boolean;
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
