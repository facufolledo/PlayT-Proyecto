import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, X, Clock, Users } from 'lucide-react';
import Button from './Button';

interface ModalAntiTrampaProps {
  isOpen: boolean;
  onClose: () => void;
  mensaje: string;
  jugadoresBloqueados?: string[];
  partidosJugados?: number;
  limite?: number;
}

export default function ModalAntiTrampa({
  isOpen,
  onClose,
  mensaje,
  jugadoresBloqueados = [],
  partidosJugados = 0,
  limite = 2
}: ModalAntiTrampaProps) {
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
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-cardBg rounded-2xl shadow-2xl max-w-md w-full border border-cardBorder overflow-hidden"
            >
              {/* Header con gradiente */}
              <div className="bg-gradient-to-r from-red-500 to-orange-500 p-6 relative">
                <button
                  onClick={onClose}
                  className="absolute top-4 right-4 text-white/80 hover:text-white transition-colors"
                >
                  <X size={24} />
                </button>
                
                <div className="flex items-center gap-3">
                  <div className="bg-white/20 backdrop-blur-sm rounded-full p-3">
                    <AlertTriangle size={32} className="text-white" />
                  </div>
                  <div>
                    <h2 className="text-white font-black text-2xl">
                      Límite Alcanzado
                    </h2>
                    <p className="text-white/80 text-sm">
                      Sistema Anti-Trampa
                    </p>
                  </div>
                </div>
              </div>

              {/* Contenido */}
              <div className="p-6 space-y-4">
                {/* Mensaje principal */}
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                  <p className="text-textPrimary text-sm leading-relaxed">
                    {mensaje}
                  </p>
                </div>

                {/* Estadísticas */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-background rounded-lg p-4 text-center">
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <Clock size={18} className="text-accent" />
                      <p className="text-textSecondary text-xs font-medium">
                        Partidos Jugados
                      </p>
                    </div>
                    <p className="text-accent text-3xl font-black">
                      {partidosJugados}/{limite}
                    </p>
                  </div>

                  <div className="bg-background rounded-lg p-4 text-center">
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <Users size={18} className="text-primary" />
                      <p className="text-textSecondary text-xs font-medium">
                        Jugadores
                      </p>
                    </div>
                    <p className="text-primary text-3xl font-black">
                      {jugadoresBloqueados.length}
                    </p>
                  </div>
                </div>

                {/* Lista de jugadores bloqueados */}
                {jugadoresBloqueados.length > 0 && (
                  <div className="bg-background rounded-lg p-4">
                    <p className="text-textSecondary text-xs font-medium mb-3">
                      Combinación de jugadores:
                    </p>
                    <div className="space-y-2">
                      {jugadoresBloqueados.map((jugador, index) => (
                        <div
                          key={index}
                          className="flex items-center gap-2 text-textPrimary text-sm"
                        >
                          <div className="w-2 h-2 rounded-full bg-accent" />
                          {jugador}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Información adicional */}
                <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
                  <p className="text-textSecondary text-xs leading-relaxed">
                    💡 <strong>¿Por qué existe este límite?</strong>
                    <br />
                    Para evitar abuso del sistema de ranking, existe un límite de{' '}
                    <strong>{limite} partidos cada 7 días</strong> entre la misma combinación de 3 jugadores.
                    <br />
                    <br />
                    Puedes jugar con otros jugadores mientras tanto.
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
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
