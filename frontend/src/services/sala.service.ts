import { authService } from './auth.service';
import { logger } from '../utils/logger';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface CrearSalaDTO {
  nombre: string;
  fecha: string;
  max_jugadores?: number;
}

export interface UnirseASalaDTO {
  codigo_invitacion: string;
}

export interface AsignarEquiposDTO {
  [jugador_id: string]: number; // jugador_id: equipo (1 o 2)
}

export interface SalaResponse {
  id_sala: string;
  nombre: string;
  fecha: string;
  estado: string;
  codigo_invitacion: string;
  id_creador: number;
  jugadores_actuales: number;
  max_jugadores: number;
  creado_en: string;
}

export interface JugadorSala {
  id_usuario: number;
  nombre_usuario: string;
  nombre: string;
  apellido: string;
  rating: number;
  equipo: number | null;
  orden: number;
}

export interface SalaCompleta extends SalaResponse {
  jugadores: JugadorSala[];
  estado_confirmacion?: string;
  resultado?: any;
  cambios_elo?: Array<{
    id_usuario: number;
    rating_antes: number;
    rating_despues: number;
    cambio_elo: number;
  }>;
  elo_aplicado?: boolean;
}

class SalaService {
  private async getHeaders(): Promise<HeadersInit> {
    const token = await authService.getToken();
    
    if (!token) {
      logger.warn('No hay token de autenticación');
    }
    
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
    };
  }

  // Crear sala
  async crearSala(datos: CrearSalaDTO): Promise<SalaResponse> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/salas/`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          ...datos,
          max_jugadores: datos.max_jugadores || 4
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error al crear sala');
      }

      const data = await response.json();
      logger.log('Sala creada:', data);
      return data;
    } catch (error: any) {
      logger.error('Error al crear sala:', error);
      throw new Error(error.message || 'Error al crear sala');
    }
  }

  // Unirse a sala
  async unirseASala(codigo: string): Promise<SalaCompleta> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/salas/unirse`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ codigo_invitacion: codigo.toUpperCase() }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error al unirse a la sala');
      }

      const data = await response.json();
      logger.log('Unido a sala:', data);
      return data;
    } catch (error: any) {
      logger.error('Error al unirse a sala:', error);
      throw new Error(error.message || 'Error al unirse a la sala');
    }
  }

  // Obtener sala por ID
  async obtenerSala(salaId: number): Promise<SalaCompleta> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/salas/${salaId}`, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error al obtener sala');
      }

      const data = await response.json();
      return data;
    } catch (error: any) {
      logger.error('Error al obtener sala:', error);
      throw new Error(error.message || 'Error al obtener sala');
    }
  }

  // Listar salas del usuario
  async listarSalas(): Promise<SalaCompleta[]> {
    try {
      const headers = await this.getHeaders();
      
      // Timeout de 30 segundos
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);
      
      const response = await fetch(`${API_URL}/salas/`, {
        method: 'GET',
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.status === 403) {
        // Solo recargar si hay un token (token expirado)
        // Si no hay token, simplemente lanzar error sin recargar
        const token = await authService.getToken();
        if (token) {
          logger.warn('Token expirado, recargando...');
          setTimeout(() => window.location.reload(), 1000);
        }
        throw new Error('No autorizado');
      }

      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage = `Error ${response.status}: ${response.statusText}`;
        try {
          const errorJson = JSON.parse(errorText);
          errorMessage = errorJson.detail || errorMessage;
        } catch (e) {
          // Si no es JSON, usar el texto tal cual
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      return data;
    } catch (error: any) {
      if (error.name === 'AbortError') {
        throw new Error('El servidor no responde. Verifica que el backend esté corriendo.');
      }
      throw error;
    }
  }

  // Asignar equipos
  async asignarEquipos(salaId: number, equipos: AsignarEquiposDTO): Promise<void> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/salas/${salaId}/asignar-equipos`, {
        method: 'POST',
        headers,
        body: JSON.stringify(equipos),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error al asignar equipos');
      }

      logger.log('Equipos asignados correctamente');
    } catch (error: any) {
      logger.error('Error al asignar equipos:', error);
      throw new Error(error.message || 'Error al asignar equipos');
    }
  }

  // Iniciar partido
  async iniciarPartido(salaId: number): Promise<{ id_partido: number }> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/salas/${salaId}/iniciar`, {
        method: 'POST',
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error del servidor:', errorData);
        
        // Si el error tiene estructura compleja (anti-trampa)
        if (typeof errorData.detail === 'object') {
          throw new Error(errorData.detail.mensaje || JSON.stringify(errorData.detail));
        }
        
        throw new Error(errorData.detail || 'Error al iniciar partido');
      }

      const data = await response.json();
      logger.log('Partido iniciado:', data);
      return data;
    } catch (error: any) {
      logger.error('Error al iniciar partido:', error);
      throw error;
    }
  }

  // Eliminar sala
  async eliminarSala(salaId: number): Promise<void> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/salas/${salaId}`, {
        method: 'DELETE',
        headers,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error al eliminar sala');
      }

      logger.log('Sala eliminada correctamente');
    } catch (error: any) {
      logger.error('Error al eliminar sala:', error);
      throw new Error(error.message || 'Error al eliminar sala');
    }
  }

  // Cargar resultado del partido
  async cargarResultado(salaId: number, resultado: any): Promise<any> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/salas/${salaId}/resultado`, {
        method: 'POST',
        headers,
        body: JSON.stringify(resultado),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error del servidor:', errorData);
        throw new Error(errorData.detail || 'Error al cargar resultado');
      }

      const data = await response.json();
      logger.log('Resultado cargado:', data);
      return data;
    } catch (error: any) {
      logger.error('Error al cargar resultado:', error);
      throw error;
    }
  }

  // Obtener resultado del partido
  async obtenerResultado(salaId: number): Promise<any> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/salas/${salaId}/resultado`, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al obtener resultado');
      }

      const data = await response.json();
      return data;
    } catch (error: any) {
      logger.error('Error al obtener resultado:', error);
      throw error;
    }
  }

  // Confirmar resultado
  async confirmarResultado(salaId: number): Promise<any> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/salas/${salaId}/confirmar`, {
        method: 'POST',
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al confirmar resultado');
      }

      const data = await response.json();
      logger.log('Resultado confirmado:', data);
      return data;
    } catch (error: any) {
      logger.error('Error al confirmar resultado:', error);
      throw error;
    }
  }

  // Reportar resultado
  async reportarResultado(salaId: number, motivo: string): Promise<any> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/salas/${salaId}/reportar`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ motivo }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al reportar resultado');
      }

      const data = await response.json();
      logger.log('Resultado reportado:', data);
      return data;
    } catch (error: any) {
      logger.error('Error al reportar resultado:', error);
      throw error;
    }
  }

  // Obtener estado de confirmaciones
  async obtenerEstadoConfirmaciones(salaId: number): Promise<any> {
    try {
      const headers = await this.getHeaders();
      const response = await fetch(`${API_URL}/resultados/${salaId}/estado`, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al obtener estado de confirmaciones');
      }

      const data = await response.json();
      logger.log('Estado de confirmaciones:', data);
      return data;
    } catch (error: any) {
      logger.error('Error al obtener estado de confirmaciones:', error);
      throw error;
    }
  }
}

export const salaService = new SalaService();
