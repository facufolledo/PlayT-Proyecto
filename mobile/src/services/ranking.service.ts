import { apiClient } from './api.client';

export const rankingService = {
  obtenerRankings: async () => {
    const response = await apiClient.get('/rankings');
    return response.data;
  },

  obtenerRankingPorCategoria: async (categoria: string) => {
    const response = await apiClient.get(`/rankings/categoria/${categoria}`);
    return response.data;
  },
};
