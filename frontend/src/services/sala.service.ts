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
      logger.log('Consultando salas en:', `${API_URL}/salas/`);
      
      // Agregar timeout de 10 segundos
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      
      const response = await fetch(`${API_URL}/salas/`, {
        method: 'GET',
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      logger.log('Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        logger.error('Error response:', errorText);
        
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
      logger.log('Salas obtenidas:', data.length);
      return data;
    } catch (error: any) {
      if (error.name === 'AbortError') {
        logger.error('Timeout al listar salas');
        throw new Error('El servidor no responde. Verifica que el backend esté corriendo.');
      }
      logger.error('Error al listar salas:', error);
      throw new Error(error.message || 'Error al listar salas');
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
        const error = await response.json();
        throw new Error(error.detail || 'Error al iniciar partido');
      }

      const data = await response.json();
      logger.log('Partido iniciado:', data);
      return data;
    } catch (error: any) {
      logger.error('Error al iniciar partido:', error);
      throw new Error(error.message || 'Error al iniciar partido');
    }
  }
}

export const salaService = new SalaService();
