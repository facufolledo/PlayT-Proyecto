import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, Wifi, WifiOff, X } from 'lucide-react';
import { ErrorInfo } from '../utils/errorHandler';

interface ErrorNotificationProps {
  error: ErrorInfo | null;
  onClose: () => void;
}

export default function ErrorNotification({ error, onClose }: ErrorNotificationProps) {
  if (!error) return null;

  const getIcon = () => {
    if (error.isNetworkError) {
      return <WifiOff size={20} className="text-red-500" />;
    }
    if (error.isServerError) {
      return <AlertCircle size={20} className="text-orange-500" />;
    }
    return <AlertCircle size={20} className="text-red-500" />;
  };

  const getBgColor = () => {
    if (error.isNetworkError) {
      return 'bg-red-500/10 border-red-500/30';
    }
    if (error.isServerError) {
      return 'bg-orange-500/10 border-orange-500/30';
    }
    return 'bg-red-500/10 border-red-500/30';
  };

  const getTextColor = () => {
    if (error.isNetworkError) {
      return 'text-red-500';
    }
    if (error.isServerError) {
      return 'text-orange-500';
    }
    return 'text-red-500';
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -50, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -50, scale: 0.95 }}
        className={`fixed top-4 right-4 z-50 max-w-md p-4 rounded-lg border ${getBgColor()} backdrop-blur-sm shadow-lg`}
      >
        <div className="flex items-start gap-3">
          {getIcon()}
          <div className="flex-1 min-w-0">
            <p className={`font-semibold text-sm ${getTextColor()}`}>
              {error.isNetworkError ? 'Error de Conexión' : 
               error.isServerError ? 'Error del Servidor' : 'Error'}
            </p>
            <p className="text-textSecondary text-xs mt-1">
              {error.message}
            </p>
            {error.statusCode && (
              <p className="text-textSecondary text-[10px] mt-1 opacity-70">
                Código: {error.statusCode}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-textSecondary hover:text-textPrimary transition-colors flex-shrink-0"
          >
            <X size={16} />
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}