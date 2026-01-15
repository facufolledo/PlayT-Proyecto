/**
 * Componente de imagen con lazy loading
 */

import { useImageLazy } from '../hooks/useImageLazy';

interface ImageLazyProps {
  src: string;
  alt: string;
  className?: string;
  fallback?: string;
  threshold?: number;
  rootMargin?: string;
}

export function ImageLazy({
  src,
  alt,
  className = '',
  fallback = '/logo-drive.png',
  threshold = 0.1,
  rootMargin = '50px'
}: ImageLazyProps) {
  const { imgRef, imageSrc, isLoading, error } = useImageLazy(src, {
    threshold,
    rootMargin
  });

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {isLoading && (
        <div className="absolute inset-0 bg-gray-700 animate-pulse" />
      )}
      <img
        ref={imgRef}
        src={error ? fallback : imageSrc}
        alt={alt}
        className={`w-full h-full object-cover transition-opacity duration-300 ${
          isLoading ? 'opacity-0' : 'opacity-100'
        }`}
        loading="lazy"
      />
    </div>
  );
}

export default ImageLazy;
