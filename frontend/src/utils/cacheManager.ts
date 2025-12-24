import { clientLogger } from './clientLogger';

interface CacheItem<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
  key: string;
}

interface CacheOptions {
  ttl?: number; // Time to live in milliseconds
  maxSize?: number;
  persistent?: boolean; // Use localStorage instead of memory
}

class CacheManager {
  private memoryCache = new Map<string, CacheItem<any>>();
  private maxSize: number;
  private defaultTTL: number;

  constructor(options: CacheOptions = {}) {
    this.maxSize = options.maxSize || 100;
    this.defaultTTL = options.ttl || 5 * 60 * 1000; // 5 minutes default
  }

  // Generar clave de caché
  private generateKey(prefix: string, params?: Record<string, any>): string {
    if (!params) return prefix;
    
    const sortedParams = Object.keys(params)
      .sort()
      .reduce((result, key) => {
        result[key] = params[key];
        return result;
      }, {} as Record<string, any>);

    return `${prefix}:${JSON.stringify(sortedParams)}`;
  }

  // Obtener del caché
  get<T>(key: string): T | null {
    // Intentar memoria primero
    const memoryItem = this.memoryCache.get(key);
    if (memoryItem && memoryItem.expiresAt > Date.now()) {
      clientLogger.debug('Cache hit (memory)', { key });
      return memoryItem.data;
    }

    // Intentar localStorage
    try {
      const stored = localStorage.getItem(`cache:${key}`);
      if (stored) {
        const item: CacheItem<T> = JSON.parse(stored);
        if (item.expiresAt > Date.now()) {
          clientLogger.debug('Cache hit (localStorage)', { key });
          // Mover a memoria para acceso más rápido
          this.memoryCache.set(key, item);
          return item.data;
        } else {
          // Expirado, limpiar
          localStorage.removeItem(`cache:${key}`);
        }
      }
    } catch (error) {
      clientLogger.warn('Cache read error', { key, error });
    }

    clientLogger.debug('Cache miss', { key });
    return null;
  }

  // Guardar en caché
  set<T>(key: string, data: T, options: CacheOptions = {}): void {
    const ttl = options.ttl || this.defaultTTL;
    const item: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      expiresAt: Date.now() + ttl,
      key
    };

    // Guardar en memoria
    this.memoryCache.set(key, item);

    // Limpiar caché si excede el tamaño máximo
    if (this.memoryCache.size > this.maxSize) {
      const oldestKey = this.memoryCache.keys().next().value;
      this.memoryCache.delete(oldestKey);
    }

    // Guardar en localStorage si es persistente
    if (options.persistent !== false) {
      try {
        localStorage.setItem(`cache:${key}`, JSON.stringify(item));
      } catch (error) {
        clientLogger.warn('Cache write error', { key, error });
      }
    }

    clientLogger.debug('Cache set', { key, ttl, persistent: options.persistent !== false });
  }

  // Invalidar caché
  invalidate(key: string): void {
    this.memoryCache.delete(key);
    localStorage.removeItem(`cache:${key}`);
    clientLogger.debug('Cache invalidated', { key });
  }

  // Invalidar por patrón
  invalidatePattern(pattern: string): void {
    const regex = new RegExp(pattern);
    
    // Limpiar memoria
    for (const key of this.memoryCache.keys()) {
      if (regex.test(key)) {
        this.memoryCache.delete(key);
      }
    }

    // Limpiar localStorage
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const key = localStorage.key(i);
      if (key && key.startsWith('cache:') && regex.test(key.substring(6))) {
        localStorage.removeItem(key);
      }
    }

    clientLogger.debug('Cache pattern invalidated', { pattern });
  }

  // Limpiar caché expirado
  cleanup(): void {
    const now = Date.now();
    let cleaned = 0;

    // Limpiar memoria
    for (const [key, item] of this.memoryCache.entries()) {
      if (item.expiresAt <= now) {
        this.memoryCache.delete(key);
        cleaned++;
      }
    }

    // Limpiar localStorage
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const key = localStorage.key(i);
      if (key && key.startsWith('cache:')) {
        try {
          const stored = localStorage.getItem(key);
          if (stored) {
            const item = JSON.parse(stored);
            if (item.expiresAt <= now) {
              localStorage.removeItem(key);
              cleaned++;
            }
          }
        } catch (error) {
          // Item corrupto, eliminar
          localStorage.removeItem(key);
          cleaned++;
        }
      }
    }

    if (cleaned > 0) {
      clientLogger.info('Cache cleanup completed', { itemsCleaned: cleaned });
    }
  }

  // Obtener estadísticas del caché
  getStats() {
    const memorySize = this.memoryCache.size;
    let localStorageSize = 0;

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('cache:')) {
        localStorageSize++;
      }
    }

    return {
      memorySize,
      localStorageSize,
      maxSize: this.maxSize,
      defaultTTL: this.defaultTTL
    };
  }
}

// Instancia singleton
export const cacheManager = new CacheManager({
  maxSize: 50,
  ttl: 5 * 60 * 1000 // 5 minutos
});

// Hook para usar caché con React
export const useCache = <T>(
  key: string,
  fetcher: () => Promise<T>,
  options: CacheOptions = {}
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [fromCache, setFromCache] = useState(false);

  const fetchData = async (forceRefresh = false) => {
    setLoading(true);
    setError(null);

    try {
      // Intentar caché primero si no es refresh forzado
      if (!forceRefresh) {
        const cached = cacheManager.get<T>(key);
        if (cached) {
          setData(cached);
          setFromCache(true);
          setLoading(false);
          return cached;
        }
      }

      // Fetch fresh data
      setFromCache(false);
      const freshData = await fetcher();
      
      // Guardar en caché
      cacheManager.set(key, freshData, options);
      setData(freshData);
      
      return freshData;
    } catch (err) {
      setError(err as Error);
      clientLogger.error('Cache fetch error', { key, error: err });
    } finally {
      setLoading(false);
    }
  };

  const invalidate = () => {
    cacheManager.invalidate(key);
    setData(null);
    setFromCache(false);
  };

  const refresh = () => fetchData(true);

  return {
    data,
    loading,
    error,
    fromCache,
    fetchData,
    invalidate,
    refresh
  };
};

// Limpiar caché automáticamente cada 10 minutos
setInterval(() => {
  cacheManager.cleanup();
}, 10 * 60 * 1000);

import { useState } from 'react';