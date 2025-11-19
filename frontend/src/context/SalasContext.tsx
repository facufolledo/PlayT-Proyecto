import { createContext, useContext, useState, ReactNode } from 'react';
import { Sala } from '../utils/types';

interface SalasContextType {
  salas: Sala[];
  addSala: (sala: Omit<Sala, 'id' | 'createdAt'>) => void;
  updateSala: (id: string, sala: Partial<Sala>) => void;
  deleteSala: (id: string) => void;
  getSalaById: (id: string) => Sala | undefined;
  updateMarcador: (id: string, equipo: 'equipoA' | 'equipoB', puntos: number) => void;
  finalizarPartido: (id: string) => void;
  confirmarResultado: (id: string, equipo: 'equipoA' | 'equipoB', jugadorId: string) => void;
  disputarResultado: (id: string, motivo: string) => void;
  getSalasPendientesConfirmacion: (jugadorId: string) => Sala[];
}

const SalasContext = createContext<SalasContextType | undefined>(undefined);

export function SalasProvider({ children }: { children: ReactNode }) {
  const [salas, setSalas] = useState<Sala[]>([]);

  const addSala = (salaData: Omit<Sala, 'id' | 'createdAt'>) => {
    const newSala: Sala = {
      ...salaData,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
    };
    setSalas(prev => [newSala, ...prev]);
  };

  const updateSala = (id: string, salaData: Partial<Sala>) => {
    setSalas(prev => prev.map(sala => 
      sala.id === id ? { ...sala, ...salaData } : sala
    ));
  };

  const deleteSala = (id: string) => {
    setSalas(prev => prev.filter(sala => sala.id !== id));
  };

  const getSalaById = (id: string) => {
    return salas.find(sala => sala.id === id);
  };

  const updateMarcador = (id: string, equipo: 'equipoA' | 'equipoB', puntos: number) => {
    setSalas(prev => prev.map(sala => {
      if (sala.id === id) {
        return {
          ...sala,
          [equipo]: {
            ...sala[equipo],
            puntos
          }
        };
      }
      return sala;
    }));
  };

  const finalizarPartido = (id: string) => {
    setSalas(prev => prev.map(sala => {
      if (sala.id === id) {
        const ganador = sala.equipoA.puntos > sala.equipoB.puntos ? 'equipoA' : 'equipoB';
        return {
          ...sala,
          estado: 'finalizada' as const,
          ganador,
          estadoConfirmacion: 'pendiente' as const,
          resultadoFinal: false
        };
      }
      return sala;
    }));
  };

  const confirmarResultado = (id: string, equipo: 'equipoA' | 'equipoB', jugadorId: string) => {
    setSalas(prev => prev.map(sala => {
      if (sala.id === id) {
        const equipoActualizado = {
          ...sala[equipo],
          confirmado: true,
          confirmadoPor: jugadorId,
          fechaConfirmacion: new Date().toISOString()
        };

        const otroEquipo = equipo === 'equipoA' ? 'equipoB' : 'equipoA';
        const ambosConfirmados = equipoActualizado.confirmado && sala[otroEquipo].confirmado;

        return {
          ...sala,
          [equipo]: equipoActualizado,
          estadoConfirmacion: ambosConfirmados ? 'confirmado' as const : 'parcial' as const,
          resultadoFinal: ambosConfirmados
        };
      }
      return sala;
    }));
  };

  const disputarResultado = (id: string, motivo: string) => {
    setSalas(prev => prev.map(sala => {
      if (sala.id === id) {
        return {
          ...sala,
          estadoConfirmacion: 'disputado' as const,
          motivoDisputa: motivo
        };
      }
      return sala;
    }));
  };

  const getSalasPendientesConfirmacion = (jugadorId: string) => {
    return salas.filter(sala => {
      if (sala.estado !== 'finalizada' || sala.resultadoFinal) return false;
      
      // Verificar si el jugador está en alguno de los equipos
      const estaEnEquipoA = 
        sala.equipoA.jugador1.id === jugadorId || 
        sala.equipoA.jugador2.id === jugadorId;
      const estaEnEquipoB = 
        sala.equipoB.jugador1.id === jugadorId || 
        sala.equipoB.jugador2.id === jugadorId;

      // Si está en equipo A y no ha confirmado
      if (estaEnEquipoA && !sala.equipoA.confirmado) return true;
      // Si está en equipo B y no ha confirmado
      if (estaEnEquipoB && !sala.equipoB.confirmado) return true;

      return false;
    });
  };

  return (
    <SalasContext.Provider value={{
      salas,
      addSala,
      updateSala,
      deleteSala,
      getSalaById,
      updateMarcador,
      finalizarPartido,
      confirmarResultado,
      disputarResultado,
      getSalasPendientesConfirmacion
    }}>
      {children}
    </SalasContext.Provider>
  );
}

export function useSalas() {
  const context = useContext(SalasContext);
  if (!context) {
    throw new Error('useSalas debe usarse dentro de SalasProvider');
  }
  return context;
}
