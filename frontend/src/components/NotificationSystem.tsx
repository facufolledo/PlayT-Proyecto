import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle, Wifi, WifiOff } from 'lucide-react';
import { clientLogger } from '../utils/clientLogger';

export type NotificationType = 'success' | 'error' | 'warning' | 'info' | 'network';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number;
  persistent?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id'>) => string;
  removeNotification: (id: string) => void;
  clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = (notification: Omit<Notification, 'id'>): string => {
    const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newNotification: Notification = {
      ...notification,
      id,
      duration: notification.duration ?? (notification.type === 'error' ? 8000 : 5000)
    };

    setNotifications(prev => [...prev, newNotification]);

    // Log notification
    clientLogger.info('Notification shown', {
      type: notification.type,
      title: notification.title,
      id
    });

    // Auto remove if not persistent
    if (!notification.persistent && newNotification.duration) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }

    return id;
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
    clientLogger.debug('Notification removed', { id });
  };

  const clearAll = () => {
    setNotifications([]);
    clientLogger.debug('All notifications cleared');
  };

  return (
    <NotificationContext.Provider value={{
      notifications,
      addNotification,
      removeNotification,
      clearAll
    }}>
      {children}
      <NotificationContainer />
    </NotificationContext.Provider>
  );
}

function NotificationContainer() {
  const { notifications, removeNotification } = useNotifications();

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      <AnimatePresence>
        {notifications.map((notification) => (
          <NotificationItem
            key={notification.id}
            notification={notification}
            onClose={() => removeNotification(notification.id)}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}

function NotificationItem({ 
  notification, 
  onClose 
}: { 
  notification: Notification; 
  onClose: () => void; 
}) {
  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'error':
        return <AlertCircle className="text-red-500" size={20} />;
      case 'warning':
        return <AlertTriangle className="text-yellow-500" size={20} />;
      case 'network':
        return <WifiOff className="text-orange-500" size={20} />;
      default:
        return <Info className="text-blue-500" size={20} />;
    }
  };

  const getColors = () => {
    switch (notification.type) {
      case 'success':
        return 'border-green-200 bg-green-50 text-green-800';
      case 'error':
        return 'border-red-200 bg-red-50 text-red-800';
      case 'warning':
        return 'border-yellow-200 bg-yellow-50 text-yellow-800';
      case 'network':
        return 'border-orange-200 bg-orange-50 text-orange-800';
      default:
        return 'border-blue-200 bg-blue-50 text-blue-800';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 300, scale: 0.9 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 300, scale: 0.9 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className={`
        relative p-4 rounded-lg border shadow-lg backdrop-blur-sm
        ${getColors()}
      `}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          {getIcon()}
        </div>
        
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-sm">{notification.title}</h4>
          {notification.message && (
            <p className="text-sm opacity-90 mt-1">{notification.message}</p>
          )}
          
          {notification.action && (
            <button
              onClick={notification.action.onClick}
              className="mt-2 text-sm font-medium underline hover:no-underline"
            >
              {notification.action.label}
            </button>
          )}
        </div>

        <button
          onClick={onClose}
          className="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity"
        >
          <X size={16} />
        </button>
      </div>

      {/* Progress bar for timed notifications */}
      {!notification.persistent && notification.duration && (
        <motion.div
          className="absolute bottom-0 left-0 h-1 bg-current opacity-30 rounded-b-lg"
          initial={{ width: '100%' }}
          animate={{ width: '0%' }}
          transition={{ duration: notification.duration / 1000, ease: 'linear' }}
        />
      )}
    </motion.div>
  );
}

// Hook para usar notificaciones
export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
}

// Hook para notificaciones de red
export function useNetworkNotifications() {
  const { addNotification, removeNotification } = useNotifications();
  const [networkNotificationId, setNetworkNotificationId] = useState<string | null>(null);

  useEffect(() => {
    const handleOffline = () => {
      const id = addNotification({
        type: 'network',
        title: 'Sin conexión a internet',
        message: 'Algunas funciones pueden no estar disponibles',
        persistent: true
      });
      setNetworkNotificationId(id);
    };

    const handleOnline = () => {
      if (networkNotificationId) {
        removeNotification(networkNotificationId);
        setNetworkNotificationId(null);
      }
      
      addNotification({
        type: 'success',
        title: 'Conexión restaurada',
        message: 'Ya puedes usar todas las funciones',
        duration: 3000
      });
    };

    window.addEventListener('offline', handleOffline);
    window.addEventListener('online', handleOnline);

    // Check initial state
    if (!navigator.onLine) {
      handleOffline();
    }

    return () => {
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('online', handleOnline);
    };
  }, [addNotification, removeNotification, networkNotificationId]);
}

// Funciones de conveniencia
export const showSuccess = (title: string, message?: string) => {
  const { addNotification } = useNotifications();
  return addNotification({ type: 'success', title, message });
};

export const showError = (title: string, message?: string) => {
  const { addNotification } = useNotifications();
  return addNotification({ type: 'error', title, message });
};

export const showWarning = (title: string, message?: string) => {
  const { addNotification } = useNotifications();
  return addNotification({ type: 'warning', title, message });
};

export const showInfo = (title: string, message?: string) => {
  const { addNotification } = useNotifications();
  return addNotification({ type: 'info', title, message });
};
