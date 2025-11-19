// Tipos compartidos de la aplicación
// Estos tipos deben coincidir con el backend

export interface Usuario {
  id: string;
  nombre: string;
  apellido: string;
  email: string;
  avatar?: string;
  dni: string;
  fecha_nacimiento: string;
  genero: 'masculino' | 'femenino';
  categoria_inicial: string;
  mano_habil?: 'derecha' | 'zurda';
  posicion_preferida?: 'drive' | 'reves' | 'indiferente';
  telefono?: string;
  ciudad?: string;
  rating: number;
  rol: 'jugador' | 'admin';
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
  participantes: number;
  ganadorId?: string;
  createdAt: string;
}

export interface Sala {
  id: string;
  nombre: string;
  fecha: string;
  estado: 'activa' | 'finalizada' | 'programada';
  categoria: string;
  equipoA: Equipo;
  equipoB: Equipo;
  ganador?: 'equipoA' | 'equipoB';
  torneoId?: string;
  creadoPor: string;
  createdAt: string;
}

export interface Equipo {
  jugador1: Jugador;
  jugador2: Jugador;
  puntos: number;
}

export interface Jugador {
  id: string;
  nombre: string;
}

export interface Ranking {
  id: string;
  nombre: string;
  rating: number;
  partidosJugados: number;
  partidosGanados: number;
  categoria: string;
  genero: 'masculino' | 'femenino';
  tendencia: 'up' | 'down' | 'stable';
  cambioReciente: number;
}

export interface PerfilCompleto {
  nombre: string;
  apellido: string;
  dni: string;
  fecha_nacimiento: string;
  genero: 'masculino' | 'femenino';
  categoria_inicial: string;
  mano_habil?: 'derecha' | 'zurda';
  posicion_preferida?: 'drive' | 'reves' | 'indiferente';
  telefono?: string;
  ciudad?: string;
}
