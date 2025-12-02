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


// Skeleton para tarjeta de torneo
export function TorneoCardSkeleton() {
  return (
    <div className="bg-card rounded-xl p-4 border border-cardBorder">
      <div className="flex items-center gap-3 mb-3">
        <SkeletonLoader variant="circular" width="48px" height="48px" />
        <div className="flex-1 space-y-2">
          <SkeletonLoader variant="text" width="70%" height="20px" />
          <SkeletonLoader variant="text" width="40%" height="16px" />
        </div>
      </div>
      <div className="flex gap-2 mb-3">
        <SkeletonLoader variant="rectangular" width="80px" height="24px" />
        <SkeletonLoader variant="rectangular" width="100px" height="24px" />
      </div>
      <div className="grid grid-cols-3 gap-2">
        <SkeletonLoader variant="rectangular" height="50px" />
        <SkeletonLoader variant="rectangular" height="50px" />
        <SkeletonLoader variant="rectangular" height="50px" />
      </div>
    </div>
  );
}

// Skeleton para lista de parejas de torneo
export function TorneoParejaSkeleton() {
  return (
    <div className="flex items-center gap-3 p-3 bg-background rounded-lg border border-cardBorder">
      <SkeletonLoader variant="text" width="30px" height="24px" />
      <div className="flex-1 space-y-1">
        <SkeletonLoader variant="text" width="80%" height="18px" />
        <SkeletonLoader variant="text" width="50%" height="14px" />
      </div>
      <SkeletonLoader variant="rectangular" width="70px" height="28px" />
    </div>
  );
}

// Skeleton para zona de torneo
export function TorneoZonaSkeleton() {
  return (
    <div className="bg-card rounded-xl p-4 border border-cardBorder">
      <SkeletonLoader variant="text" width="120px" height="24px" className="mb-4" />
      <div className="space-y-2">
        <TorneoParejaSkeleton />
        <TorneoParejaSkeleton />
        <TorneoParejaSkeleton />
      </div>
    </div>
  );
}

// Skeleton para fixture de torneo
export function TorneoFixtureSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="bg-card rounded-xl p-4 border border-cardBorder">
          <div className="flex items-center justify-between mb-3">
            <SkeletonLoader variant="text" width="100px" height="20px" />
            <SkeletonLoader variant="rectangular" width="80px" height="24px" />
          </div>
          <div className="flex items-center justify-between">
            <div className="flex-1 space-y-1">
              <SkeletonLoader variant="text" width="70%" height="16px" />
            </div>
            <SkeletonLoader variant="text" width="50px" height="24px" />
            <div className="flex-1 space-y-1 text-right">
              <SkeletonLoader variant="text" width="70%" height="16px" className="ml-auto" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// Skeleton para bracket de playoffs
export function TorneoPlayoffsSkeleton() {
  return (
    <div className="bg-card rounded-xl p-6 border border-cardBorder">
      <div className="flex items-center gap-2 mb-6">
        <SkeletonLoader variant="circular" width="32px" height="32px" />
        <SkeletonLoader variant="text" width="180px" height="24px" />
      </div>
      <div className="flex gap-8 overflow-x-auto pb-4">
        {[1, 2, 3, 4].map((col) => (
          <div key={col} className="flex flex-col gap-4 min-w-[200px]">
            <SkeletonLoader variant="text" width="80px" height="20px" className="mb-2" />
            {[1, 2].map((match) => (
              <div key={match} className="bg-background rounded-lg p-3 border border-cardBorder">
                <SkeletonLoader variant="text" width="90%" height="16px" className="mb-2" />
                <SkeletonLoader variant="text" width="90%" height="16px" />
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

// Skeleton para detalle de torneo completo
export function TorneoDetalleSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-card rounded-xl p-6 border border-cardBorder">
        <div className="flex items-center gap-4 mb-4">
          <SkeletonLoader variant="circular" width="64px" height="64px" />
          <div className="flex-1 space-y-2">
            <SkeletonLoader variant="text" width="60%" height="28px" />
            <SkeletonLoader variant="text" width="40%" height="20px" />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <SkeletonLoader variant="rectangular" height="70px" />
          <SkeletonLoader variant="rectangular" height="70px" />
          <SkeletonLoader variant="rectangular" height="70px" />
        </div>
      </div>
      
      {/* Tabs */}
      <div className="flex gap-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <SkeletonLoader key={i} variant="rectangular" width="100px" height="36px" />
        ))}
      </div>
      
      {/* Content */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <TorneoZonaSkeleton />
        <TorneoZonaSkeleton />
      </div>
    </div>
  );
}
