import { motion, AnimatePresence } from 'framer-motion';
import { Database, RefreshCw, Clock, Zap } from 'lucide-react';

interface CacheIndicatorProps {
  fromCache: boolean;
  loading: boolean;
  onRefresh?: () => void;
  className?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export default function CacheIndicator({
  fromCache,
  loading,
  onRefresh,
  className = '',
  showLabel = true,
  size = 'sm'
}: CacheIndicatorProps) {
  const sizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  const iconSizes = {
    sm: 12,
    md: 16,
    lg: 20
  };

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`flex items-center gap-1 text-blue-500 ${sizeClasses[size]} ${className}`}
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        >
          <RefreshCw size={iconSizes[size]} />
        </motion.div>
        {showLabel && <span>Cargando...</span>}
      </motion.div>
    );
  }

  return (
    <AnimatePresence>
      {(fromCache || onRefresh) && (
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -10 }}
          className={`flex items-center gap-1 ${className}`}
        >
          {fromCache ? (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className={`flex items-center gap-1 text-green-500 ${sizeClasses[size]}`}
            >
              <motion.div
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [0.7, 1, 0.7]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <Zap size={iconSizes[size]} />
              </motion.div>
              {showLabel && <span>Caché</span>}
            </motion.div>
          ) : (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className={`flex items-center gap-1 text-blue-500 ${sizeClasses[size]}`}
            >
              <Database size={iconSizes[size]} />
              {showLabel && <span>Actualizado</span>}
            </motion.div>
          )}

          {onRefresh && (
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={onRefresh}
              className={`ml-1 text-textSecondary hover:text-primary transition-colors`}
              title="Actualizar datos"
            >
              <RefreshCw size={iconSizes[size]} />
            </motion.button>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Componente para mostrar tiempo desde la última actualización
export function LastUpdated({ 
  timestamp, 
  className = '' 
}: { 
  timestamp: number; 
  className?: string; 
}) {
  const getTimeAgo = (timestamp: number) => {
    const now = Date.now();
    const diff = now - timestamp;
    
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days > 0) return `hace ${days}d`;
    if (hours > 0) return `hace ${hours}h`;
    if (minutes > 0) return `hace ${minutes}m`;
    return 'ahora';
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={`flex items-center gap-1 text-xs text-textSecondary ${className}`}
    >
      <Clock size={12} />
      <span>{getTimeAgo(timestamp)}</span>
    </motion.div>
  );
}