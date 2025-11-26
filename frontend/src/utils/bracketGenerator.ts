import { Usuario } from './types';

export interface Partido {
  id: string;
  jugador1?: Usuario;
  jugador2?: Usuario;
  ganador?: Usuario;
  puntos1?: number;
  puntos2?: number;
  ronda: number;
  posicion: number;
  estado: 'pendiente' | 'en-curso' | 'finalizado';
}

export interface Ronda {
  numero: number;
  nombre: string;
  partidos: Partido[];
}

export interface Bracket {
  rondas: Ronda[];
  tipo: 'eliminacion-simple' | 'eliminacion-doble' | 'round-robin' | 'grupos';
}

/**
 * Genera un bracket de eliminación simple
 * @param participantes Lista de usuarios participantes
 * @returns Bracket completo con todas las rondas
 */
export function generarBracketEliminacionSimple(participantes: Usuario[]): Bracket {
  const numParticipantes = participantes.length;
  const numRondas = Math.ceil(Math.log2(numParticipantes));
  const rondas: Ronda[] = [];

  // Nombres de las rondas según el número de participantes
  const nombresRondas = getNombresRondas(numRondas);

  // Primera ronda - emparejar participantes
  const primeraRonda: Partido[] = [];
  for (let i = 0; i < numParticipantes; i += 2) {
    const partido: Partido = {
      id: `r1-p${i / 2}`,
      jugador1: participantes[i],
      jugador2: participantes[i + 1] || undefined, // Puede ser undefined si hay número impar
      ronda: 1,
      posicion: i / 2,
      estado: 'pendiente',
    };

    // Si no hay jugador2, el jugador1 pasa automáticamente (bye)
    if (!partido.jugador2) {
      partido.ganador = partido.jugador1;
      partido.estado = 'finalizado';
    }

    primeraRonda.push(partido);
  }

  rondas.push({
    numero: 1,
    nombre: nombresRondas[0],
    partidos: primeraRonda,
  });

  // Crear rondas siguientes (vacías por ahora)
  let numPartidosRonda = Math.ceil(primeraRonda.length / 2);
  for (let r = 2; r <= numRondas; r++) {
    const partidosRonda: Partido[] = [];
    for (let p = 0; p < numPartidosRonda; p++) {
      partidosRonda.push({
        id: `r${r}-p${p}`,
        ronda: r,
        posicion: p,
        estado: 'pendiente',
      });
    }

    rondas.push({
      numero: r,
      nombre: nombresRondas[r - 1],
      partidos: partidosRonda,
    });

    numPartidosRonda = Math.ceil(numPartidosRonda / 2);
  }

  return {
    rondas,
    tipo: 'eliminacion-simple',
  };
}

/**
 * Avanza al ganador de un partido a la siguiente ronda
 */
export function avanzarGanador(bracket: Bracket, partidoId: string, ganador: Usuario, puntos1: number, puntos2: number): Bracket {
  const nuevoBracket = { ...bracket };
  
  // Encontrar el partido
  for (const ronda of nuevoBracket.rondas) {
    const partido = ronda.partidos.find(p => p.id === partidoId);
    if (partido) {
      // Actualizar partido actual
      partido.ganador = ganador;
      partido.puntos1 = puntos1;
      partido.puntos2 = puntos2;
      partido.estado = 'finalizado';

      // Si no es la última ronda, avanzar a la siguiente
      if (ronda.numero < nuevoBracket.rondas.length) {
        const siguienteRonda = nuevoBracket.rondas[ronda.numero]; // numero es 1-indexed
        const posicionSiguiente = Math.floor(partido.posicion / 2);
        const siguientePartido = siguienteRonda.partidos[posicionSiguiente];

        // Determinar si va como jugador1 o jugador2
        if (partido.posicion % 2 === 0) {
          siguientePartido.jugador1 = ganador;
        } else {
          siguientePartido.jugador2 = ganador;
        }

        // Si ambos jugadores están asignados, el partido está listo
        if (siguientePartido.jugador1 && siguientePartido.jugador2) {
          siguientePartido.estado = 'pendiente';
        }
      }

      break;
    }
  }

  return nuevoBracket;
}

/**
 * Obtiene los nombres de las rondas según el número total
 */
function getNombresRondas(numRondas: number): string[] {
  const nombres: string[] = [];
  
  if (numRondas === 1) return ['Final'];
  if (numRondas === 2) return ['Semifinales', 'Final'];
  if (numRondas === 3) return ['Cuartos de Final', 'Semifinales', 'Final'];
  if (numRondas === 4) return ['Octavos de Final', 'Cuartos de Final', 'Semifinales', 'Final'];
  if (numRondas === 5) return ['Dieciseisavos', 'Octavos de Final', 'Cuartos de Final', 'Semifinales', 'Final'];
  
  // Para más rondas, usar números
  for (let i = 1; i <= numRondas - 3; i++) {
    nombres.push(`Ronda ${i}`);
  }
  nombres.push('Cuartos de Final', 'Semifinales', 'Final');
  
  return nombres;
}

/**
 * Obtiene el campeón del bracket
 */
export function obtenerCampeon(bracket: Bracket): Usuario | null {
  const ultimaRonda = bracket.rondas[bracket.rondas.length - 1];
  const finalPartido = ultimaRonda.partidos[0];
  return finalPartido.ganador || null;
}

/**
 * Calcula el progreso del torneo (% de partidos completados)
 */
export function calcularProgreso(bracket: Bracket): number {
  let totalPartidos = 0;
  let partidosCompletados = 0;

  for (const ronda of bracket.rondas) {
    totalPartidos += ronda.partidos.length;
    partidosCompletados += ronda.partidos.filter(p => p.estado === 'finalizado').length;
  }

  return totalPartidos > 0 ? Math.round((partidosCompletados / totalPartidos) * 100) : 0;
}
