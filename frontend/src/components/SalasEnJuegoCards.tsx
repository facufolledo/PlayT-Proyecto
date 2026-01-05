import { motion } from 'framer-motion';
import { Eye, Zap } from 'lucide-react';
import Button from './Button';
import { Sala } from '../utils/types';

interface SalasEnJuegoCardsProps {
  salas: Sala[];
  onOpenSala: (sala: Sala) => void;
  maxVisible?: number;
}

export default function SalasEnJuegoCards({ salas, onOpenSala, maxVisible = 4 }: SalasEnJuegoCardsProps) {
  const salasVisibles = salas.slice(0, maxVisible);

  if (salasVisibles.length === 0) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {salasVisibles.map((sala, index) => {
        // Calcular sets ganados
        const setsA = sala.resultado?.sets?.filter((s: any) => s.ganador === 'equipoA').length || 0;
        const setsB = sala.resultado?.sets?.filter((s: any) => s.ganador === 'equipoB').length || 0;

        return (
          <motion.div
            key={sala.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="group bg-cardBg border border-green-500/30 hover:border-green-500/60 rounded-xl p-4 transition-all duration-200"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-xs font-bold text-green-400">EN JUEGO</span>
              </div>
              <div className="flex items-center gap-1 text-xs text-textSecondary">
                <Zap size={12} className="text-green-400" />
                <span>En vivo</span>
              </div>
            </div>

            <h3 className="font-bold text-textPrimary mb-3 truncate">{sala.nombre}</h3>

            {/* Marcador compacto */}
            <div className="flex items-center justify-center gap-4 mb-3 bg-background/50 rounded-lg p-3">
              <div className="text-center">
                <p className="text-xs text-primary font-medium mb-1">Equipo A</p>
                <p className="text-2xl font-black text-primary">{setsA}</p>
              </div>
              <div className="text-textSecondary text-sm font-bold">VS</div>
              <div className="text-center">
                <p className="text-xs text-secondary font-medium mb-1">Equipo B</p>
                <p className="text-2xl font-black text-secondary">{setsB}</p>
              </div>
            </div>

            <Button
              variant="secondary"
              className="w-full text-xs py-2"
              onClick={() => onOpenSala(sala)}
            >
              <Eye size={14} className="mr-1" />
              Ver Partido
            </Button>
          </motion.div>
        );
      })}
    </div>
  );
}
