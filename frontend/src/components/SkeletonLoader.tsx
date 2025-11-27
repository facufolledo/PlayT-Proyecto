import { motion } from 'framer-motion';

interface SkeletonLoaderProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'card';
  width?: string;
  height?: string;
  count?: number;
}

export default function SkeletonLoader({ 
  className = '', 
  variant = 'rectangular',
  width = '100%',
  height = '20px',
  count = 1
}: SkeletonLoaderProps) {
  const baseClasses = 'bg-gradient-to-r from-cardBorder via-cardBorder/50 to-cardBorder animate-pulse';
  
  const variantClasses = {
    text: 'rounded h-4',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
    card: 'rounded-xl'
  };

  const skeletons = Array.from({ length: count }, (_, i) => (
    <motion.div
      key={i}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: i * 0.05 }}
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      style={{ width, height }}
    />
  ));

  return count > 1 ? <div className="space-y-3">{skeletons}</div> : skeletons[0];
}

// Skeleton para tarjeta de sala
export function SalaCardSkeleton() {
  return (
    <div className="bg-cardBg rounded-xl p-4 border border-cardBorder">
      <div className="flex items-center justify-between mb-3">
        <SkeletonLoader variant="text" width="60%" height="24px" />
        <SkeletonLoader variant="circular" width="40px" height="40px" />
      </div>
      <div className="space-y-2 mb-3">
        <SkeletonLoader variant="text" width="80%" />
        <SkeletonLoader variant="text" width="60%" />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <SkeletonLoader variant="rectangular" height="60px" />
        <SkeletonLoader variant="rectangular" height="60px" />
      </div>
    </div>
  );
}

// Skeleton para tarjeta de partido en historial
export function PartidoCardSkeleton() {
  return (
    <div className="bg-cardBg rounded-xl p-4 border border-cardBorder">
      <div className="flex items-center justify-between mb-3">
        <SkeletonLoader variant="text" width="40%" height="20px" />
        <SkeletonLoader variant="rectangular" width="60px" height="24px" />
      </div>
      <div className="grid grid-cols-2 gap-4 mb-3">
        <div className="space-y-2">
          <SkeletonLoader variant="text" width="80%" />
          <SkeletonLoader variant="text" width="60%" />
        </div>
        <div className="space-y-2">
          <SkeletonLoader variant="text" width="80%" />
          <SkeletonLoader variant="text" width="60%" />
        </div>
      </div>
      <div className="flex items-center justify-center gap-4 py-2">
        <SkeletonLoader variant="text" width="40px" height="32px" />
        <SkeletonLoader variant="text" width="20px" height="24px" />
        <SkeletonLoader variant="text" width="40px" height="32px" />
      </div>
    </div>
  );
}

// Skeleton para perfil de usuario
export function PerfilSkeleton() {
  return (
    <div className="bg-cardBg rounded-2xl p-6 border border-cardBorder">
      <div className="flex flex-col items-center mb-6">
        <SkeletonLoader variant="circular" width="120px" height="120px" className="mb-4" />
        <SkeletonLoader variant="text" width="200px" height="28px" className="mb-2" />
        <SkeletonLoader variant="text" width="150px" height="20px" />
      </div>
      <div className="space-y-3">
        <SkeletonLoader variant="rectangular" height="60px" />
        <SkeletonLoader variant="rectangular" height="40px" />
        <SkeletonLoader variant="rectangular" height="40px" />
      </div>
    </div>
  );
}

// Skeleton para lista de ranking
export function RankingItemSkeleton() {
  return (
    <div className="flex items-center gap-3 p-3 bg-cardBg rounded-lg border border-cardBorder">
      <SkeletonLoader variant="text" width="30px" height="24px" />
      <SkeletonLoader variant="circular" width="40px" height="40px" />
      <div className="flex-1 space-y-2">
        <SkeletonLoader variant="text" width="60%" />
        <SkeletonLoader variant="text" width="40%" />
      </div>
      <SkeletonLoader variant="text" width="60px" height="28px" />
    </div>
  );
}
