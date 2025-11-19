import { ReactNode } from 'react';
import { motion, useReducedMotion } from 'framer-motion';

interface CardProps {
  children: ReactNode;
  className?: string;
  hoverable?: boolean;
  gradient?: boolean;
  compact?: boolean;
}

export default function Card({ 
  children, 
  className = '', 
  hoverable = false, 
  gradient = false,
  compact = false 
}: CardProps) {
  const shouldReduceMotion = useReducedMotion();

  // Animaciones más suaves para móviles
  const hoverAnimation = hoverable && !shouldReduceMotion ? { 
    y: -4,
    scale: 1.01,
    boxShadow: '0 12px 24px -5px rgba(59, 130, 246, 0.25)',
    borderColor: 'rgba(59, 130, 246, 0.4)',
    transition: { duration: 0.2, ease: "easeOut" }
  } : {};

  const tapAnimation = hoverable ? {
    scale: 0.98,
    transition: { duration: 0.1 }
  } : {};

  return (
    <motion.div
      initial={shouldReduceMotion ? false : { opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      whileHover={hoverAnimation}
      whileTap={tapAnimation}
      className={`
        relative bg-cardBg/95 backdrop-blur-sm border border-cardBorder 
        rounded-lg md:rounded-xl 
        ${compact ? 'p-2.5 md:p-3' : 'p-3 md:p-5'} 
        overflow-hidden transition-all duration-200
        ${hoverable ? 'cursor-pointer active:scale-[0.98]' : ''}
        ${className}
      `}
    >
      {gradient && (
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 pointer-events-none" />
      )}
      {hoverable && (
        <div className="absolute inset-0 bg-gradient-to-br from-primary/0 to-primary/0 hover:from-primary/5 hover:to-transparent transition-all duration-200 pointer-events-none" />
      )}
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
}
