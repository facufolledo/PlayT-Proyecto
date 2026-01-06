import { motion } from 'framer-motion';

interface LoadingSkeletonProps {
  variant?: 'text' | 'card' | 'avatar' | 'button' | 'table' | 'tournament' | 'ranking';
  lines?: number;
  className?: string;
  animate?: boolean;
}

export default function LoadingSkeleton({ 
  variant = 'text', 
  lines = 1, 
  className = '',
  animate = true 
}: LoadingSkeletonProps) {
  const baseClasses = `bg-gradient-to-r from-cardBorder via-cardBorder/50 to-cardBorder rounded`;
  
  const shimmerAnimation = animate ? {
    backgroundPosition: ['200% 0', '-200% 0'],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'linear' as const
    }
  } : {};

  const shimmerClasses = animate ? 'bg-gradient-to-r from-cardBorder via-cardBorder/30 to-cardBorder bg-[length:200%_100%]' : baseClasses;

  const renderSkeleton = () => {
    switch (variant) {
      case 'text':
        return (
          <div className={`space-y-2 ${className}`}>
            {Array.from({ length: lines }).map((_, i) => (
              <motion.div
                key={i}
                className={`h-4 ${shimmerClasses} ${i === lines - 1 ? 'w-3/4' : 'w-full'}`}
                animate={animate ? shimmerAnimation : {}}
              />
            ))}
          </div>
        );

      case 'card':
        return (
          <div className={`p-4 border border-cardBorder rounded-lg ${className}`}>
            <div className="space-y-3">
              <motion.div 
                className={`h-6 w-3/4 ${shimmerClasses}`}
                animate={animate ? shimmerAnimation : {}}
              />
              <motion.div 
                className={`h-4 w-full ${shimmerClasses}`}
                animate={animate ? shimmerAnimation : {}}
              />
              <motion.div 
                className={`h-4 w-2/3 ${shimmerClasses}`}
                animate={animate ? shimmerAnimation : {}}
              />
            </div>
          </div>
        );

      case 'avatar':
        return (
          <motion.div 
            className={`w-10 h-10 rounded-full ${shimmerClasses} ${className}`}
            animate={animate ? shimmerAnimation : {}}
          />
        );

      case 'button':
        return (
          <motion.div 
            className={`h-10 w-24 rounded-lg ${shimmerClasses} ${className}`}
            animate={animate ? shimmerAnimation : {}}
          />
        );

      case 'table':
        return (
          <div className={`space-y-2 ${className}`}>
            {/* Header */}
            <div className="grid grid-cols-4 gap-4 p-3 border-b border-cardBorder">
              {Array.from({ length: 4 }).map((_, i) => (
                <motion.div 
                  key={i}
                  className={`h-4 ${shimmerClasses}`}
                  animate={animate ? shimmerAnimation : {}}
                />
              ))}
            </div>
            {/* Rows */}
            {Array.from({ length: 5 }).map((_, rowIndex) => (
              <div key={rowIndex} className="grid grid-cols-4 gap-4 p-3">
                {Array.from({ length: 4 }).map((_, colIndex) => (
                  <motion.div 
                    key={colIndex}
                    className={`h-4 ${shimmerClasses}`}
                    animate={animate ? shimmerAnimation : {}}
                    style={{ animationDelay: `${(rowIndex * 4 + colIndex) * 0.1}s` }}
                  />
                ))}
              </div>
            ))}
          </div>
        );

      case 'tournament':
        return (
          <div className={`p-4 border border-cardBorder rounded-lg ${className}`}>
            <div className="space-y-4">
              {/* Header */}
              <div className="flex items-center justify-between">
                <motion.div 
                  className={`h-6 w-1/3 ${shimmerClasses}`}
                  animate={animate ? shimmerAnimation : {}}
                />
                <motion.div 
                  className={`h-8 w-20 rounded ${shimmerClasses}`}
                  animate={animate ? shimmerAnimation : {}}
                />
              </div>
              
              {/* Info */}
              <div className="space-y-2">
                <motion.div 
                  className={`h-4 w-full ${shimmerClasses}`}
                  animate={animate ? shimmerAnimation : {}}
                />
                <motion.div 
                  className={`h-4 w-2/3 ${shimmerClasses}`}
                  animate={animate ? shimmerAnimation : {}}
                />
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="text-center">
                    <motion.div 
                      className={`h-8 w-full ${shimmerClasses} mb-1`}
                      animate={animate ? shimmerAnimation : {}}
                    />
                    <motion.div 
                      className={`h-3 w-3/4 mx-auto ${shimmerClasses}`}
                      animate={animate ? shimmerAnimation : {}}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case 'ranking':
        return (
          <div className={`space-y-2 ${className}`}>
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="flex items-center gap-4 p-3 border border-cardBorder rounded-lg">
                {/* Position */}
                <motion.div 
                  className={`w-8 h-6 ${shimmerClasses}`}
                  animate={animate ? shimmerAnimation : {}}
                />
                
                {/* Avatar */}
                <motion.div 
                  className={`w-10 h-10 rounded-full ${shimmerClasses}`}
                  animate={animate ? shimmerAnimation : {}}
                />
                
                {/* Name */}
                <div className="flex-1 space-y-1">
                  <motion.div 
                    className={`h-4 w-3/4 ${shimmerClasses}`}
                    animate={animate ? shimmerAnimation : {}}
                  />
                  <motion.div 
                    className={`h-3 w-1/2 ${shimmerClasses}`}
                    animate={animate ? shimmerAnimation : {}}
                  />
                </div>
                
                {/* Rating */}
                <motion.div 
                  className={`w-16 h-8 ${shimmerClasses}`}
                  animate={animate ? shimmerAnimation : {}}
                />
                
                {/* Category */}
                <motion.div 
                  className={`w-12 h-6 rounded-full ${shimmerClasses}`}
                  animate={animate ? shimmerAnimation : {}}
                />
              </div>
            ))}
          </div>
        );

      default:
        return (
          <motion.div 
            className={`h-4 w-full ${shimmerClasses} ${className}`}
            animate={animate ? shimmerAnimation : {}}
          />
        );
    }
  };

  return renderSkeleton();
}

// Componente específico para loading de listas
export function ListSkeleton({ 
  items = 5, 
  className = '' 
}: { 
  items?: number; 
  className?: string; 
}) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: items }).map((_, i) => (
        <LoadingSkeleton key={i} variant="card" />
      ))}
    </div>
  );
}

// Componente para loading de grids
export function GridSkeleton({ 
  items = 6, 
  columns = 3, 
  className = '' 
}: { 
  items?: number; 
  columns?: number; 
  className?: string; 
}) {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-${columns} gap-4 ${className}`}>
      {Array.from({ length: items }).map((_, i) => (
        <LoadingSkeleton key={i} variant="card" />
      ))}
    </div>
  );
}
