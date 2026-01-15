/**
 * Hook para usar el sistema de cache
 */

import { useState, useEffect, useCallback } from 'react';
import { cacheManager } from '../utils/cacheManager';

interface UseCacheOptions<T> {
  key: string;
  fetcher: () => Promise<T>;
  ttl?: number;
  enabled?: boolean;
  refetchOnMount?: boolean;
}

interface UseCacheReturn<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  invalidate: () => void;
}

export function useCache<T>({
  key,
  fetcher,
  ttl,
  enabled = true,
  refetchOnMount = false
}: UseCacheOptions<T>): UseCacheReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const loadData = useCallback(async (forceRefetch = false) => {
    if (!enabled) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Si forzamos refetch, invalidar cache primero
      if (forceRefetch) {
        cacheManager.invalidate(key);
      }

      // Intentar obtener del cache o cargar
      const result = await cacheManager.getOrFetch(key, fetcher, ttl);
      setData(result);
    } catch (err) {
      setError(err as Error);
      console.error(`Error loading cached data for key "${key}":`, err);
    } finally {
      setLoading(false);
    }
  }, [key, fetcher, ttl, enabled]);

  const refetch = useCallback(async () => {
    await loadData(true);
  }, [loadData]);

  const invalidate = useCallback(() => {
    cacheManager.invalidate(key);
    setData(null);
  }, [key]);

  useEffect(() => {
    loadData(refetchOnMount);
  }, [loadData, refetchOnMount]);

  return {
    data,
    loading,
    error,
    refetch,
    invalidate
  };
}

/**
 * Hook simplificado para datos que no cambian frecuentemente
 */
export function useStaticCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl = 30 * 60 * 1000 // 30 minutos por defecto
) {
  return useCache({ key, fetcher, ttl, refetchOnMount: false });
}

/**
 * Hook para datos que cambian frecuentemente
 */
export function useDynamicCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl = 1 * 60 * 1000 // 1 minuto por defecto
) {
  return useCache({ key, fetcher, ttl, refetchOnMount: true });
}
