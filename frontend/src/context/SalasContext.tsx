import { createContext, useContext, useState, ReactNode } from 'react';
import { Sala } from '../utils/types';
import { salaService, SalaCompleta } from '../services/sala.service';
import { logger } from '../utils/logger';

interface SalasContextType {
  salas: Sala[];
  addSala: (sala: Omit<Sala, 'id' | 'createdAt'>) => Promise<string>;
  updateSala: (id: string, sala: Partial<Sala>) => void;
  deleteSala: (id: string) => Promise<void>;
  getSalaById: (id: string) => Sala | undefined;
  updateMarcador: (id: string, equipo: 'equipoA' | 'equipoB', puntos: number) => void;
  finalizarPartido: (id: string) => void;
  confirmarResultado: (id: string, equipo: 'equipoA' | 'equipoB', jugadorId: string) => void;
  disputarResultado: (id: string, motivo: string) => void;
  getSalasPendientesConfirmacion: (jugadorId: string) => Sala[];
  cargarSalas: () => Promise<void>;
  loading: boolean;
}

const SalasContext = createContext<SalasContextType | undefined>(undefined);

// Función para convertir SalaCompleta del backend a Sala del frontend
function convertirSalaBackendAFrontend(salaBackend: SalaCompleta): Sala {
  console.log('🔍 Convirtiendo sala:', salaBackend);
  const jugadores = salaBackend.jugadores || [];
  console.log('👥 Jugadores:', jugadores);
  
  // Separar jugadores por equipo (solo si tienen equipo asignado)
  const equipoA = jugadores.filter(j => j.equipo === 1);
  const equipoB = jugadores.filter(j => j.equipo === 2);
  const hayEquiposAsignados = equipoA.length > 0 && equipoB.length > 0;
  
  return {
    id: salaBackend.id_sala,
    nombre: salaBackend.nombre,
    fecha: salaBackend.fecha,
    estado: salaBackend.estado as any,
    codigoInvitacion: salaBackend.codigo_invitacion,
    jugadores: jugadores.map(j => ({
      id: (j.id || j.id_usuario)?.toString() || '',
      nombre: j.nombre || j.nombre_usuario || `${j.nombre} ${j.apellido}`.trim() || 'Usuario',
      rating: j.rating || 1500,
      esCreador: j.esCreador || (j.id_usuario === salaBackend.id_creador) || (j.id === salaBackend.id_creador?.toString())
    })),
    equiposAsignados: hayEquiposAsignados,
    equipoA: {
      jugador1: equipoA[0] ? {
        id: (equipoA[0].id || equipoA[0].id_usuario)?.toString() || '',
        nombre: equipoA[0].nombre || equipoA[0].nombre_usuario || `${equipoA[0].nombre} ${equipoA[0].apellido}` || 'Usuario',
        rating: equipoA[0].rating || 1500
      } : { id: '', nombre: '' },
      jugador2: equipoA[1] ? {
        id: (equipoA[1].id || equipoA[1].id_usuario)?.toString() || '',
        nombre: equipoA[1].nombre || equipoA[1].nombre_usuario || `${equipoA[1].nombre} ${equipoA[1].apellido}` || 'Usuario',
        rating: equipoA[1].rating || 1500
      } : { id: '', nombre: '' },
      puntos: 0,
      confirmado: false
    },
    equipoB: {
      jugador1: equipoB[0] ? {
        id: (equipoB[0].id || equipoB[0].id_usuario)?.toString() || '',
        nombre: equipoB[0].nombre || equipoB[0].nombre_usuario || `${equipoB[0].nombre} ${equipoB[0].apellido}` || 'Usuario',
        rating: equipoB[0].rating || 1500
      } : { id: '', nombre: '' },
      jugador2: equipoB[1] ? {
        id: (equipoB[1].id || equipoB[1].id_usuario)?.toString() || '',
        nombre: equipoB[1].nombre || equipoB[1].nombre_usuario || `${equipoB[1].nombre} ${equipoB[1].apellido}` || 'Usuario',
        rating: equipoB[1].rating || 1500
      } : { id: '', nombre: '' },
      puntos: 0,
      confirmado: false
    },
    creadoPor: salaBackend.id_creador?.toString() || '',
    creador_id: salaBackend.id_creador,
    estadoConfirmacion: (salaBackend.estado_confirmacion as any) || 'sin_resultado',
    resultado: salaBackend.resultado,
    cambiosElo: salaBackend.cambios_elo,
    eloAplicado: salaBackend.elo_aplicado,
    formato: 'best_of_3',
    createdAt: salaBackend.creado_en
  };
}

export function SalasProvider({ children }: { children: ReactNode }) {
  const [salas, setSalas] = useState<Sala[]>([]);
  const [loading, setLoading] = useState(false);

  // Cargar salas del backend
  const cargarSalas = async () => {
    try {
      setLoading(true);
      const salasBackend = await salaService.listarSalas();
      const salasConvertidas = salasBackend.map(convertirSalaBackendAFrontend);
      setSalas(salasConvertidas);
    } catch (error: any) {
      logger.error('Error al cargar salas:', error);
      // No hacer nada más, simplemente fallar silenciosamente
    } finally {
      setLoading(false);
    }
  };

  // NO cargar salas automáticamente al montar
  // Las páginas que necesiten salas deben llamar a cargarSalas() explícitamente

  const addSala = async (salaData: Omit<Sala, 'id' | 'createdAt'>): Promise<string> => {
    try {
      const salaCreada = await salaService.crearSala({
        nombre: salaData.nombre,
        fecha: salaData.fecha,
        max_jugadores: 4
      });
      
      // Recargar salas para obtener la sala completa con jugadores
      await cargarSalas();
      
      return salaCreada.codigo_invitacion;
    } catch (error: any) {
      logger.error('Error al crear sala:', error);
      throw error;
    }
  };

  const updateSala = (id: string, salaData: Partial<Sala>) => {
    setSalas(prev => prev.map(sala => 
      sala.id === id ? { ...sala, ...salaData } : sala
    ));
  };

  const deleteSala = async (id: string) => {
    try {
      await salaService.eliminarSala(parseInt(id));
      setSalas(prev => prev.filter(sala => sala.id !== id));
    } catch (error: any) {
      logger.error('Error al eliminar sala:', error);
      throw error;
    }
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
          estadoConfirmacion: 'pendiente_confirmacion' as const,
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
          estadoConfirmacion: ambosConfirmados ? 'confirmado' as const : 'pendiente_confirmacion' as const,
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
      // Solo salas con resultado pendiente de confirmación
      if (sala.estadoConfirmacion !== 'pendiente_confirmacion') return false;
      
      // Verificar si el jugador está en la sala
      const estaEnSala = sala.jugadores?.some(j => j.id === jugadorId);
      if (!estaEnSala) return false;
      
      // Verificar que no sea el creador (el creador no confirma su propio resultado)
      if (sala.creador_id?.toString() === jugadorId) return false;
      
      // TODO: Verificar si ya confirmó consultando al backend
      // Por ahora, si cumple las condiciones anteriores, se considera pendiente
      return true;
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
      getSalasPendientesConfirmacion,
      cargarSalas,
      loading
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
