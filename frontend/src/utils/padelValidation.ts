// Utilidades de validación para reglas de pádel

import { Set, SuperTiebreak } from './padelTypes';

/**
 * Valida si un set es válido según las reglas de pádel
 * Casos válidos:
 * - 6-0, 6-1, 6-2, 6-3, 6-4 (ventaja de 2+ games)
 * - 7-5 (ventaja de 2 games)
 * - 7-6 (tiebreak)
 */
export function validarSet(gamesA: number, gamesB: number): boolean {
  const diff = Math.abs(gamesA - gamesB);
  const max = Math.max(gamesA, gamesB);
  const min = Math.min(gamesA, gamesB);
  
  // Casos inválidos básicos
  if (max > 7 || min < 0) return false;
  
  // Set a 6 games con ventaja de 2+
  if (max === 6) return diff >= 2;
  
  // Set a 7 games (7-5 o 7-6)
  if (max === 7) return min === 5 || min === 6;
  
  return false;
}

/**
 * Verifica si un set está completo
 */
export function setCompleto(gamesA: number, gamesB: number): boolean {
  const max = Math.max(gamesA, gamesB);
  const diff = Math.abs(gamesA - gamesB);
  
  // Set terminado a 6 con ventaja de 2+
  if (max === 6 && diff >= 2) return true;
  
  // Set terminado a 7 (7-5 o 7-6)
  if (max === 7) return true;
  
  return false;
}

/**
 * Verifica si se debe jugar tiebreak (6-6)
 */
export function requiereTiebreak(gamesA: number, gamesB: number): boolean {
  return gamesA === 6 && gamesB === 6;
}

/**
 * Valida si un supertiebreak es válido
 * Reglas:
 * - Gana el primero en llegar a 10 puntos
 * - Si ambos llegan a 9 o más, se requiere diferencia de 2 puntos
 * - Ejemplos válidos: 10-0, 10-5, 10-8, 11-9, 13-11, 15-13
 */
export function validarSuperTiebreak(puntosA: number, puntosB: number): boolean {
  const diff = Math.abs(puntosA - puntosB);
  const max = Math.max(puntosA, puntosB);
  const min = Math.min(puntosA, puntosB);
  
  // Casos inválidos básicos
  if (min < 0) return false;
  
  // Debe llegar a 10 como mínimo
  if (max < 10) return false;
  
  // Si el máximo es 10
  if (max === 10) {
    // Si el mínimo es 9, necesita diferencia de 2 (sería 11-9)
    if (min >= 9) return false;
    // Cualquier otro resultado es válido: 10-0, 10-1, ..., 10-8
    return true;
  }
  
  // Si el máximo es mayor a 10, debe haber ventaja de exactamente 2
  if (max > 10) return diff === 2;
  
  return true;
}

/**
 * Verifica si un supertiebreak está completo
 */
export function supertiebreakCompleto(puntosA: number, puntosB: number): boolean {
  const diff = Math.abs(puntosA - puntosB);
  const max = Math.max(puntosA, puntosB);
  const min = Math.min(puntosA, puntosB);
  
  // Si alguien llegó a 10 y el otro tiene menos de 9, está completo
  if (max === 10 && min < 9) return true;
  
  // Si alguien tiene más de 10, debe haber diferencia de 2
  if (max > 10 && diff >= 2) return true;
  
  return false;
}

/**
 * Determina el ganador de un set
 */
export function ganadorSet(gamesA: number, gamesB: number): 'equipoA' | 'equipoB' | null {
  if (!setCompleto(gamesA, gamesB)) return null;
  return gamesA > gamesB ? 'equipoA' : 'equipoB';
}

/**
 * Determina el ganador de un supertiebreak
 */
export function ganadorSuperTiebreak(puntosA: number, puntosB: number): 'equipoA' | 'equipoB' | null {
  if (!supertiebreakCompleto(puntosA, puntosB)) return null;
  return puntosA > puntosB ? 'equipoA' : 'equipoB';
}

/**
 * Cuenta los sets ganados por cada equipo
 */
export function contarSetsGanados(sets: Set[]): { equipoA: number; equipoB: number } {
  return sets.reduce(
    (acc, set) => {
      if (set.ganador === 'equipoA') acc.equipoA++;
      if (set.ganador === 'equipoB') acc.equipoB++;
      return acc;
    },
    { equipoA: 0, equipoB: 0 }
  );
}

/**
 * Determina si se debe jugar supertiebreak (1-1 en sets)
 */
export function requiereSuperTiebreak(sets: Set[]): boolean {
  const setsGanados = contarSetsGanados(sets);
  return setsGanados.equipoA === 1 && setsGanados.equipoB === 1;
}

/**
 * Valida si se puede incrementar un game
 * NOTA: Permitimos incrementar libremente para facilitar la carga de resultados.
 * La validación final se hace al guardar el resultado.
 */
export function puedeIncrementarGame(gamesA: number, gamesB: number): { equipoA: boolean; equipoB: boolean } {
  // Permitir incrementar libremente hasta 7 para facilitar la carga
  // Esto permite cargar primero los games de un equipo y luego del otro
  // Ejemplo: cargar 6-0, luego modificar a 6-4
  const puedeA = gamesA < 7;
  const puedeB = gamesB < 7;
  
  return { equipoA: puedeA, equipoB: puedeB };
}

/**
 * Valida si se puede incrementar un punto en supertiebreak
 */
export function puedeIncrementarPunto(puntosA: number, puntosB: number): { equipoA: boolean; equipoB: boolean } {
  // Si el supertiebreak ya está completo, no se puede incrementar
  if (supertiebreakCompleto(puntosA, puntosB)) {
    return { equipoA: false, equipoB: false };
  }
  
  return { equipoA: true, equipoB: true };
}

/**
 * Mensajes de error para validaciones
 */
export function obtenerMensajeError(tipo: 'set' | 'supertiebreak', gamesA: number, gamesB: number): string {
  if (tipo === 'set') {
    if (gamesA > 7 || gamesB > 7) {
      return 'Un set no puede tener más de 7 games';
    }
    if (gamesA === 6 && gamesB === 6) {
      return 'En 6-6 se debe jugar tiebreak (resultado 7-6)';
    }
    const max = Math.max(gamesA, gamesB);
    const diff = Math.abs(gamesA - gamesB);
    if (max === 6 && diff < 2) {
      return 'Para ganar 6 games, debe haber ventaja de 2 o más';
    }
    if (max === 7 && (gamesB !== 5 && gamesB !== 6) && (gamesA !== 5 && gamesA !== 6)) {
      return 'Un set a 7 games solo puede ser 7-5 o 7-6';
    }
  } else {
    const max = Math.max(gamesA, gamesB);
    const min = Math.min(gamesA, gamesB);
    const diff = Math.abs(gamesA - gamesB);
    
    if (max < 10) {
      return 'El supertiebreak debe llegar a 10 puntos';
    }
    if (max === 10 && min >= 9) {
      return 'Con 10-9 el supertiebreak continúa (debe haber diferencia de 2)';
    }
    if (max > 10 && diff !== 2) {
      return 'El supertiebreak extendido requiere diferencia de exactamente 2 puntos';
    }
  }
  return 'Resultado inválido';
}
