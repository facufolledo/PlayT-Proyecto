import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Users, ArrowRight, ArrowLeft, Save, AlertCircle } from 'lucide-react';
import Modal from './Modal';
import Button from './Button';
import { Sala } from '../utils/types';

interface AsignarEquiposProps {
  isOpen: boolean;
  onClose: () => void;
  sala: Sala;
  onGuardar: (equipo1: string[], equipo2: string[]) => void;
}

interface Jugador {
  id: string;
  nombre: string;
  rating?: number;
}

export default function AsignarEquipos({ isOpen, onClose, sala, onGuardar }: AsignarEquiposProps) {
  const jugadores: Jugador[] = sala.jugadores || [];
  
  const [equipo1, setEquipo1] = useState<Jugador[]>([]);
  const [equipo2, setEquipo2] = useState<Jugador[]>([]);
  const [sinAsignar, setSinAsignar] = useState<Jugador[]>(jugadores);
  const [jugadorSeleccionado, setJugadorSeleccionado] = useState<string | null>(null);

  const moverAEquipo1 = (jugador: Jugador) => {
    if (equipo1.length >= 2) return;
    
    setSinAsignar(prev => prev.filter(j => j.id !== jugador.id));
    setEquipo2(prev => prev.filter(j => j.id !== jugador.id));
    setEquipo1(prev => [...prev, jugador]);
    setJugadorSeleccionado(null);
  };

  const moverAEquipo2 = (jugador: Jugador) => {
    if (equipo2.length >= 2) return;
    
    setSinAsignar(prev => prev.filter(j => j.id !== jugador.id));
    setEquipo1(prev => prev.filter(j => j.id !== jugador.id));
    setEquipo2(prev => [...prev, jugador]);
    setJugadorSeleccionado(null);
  };

  const moverASinAsignar = (jugador: Jugador) => {
    setEquipo1(prev => prev.filter(j => j.id !== jugador.id));
    setEquipo2(prev => prev.filter(j => j.id !== jugador.id));
    setSinAsignar(prev => [...prev, jugador]);
    setJugadorSeleccionado(null);
  };

  const calcularPromedioRating = (equipo: Jugador[]) => {
    if (equipo.length === 0) return 0;
    const suma = equipo.reduce((acc, j) => acc + (j.rating || 1000), 0);
    return Math.round(suma / equipo.length);
  };

  const diferencia = Math.abs(
    calcularPromedioRating(equipo1) - calcularPromedioRating(equipo2)
  );

  const equiposBalanceados = diferencia <= 100;
  const puedeGuardar = equipo1.length === 2 && equipo2.length === 2;

  const handleGuardar = () => {
    if (!puedeGuardar) return;
    
    onGuardar(
      equipo1.map(j => j.id),
      equipo2.map(j => j.id)
    );
    onClose();
  };

  const asignacionAutomatica = () => {
    const jugadoresOrdenados = [...jugadores].sort((a, b) => 
      (b.rating || 1000) - (a.rating || 1000)
    );

    setEquipo1([jugadoresOrdenados[0], jugadoresOrdenados[3]]);
    setEquipo2([jugadoresOrdenados[1], jugadoresOrdenados[2]]);
    setSinAsignar([]);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="bg-cardBg rounded-2xl p-8 w-full max-w-5xl max-h-[90vh] overflow-y-auto border border-cardBorder">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-textPrimary flex items-center gap-2">
            <Users size={28} />
            Asignar Equipos
          </h2>
          <button
            onClick={onClose}
            className="text-textSecondary hover:text-textPrimary transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Botón de asignación automática */}
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={asignacionAutomatica}
            className="w-full flex items-center justify-center gap-2"
          >
            <Users size={18} />
            Asignación Automática (Balanceada)
          </Button>
        </div>

        {/* Jugadores sin asignar */}
        {sinAsignar.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-textSecondary mb-3">
              Jugadores sin asignar
            </h3>
            <div className="flex flex-wrap gap-2">
              {sinAsignar.map(jugador => (
                <motion.div
                  key={jugador.id}
                  layoutId={jugador.id}
                  className={`bg-background rounded-xl p-3 border-2 cursor-pointer transition-all ${
                    jugadorSeleccionado === jugador.id
                      ? 'border-primary scale-105'
                      : 'border-cardBorder hover:border-primary/50'
                  }`}
                  onClick={() => setJugadorSeleccionado(
                    jugadorSeleccionado === jugador.id ? null : jugador.id
                  )}
                >
                  <p className="text-textPrimary font-semibold text-sm">{jugador.nombre}</p>
                  <p className="text-textSecondary text-xs">Rating: {jugador.rating || 1000}</p>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Equipos */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Equipo 1 */}
          <motion.div
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="bg-gradient-to-br from-primary/20 to-primary/5 rounded-2xl p-6 border-2 border-primary/30"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-black text-primary">EQUIPO 1</h3>
              <div className="bg-primary/20 px-3 py-1 rounded-full">
                <span className="text-primary font-bold text-sm">{equipo1.length}/2</span>
              </div>
            </div>

            <div className="space-y-3 min-h-[200px]">
              <AnimatePresence>
                {equipo1.map((jugador, index) => (
                  <motion.div
                    key={jugador.id}
                    layoutId={jugador.id}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="bg-background rounded-xl p-4 border border-primary/30 cursor-pointer hover:bg-background/80 transition-colors"
                    onClick={() => moverASinAsignar(jugador)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-textPrimary font-semibold">{jugador.nombre}</p>
                        <p className="text-textSecondary text-sm">Rating: {jugador.rating || 1000}</p>
                      </div>
                      <span className="text-primary font-bold text-2xl">{index + 1}</span>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {equipo1.length < 2 && jugadorSeleccionado && (
                <motion.button
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  onClick={() => {
                    const jugador = sinAsignar.find(j => j.id === jugadorSeleccionado) ||
                                   equipo2.find(j => j.id === jugadorSeleccionado);
                    if (jugador) moverAEquipo1(jugador);
                  }}
                  className="w-full border-2 border-dashed border-primary/50 rounded-xl p-4 text-primary hover:bg-primary/10 transition-colors flex items-center justify-center gap-2"
                >
                  <ArrowLeft size={20} />
                  Agregar aquí
                </motion.button>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-primary/20">
              <p className="text-textSecondary text-sm">Rating Promedio</p>
              <p className="text-primary font-bold text-2xl">
                {calcularPromedioRating(equipo1)}
              </p>
            </div>
          </motion.div>

          {/* Equipo 2 */}
          <motion.div
            initial={{ x: 20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="bg-gradient-to-br from-secondary/20 to-secondary/5 rounded-2xl p-6 border-2 border-secondary/30"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-black text-secondary">EQUIPO 2</h3>
              <div className="bg-secondary/20 px-3 py-1 rounded-full">
                <span className="text-secondary font-bold text-sm">{equipo2.length}/2</span>
              </div>
            </div>

            <div className="space-y-3 min-h-[200px]">
              <AnimatePresence>
                {equipo2.map((jugador, index) => (
                  <motion.div
                    key={jugador.id}
                    layoutId={jugador.id}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="bg-background rounded-xl p-4 border border-secondary/30 cursor-pointer hover:bg-background/80 transition-colors"
                    onClick={() => moverASinAsignar(jugador)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-textPrimary font-semibold">{jugador.nombre}</p>
                        <p className="text-textSecondary text-sm">Rating: {jugador.rating || 1000}</p>
                      </div>
                      <span className="text-secondary font-bold text-2xl">{index + 1}</span>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {equipo2.length < 2 && jugadorSeleccionado && (
                <motion.button
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  onClick={() => {
                    const jugador = sinAsignar.find(j => j.id === jugadorSeleccionado) ||
                                   equipo1.find(j => j.id === jugadorSeleccionado);
                    if (jugador) moverAEquipo2(jugador);
                  }}
                  className="w-full border-2 border-dashed border-secondary/50 rounded-xl p-4 text-secondary hover:bg-secondary/10 transition-colors flex items-center justify-center gap-2"
                >
                  Agregar aquí
                  <ArrowRight size={20} />
                </motion.button>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-secondary/20">
              <p className="text-textSecondary text-sm">Rating Promedio</p>
              <p className="text-secondary font-bold text-2xl">
                {calcularPromedioRating(equipo2)}
              </p>
            </div>
          </motion.div>
        </div>

        {/* Indicador de balance */}
        {puedeGuardar && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`rounded-xl p-4 mb-6 flex items-start gap-3 ${
              equiposBalanceados
                ? 'bg-secondary/10 border border-secondary/30'
                : 'bg-accent/10 border border-accent/30'
            }`}
          >
            <AlertCircle 
              size={20} 
              className={`flex-shrink-0 mt-0.5 ${
                equiposBalanceados ? 'text-secondary' : 'text-accent'
              }`} 
            />
            <div>
              <p className={`font-semibold ${
                equiposBalanceados ? 'text-secondary' : 'text-accent'
              }`}>
                {equiposBalanceados ? '✓ Equipos Balanceados' : '⚠️ Equipos Desbalanceados'}
              </p>
              <p className="text-textSecondary text-sm">
                Diferencia de rating: {diferencia} puntos
                {!equiposBalanceados && ' (Recomendado: ≤100 puntos)'}
              </p>
            </div>
          </motion.div>
        )}

        {/* Acciones */}
        <div className="flex gap-3">
          <Button
            variant="secondary"
            onClick={onClose}
            className="flex-1"
          >
            Cancelar
          </Button>
          <Button
            variant="primary"
            onClick={handleGuardar}
            disabled={!puedeGuardar}
            className="flex-1 flex items-center justify-center gap-2"
          >
            <Save size={18} />
            Guardar Equipos
          </Button>
        </div>

        {/* Instrucciones */}
        <div className="mt-4 text-center text-textSecondary text-xs">
          💡 Haz clic en un jugador para seleccionarlo, luego haz clic en "Agregar aquí" en el equipo deseado
        </div>
      </div>
    </Modal>
  );
}
