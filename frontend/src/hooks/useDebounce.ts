import { useState, useEffect } from 'react';

/**
 * Hook para debounce genérico
 * @param value - Valor a hacer debounce
 * @param delay - Delay en milisegundos
 * @returns Valor con debounce aplicado
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Hook específico para búsquedas con debounce
 * @param searchTerm - Término de búsqueda
 * @param delay - Delay en milisegundos (default: 300ms)
 * @returns Objeto con término con debounce y estado de búsqueda
 */
export function useSearchDebounce(searchTerm: string, delay: number = 300) {
  const [isSearching, setIsSearching] = useState(false);
  const debouncedSearchTerm = useDebounce(searchTerm, delay);

  useEffect(() => {
    if (searchTerm !== debouncedSearchTerm) {
      setIsSearching(true);
    } else {
      setIsSearching(false);
    }
  }, [searchTerm, debouncedSearchTerm]);

  return {
    debouncedSearchTerm,
    isSearching
  };
}