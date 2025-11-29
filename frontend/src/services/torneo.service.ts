import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Tipos para crear/actualizar torneos
export interface TorneoCreate {
  nombre: string;
  descripcion: string;
  fecha_inicio: string;
  fecha_fin: string;
  lugar?: string;
  ubicacion?: string; // Alias para compatibilidad
  categoria: string;
  max_parejas: number;
  premio?: string;
}

// Tipo del backend
export interface TorneoBackend {
  id: number;
  nombre: string;
  descripcion: string;
  fecha_inicio: string;
  fecha_fin: string;
  lugar: string;
  categoria: string;
  max_parejas: number;
  parejas_inscritas?: number;
  estado: string;
  premio?: string;
  owner_id: number;
  created_at: string;
}

// Tipo para el frontend (compatible con el Context)
export interface Torneo {
  id_torneo: number;
  nombre: string;
  descripcion: string;
  fecha_inicio: string;
  fecha_fin: string;
  ubicacion: string;
  categoria: string;
  max_parejas: number;
  parejas_inscritas: number;
  estado: 'inscripcion' | 'armando_zonas' | 'fase_grupos' | 'fase_eliminacion' | 'finalizado';
  premio?: string;
  owner_id: number;
}

// Tipos para inscripciones
export interface ParejaInscripcion {
  jugador1_id: number;
  jugador2_id: number;
  nombre_pareja: string;
}

export interface Pareja {
  id: number;
  id_pareja?: number; // Alias para compatibilidad
  torneo_id: number;
  jugador1_id: number;
  jugador2_id: number;
  nombre_pareja: string;
  estado: 'inscripta' | 'confirmada' | 'baja';
  jugador1_nombre?: string;
  jugador2_nombre?: string;
}

export interface EstadisticasTorneo {
  torneo_id: number;
  total_parejas: number;
  total_partidos: number;
  partidos_jugados: number;
  partidos_pendientes: number;
  zonas: number;
  fase_actual: string;
}

class TorneoService {
  private getAuthHeaders() {
    const token = localStorage.getItem('token') || localStorage.getItem('firebase_token');
    return {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };
  }

  // CRUD Torneos
  async listarTorneos(params?: {
    skip?: number;
    limit?: number;
    estado?: string;
    categoria?: string;
  }): Promise<Torneo[]> {
    const response = await axios.get(`${API_URL}/torneos`, { params });
    return response.data;
  }

  async obtenerTorneo(torneoId: number): Promise<Torneo> {
    const response = await axios.get(`${API_URL}/torneos/${torneoId}`);
    return response.data;
  }

  async crearTorneo(data: TorneoCreate): Promise<Torneo> {
    const response = await axios.post(
      `${API_URL}/torneos`,
      data,
      this.getAuthHeaders()
    );
    return response.data;
  }

  async actualizarTorneo(torneoId: number, data: Partial<TorneoCreate>): Promise<Torneo> {
    const response = await axios.put(
      `${API_URL}/torneos/${torneoId}`,
      data,
      this.getAuthHeaders()
    );
    return response.data;
  }

  async eliminarTorneo(torneoId: number): Promise<void> {
    await axios.delete(
      `${API_URL}/torneos/${torneoId}`,
      this.getAuthHeaders()
    );
  }

  // Estado
  async cambiarEstado(torneoId: number, nuevoEstado: string): Promise<Torneo> {
    const response = await axios.patch(
      `${API_URL}/torneos/${torneoId}/estado`,
      { nuevo_estado: nuevoEstado },
      this.getAuthHeaders()
    );
    return response.data;
  }

  // Estadísticas
  async obtenerEstadisticas(torneoId: number): Promise<EstadisticasTorneo> {
    const response = await axios.get(`${API_URL}/torneos/${torneoId}/estadisticas`);
    return response.data;
  }

  // Inscripciones
  async inscribirPareja(
    torneoId: number,
    data: { jugador1_id: number; jugador2_id: number; nombre_pareja: string }
  ): Promise<Pareja> {
    const response = await axios.post(
      `${API_URL}/torneos/${torneoId}/inscribir`,
      data,
      this.getAuthHeaders()
    );
    return response.data;
  }

  async listarParejas(torneoId: number, estado?: string): Promise<Pareja[]> {
    const response = await axios.get(`${API_URL}/torneos/${torneoId}/parejas`, {
      params: { estado },
    });
    return response.data;
  }

  async confirmarPareja(torneoId: number, parejaId: number): Promise<Pareja> {
    const response = await axios.patch(
      `${API_URL}/torneos/${torneoId}/parejas/${parejaId}/confirmar`,
      {},
      this.getAuthHeaders()
    );
    return response.data;
  }

  async rechazarPareja(torneoId: number, parejaId: number, motivo?: string): Promise<void> {
    await axios.delete(
      `${API_URL}/torneos/${torneoId}/parejas/${parejaId}/rechazar`,
      {
        ...this.getAuthHeaders(),
        params: { motivo },
      }
    );
  }

  async darBajaPareja(torneoId: number, parejaId: number, motivo?: string): Promise<Pareja> {
    const response = await axios.patch(
      `${API_URL}/torneos/${torneoId}/parejas/${parejaId}/baja`,
      {},
      {
        ...this.getAuthHeaders(),
        params: { motivo },
      }
    );
    return response.data;
  }

  // Validaciones
  validarDatosTorneo(data: TorneoCreate): string[] {
    const errores: string[] = [];
    
    if (!data.nombre || data.nombre.trim().length < 3) {
      errores.push('El nombre debe tener al menos 3 caracteres');
    }
    
    if (!data.descripcion || data.descripcion.trim().length < 10) {
      errores.push('La descripción debe tener al menos 10 caracteres');
    }
    
    if (!data.fecha_inicio) {
      errores.push('La fecha de inicio es requerida');
    }
    
    if (!data.fecha_fin) {
      errores.push('La fecha de fin es requerida');
    }
    
    if (data.fecha_inicio && data.fecha_fin && new Date(data.fecha_inicio) > new Date(data.fecha_fin)) {
      errores.push('La fecha de inicio debe ser anterior a la fecha de fin');
    }
    
    if (!data.max_parejas || data.max_parejas < 2) {
      errores.push('Debe haber al menos 2 parejas');
    }
    
    return errores;
  }

  validarInscripcionPareja(data: ParejaInscripcion): string[] {
    const errores: string[] = [];
    
    if (!data.jugador1_id) {
      errores.push('Debe seleccionar el jugador 1');
    }
    
    if (!data.jugador2_id) {
      errores.push('Debe seleccionar el jugador 2');
    }
    
    if (data.jugador1_id === data.jugador2_id) {
      errores.push('Los jugadores deben ser diferentes');
    }
    
    if (!data.nombre_pareja || data.nombre_pareja.trim().length < 3) {
      errores.push('El nombre de la pareja debe tener al menos 3 caracteres');
    }
    
    return errores;
  }
}

// Exportar instancia por defecto para compatibilidad con Context
const torneoServiceInstance = new TorneoService();
export default torneoServiceInstance;

// También exportar como named export
export const torneoService = torneoServiceInstance;
