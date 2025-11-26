import { apiClient } from './api.client';
import { Torneo } from '../types';

export const torneoService = {
  obtenerTorneos: async (): Promise<Torneo[]> => {
    const response = await apiClient.get('/torneos');
    return response.data;
  },

  obtenerTorneoPorId: async (id: number): Promise<Torneo> => {
    const response = await apiClient.get(`/torneos/${id}`);
    return response.data;
  },

  crearTorneo: async (data: Partial<Torneo>): Promise<Torneo> => {
    const response = await apiClient.post('/torneos', data);
    return response.data;
  },

  inscribirseEnTorneo: async (torneoId: number): Promise<void> => {
    await apiClient.post(`/torneos/${torneoId}/inscribirse`);
  },

  desinscribirseDelTorneo: async (torneoId: number): Promise<void> => {
    await apiClient.post(`/torneos/${torneoId}/desinscribirse`);
  },

  iniciarTorneo: async (torneoId: number): Promise<void> => {
    await apiClient.post(`/torneos/${torneoId}/iniciar`);
  },
};
