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
  const jugadores = salaBackend.jugadores || [];
  
  // Separar jugadores por equipo (solo si tienen equipo asignado)
  const equipoA = jugadores.filter(j => j.equipo === 1);
  const equipoB = jugadores.filter(j => j.equipo === 2);
  const hayEquiposAsignados = equipoA.length > 0 && equipoB.length > 0;
  
  // El backend puede devolver "id" o "id_usuario" dependiendo del endpoint
  const getJugadorId = (j: any): string => {
    return (j.id || j.id_usuario)?.toString() || '';
  };
  
  const getJugadorNombre = (j: any): string => {
    // El backend puede enviar nombre completo o separado
    // Priorizar nombre completo ya construido, luego nombre + apellido, luego nombre_usuario
    if (j.nombre && j.nombre.trim()) return j.nombre.trim();
    if (j.nombre_usuario) return j.nombre_usuario;
    return 'Usuario';
  };
  
  // Obtener nombre_usuario del jugador
  const getJugadorNombreUsuario = (j: any): string | undefined => {
    return j.nombre_usuario || undefined;
  };
  
  return {
    id: salaBackend.id_sala,
    nombre: salaBackend.nombre,
    fecha: salaBackend.fecha,
    estado: salaBackend.estado as any,
    codigoInvitacion: salaBackend.codigo_invitacion,
    jugadores: jugadores.map(j => ({
      id: getJugadorId(j),
      nombre: getJugadorNombre(j),
      nombreUsuario: getJugadorNombreUsuario(j),
      rating: j.rating || 1500,
      esCreador: getJugadorId(j) === salaBackend.id_creador?.toString()
    })),
    equiposAsignados: hayEquiposAsignados,
    equipoA: {
      jugador1: equipoA[0] ? {
        id: getJugadorId(equipoA[0]),
        nombre: getJugadorNombre(equipoA[0]),
        nombreUsuario: getJugadorNombreUsuario(equipoA[0]),
        rating: equipoA[0].rating || 1500
      } : { id: '', nombre: '' },
      jugador2: equipoA[1] ? {
        id: getJugadorId(equipoA[1]),
        nombre: getJugadorNombre(equipoA[1]),
        nombreUsuario: getJugadorNombreUsuario(equipoA[1]),
        rating: equipoA[1].rating || 1500
      } : { id: '', nombre: '' },
      puntos: 0,
      confirmado: false
    },
    equipoB: {
      jugador1: equipoB[0] ? {
        id: getJugadorId(equipoB[0]),
        nombre: getJugadorNombre(equipoB[0]),
        nombreUsuario: getJugadorNombreUsuario(equipoB[0]),
        rating: equipoB[0].rating || 1500
      } : { id: '', nombre: '' },
      jugador2: equipoB[1] ? {
        id: getJugadorId(equipoB[1]),
        nombre: getJugadorNombre(equipoB[1]),
        nombreUsuario: getJugadorNombreUsuario(equipoB[1]),
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
    usuariosConfirmados: salaBackend.usuarios_confirmados || [],
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

  const confirmarResultado = async (id: string, equipo: 'equipoA' | 'equipoB', jugadorId: string) => {
    try {
      // Llamar al backend para confirmar
      await salaService.confirmarResultado(parseInt(id));
      
      // Actualizar estado local
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
      
      // Recargar salas para obtener el estado actualizado del backend
      await cargarSalas();
    } catch (error) {
      console.error('Error al confirmar resultado:', error);
      logger.error('Error al confirmar resultado', error);
    }
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
      // Solo salas con estado pendiente_confirmacion
      if (sala.estadoConfirmacion !== 'pendiente_confirmacion') return false;
      
      // Verificar si el jugador está en la sala
      const estaEnSala = sala.jugadores?.some(j => j.id === jugadorId);
      if (!estaEnSala) return false;
      
      // Verificar que no sea el creador (el creador no confirma su propio resultado)
      if (sala.creador_id?.toString() === jugadorId) return false;
      
      // Verificar si el usuario ya confirmó (usando el nuevo campo del backend)
      const jugadorIdNum = parseInt(jugadorId);
      if (sala.usuariosConfirmados?.includes(jugadorIdNum)) return false;
      
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
