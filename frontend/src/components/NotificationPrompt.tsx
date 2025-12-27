/**
 * Componente para solicitar permiso de notificaciones
 */
import { useState, useEffect } from 'react';
import { Bell, BellOff, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNotifications } from '../hooks/useNotifications';
import { useAuth } from '../context/AuthContext';
import Button from './Button';

export default function NotificationPrompt() {
  const { usuario } = useAuth();
  const { isSupported, permissionStatus, requestPermission } = useNotifications(!!usuario);
  const [dismissed, setDismissed] = useState(false);
  const [loading, setLoading] = useState(false);

  // Verificar si ya se mostró antes
  useEffect(() => {
    const wasDismissed = localStorage.getItem('notification_prompt_dismissed');
    if (wasDismissed) setDismissed(true);
  }, []);

  // No mostrar si no está soportado, ya tiene permiso, o fue descartado
  if (!isSupported || permissionStatus === 'granted' || permissionStatus === 'denied' || dismissed) {
    return null;
  }

  const handleEnable = async () => {
    setLoading(true);
    await requestPermission();
    setLoading(false);
  };

  const handleDismiss = () => {
    setDismissed(true);
    localStorage.setItem('notification_prompt_dismissed', 'true');
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="bg-gradient-to-r from-primary/20 to-secondary/20 border border-primary/30 rounded-xl p-4 mb-4"
      >
        <div className="flex items-start gap-3">
          <div className="bg-primary/20 p-2 rounded-lg">
            <Bell className="text-primary" size={20} />
          </div>
          
          <div className="flex-1">
            <h3 className="font-bold text-textPrimary mb-1">
              Activa las notificaciones
            </h3>
            <p className="text-textSecondary text-sm mb-3">
              Recibe alertas cuando te inviten a torneos, confirmen resultados o actualicen tu rating.
            </p>
            
            <div className="flex gap-2">
              <Button
                variant="primary"
                size="sm"
                onClick={handleEnable}
                disabled={loading}
              >
                {loading ? 'Activando...' : 'Activar'}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleDismiss}
              >
                Ahora no
              </Button>
            </div>
          </div>

          <button
            onClick={handleDismiss}
            className="text-textSecondary hover:text-textPrimary transition-colors"
          >
            <X size={18} />
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
