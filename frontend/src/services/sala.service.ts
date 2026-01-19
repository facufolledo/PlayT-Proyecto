import { authService } from './auth.service';
import { logger } from '../utils/logger';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// OPTIMIZACIÓN: Cache simple para salas
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number; // Time to live en ms
}

class SimpleCache {
  private cache = new Map<string, CacheEntry<any>>();

  set<T>(key: string, data: T, ttlMs: number = 30000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttlMs
    });
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    const now = Date.now();
    if (now - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  invalidate(pattern?: string): void {
    if (!pattern) {
      this.cache.clear();
      return;
    }

    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    }
  }
}

const cache = new SimpleCache();

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
  id?: string | number;  // El backend puede devolver "id" en listar_salas
  id_usuario?: number;   // O "id_usuario" en obtener_sala
  nombre_usuario?: string;
  nombre: string;
  apellido?: string;
  rating: number;
  equipo: number | null;
  orden?: number;
  esCreador?: boolean;
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
  usuarios_confirmados?: number[];  // IDs de usuarios que ya confirmaron
}

class SalaService {
  private pendingRequests = new Map<string, Promise<any>>();

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

  // OPTIMIZACIÓN: Request con timeout y retry
  private async fetchWithTimeout(
    url: string, 
    options: RequestInit, 
    timeoutMs: number = 10000,
    retries: number = 1
  ): Promise<Response> {
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
        
        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);
        return response;
        
      } catch (error: any) {
        if (attempt === retries) throw error;
        
        // Retry solo en errores de red, no en errores de servidor
        if (error.name === 'AbortError' || error.message === 'Failed to fetch') {
          logger.warn(`Intento ${attempt + 1} falló, reintentando...`);
          await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
          continue;
        }
        
        throw error;
      }
    }
    
    throw new Error('Max retries reached');
  }

  // OPTIMIZACIÓN: Deduplicación de requests
  private async deduplicateRequest<T>(key: string, requestFn: () => Promise<T>): Promise<T> {
    if (this.pendingRequests.has(key)) {
      return this.pendingRequests.get(key);
    }

    const promise = requestFn().finally(() => {
      this.pendingRequests.delete(key);
    });

    this.pendingRequests.set(key, promise);
    return promise;
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

  // Unirse a sala (OPTIMIZADO)
  async unirseASala(codigo: string): Promise<SalaCompleta> {
    const cacheKey = `unirse_${codigo}`;
    
    return this.deduplicateRequest(cacheKey, async () => {
      try {
        const headers = await this.getHeaders();
        
        // OPTIMIZACIÓN: Timeout más corto (10s en lugar de 30s)
        const response = await this.fetchWithTimeout(
          `${API_URL}/salas/unirse`,
          {
            method: 'POST',
            headers,
            body: JSON.stringify({ codigo_invitacion: codigo.toUpperCase() }),
          },
          10000, // 10 segundos
          2 // 2 reintentos
        );

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Error al unirse a la sala');
        }

        const data = await response.json();
        
        // OPTIMIZACIÓN: Invalidar cache de salas al unirse
        cache.invalidate('salas_list');
        
        return data;
      } catch (error: any) {
        logger.error('Error al unirse a sala:', error);
        
        // Mensajes de error más específicos
        if (error.name === 'AbortError') {
          throw new Error('La conexión tardó demasiado. Verifica tu internet.');
        }
        if (error.message === 'Failed to fetch') {
          throw new Error('No se pudo conectar. Verifica que el servidor esté disponible.');
        }
        throw new Error(error.message || 'Error al unirse a la sala');
      }
    });
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

  // Listar salas del usuario (OPTIMIZADO CON CACHE)
  async listarSalas(forceRefresh: boolean = false): Promise<SalaCompleta[]> {
    const cacheKey = 'salas_list';
    
    // OPTIMIZACIÓN: Usar cache si no se fuerza refresh
    if (!forceRefresh) {
      const cached = cache.get<SalaCompleta[]>(cacheKey);
      if (cached) {
        logger.log('Usando salas desde cache');
        return cached;
      }
    }

    return this.deduplicateRequest(cacheKey, async () => {
      try {
        const headers = await this.getHeaders();
        
        // OPTIMIZACIÓN: Timeout más corto y reintentos
        const response = await this.fetchWithTimeout(
          `${API_URL}/salas/`,
          {
            method: 'GET',
            headers,
          },
          8000, // 8 segundos (más rápido)
          2 // 2 reintentos
        );

        if (response.status === 403) {
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
        
        // OPTIMIZACIÓN: Guardar en cache por 30 segundos
        cache.set(cacheKey, data, 30000);
        
        return data;
      } catch (error: any) {
        if (error.name === 'AbortError') {
          throw new Error('El servidor no responde. Verifica tu conexión.');
        }
        throw error;
      }
    });
  }

  // Asignar equipos
  async asignarEquipos(salaId: number, equipos: AsignarEquiposDTO): Promise<void> {
    try {
      const headers = await this.getHeaders();
      
      // Timeout de 30 segundos
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);
      
      const response = await fetch(`${API_URL}/salas/${salaId}/asignar-equipos`, {
        method: 'POST',
        headers,
        body: JSON.stringify(equipos),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

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
      
      // Timeout de 30 segundos
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);
      
      const response = await fetch(`${API_URL}/salas/${salaId}/iniciar`, {
        method: 'POST',
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json();
        
        // Si el error tiene estructura compleja (anti-trampa)
        if (typeof errorData.detail === 'object') {
          throw new Error(errorData.detail.mensaje || JSON.stringify(errorData.detail));
        }
        
        throw new Error(errorData.detail || 'Error al iniciar partido');
      }

      const data = await response.json();
      return data;
    } catch (error: any) {
      logger.error('Error al iniciar partido:', error);
      if (error.name === 'AbortError') {
        throw new Error('El servidor tardó demasiado. Intenta de nuevo.');
      }
      if (error.message === 'Failed to fetch') {
        throw new Error('No se pudo conectar al servidor.');
      }
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

  // OPTIMIZACIÓN: Métodos para gestión de cache
  invalidateCache(pattern?: string): void {
    cache.invalidate(pattern);
    logger.log('Cache invalidado:', pattern || 'todo');
  }

  // OPTIMIZACIÓN: Refresh forzado de salas
  async refreshSalas(): Promise<SalaCompleta[]> {
    return this.listarSalas(true);
  }

  // OPTIMIZACIÓN: Obtener sala con cache
  async obtenerSalaOptimizada(salaId: number, useCache: boolean = true): Promise<SalaCompleta> {
    const cacheKey = `sala_${salaId}`;
    
    if (useCache) {
      const cached = cache.get<SalaCompleta>(cacheKey);
      if (cached) {
        return cached;
      }
    }

    try {
      const headers = await this.getHeaders();
      const response = await this.fetchWithTimeout(
        `${API_URL}/salas/${salaId}`,
        {
          method: 'GET',
          headers,
        },
        5000 // 5 segundos para sala individual
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error al obtener sala');
      }

      const data = await response.json();
      
      // Cache por 15 segundos (más corto para datos específicos)
      cache.set(cacheKey, data, 15000);
      
      return data;
    } catch (error: any) {
      logger.error('Error al obtener sala:', error);
      throw new Error(error.message || 'Error al obtener sala');
    }
  }
}

export const salaService = new SalaService();