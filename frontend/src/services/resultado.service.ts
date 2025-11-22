/**
 * Servicio para manejar resultados de partidos y confirmaciones
 */
import { apiService } from './api';

interface ResultadoPadelBackend {
  id_sala: string;
  id_creador: number;
  sets: Array<{ equipo1: number; equipo2: number }>;
  ganador_equipo: 'equipo1' | 'equipo2';
}

class ResultadoService {
  /**
   * Crear resultado de un partido (creador)
   */
  async crearResultado(resultado: ResultadoPadelBackend) {
    try {
      const response = await apiService.post('/resultados', resultado);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error al crear resultado');
    }
  }

  /**
   * Confirmar resultado de un partido (rival)
   */
  async confirmarResultado(salaId: string, idUsuario: number) {
    try {
      const response = await apiService.post(`/resultados/${salaId}/confirmar`, {
        id_usuario: idUsuario
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error al confirmar resultado');
    }
  }

  /**
   * Obtener resultado de un partido
   */
  async obtenerResultado(salaId: string) {
    try {
      const response = await apiService.get(`/resultados/${salaId}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error al obtener resultado');
    }
  }

  /**
   * Obtener confirmaciones pendientes del usuario
   */
  async obtenerConfirmacionesPendientes(idUsuario: number) {
    try {
      const response = await apiService.get(`/resultados/pendientes/${idUsuario}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Error al obtener confirmaciones pendientes');
    }
  }
}

export const resultadoService = new ResultadoService();
