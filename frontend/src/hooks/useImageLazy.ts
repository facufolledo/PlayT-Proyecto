/**
 * Hook para lazy loading de imágenes
 */

import { useState, useEffect, useRef } from 'react';

interface UseImageLazyOptions {
  threshold?: number;
  rootMargin?: string;
  placeholder?: string;
}

export function useImageLazy(
  src: string,
  options: UseImageLazyOptions = {}
) {
  const {
    threshold = 0.1,
    rootMargin = '50px',
    placeholder = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect fill="%23242B3D" width="400" height="300"/%3E%3C/svg%3E'
  } = options;

  const [imageSrc, setImageSrc] = useState(placeholder);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    if (!src) {
      setIsLoading(false);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // Cargar imagen cuando sea visible
            const img = new Image();
            
            img.onload = () => {
              setImageSrc(src);
              setIsLoading(false);
              setError(false);
            };
            
            img.onerror = () => {
              setError(true);
              setIsLoading(false);
            };
            
            img.src = src;
            
            // Dejar de observar
            if (imgRef.current) {
              observer.unobserve(imgRef.current);
            }
          }
        });
      },
      { threshold, rootMargin }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => {
      if (imgRef.current) {
        observer.unobserve(imgRef.current);
      }
    };
  }, [src, threshold, rootMargin]);

  return {
    imgRef,
    imageSrc,
    isLoading,
    error
  };
}
