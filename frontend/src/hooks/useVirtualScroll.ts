/**
 * Hook para virtual scrolling (renderizar solo elementos visibles)
 */

import { useState, useEffect, useRef, useMemo } from 'react';

interface UseVirtualScrollOptions {
  itemHeight: number;
  containerHeight: number;
  overscan?: number;
}

export function useVirtualScroll<T>(
  items: T[],
  options: UseVirtualScrollOptions
) {
  const { itemHeight, containerHeight, overscan = 3 } = options;
  
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // Calcular qué items son visibles
  const { visibleItems, startIndex, endIndex, totalHeight, offsetY } = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );
    
    const visibleItems = items.slice(startIndex, endIndex + 1);
    const totalHeight = items.length * itemHeight;
    const offsetY = startIndex * itemHeight;

    return {
      visibleItems,
      startIndex,
      endIndex,
      totalHeight,
      offsetY
    };
  }, [items, scrollTop, itemHeight, containerHeight, overscan]);

  // Manejar scroll
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      setScrollTop(container.scrollTop);
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  return {
    containerRef,
    visibleItems,
    startIndex,
    endIndex,
    totalHeight,
    offsetY
  };
}
