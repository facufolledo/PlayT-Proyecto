import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertTriangle, XCircle, Info } from 'lucide-react';

interface ErrorMessageProps {
  message: string;
  type?: 'error' | 'warning' | 'info';
  onClose?: () => void;
  className?: string;
}

export default function ErrorMessage({ 
  message, 
  type = 'error', 
  onClose,
  className = '' 
}: ErrorMessageProps) {
  const config = {
    error: {
      icon: XCircle,
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/50',
      textColor: 'text-red-500',
      iconColor: 'text-red-500'
    },
    warning: {
      icon: AlertTriangle,
      bgColor: 'bg-yellow-500/10',
      borderColor: 'border-yellow-500/50',
      textColor: 'text-yellow-500',
      iconColor: 'text-yellow-500'
    },
    info: {
      icon: Info,
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/50',
      textColor: 'text-blue-500',
      iconColor: 'text-blue-500'
    }
  };

  const { icon: Icon, bgColor, borderColor, textColor, iconColor } = config[type];

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -10, scale: 0.95 }}
        transition={{ type: 'spring', duration: 0.3 }}
        className={`${bgColor} border ${borderColor} rounded-lg p-3 md:p-4 flex items-start gap-3 ${className}`}
      >
        <Icon size={20} className={`${iconColor} flex-shrink-0 mt-0.5`} />
        <p className={`${textColor} text-sm flex-1`}>{message}</p>
        {onClose && (
          <button
            onClick={onClose}
            className={`${textColor} hover:opacity-70 transition-opacity flex-shrink-0`}
          >
            <X size={18} />
          </button>
        )}
      </motion.div>
    </AnimatePresence>
  );
}

// Componente para lista de errores
interface ErrorListProps {
  errors: string[];
  onClear?: () => void;
  type?: 'error' | 'warning' | 'info';
}

export function ErrorList({ errors, onClear, type = 'error' }: ErrorListProps) {
  if (errors.length === 0) return null;

  return (
    <div className="space-y-2">
      {errors.map((error, index) => (
        <ErrorMessage
          key={index}
          message={error}
          type={type}
          onClose={errors.length === 1 ? onClear : undefined}
        />
      ))}
      {errors.length > 1 && onClear && (
        <button
          onClick={onClear}
          className="text-textSecondary hover:text-textPrimary text-sm transition-colors"
        >
          Limpiar todos
        </button>
      )}
    </div>
  );
}
