import { useState, useEffect, useRef, ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface LazyComponentProps {
  children: ReactNode;
  fallback?: ReactNode;
  delay?: number;
  threshold?: number;
  rootMargin?: string;
  className?: string;
}

export default function LazyComponent({
  children,
  fallback = <div className="animate-pulse bg-gray-200 h-20 rounded"></div>,
  delay = 0,
  threshold = 0.1,
  rootMargin = '50px',
  className = ''
}: LazyComponentProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [shouldRender, setShouldRender] = useState(false);
  const elementRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      {
        threshold,
        rootMargin
      }
    );

    if (elementRef.current) {
      observer.observe(elementRef.current);
    }

    return () => observer.disconnect();
  }, [threshold, rootMargin]);

  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        setShouldRender(true);
      }, delay);

      return () => clearTimeout(timer);
    }
  }, [isVisible, delay]);

  return (
    <div ref={elementRef} className={className}>
      <AnimatePresence mode="wait">
        {shouldRender ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            key="fallback"
          >
            {fallback}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}