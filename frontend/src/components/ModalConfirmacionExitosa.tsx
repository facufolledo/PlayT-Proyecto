import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, X, TrendingUp, TrendingDown, Users } from 'lucide-react';
import Button from './Button';

interface ModalConfirmacionExitosaProps {
  isOpen: boolean;
  onClose: () => void;
  confirmacionesTotales: number;
  faltanConfirmar: number;
  eloAplicado: boolean;
  cambioEloEstimado?: number;
  jugadoresFaltantes?: string[];
}

export default function ModalConfirmacionExitosa({
  isOpen,
  onClose,
  confirmacionesTotales,
  faltanConfirmar,
  eloAplicado,
  cambioEloEstimado = 0,
  jugadoresFaltantes = []
}: ModalConfirmacionExitosaProps) {
  const esPositivo = cambioEloEstimado > 0;

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
              {/* Header */}
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
                    <CheckCircle size={48} className="text-white" />
                  </motion.div>
                  <motion.h2
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="text-white font-black text-2xl"
                  >
                    {eloAplicado ? '¡Elo Actualizado!' : '¡Resultado Confirmado!'}
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
                {/* Estado de confirmaciones */}
                <div className="bg-secondary/10 border border-secondary/30 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-textSecondary text-sm">Confirmaciones:</span>
                    <span className="text-secondary font-bold text-lg">
                      {confirmacionesTotales}/3
                    </span>
                  </div>
                  <div className="w-full bg-background rounded-full h-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(confirmacionesTotales / 3) * 100}%` }}
                      transition={{ delay: 0.5, duration: 0.5 }}
                      className="bg-gradient-to-r from-secondary to-accent h-2 rounded-full"
                    />
                  </div>
                </div>

                {/* Cambio de Elo */}
                {cambioEloEstimado !== 0 && (
                  <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.6, type: 'spring', stiffness: 200 }}
                    className={`${esPositivo ? 'bg-gradient-to-br from-green-500/20 to-green-600/10 border-green-500/40' : 'bg-gradient-to-br from-red-500/20 to-red-600/10 border-red-500/40'} border-2 rounded-xl p-6 relative overflow-hidden`}
                  >
                    {/* Efecto de brillo */}
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent animate-shimmer" />
                    
                    <div className="relative z-10">
                      <div className="flex items-center justify-center gap-3 mb-3">
                        <motion.div
                          initial={{ rotate: -180, scale: 0 }}
                          animate={{ rotate: 0, scale: 1 }}
                          transition={{ delay: 0.7, type: 'spring', stiffness: 200 }}
                        >
                          {esPositivo ? (
                            <TrendingUp size={32} className="text-green-500" />
                          ) : (
                            <TrendingDown size={32} className="text-red-500" />
                          )}
                        </motion.div>
                        <div className="text-center">
                          <p className="text-textSecondary text-xs font-medium mb-1">
                            {eloAplicado ? 'Tu rating cambió' : 'Cambio estimado'}
                          </p>
                          <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ delay: 0.8, type: 'spring', stiffness: 150 }}
                            className={`font-black text-5xl ${esPositivo ? 'text-green-500' : 'text-red-500'}`}
                          >
                            {esPositivo ? '+' : ''}{cambioEloEstimado}
                          </motion.div>
                          <p className="text-textSecondary text-xs mt-1">
                            puntos de Elo
                          </p>
                        </div>
                      </div>
                      
                      {!eloAplicado && (
                        <p className="text-textSecondary text-xs text-center mt-3 opacity-70">
                          Este cambio se aplicará cuando todos confirmen
                        </p>
                      )}
                      
                      {eloAplicado && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 1 }}
                          className="text-center mt-3"
                        >
                          <p className={`text-sm font-bold ${esPositivo ? 'text-green-500' : 'text-red-500'}`}>
                            {esPositivo ? '¡Felicitaciones! 🎉' : '¡Sigue practicando! 💪'}
                          </p>
                        </motion.div>
                      )}
                    </div>
                  </motion.div>
                )}

                {/* Jugadores faltantes */}
                {!eloAplicado && faltanConfirmar > 0 && jugadoresFaltantes.length > 0 && (
                  <div className="bg-accent/10 border border-accent/30 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Users size={18} className="text-accent" />
                      <span className="text-accent font-bold text-sm">
                        Faltan {faltanConfirmar} confirmación{faltanConfirmar > 1 ? 'es' : ''}:
                      </span>
                    </div>
                    <div className="space-y-2">
                      {jugadoresFaltantes.map((jugador, index) => (
                        <div key={index} className="flex items-center gap-2 text-textPrimary text-sm">
                          <div className="w-2 h-2 rounded-full bg-accent" />
                          {jugador}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Mensaje final */}
                <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
                  <p className="text-textPrimary text-sm text-center">
                    {eloAplicado 
                      ? '¡Todos confirmaron! Tu rating ha sido actualizado.'
                      : 'Esperando que los demás jugadores confirmen el resultado.'}
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
