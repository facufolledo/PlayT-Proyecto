import { apiService } from './api';

export interface PerfilPublico {
  id_usuario: number;
  nombre: string;
  apellido: string;
  nombre_usuario: string;
  email?: string; // Solo si es el propio perfil
  rating: number;
  posicion_preferida?: string;
  mano_dominante?: string;
  ciudad?: string;
  pais?: string;
  fecha_registro: string;
  foto_perfil?: string;
  activo: boolean;
}

export interface EstadisticasJugador {
  partidos_jugados: number;
  partidos_ganados: number;
  partidos_perdidos: number;
  porcentaje_victorias: number;
  racha_actual: {
    tipo: 'victorias' | 'derrotas';
    cantidad: number;
  };
  mejor_rating: number;
  peor_rating: number;
  rating_actual: number;
  torneos_participados: number;
  torneos_ganados: number;
  finales_jugadas: number;
  sets_ganados: number;
  sets_perdidos: number;
  games_ganados: number;
  games_perdidos: number;
  cambio_rating_total: number;
  winrate_torneos: number;
  winrate_amistosos: number;
  mejor_racha: number;
}

export interface PartidoHistorial {
  id_partido: number;
  fecha: string;
  estado: string;
  tipo?: string;
  jugadores: Array<{
    id_usuario: number;
    nombre_usuario: string;
    nombre: string;
    apellido: string;
    equipo: number;
    rating: number;
  }>;
  resultado?: {
    sets_eq1: number;
    sets_eq2: number;
    detalle_sets: Array<{
      set: number;
      juegos_eq1: number;
      juegos_eq2: number;
      tiebreak_eq1?: number;
      tiebreak_eq2?: number;
    }>;
    confirmado: boolean;
    desenlace: string;
  };
  historial_rating?: {
    rating_antes: number;
    delta: number;
    rating_despues: number;
  };
}

class PerfilService {
  // Obtener perfil público por username
  async getPerfilPublico(username: string): Promise<PerfilPublico> {
    try {
      const response = await apiService.get(`/usuarios/perfil-publico/${username}`);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error('Jugador no encontrado');
      }
      throw new Error('Error al cargar el perfil');
    }
  }

  // Obtener estadísticas de un jugador
  async getEstadisticas(userId: number): Promise<EstadisticasJugador> {
    try {
      const response = await apiService.get(`/usuarios/${userId}/estadisticas`);
      return response.data;
    } catch (error) {
      throw new Error('Error al cargar estadísticas');
    }
  }

  // Obtener historial de partidos
  async getHistorial(userId: number, limit = 50): Promise<PartidoHistorial[]> {
    try {
      const response = await apiService.get(`/partidos/usuario/${userId}?limit=${limit}`);
      
      // Eliminar duplicados por id_partido (igual que en MiPerfil)
      const partidosUnicos = response.data.filter((partido: PartidoHistorial, index: number, self: PartidoHistorial[]) =>
        index === self.findIndex((p) => p.id_partido === partido.id_partido)
      );
      
      return partidosUnicos;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return []; // No hay partidos
      }
      throw new Error('Error al cargar historial');
    }
  }

  // Buscar jugadores públicamente
  async buscarJugadores(query: string, limit = 20): Promise<PerfilPublico[]> {
    try {
      const response = await apiService.get(`/usuarios/buscar-publico?q=${query}&limit=${limit}`);
      return response.data;
    } catch (error) {
      throw new Error('Error en la búsqueda');
    }
  }

  // Comparar dos jugadores
  async compararJugadores(userId1: number, userId2: number) {
    try {
      const response = await apiService.get(`/usuarios/comparar/${userId1}/${userId2}`);
      return response.data;
    } catch (error) {
      throw new Error('Error al comparar jugadores');
    }
  }

  // Obtener evolución del rating
  async getEvolucionRating(userId: number, dias = 90) {
    try {
      const response = await apiService.get(`/usuarios/${userId}/evolucion?dias=${dias}`);
      return response.data;
    } catch (error) {
      throw new Error('Error al cargar evolución del rating');
    }
  }

  // Obtener torneos del jugador
  async getTorneos(userId: number) {
    try {
      const response = await apiService.get(`/usuarios/${userId}/torneos`);
      return response.data;
    } catch (error) {
      throw new Error('Error al cargar torneos');
    }
  }
}

export const perfilService = new PerfilService();