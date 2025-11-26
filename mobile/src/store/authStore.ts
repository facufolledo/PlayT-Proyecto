import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Usuario } from '../types';
import { logger } from '../utils/logger';

interface AuthState {
  usuario: Usuario | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUsuario: (usuario: Usuario | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
  loadUser: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  usuario: null,
  isAuthenticated: false,
  isLoading: true,

  setUsuario: (usuario) => {
    set({ usuario, isAuthenticated: !!usuario });
    if (usuario) {
      AsyncStorage.setItem('usuario', JSON.stringify(usuario));
    } else {
      AsyncStorage.removeItem('usuario');
    }
  },

  setLoading: (loading) => set({ isLoading: loading }),

  logout: () => {
    set({ usuario: null, isAuthenticated: false });
    AsyncStorage.removeItem('usuario');
  },

  loadUser: async () => {
    try {
      const usuarioStr = await AsyncStorage.getItem('usuario');
      if (usuarioStr) {
        const usuario = JSON.parse(usuarioStr);
        set({ usuario, isAuthenticated: true });
      }
    } catch (error) {
      logger.error('Error loading user:', error);
    } finally {
      set({ isLoading: false });
    }
  },

  checkAuth: async () => {
    set({ isLoading: true });
    try {
      const usuarioStr = await AsyncStorage.getItem('usuario');
      if (usuarioStr) {
        const usuario = JSON.parse(usuarioStr);
        set({ usuario, isAuthenticated: true, isLoading: false });
      } else {
        set({ usuario: null, isAuthenticated: false, isLoading: false });
      }
    } catch (error) {
      logger.error('Error checking auth:', error);
      set({ usuario: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
