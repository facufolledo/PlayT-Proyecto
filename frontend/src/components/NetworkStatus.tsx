import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Wifi, WifiOff, RefreshCw, AlertTriangle } from 'lucide-react';
import { clientLogger } from '../utils/clientLogger';

interface NetworkStatusProps {
  className?: string;
}

export default function NetworkStatus({ className = '' }: NetworkStatusProps) {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showStatus, setShowStatus] = useState(false);
  const [lastOfflineTime, setLastOfflineTime] = useState<Date | null>(null);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setShowStatus(true);
      clientLogger.info('Network connection restored');
      
      if (lastOfflineTime) {
        const offlineDuration = Date.now() - lastOfflineTime.getTime();
        clientLogger.performance('Offline duration', offlineDuration, 'ms');
      }

      // Ocultar después de 3 segundos
      setTimeout(() => setShowStatus(false), 3000);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowStatus(true);
      setLastOfflineTime(new Date());
      clientLogger.warn('Network connection lost');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Mostrar estado inicial si está offline
    if (!navigator.onLine) {
      setShowStatus(true);
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [lastOfflineTime]);

  // Auto-hide después de estar online por un tiempo
  useEffect(() => {
    if (isOnline && showStatus) {
      const timer = setTimeout(() => {
        setShowStatus(false);
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [isOnline, showStatus]);

  return (
    <AnimatePresence>
      {showStatus && (
        <motion.div
          initial={{ opacity: 0, y: -50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.9 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className={`fixed top-4 right-4 z-50 ${className}`}
        >
          <div className={`
            flex items-center gap-2 px-4 py-2 rounded-lg shadow-lg border
            ${isOnline 
              ? 'bg-green-500 text-white border-green-600' 
              : 'bg-red-500 text-white border-red-600'
            }
          `}>
            <motion.div
              animate={{ 
                rotate: isOnline ? 0 : [0, 10, -10, 0],
                scale: isOnline ? 1 : [1, 1.1, 1]
              }}
              transition={{ 
                duration: isOnline ? 0.3 : 0.5,
                repeat: isOnline ? 0 : Infinity,
                repeatDelay: 1
              }}
            >
              {isOnline ? (
                <Wifi size={16} />
              ) : (
                <WifiOff size={16} />
              )}
            </motion.div>
            
            <span className="text-sm font-medium">
              {isOnline ? 'Conectado' : 'Sin conexión'}
            </span>

            {!isOnline && (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              >
                <RefreshCw size={14} />
              </motion.div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Hook para detectar estado de red
export const useNetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [connectionType, setConnectionType] = useState<string>('unknown');

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Detectar tipo de conexión si está disponible
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      setConnectionType(connection.effectiveType || 'unknown');

      const handleConnectionChange = () => {
        setConnectionType(connection.effectiveType || 'unknown');
        clientLogger.info('Connection type changed', { 
          type: connection.effectiveType,
          downlink: connection.downlink,
          rtt: connection.rtt
        });
      };

      connection.addEventListener('change', handleConnectionChange);

      return () => {
        window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
        connection.removeEventListener('change', handleConnectionChange);
      };
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return { isOnline, connectionType };
};