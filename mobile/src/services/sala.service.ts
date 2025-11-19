import { apiClient } from './api.client';
import { Sala } from '../types';

export const salaService = {
  obtenerSalas: async (): Promise<Sala[]> => {
    const response = await apiClient.get('/salas');
    return response.data;
  },

  obtenerSalaPorId: async (id: number): Promise<Sala> => {
    const response = await apiClient.get(`/salas/${id}`);
    return response.data;
  },

  crearSala: async (data: Partial<Sala>): Promise<Sala> => {
    const response = await apiClient.post('/salas', data);
    return response.data;
  },

  unirseASala: async (salaId: number): Promise<void> => {
    await apiClient.post(`/salas/${salaId}/unirse`);
  },

  salirDeSala: async (salaId: number): Promise<void> => {
    await apiClient.post(`/salas/${salaId}/salir`);
  },

  iniciarPartido: async (salaId: number): Promise<void> => {
    await apiClient.post(`/salas/${salaId}/iniciar`);
  },
};
