import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, X } from 'lucide-react';
import Button from './Button';

interface ModalExitoProps {
  isOpen: boolean;
  onClose: () => void;
  titulo: string;
  mensaje: string;
  icono?: React.ReactNode;
}

export default function ModalExito({
  isOpen,
  onClose,
  titulo,
  mensaje,
  icono
}: ModalExitoProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              transition={{ type: 'spring', duration: 0.5 }}
              className="bg-cardBg rounded-2xl shadow-2xl max-w-md w-full border border-cardBorder overflow-hidden"
            >
              {/* Header con gradiente */}
              <div className="bg-gradient-to-r from-secondary to-accent p-6 relative">
                <button
                  onClick={onClose}
                  className="absolute top-4 right-4 text-white/80 hover:text-white transition-colors"
                >
                  <X size={24} />
                </button>
                
                <div className="flex flex-col items-center text-center">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                    className="bg-white/20 backdrop-blur-sm rounded-full p-4 mb-4"
                  >
                    {icono || <CheckCircle size={48} className="text-white" />}
                  </motion.div>
                  <motion.h2
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="text-white font-black text-2xl"
                  >
                    {titulo}
                  </motion.h2>
                </div>
              </div>

              {/* Contenido */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="p-6 space-y-4"
              >
                {/* Mensaje */}
                <div className="bg-secondary/10 border border-secondary/30 rounded-lg p-4">
                  <p className="text-textPrimary text-sm leading-relaxed text-center">
                    {mensaje}
                  </p>
                </div>

                {/* Botón */}
                <Button
                  variant="primary"
                  onClick={onClose}
                  className="w-full"
                >
                  Entendido
                </Button>
              </motion.div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
