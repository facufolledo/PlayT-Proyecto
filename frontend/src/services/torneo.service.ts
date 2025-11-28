import { authService } from './auth.service';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ============================================
// TIPOS PARA EL BACKEND
// ============================================

export interface TorneoCreate {
  nombre: string;
  descripcion?: string;
  categoria: string;
  fecha_inicio: string; // YYYY-MM-DD
  fecha_fin: string;    // YYYY-MM-DD
  lugar?: string;
  reglas_json?: {
    puntos_victoria?: number;
    puntos_derrota?: number;
    sets_para_ganar?: number;
  };
}

export interface TorneoBackend {
  id: number;
  nombre: string;
  descripcion?: string;
  tipo: string;
  categoria: string;
  estado: 'INSCRIPCION' | 'ARMANDO_ZONAS' | 'FASE_GRUPOS' | 'FASE_ELIMINACION' | 'FINALIZADO';
  fecha_inicio: string;
  fecha_fin: string;
  lugar?: string;
  reglas_json?: any;
  creado_por: number;
  created_at: string;
  updated_at: string;
}

export interface ParejaInscripcion {
  jugador1_id: number;
  jugador2_id: number;
  observaciones?: string;
}

export interface Pareja {
  id: number;
  torneo_id: number;
  jugador1: {
    id: number;
    nombre: string;
    apellido: string;
    foto_perfil?: string;
    rating?: number;
    categoria?: string;
  };
  jugador2: {
    id: number;
    nombre: string;
    apellido: string;
    foto_perfil?: string;
    rating?: number;
    categoria?: string;
  };
  estado: 'inscripta' | 'confirmada' | 'baja';
  categoria_asignada?: string;
  observaciones?: string;
  created_at: string;
}

// ============================================
// SERVICIO
// ============================================

class TorneoService {
  private async getHeaders(): Promise<HeadersInit> {
    const token = await authService.getToken();
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }
  
  // Listar torneos
  async listarTorneos(filtros?: {
    skip?: number;
    limit?: number;
    estado?: string;
    categoria?: string;
  }): Promise<TorneoBackend[]> {
    try {
      const params = new URLSearchParams();
      
      if (filtros?.skip) params.append('skip', filtros.skip.toString());
      if (filtros?.limit) params.append('limit', filtros.limit.toString());
      if (filtros?.estado) params.append('estado', filtros.estado);
      if (filtros?.categoria) params.append('categoria', filtros.categoria);
      
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/torneos?${params.toString()}`, {
        method: 'GET',
        headers,
      });
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al listar torneos:', error);
      throw error;
    }
  }
  
  // Obtener un torneo
  async obtenerTorneo(id: number): Promise<TorneoBackend> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/torneos/${id}`, {
        method: 'GET',
        headers,
      });
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al obtener torneo:', error);
      throw error;
    }
  }
  
  // Crear torneo
  async crearTorneo(data: TorneoCreate): Promise<TorneoBackend> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/torneos`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al crear torneo:', error);
      throw error;
    }
  }
  
  // Actualizar torneo
  async actualizarTorneo(id: number, data: Partial<TorneoCreate>): Promise<TorneoBackend> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/torneos/${id}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al actualizar torneo:', error);
      throw error;
    }
  }
  
  // Eliminar torneo
  async eliminarTorneo(id: number): Promise<void> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/torneos/${id}`, {
        method: 'DELETE',
        headers,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error al eliminar torneo:', error);
      throw error;
    }
  }
  
  // Cambiar estado
  async cambiarEstado(id: number, nuevoEstado: string): Promise<TorneoBackend> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/torneos/${id}/estado?nuevo_estado=${nuevoEstado}`, {
        method: 'PATCH',
        headers,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al cambiar estado:', error);
      throw error;
    }
  }
  
  // Obtener estadísticas
  async obtenerEstadisticas(id: number) {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/torneos/${id}/estadisticas`, {
        method: 'GET',
        headers,
      });
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al obtener estadísticas:', error);
      throw error;
    }
  }
  
  // ============================================
  // INSCRIPCIONES
  // ============================================
  
  async inscribirPareja(torneoId: number, data: ParejaInscripcion): Promise<Pareja> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/torneos/${torneoId}/inscribir`, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al inscribir pareja:', error);
      throw error;
    }
  }
  
  async listarParejas(torneoId: number, estado?: string): Promise<Pareja[]> {
    try {
      const params = estado ? `?estado=${estado}` : '';
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/torneos/${torneoId}/parejas${params}`, {
        method: 'GET',
        headers,
      });
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al listar parejas:', error);
      throw error;
    }
  }
  
  async confirmarPareja(torneoId: number, parejaId: number): Promise<Pareja> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/torneos/${torneoId}/parejas/${parejaId}/confirmar`, {
        method: 'PATCH',
        headers,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al confirmar pareja:', error);
      throw error;
    }
  }
  
  async rechazarPareja(torneoId: number, parejaId: number, motivo?: string): Promise<void> {
    try {
      const params = motivo ? `?motivo=${encodeURIComponent(motivo)}` : '';
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/torneos/${torneoId}/parejas/${parejaId}/rechazar${params}`, {
        method: 'DELETE',
        headers,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error al rechazar pareja:', error);
      throw error;
    }
  }
  
  async darBajaPareja(torneoId: number, parejaId: number, motivo?: string): Promise<Pareja> {
    try {
      const params = motivo ? `?motivo=${encodeURIComponent(motivo)}` : '';
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/torneos/${torneoId}/parejas/${parejaId}/baja${params}`, {
        method: 'PATCH',
        headers,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error al dar de baja pareja:', error);
      throw error;
    }
  }
  
  // ============================================
  // VALIDACIONES
  // ============================================
  
  validarDatosTorneo(data: TorneoCreate): string[] {
    const errores: string[] = [];
    
    if (!data.nombre || data.nombre.trim().length < 3) {
      errores.push('El nombre debe tener al menos 3 caracteres');
    }
    
    if (!data.categoria) {
      errores.push('La categoría es obligatoria');
    }
    
    if (!data.fecha_inicio) {
      errores.push('La fecha de inicio es obligatoria');
    }
    
    if (!data.fecha_fin) {
      errores.push('La fecha de fin es obligatoria');
    }
    
    if (data.fecha_inicio && data.fecha_fin && data.fecha_inicio >= data.fecha_fin) {
      errores.push('La fecha de fin debe ser posterior a la fecha de inicio');
    }
    
    return errores;
  }
  
  validarInscripcionPareja(data: ParejaInscripcion): string[] {
    const errores: string[] = [];
    
    if (!data.jugador1_id) {
      errores.push('Debe seleccionar el primer jugador');
    }
    
    if (!data.jugador2_id) {
      errores.push('Debe seleccionar el segundo jugador');
    }
    
    if (data.jugador1_id === data.jugador2_id) {
      errores.push('Los jugadores deben ser diferentes');
    }
    
    return errores;
  }
}

export const torneoService = new TorneoService();
export default torneoService;
