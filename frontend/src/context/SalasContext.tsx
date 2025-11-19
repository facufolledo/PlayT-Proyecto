import { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { Sala, Jugador } from '../utils/types';
import { salaService, SalaCompleta } from '../services/sala.service';
import { useAuth } from './AuthContext';
import { logger } from '../utils/logger';

interface SalasContextType {
  salas: Sala[];
  loading: boolean;
  error: string | null;
  addSala: (sala: Omit<Sala, 'id' | 'createdAt'>) => Promise<string>;
  updateSala: (id: string, sala: Partial<Sala>) => void;
  deleteSala: (id: string) => void;
  getSalaById: (id: string) => Sala | undefined;
  unirseASala: (codigo: string) => Promise<void>;
  asignarEquipos: (id: string, equipo1Ids: string[], equipo2Ids: string[]) => Promise<void>;
  updateMarcador: (id: string, equipo: 'equipoA' | 'equipoB', puntos: number) => void;
  finalizarPartido: (id: string, sets: { equipoA: number; equipoB: number }[]) => void;
  confirmarResultado: (id: string, equipo: 'equipoA' | 'equipoB', jugadorId: string) => void;
  disputarResultado: (id: string, motivo: string) => void;
  getSalasPendientesConfirmacion: (jugadorId: string) => Sala[];
  recargarSalas: () => Promise<void>;
}

const SalasContext = createContext<SalasContextType | undefined>(undefined);

// Función para convertir sala del backend al formato del frontend
function convertirSalaBackendAFrontend(salaBackend: SalaCompleta): Sala {
  const jugadores: Jugador[] = salaBackend.jugadores.map(j => ({
    id: j.id_usuario.toString(),
    nombre: j.nombre || j.nombre_usuario,
    rating: j.rating,
    esCreador: j.id_usuario === salaBackend.id_creador
  }));

  // Separar jugadores por equipo
  const jugadoresEquipo1 = salaBackend.jugadores.filter(j => j.equipo === 1);
  const jugadoresEquipo2 = salaBackend.jugadores.filter(j => j.equipo === 2);

  return {
    id: salaBackend.id_sala,
    nombre: salaBackend.nombre,
    fecha: salaBackend.fecha,
    estado: salaBackend.estado as any,
    codigoInvitacion: salaBackend.codigo_invitacion,
    jugadores: jugadores,
    equiposAsignados: jugadoresEquipo1.length > 0 && jugadoresEquipo2.length > 0,
    creadoPor: salaBackend.id_creador.toString(),
    estadoConfirmacion: 'pendiente',
    resultadoFinal: false,
    createdAt: salaBackend.creado_en,
    equipoA: {
      jugador1: jugadoresEquipo1[0] ? {
        id: jugadoresEquipo1[0].id_usuario.toString(),
        nombre: jugadoresEquipo1[0].nombre || jugadoresEquipo1[0].nombre_usuario
      } : { id: '', nombre: '' },
      jugador2: jugadoresEquipo1[1] ? {
        id: jugadoresEquipo1[1].id_usuario.toString(),
        nombre: jugadoresEquipo1[1].nombre || jugadoresEquipo1[1].nombre_usuario
      } : { id: '', nombre: '' },
      puntos: 0,
      confirmado: false
    },
    equipoB: {
      jugador1: jugadoresEquipo2[0] ? {
        id: jugadoresEquipo2[0].id_usuario.toString(),
        nombre: jugadoresEquipo2[0].nombre || jugadoresEquipo2[0].nombre_usuario
      } : { id: '', nombre: '' },
      jugador2: jugadoresEquipo2[1] ? {
        id: jugadoresEquipo2[1].id_usuario.toString(),
        nombre: jugadoresEquipo2[1].nombre || jugadoresEquipo2[1].nombre_usuario
      } : { id: '', nombre: '' },
      puntos: 0,
      confirmado: false
    }
  };
}

export function SalasProvider({ children }: { children: ReactNode }) {
  const [salas, setSalas] = useState<Sala[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { usuario } = useAuth();

  // Cargar salas al montar el componente
  useEffect(() => {
    if (usuario) {
      logger.log('Usuario autenticado, cargando salas...');
      recargarSalas();
    } else {
      logger.log('Usuario no autenticado, no se cargan salas');
      setSalas([]);
      setLoading(false);
    }
  }, [usuario]);

  // Recargar salas desde el backend
  const recargarSalas = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const salasBackend = await salaService.listarSalas();
      const salasConvertidas = salasBackend.map(convertirSalaBackendAFrontend);
      
      setSalas(salasConvertidas);
      logger.log('Salas cargadas:', salasConvertidas.length);
    } catch (err: any) {
      const errorMsg = err.message || 'Error al cargar salas';
      setError(errorMsg);
      logger.error('Error al cargar salas:', err);
      
      // Si hay error, mostrar array vacío en lugar de quedarse cargando
      setSalas([]);
    } finally {
      setLoading(false);
    }
  };

  const addSala = async (salaData: Omit<Sala, 'id' | 'createdAt'>): Promise<string> => {
    try {
      setLoading(true);
      setError(null);
      
      // Crear sala en el backend
      const salaCreada = await salaService.crearSala({
        nombre: salaData.nombre,
        fecha: salaData.fecha,
        max_jugadores: 4
      });
      
      logger.log('Sala creada en backend:', salaCreada);
      
      // Recargar salas
      await recargarSalas();
      
      return salaCreada.codigo_invitacion;
    } catch (err: any) {
      setError(err.message);
      logger.error('Error al crear sala:', err);
      throw err;
    } finally {
      setLoading(false);
    }
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

  const unirseASala = async (codigo: string): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      // Unirse a la sala en el backend
      await salaService.unirseASala(codigo);
      
      logger.log('Unido a sala con código:', codigo);
      
      // Recargar salas
      await recargarSalas();
    } catch (err: any) {
      setError(err.message);
      logger.error('Error al unirse a sala:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const asignarEquipos = async (id: string, equipo1Ids: string[], equipo2Ids: string[]): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      // Crear objeto de equipos para el backend
      const equipos: { [key: string]: number } = {};
      equipo1Ids.forEach(jugadorId => {
        equipos[jugadorId] = 1;
      });
      equipo2Ids.forEach(jugadorId => {
        equipos[jugadorId] = 2;
      });
      
      // Asignar equipos en el backend
      await salaService.asignarEquipos(parseInt(id), equipos);
      
      logger.log('Equipos asignados en backend');
      
      // Recargar salas
      await recargarSalas();
    } catch (err: any) {
      setError(err.message);
      logger.error('Error al asignar equipos:', err);
      throw err;
    } finally {
      setLoading(false);
    }
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

  const finalizarPartido = (id: string, sets: { equipoA: number; equipoB: number }[]) => {
    setSalas(prev => prev.map(sala => {
      if (sala.id === id) {
        const ganador = sala.equipoA.puntos > sala.equipoB.puntos ? 'equipoA' : 'equipoB';
        return {
          ...sala,
          estado: 'finalizada' as const,
          sets,
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
      loading,
      error,
      addSala,
      updateSala,
      deleteSala,
      getSalaById,
      unirseASala,
      asignarEquipos,
      updateMarcador,
      finalizarPartido,
      confirmarResultado,
      disputarResultado,
      getSalasPendientesConfirmacion,
      recargarSalas
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
