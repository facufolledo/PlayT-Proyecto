import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, Plus, Minus, Trophy, RotateCcw } from 'lucide-react';
import Modal from './Modal';
import Button from './Button';
import { Sala } from '../utils/types';
import { useSalas } from '../context/SalasContext';

interface MarcadorInteractivoProps {
  isOpen: boolean;
  onClose: () => void;
  sala: Sala | null;
}

export default function MarcadorInteractivo({ isOpen, onClose, sala }: MarcadorInteractivoProps) {
  const { updateMarcador, finalizarPartido, updateSala } = useSalas();
  const [puntosA, setPuntosA] = useState(0);
  const [puntosB, setPuntosB] = useState(0);

  useEffect(() => {
    if (sala) {
      setPuntosA(sala.equipoA.puntos);
      setPuntosB(sala.equipoB.puntos);
    }
  }, [sala]);

  if (!sala) return null;

  const handleUpdatePuntos = (equipo: 'equipoA' | 'equipoB', delta: number) => {
    if (equipo === 'equipoA') {
      const newPuntos = Math.max(0, puntosA + delta);
      setPuntosA(newPuntos);
      updateMarcador(sala.id, 'equipoA', newPuntos);
    } else {
      const newPuntos = Math.max(0, puntosB + delta);
      setPuntosB(newPuntos);
      updateMarcador(sala.id, 'equipoB', newPuntos);
    }

    if (sala.estado === 'programada') {
      updateSala(sala.id, { estado: 'activa' });
    }
  };

  const handleFinalizar = () => {
    if (puntosA === puntosB) {
      alert('No puede haber empate. Ajusta el marcador.');
      return;
    }
    finalizarPartido(sala.id);
    onClose();
  };

  const handleReset = () => {
    if (confirm('¿Reiniciar el marcador a 0-0?')) {
      setPuntosA(0);
      setPuntosB(0);
      updateMarcador(sala.id, 'equipoA', 0);
      updateMarcador(sala.id, 'equipoB', 0);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="bg-cardBg rounded-3xl p-8 w-full max-w-5xl border border-cardBorder shadow-2xl">
        {/* Header mejorado */}
        <div className="flex items-center justify-between mb-8">
          <motion.div
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
          >
            <h2 className="text-3xl font-bold text-textPrimary mb-1">
              {sala.nombre}
            </h2>
            <p className="text-textSecondary text-sm flex items-center gap-2">
              <motion.span 
                animate={{ scale: [1, 1.2, 1], opacity: [1, 0.5, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="w-2 h-2 bg-primary rounded-full"
              />
              {new Date(sala.fecha).toLocaleDateString('es-ES', { 
                weekday: 'long', 
                day: 'numeric', 
                month: 'long', 
                year: 'numeric' 
              })}
            </p>
          </motion.div>
          <motion.button
            onClick={onClose}
            whileHover={{ scale: 1.1, rotate: 90 }}
            whileTap={{ scale: 0.9 }}
            className="text-textSecondary hover:text-textPrimary transition-colors bg-cardBorder rounded-full p-2"
          >
            <X size={24} />
          </motion.button>
        </div>

        {/* Marcador estilo eSports */}
        <div className="relative bg-gradient-to-br from-background to-cardBg rounded-2xl p-8 mb-8 border border-cardBorder overflow-hidden">
          
          <div className="grid grid-cols-3 gap-8 relative z-10">
            {/* Equipo A */}
            <motion.div
              className="relative"
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="relative bg-cardBg rounded-xl p-6 border border-primary/20 backdrop-blur-sm group-hover:border-primary/40 transition-colors">
                {/* Subtle glow */}
                <div className="absolute -inset-[1px] bg-gradient-to-br from-primary to-blue-600 opacity-0 group-hover:opacity-20 transition-opacity rounded-xl -z-10 blur" />
                <motion.div 
                  className="text-center mb-6"
                  whileHover={{ scale: 1.05 }}
                >
                  <div className="bg-primary/20 rounded-xl p-3 mb-4">
                    <h3 className="text-2xl font-black text-primary mb-3 tracking-wide">EQUIPO A</h3>
                    <p className="text-textPrimary font-bold text-lg">{sala.equipoA.jugador1.nombre}</p>
                    <p className="text-textPrimary font-bold text-lg">{sala.equipoA.jugador2.nombre}</p>
                  </div>
                </motion.div>

                <motion.div
                  className="text-center mb-6 relative"
                  key={puntosA}
                  initial={{ scale: 1.5, opacity: 0, rotateY: 180 }}
                  animate={{ scale: 1, opacity: 1, rotateY: 0 }}
                  transition={{ type: 'spring', stiffness: 200 }}
                >
                  <div className="relative inline-block">
                    <div className="absolute inset-0 bg-primary blur-2xl opacity-50" />
                    <div className="relative text-8xl font-black text-primary drop-shadow-2xl">
                      {puntosA}
                    </div>
                  </div>
                  <p className="text-textSecondary text-sm font-bold mt-2 uppercase tracking-wider">Puntos</p>
                </motion.div>

                <div className="flex gap-3">
                  <motion.div className="flex-1" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Button
                      variant="ghost"
                      onClick={() => handleUpdatePuntos('equipoA', -1)}
                      className="w-full flex items-center justify-center gap-2 bg-red-500/20 hover:bg-red-500/30 border-red-500/50"
                      disabled={puntosA === 0}
                    >
                      <Minus size={24} strokeWidth={3} />
                    </Button>
                  </motion.div>
                  <motion.div className="flex-1" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Button
                      variant="primary"
                      onClick={() => handleUpdatePuntos('equipoA', 1)}
                      className="w-full flex items-center justify-center gap-2"
                    >
                      <Plus size={24} strokeWidth={3} />
                    </Button>
                  </motion.div>
                </div>
              </div>
            </motion.div>

            {/* VS Central */}
            <div className="flex items-center justify-center">
              <motion.div
                animate={{ 
                  scale: [1, 1.05, 1]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                className="bg-cardBorder rounded-2xl w-20 h-20 flex items-center justify-center border border-cardBorder"
              >
                <span className="text-2xl font-bold text-textSecondary">VS</span>
              </motion.div>
            </div>

            {/* Equipo B */}
            <motion.div
              className="relative"
              initial={{ x: 50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="relative bg-cardBg rounded-xl p-6 border border-secondary/20 backdrop-blur-sm group-hover:border-secondary/40 transition-colors">
                {/* Subtle glow */}
                <div className="absolute -inset-[1px] bg-gradient-to-br from-secondary to-pink-600 opacity-0 group-hover:opacity-20 transition-opacity rounded-xl -z-10 blur" />
                <motion.div 
                  className="text-center mb-6"
                  whileHover={{ scale: 1.05 }}
                >
                  <div className="bg-secondary/20 rounded-xl p-3 mb-4">
                    <h3 className="text-2xl font-black text-secondary mb-3 tracking-wide">EQUIPO B</h3>
                    <p className="text-textPrimary font-bold text-lg">{sala.equipoB.jugador1.nombre}</p>
                    <p className="text-textPrimary font-bold text-lg">{sala.equipoB.jugador2.nombre}</p>
                  </div>
                </motion.div>

                <motion.div
                  className="text-center mb-6 relative"
                  key={puntosB}
                  initial={{ scale: 1.5, opacity: 0, rotateY: 180 }}
                  animate={{ scale: 1, opacity: 1, rotateY: 0 }}
                  transition={{ type: 'spring', stiffness: 200 }}
                >
                  <div className="relative inline-block">
                    <div className="absolute inset-0 bg-secondary blur-2xl opacity-50" />
                    <div className="relative text-8xl font-black text-secondary drop-shadow-2xl">
                      {puntosB}
                    </div>
                  </div>
                  <p className="text-textSecondary text-sm font-bold mt-2 uppercase tracking-wider">Puntos</p>
                </motion.div>

                <div className="flex gap-3">
                  <motion.div className="flex-1" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Button
                      variant="ghost"
                      onClick={() => handleUpdatePuntos('equipoB', -1)}
                      className="w-full flex items-center justify-center gap-2 bg-red-500/20 hover:bg-red-500/30 border-red-500/50"
                      disabled={puntosB === 0}
                    >
                      <Minus size={24} strokeWidth={3} />
                    </Button>
                  </motion.div>
                  <motion.div className="flex-1" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Button
                      variant="secondary"
                      onClick={() => handleUpdatePuntos('equipoB', 1)}
                      className="w-full flex items-center justify-center gap-2"
                    >
                      <Plus size={24} strokeWidth={3} />
                    </Button>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Acciones */}
        <div className="flex gap-3">
          <Button
            variant="secondary"
            onClick={handleReset}
            className="flex items-center justify-center gap-2"
          >
            <RotateCcw size={18} />
            Reiniciar
          </Button>
          <Button
            variant="primary"
            onClick={handleFinalizar}
            className="flex-1 flex items-center justify-center gap-2"
            disabled={puntosA === 0 && puntosB === 0}
          >
            <Trophy size={18} />
            Finalizar Partido
          </Button>
        </div>

        {puntosA !== puntosB && (puntosA > 0 || puntosB > 0) && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 text-center"
          >
            <p className="text-textSecondary text-sm">
              Ganador actual:{' '}
              <span className={puntosA > puntosB ? 'text-primary font-bold' : 'text-secondary font-bold'}>
                {puntosA > puntosB ? 'Equipo A' : 'Equipo B'}
              </span>
            </p>
          </motion.div>
        )}
      </div>
    </Modal>
  );
}
