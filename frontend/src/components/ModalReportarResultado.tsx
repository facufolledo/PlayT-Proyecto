import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Trophy, AlertCircle } from 'lucide-react';
import Modal from './Modal';
import Button from './Button';
import Input from './Input';
import { Sala } from '../utils/types';
import { useSalas } from '../context/SalasContext';

interface ModalReportarResultadoProps {
  isOpen: boolean;
  onClose: () => void;
  sala: Sala | null;
}

export default function ModalReportarResultado({ isOpen, onClose, sala }: ModalReportarResultadoProps) {
  const { finalizarPartido, updateSala } = useSalas();
  const [sets, setSets] = useState([
    { equipoA: 0, equipoB: 0 },
    { equipoA: 0, equipoB: 0 },
    { equipoA: 0, equipoB: 0 }
  ]);

  if (!sala) return null;

  const handleSetChange = (index: number, equipo: 'equipoA' | 'equipoB', value: string) => {
    const numValue = parseInt(value) || 0;
    const newSets = [...sets];
    newSets[index] = { ...newSets[index], [equipo]: numValue };
    setSets(newSets);
  };

  const calcularGanador = () => {
    let setsGanadosA = 0;
    let setsGanadosB = 0;

    sets.forEach(set => {
      if (set.equipoA > set.equipoB) setsGanadosA++;
      else if (set.equipoB > set.equipoA) setsGanadosB++;
    });

    return { setsGanadosA, setsGanadosB };
  };

  const validarResultado = () => {
    const { setsGanadosA, setsGanadosB } = calcularGanador();
    
    // Debe haber un ganador claro (2 sets mínimo)
    if (setsGanadosA < 2 && setsGanadosB < 2) {
      return 'Debe haber un ganador con al menos 2 sets';
    }

    // Validar que cada set tenga puntos válidos
    for (let i = 0; i < sets.length; i++) {
      const set = sets[i];
      if (set.equipoA === 0 && set.equipoB === 0) continue; // Set no jugado
      
      if (set.equipoA === set.equipoB) {
        return `Set ${i + 1}: No puede haber empate`;
      }

      // Validar puntos mínimos (6 games para ganar)
      const ganador = set.equipoA > set.equipoB ? set.equipoA : set.equipoB;
      const perdedor = set.equipoA > set.equipoB ? set.equipoB : set.equipoA;

      if (ganador < 6) {
        return `Set ${i + 1}: El ganador debe tener al menos 6 games`;
      }

      if (ganador === 6 && perdedor > 4) {
        return `Set ${i + 1}: Si el ganador tiene 6, el perdedor debe tener máximo 4`;
      }

      if (ganador === 7 && (perdedor < 5 || perdedor > 6)) {
        return `Set ${i + 1}: Si el ganador tiene 7, el perdedor debe tener 5 o 6`;
      }
    }

    return null;
  };

  const handleFinalizar = () => {
    const error = validarResultado();
    if (error) {
      alert(error);
      return;
    }

    const { setsGanadosA, setsGanadosB } = calcularGanador();
    
    // Actualizar puntos en la sala
    updateSala(sala.id, {
      equipoA: { ...sala.equipoA, puntos: setsGanadosA },
      equipoB: { ...sala.equipoB, puntos: setsGanadosB }
    });

    // Finalizar partido con los sets
    finalizarPartido(sala.id, sets.filter(s => s.equipoA > 0 || s.equipoB > 0));
    
    onClose();
  };

  const { setsGanadosA, setsGanadosB } = calcularGanador();

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="bg-cardBg rounded-2xl p-8 w-full max-w-3xl border border-cardBorder">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-textPrimary">Reportar Resultado</h2>
          <button
            onClick={onClose}
            className="text-textSecondary hover:text-textPrimary transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Info del partido */}
        <div className="bg-background rounded-xl p-4 mb-6">
          <h3 className="text-lg font-bold text-textPrimary mb-2">{sala.nombre}</h3>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-textSecondary text-sm mb-1">Equipo A</p>
              <p className="text-textPrimary font-semibold">{sala.equipoA.jugador1.nombre}</p>
              <p className="text-textPrimary font-semibold">{sala.equipoA.jugador2.nombre}</p>
            </div>
            <div className="flex items-center justify-center">
              <span className="text-textSecondary font-bold">VS</span>
            </div>
            <div>
              <p className="text-textSecondary text-sm mb-1">Equipo B</p>
              <p className="text-textPrimary font-semibold">{sala.equipoB.jugador1.nombre}</p>
              <p className="text-textPrimary font-semibold">{sala.equipoB.jugador2.nombre}</p>
            </div>
          </div>
        </div>

        {/* Sets */}
        <div className="space-y-4 mb-6">
          <h3 className="text-lg font-bold text-textPrimary">Resultado por Sets</h3>
          
          {sets.map((set, index) => (
            <div key={index} className="bg-background rounded-xl p-4">
              <p className="text-textSecondary text-sm font-medium mb-3">Set {index + 1}</p>
              <div className="grid grid-cols-3 gap-4 items-center">
                <div>
                  <label className="block text-textSecondary text-xs mb-2">Equipo A</label>
                  <Input
                    type="number"
                    min="0"
                    max="7"
                    value={set.equipoA}
                    onChange={(e) => handleSetChange(index, 'equipoA', e.target.value)}
                    className="text-center text-2xl font-bold"
                  />
                </div>
                <div className="text-center text-textSecondary font-bold">-</div>
                <div>
                  <label className="block text-textSecondary text-xs mb-2">Equipo B</label>
                  <Input
                    type="number"
                    min="0"
                    max="7"
                    value={set.equipoB}
                    onChange={(e) => handleSetChange(index, 'equipoB', e.target.value)}
                    className="text-center text-2xl font-bold"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Resumen */}
        <div className="bg-gradient-to-br from-primary/10 to-secondary/10 rounded-xl p-6 mb-6 border border-primary/20">
          <div className="flex items-center justify-between mb-4">
            <div className="text-center flex-1">
              <p className="text-textSecondary text-sm mb-1">Sets Ganados</p>
              <p className="text-4xl font-black text-primary">{setsGanadosA}</p>
            </div>
            <div className="text-2xl font-bold text-textSecondary">-</div>
            <div className="text-center flex-1">
              <p className="text-textSecondary text-sm mb-1">Sets Ganados</p>
              <p className="text-4xl font-black text-secondary">{setsGanadosB}</p>
            </div>
          </div>

          {(setsGanadosA >= 2 || setsGanadosB >= 2) && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-center gap-2 py-3 bg-accent/20 rounded-lg"
            >
              <Trophy size={20} className="text-accent" />
              <span className="text-accent font-bold">
                Ganador: {setsGanadosA > setsGanadosB ? 'Equipo A' : 'Equipo B'}
              </span>
            </motion.div>
          )}
        </div>

        {/* Info */}
        <div className="bg-primary/10 border border-primary/30 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-3">
            <AlertCircle size={20} className="text-primary flex-shrink-0 mt-0.5" />
            <div className="text-sm text-textSecondary">
              <p className="font-semibold text-textPrimary mb-1">Reglas de validación:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>El ganador debe tener al menos 2 sets</li>
                <li>Cada set debe tener un ganador claro (no empates)</li>
                <li>Mínimo 6 games para ganar un set</li>
                <li>Si es 6-5, el siguiente game define (7-5 o 6-6 → tie-break)</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Acciones */}
        <div className="flex gap-3">
          <Button variant="secondary" onClick={onClose} className="flex-1">
            Cancelar
          </Button>
          <Button
            variant="primary"
            onClick={handleFinalizar}
            className="flex-1 flex items-center justify-center gap-2"
            disabled={setsGanadosA < 2 && setsGanadosB < 2}
          >
            <Trophy size={18} />
            Finalizar y Reportar
          </Button>
        </div>
      </div>
    </Modal>
  );
}
