import { createContext, useContext, useState, ReactNode } from 'react';
import { Torneo, Usuario } from '../utils/types';
import { Bracket, generarBracketEliminacionSimple, avanzarGanador } from '../utils/bracketGenerator';
import { logger } from '../utils/logger';

interface TorneosContextType {
  torneos: Torneo[];
  brackets: Map<string, Bracket>;
  addTorneo: (torneo: Omit<Torneo, 'id' | 'createdAt'>) => void;
  updateTorneo: (id: string, torneo: Partial<Torneo>) => void;
  deleteTorneo: (id: string) => void;
  getTorneoById: (id: string) => Torneo | undefined;
  finalizarTorneo: (id: string, ganadorId: string) => void;
  agregarSalaATorneo: (torneoId: string, salaId: string) => void;
  inscribirUsuario: (torneoId: string, usuarioId: string) => void;
  iniciarTorneo: (id: string, participantes: Usuario[]) => void;
  getBracket: (torneoId: string) => Bracket | undefined;
  actualizarPartidoBracket: (torneoId: string, partidoId: string, ganador: Usuario, puntos1: number, puntos2: number) => void;
}

const TorneosContext = createContext<TorneosContextType | undefined>(undefined);

export function TorneosProvider({ children }: { children: ReactNode }) {
  const [torneos, setTorneos] = useState<Torneo[]>([]);
  const [brackets, setBrackets] = useState<Map<string, Bracket>>(new Map());

  const addTorneo = (torneoData: Omit<Torneo, 'id' | 'createdAt'>) => {
    const newTorneo: Torneo = {
      ...torneoData,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
    };
    setTorneos(prev => [newTorneo, ...prev]);
  };

  const updateTorneo = (id: string, torneoData: Partial<Torneo>) => {
    setTorneos(prev => prev.map(torneo => 
      torneo.id === id ? { ...torneo, ...torneoData } : torneo
    ));
  };

  const deleteTorneo = (id: string) => {
    setTorneos(prev => prev.filter(torneo => torneo.id !== id));
  };

  const getTorneoById = (id: string) => {
    return torneos.find(torneo => torneo.id === id);
  };

  const finalizarTorneo = (id: string, ganadorId: string) => {
    setTorneos(prev => prev.map(torneo => {
      if (torneo.id === id) {
        return {
          ...torneo,
          estado: 'finalizado' as const,
          ganadorId
        };
      }
      return torneo;
    }));
  };

  const agregarSalaATorneo = (torneoId: string, salaId: string) => {
    setTorneos(prev => prev.map(torneo => {
      if (torneo.id === torneoId) {
        return {
          ...torneo,
          salasIds: [...torneo.salasIds, salaId]
        };
      }
      return torneo;
    }));
  };

  const inscribirUsuario = (torneoId: string, usuarioId: string) => {
    // TODO: Implementar lógica de inscripción cuando tengamos el modelo extendido
    logger.log('Usuario inscrito:', usuarioId, 'al torneo:', torneoId);
  };

  const iniciarTorneo = (id: string, participantes: Usuario[]) => {
    // Generar bracket según el formato
    const torneo = getTorneoById(id);
    if (!torneo) return;

    let bracket: Bracket;
    if (torneo.formato === 'eliminacion-simple') {
      bracket = generarBracketEliminacionSimple(participantes);
    } else {
      // TODO: Implementar otros formatos
      bracket = generarBracketEliminacionSimple(participantes);
    }

    // Guardar bracket
    setBrackets(prev => new Map(prev).set(id, bracket));

    // Actualizar estado del torneo
    setTorneos(prev => prev.map(t => {
      if (t.id === id) {
        return {
          ...t,
          estado: 'activo' as const
        };
      }
      return t;
    }));
  };

  const getBracket = (torneoId: string): Bracket | undefined => {
    return brackets.get(torneoId);
  };

  const actualizarPartidoBracket = (torneoId: string, partidoId: string, ganador: Usuario, puntos1: number, puntos2: number) => {
    const bracket = brackets.get(torneoId);
    if (!bracket) return;

    const nuevoBracket = avanzarGanador(bracket, partidoId, ganador, puntos1, puntos2);
    setBrackets(prev => new Map(prev).set(torneoId, nuevoBracket));
  };

  return (
    <TorneosContext.Provider value={{
      torneos,
      brackets,
      addTorneo,
      updateTorneo,
      deleteTorneo,
      getTorneoById,
      finalizarTorneo,
      agregarSalaATorneo,
      inscribirUsuario,
      iniciarTorneo,
      getBracket,
      actualizarPartidoBracket
    }}>
      {children}
    </TorneosContext.Provider>
  );
}

export function useTorneos() {
  const context = useContext(TorneosContext);
  if (!context) {
    throw new Error('useTorneos debe usarse dentro de TorneosProvider');
  }
  return context;
}
