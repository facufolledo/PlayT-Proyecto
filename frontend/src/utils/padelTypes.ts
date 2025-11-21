// Tipos para el sistema de marcador de pádel

export interface Set {
  gamesEquipoA: number;
  gamesEquipoB: number;
  ganador?: 'equipoA' | 'equipoB';
  completado: boolean;
}

export interface SuperTiebreak {
  puntosEquipoA: number;
  puntosEquipoB: number;
  ganador?: 'equipoA' | 'equipoB';
  completado: boolean;
}

export type FormatoPartido = 'best_of_3' | 'un_set';

export interface ResultadoPartido {
  formato: FormatoPartido;
  sets: Set[];
  supertiebreak?: SuperTiebreak;
  ganador?: 'equipoA' | 'equipoB';
  completado: boolean;
  creadoPor?: string; // ID del usuario que creó el resultado
  confirmadoPor?: string[]; // IDs de usuarios que confirmaron
  reportadoPor?: string[]; // IDs de usuarios que reportaron
}

export type EstadoConfirmacion = 'sin_resultado' | 'pendiente_confirmacion' | 'confirmado' | 'disputado';
