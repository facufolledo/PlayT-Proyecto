import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, CheckCircle, AlertTriangle, Trophy } from 'lucide-react';
import Modal from './Modal';
import Button from './Button';
import { Sala } from '../utils/types';
import { useSalas } from '../context/SalasContext';
import { useAuth } from '../context/AuthContext';

interface ModalConfirmarResultadoProps {
  isOpen: boolean;
  onClose: () => void;
  sala: Sala | null;
}

export default function ModalConfirmarResultado({ isOpen, onClose, sala }: ModalConfirmarResultadoProps) {
  const { confirmarResultado, disputarResultado } = useSalas();
  const { usuario } = useAuth();
  const [mostrarDisputa, setMostrarDisputa] = useState(false);
  const [motivoDisputa, setMotivoDisputa] = useState('');

  if (!sala || !usuario) return null;

  // Determinar en qué equipo está el usuario
  const estaEnEquipoA = 
    sala.equipoA.jugador1.id === usuario.id || 
    sala.equipoA.jugador2.id === usuario.id;
  const estaEnEquipoB = 
    sala.equipoB.jugador1.id === usuario.id || 
    sala.equipoB.jugador2.id === usuario.id;

  const miEquipo = estaEnEquipoA ? 'equipoA' : estaEnEquipoB ? 'equipoB' : null;
  const yaConfirme = miEquipo ? sala[miEquipo].confirmado : false;

  const handleConfirmar = () => {
    if (!miEquipo) return;
    confirmarResultado(sala.id, miEquipo, usuario.id);
    onClose();
  };

  const handleDisputar = () => {
    if (!motivoDisputa.trim()) {
      alert('Por favor indica el motivo de la disputa');
      return;
    }
    disputarResultado(sala.id, motivoDisputa);
    setMostrarDisputa(false);
    setMotivoDisputa('');
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="bg-cardBg rounded-2xl p-8 w-full max-w-2xl border border-cardBorder">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-textPrimary">Confirmar Resultado</h2>
          <button
            onClick={onClose}
            className="text-textSecondary hover:text-textPrimary transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Información del partido */}
        <div className="bg-background rounded-xl p-6 mb-6">
          <h3 className="text-lg font-bold text-textPrimary mb-4">{sala.nombre}</h3>
          
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <p className="text-textSecondary text-sm mb-2">Equipo A</p>
              <p className="text-textPrimary font-semibold">{sala.equipoA.jugador1.nombre}</p>
              <p className="text-textPrimary font-semibold">{sala.equipoA.jugador2.nombre}</p>
              <p className="text-4xl font-black text-primary mt-3">{sala.equipoA.puntos}</p>
              {sala.equipoA.confirmado && (
                <div className="flex items-center justify-center gap-1 mt-2 text-secondary text-sm">
                  <CheckCircle size={16} />
                  <span>Confirmado</span>
                </div>
              )}
            </div>

            <div className="flex items-center justify-center">
              <span className="text-2xl font-bold text-textSecondary">VS</span>
            </div>

            <div className="text-center">
              <p className="text-textSecondary text-sm mb-2">Equipo B</p>
              <p className="text-textPrimary font-semibold">{sala.equipoB.jugador1.nombre}</p>
              <p className="text-textPrimary font-semibold">{sala.equipoB.jugador2.nombre}</p>
              <p className="text-4xl font-black text-secondary mt-3">{sala.equipoB.puntos}</p>
              {sala.equipoB.confirmado && (
                <div className="flex items-center justify-center gap-1 mt-2 text-secondary text-sm">
                  <CheckCircle size={16} />
                  <span>Confirmado</span>
                </div>
              )}
            </div>
          </div>

          {/* Detalle de sets */}
          {sala.sets && sala.sets.length > 0 && (
            <div className="mt-4 space-y-2">
              <p className="text-textSecondary text-sm font-medium">Detalle por sets:</p>
              <div className="grid grid-cols-3 gap-2">
                {sala.sets.map((set, index) => (
                  <div key={index} className="bg-cardBg rounded-lg p-2 text-center">
                    <p className="text-textSecondary text-xs mb-1">Set {index + 1}</p>
                    <p className="text-textPrimary font-bold">
                      {set.equipoA} - {set.equipoB}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {sala.ganador && (
            <div className="flex items-center justify-center gap-2 py-3 bg-accent/10 rounded-lg mt-4">
              <Trophy size={20} className="text-accent" />
              <span className="text-accent font-bold">
                Ganador: {sala.ganador === 'equipoA' ? 'Equipo A' : 'Equipo B'}
              </span>
            </div>
          )}
        </div>

        {/* Estado de confirmación */}
        <div className="mb-6">
          {yaConfirme ? (
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-secondary/10 border border-secondary/30 rounded-xl p-4 text-center"
            >
              <CheckCircle size={48} className="text-secondary mx-auto mb-2" />
              <p className="text-secondary font-bold text-lg">Ya confirmaste este resultado</p>
              <p className="text-textSecondary text-sm mt-1">
                Esperando confirmación del otro equipo
              </p>
            </motion.div>
          ) : (
            <div className="bg-primary/10 border border-primary/30 rounded-xl p-4 text-center">
              <AlertTriangle size={48} className="text-primary mx-auto mb-2" />
              <p className="text-textPrimary font-bold text-lg">Confirma el resultado</p>
              <p className="text-textSecondary text-sm mt-1">
                ¿Estás de acuerdo con el resultado mostrado?
              </p>
            </div>
          )}
        </div>

        {/* Acciones */}
        {!yaConfirme && !mostrarDisputa && (
          <div className="flex gap-3">
            <Button
              variant="ghost"
              onClick={() => setMostrarDisputa(true)}
              className="flex-1"
            >
              Disputar Resultado
            </Button>
            <Button
              variant="primary"
              onClick={handleConfirmar}
              className="flex-1 flex items-center justify-center gap-2"
            >
              <CheckCircle size={20} />
              Confirmar Resultado
            </Button>
          </div>
        )}

        {/* Formulario de disputa */}
        {mostrarDisputa && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div>
              <label className="block text-textSecondary text-sm font-medium mb-2">
                Motivo de la disputa
              </label>
              <textarea
                value={motivoDisputa}
                onChange={(e) => setMotivoDisputa(e.target.value)}
                placeholder="Explica por qué no estás de acuerdo con el resultado..."
                className="w-full bg-background border border-cardBorder rounded-xl px-4 py-3 text-textPrimary placeholder-textSecondary focus:outline-none focus:border-primary transition-colors resize-none"
                rows={4}
              />
            </div>
            <div className="flex gap-3">
              <Button
                variant="ghost"
                onClick={() => {
                  setMostrarDisputa(false);
                  setMotivoDisputa('');
                }}
                className="flex-1"
              >
                Cancelar
              </Button>
              <Button
                variant="secondary"
                onClick={handleDisputar}
                className="flex-1"
              >
                Enviar Disputa
              </Button>
            </div>
          </motion.div>
        )}
      </div>
    </Modal>
  );
}
