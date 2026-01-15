/**
 * Hook para prefetching inteligente de datos
 */

import { useEffect, useRef } from 'react';
import { cacheManager } from '../utils/cacheManager';

interface UsePrefetchOptions {
  enabled?: boolean;
  delay?: number;
}

export function usePrefetch(
  key: string,
  fetcher: () => Promise<any>,
  options: UsePrefetchOptions = {}
) {
  const { enabled = true, delay = 0 } = options;
  const hasPrefetched = useRef(false);

  useEffect(() => {
    if (!enabled || hasPrefetched.current) return;

    const timer = setTimeout(async () => {
      // Solo prefetch si no está en cache
      if (!cacheManager.has(key)) {
        try {
          const data = await fetcher();
          cacheManager.set(key, data);
          console.log(`🔮 Prefetched: ${key}`);
        } catch (error) {
          console.warn(`Failed to prefetch ${key}:`, error);
        }
      }
      hasPrefetched.current = true;
    }, delay);

    return () => clearTimeout(timer);
  }, [key, fetcher, enabled, delay]);
}

/**
 * Hook para prefetch al hacer hover
 */
export function usePrefetchOnHover(
  key: string,
  fetcher: () => Promise<any>
) {
  const handleMouseEnter = () => {
    if (!cacheManager.has(key)) {
      fetcher()
        .then(data => {
          cacheManager.set(key, data);
          console.log(`🔮 Prefetched on hover: ${key}`);
        })
        .catch(error => {
          console.warn(`Failed to prefetch ${key}:`, error);
        });
    }
  };

  return { onMouseEnter: handleMouseEnter };
}
