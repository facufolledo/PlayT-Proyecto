import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Users, Trophy, AlertCircle, CheckCircle } from 'lucide-react';
import Button from './Button';
import { Torneo } from '../utils/types';
import { useAuth } from '../context/AuthContext';

interface ModalInscripcionTorneoProps {
  isOpen: boolean;
  onClose: () => void;
  torneo: Torneo | null;
  onInscribir: (torneoId: string) => void;
}

export default function ModalInscripcionTorneo({ isOpen, onClose, torneo, onInscribir }: ModalInscripcionTorneoProps) {
  const { usuario } = useAuth();
  const [confirmado, setConfirmado] = useState(false);

  // Helper para parsear fechas sin problemas de zona horaria
  const parseFechaSinZonaHoraria = (fechaISO: string): Date => {
    const [year, month, day] = fechaISO.split('-').map(Number);
    return new Date(year, month - 1, day);
  };

  if (!torneo || !usuario) return null;

  const handleInscribir = () => {
    onInscribir(torneo.id);
    setConfirmado(true);
    setTimeout(() => {
      setConfirmado(false);
      onClose();
    }, 2000);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />
          
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="bg-cardBg rounded-2xl border border-cardBorder shadow-2xl w-full max-w-lg"
            >
              <div className="bg-cardBg border-b border-cardBorder p-6 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="bg-accent/10 p-3 rounded-lg">
                    <Trophy className="text-accent" size={24} />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-textPrimary">Inscripción al Torneo</h2>
                    <p className="text-textSecondary text-sm">{torneo.nombre}</p>
                  </div>
                </div>
                <motion.button
                  whileHover={{ scale: 1.1, rotate: 90 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={onClose}
                  className="text-textSecondary hover:text-textPrimary transition-colors"
                >
                  <X size={24} />
                </motion.button>
              </div>

              <div className="p-6">
                {!confirmado ? (
                  <>
                    {/* Información del torneo */}
                    <div className="space-y-4 mb-6">
                      <div className="bg-background rounded-lg p-4 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-textSecondary text-sm">Formato:</span>
                          <span className="text-textPrimary font-bold">
                            {torneo.formato === 'eliminacion-simple' && 'Eliminación Simple'}
                            {torneo.formato === 'eliminacion-doble' && 'Eliminación Doble'}
                            {torneo.formato === 'round-robin' && 'Round Robin'}
                            {torneo.formato === 'grupos' && 'Por Grupos'}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-textSecondary text-sm">Categoría:</span>
                          <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-bold">
                            {torneo.categoria}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-textSecondary text-sm">Participantes:</span>
                          <span className="text-textPrimary font-bold flex items-center gap-2">
                            <Users size={16} />
                            {torneo.participantes} jugadores
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-textSecondary text-sm">Fechas:</span>
                          <span className="text-textPrimary font-bold text-sm">
                            {parseFechaSinZonaHoraria(torneo.fechaInicio).toLocaleDateString('es-ES', { 
                              day: 'numeric', 
                              month: 'short' 
                            })} - {parseFechaSinZonaHoraria(torneo.fechaFin).toLocaleDateString('es-ES', { 
                              day: 'numeric', 
                              month: 'short' 
                            })}
                          </span>
                        </div>
                      </div>

                      {torneo.descripcion && (
                        <div className="bg-background rounded-lg p-4">
                          <p className="text-textSecondary text-sm">{torneo.descripcion}</p>
                        </div>
                      )}
                    </div>

                    {/* Advertencia */}
                    <div className="bg-accent/10 border border-accent/30 rounded-lg p-4 mb-6 flex items-start gap-3">
                      <AlertCircle className="text-accent flex-shrink-0 mt-0.5" size={20} />
                      <div>
                        <p className="text-accent font-bold text-sm mb-1">Importante</p>
                        <p className="text-textSecondary text-xs">
                          Al inscribirte te comprometes a participar en el torneo. 
                          Asegúrate de estar disponible en las fechas indicadas.
                        </p>
                      </div>
                    </div>

                    {/* Botones */}
                    <div className="flex gap-3">
                      <Button
                        variant="ghost"
                        onClick={onClose}
                        className="flex-1"
                      >
                        Cancelar
                      </Button>
                      <Button
                        variant="accent"
                        onClick={handleInscribir}
                        className="flex-1"
                      >
                        Confirmar Inscripción
                      </Button>
                    </div>
                  </>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center py-8"
                  >
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", stiffness: 200 }}
                      className="bg-secondary/10 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4"
                    >
                      <CheckCircle size={40} className="text-secondary" />
                    </motion.div>
                    <h3 className="text-2xl font-bold text-textPrimary mb-2">
                      ¡Inscripción Exitosa!
                    </h3>
                    <p className="text-textSecondary">
                      Te has inscrito al torneo {torneo.nombre}
                    </p>
                  </motion.div>
                )}
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
