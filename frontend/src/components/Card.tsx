import { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: ReactNode;
  className?: string;
  hoverable?: boolean;
  gradient?: boolean;
}

export default function Card({ children, className = '', hoverable = false, gradient = false }: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      whileHover={hoverable ? { 
        y: -8, 
        scale: 1.02,
        boxShadow: '0 20px 40px -5px rgba(0, 85, 255, 0.3)',
        borderColor: 'rgba(0, 85, 255, 0.5)'
      } : {}}
      className={`relative bg-cardBg border border-cardBorder rounded-2xl p-6 overflow-hidden transition-all duration-300 ${
        hoverable ? 'cursor-pointer' : ''
      } ${className}`}
    >
      {gradient && (
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 pointer-events-none" />
      )}
      {hoverable && (
        <div className="absolute inset-0 bg-gradient-to-br from-primary/0 to-primary/0 hover:from-primary/5 hover:to-transparent transition-all duration-300 pointer-events-none" />
      )}
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
}
