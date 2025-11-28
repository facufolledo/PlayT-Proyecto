// Servicio de API para comunicación con el backend
import axios, { AxiosInstance } from 'axios';
import { logger } from '../utils/logger';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface UsuarioResponse {
  id_usuario: number;
  nombre_usuario: string;
  email: string;
  nombre: string;
  apellido: string;
  sexo: 'M' | 'F';
  ciudad?: string;
  pais?: string;
  rating: number;
  partidos_jugados: number;
  id_categoria?: number;
  foto_perfil?: string;
  posicion_preferida?: 'drive' | 'reves';
  mano_dominante?: 'derecha' | 'zurda';
  dni?: string;
  fecha_nacimiento?: string;
  telefono?: string;
  puede_crear_torneos?: boolean;
  es_administrador?: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para agregar token a las peticiones
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Interceptor para manejar errores de autenticación
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        // Si es un error 401 y no hemos intentado renovar el token
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            // Intentar obtener el token guardado en localStorage
            const savedToken = localStorage.getItem('firebase_token');
            
            if (savedToken) {
              console.log('🔄 Usando token guardado de Firebase...');
              // Reintentar la petición original con el token guardado
              originalRequest.headers.Authorization = `Bearer ${savedToken}`;
              return this.api(originalRequest);
            } else {
              // No hay token guardado, redirigir a login
              localStorage.removeItem('access_token');
              localStorage.removeItem('usuario');
              window.location.href = '/login';
            }
          } catch (refreshError) {
            console.error('Error al renovar token:', refreshError);
            localStorage.removeItem('access_token');
            localStorage.removeItem('usuario');
            localStorage.removeItem('firebase_token');
            window.location.href = '/login';
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  // Login con email y contraseña
  async login(email: string, password: string): Promise<TokenResponse> {
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const response = await this.api.post<TokenResponse>('/auth/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error: any) {
      logger.error('Error en login:', error);
      throw error;
    }
  }

  // Autenticación con Firebase
  async firebaseAuth(firebaseToken: string): Promise<UsuarioResponse> {
    try {
      const response = await this.api.post<UsuarioResponse>('/auth/firebase-auth', {
        firebase_token: firebaseToken,
      });

      return response.data;
    } catch (error: any) {
      logger.error('Error en autenticación con Firebase:', error);
      throw error;
    }
  }

  // Obtener información del usuario actual
  async getMe(): Promise<UsuarioResponse> {
    try {
      const response = await this.api.get<UsuarioResponse>('/auth/me');
      return response.data;
    } catch (error: any) {
      logger.error('Error al obtener usuario:', error);
      throw error;
    }
  }

  // Obtener categorías disponibles
  async getCategorias(): Promise<any[]> {
    try {
      const response = await this.api.get('/auth/categorias');
      return response.data;
    } catch (error: any) {
      logger.error('Error al obtener categorías:', error);
      throw error;
    }
  }

  // Obtener ranking general
  async getRankingGeneral(limit: number = 100, offset: number = 0, sexo?: 'masculino' | 'femenino'): Promise<any[]> {
    try {
      const params: any = { limit, offset };
      if (sexo) {
        params.sexo = sexo;
      }
      const response = await this.api.get('/ranking/', { params });
      return response.data;
    } catch (error: any) {
      logger.error('Error al obtener ranking general:', error);
      throw error;
    }
  }

  // Obtener ranking por categoría
  async getRankingPorCategoria(idCategoria: number, sexo?: 'masculino' | 'femenino'): Promise<any> {
    try {
      const params: any = {};
      if (sexo) {
        params.sexo = sexo;
      }
      const response = await this.api.get(`/categorias/${idCategoria}/jugadores`, { params });
      return response.data;
    } catch (error: any) {
      logger.error('Error al obtener ranking por categoría:', error);
      throw error;
    }
  }

  // Obtener ranking global (endpoint alternativo)
  async getRankingGlobal(limit: number = 100): Promise<any[]> {
    try {
      const response = await this.api.get('/categorias/ranking/global', {
        params: { limit }
      });
      return response.data;
    } catch (error: any) {
      logger.error('Error al obtener ranking global:', error);
      throw error;
    }
  }
}

export const apiService = new ApiService();
