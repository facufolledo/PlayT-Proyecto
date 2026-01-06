import { motion } from 'framer-motion';
import { Calendar, Play, Eye, Users } from 'lucide-react';
import Button from './Button';
import { PlayerLink } from './UserLink';
import { Sala } from '../utils/types';

interface MisSalasCardsProps {
  salas: Sala[];
  onOpenSala: (sala: Sala) => void;
  maxVisible?: number;
}

const getEstadoConfig = (estado: string) => {
  switch (estado) {
    case 'esperando':
      return { color: 'text-purple-400', bg: 'bg-purple-500', dot: 'bg-purple-500', label: 'ESPERANDO' };
    case 'activa':
    case 'en_juego':
      return { color: 'text-green-400', bg: 'bg-green-500', dot: 'bg-green-500 animate-pulse', label: 'EN JUEGO' };
    case 'finalizada':
      return { color: 'text-amber-400', bg: 'bg-amber-500', dot: 'bg-amber-500', label: 'FINALIZADA' };
    case 'programada':
      return { color: 'text-blue-400', bg: 'bg-blue-500', dot: 'bg-blue-500', label: 'PROGRAMADA' };
    default:
      return { color: 'text-gray-400', bg: 'bg-gray-500', dot: 'bg-gray-500', label: estado.toUpperCase() };
  }
};

const formatFecha = (fecha: string) => {
  const date = new Date(fecha);
  const hoy = new Date();
  const manana = new Date(hoy);
  manana.setDate(manana.getDate() + 1);
  
  if (date.toDateString() === hoy.toDateString()) {
    return `Hoy ${date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}`;
  }
  if (date.toDateString() === manana.toDateString()) {
    return `Mañana ${date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}`;
  }
  return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
};

export default function MisSalasCards({ salas, onOpenSala, maxVisible = 5 }: MisSalasCardsProps) {
  const salasVisibles = salas.slice(0, maxVisible);

  if (salasVisibles.length === 0) {
    return (
      <div className="bg-cardBg/50 border border-cardBorder rounded-xl p-6 text-center">
        <p className="text-textSecondary text-sm">No tienes salas activas</p>
        <p className="text-textSecondary/60 text-xs mt-1">Crea una sala o únete a una existente</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {salasVisibles.map((sala, index) => {
        const config = getEstadoConfig(sala.estado);
        const jugadoresCount = sala.jugadores?.length || 0;
        const esCreador = sala.jugadores?.some(j => j.esCreador);

        return (
          <motion.div
            key={sala.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="group bg-cardBg border border-cardBorder hover:border-primary/50 rounded-xl p-4 transition-all duration-200 cursor-pointer"
            onClick={() => onOpenSala(sala)}
          >
            <div className="flex items-center justify-between gap-4">
              {/* Info principal */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-bold text-textPrimary truncate">{sala.nombre}</h3>
                  {esCreador && <span className="text-amber-400 text-sm">👑</span>}
                </div>
                <div className="flex items-center gap-3 text-xs text-textSecondary">
                  <span className="flex items-center gap-1">
                    <Users size={12} />
                    {jugadoresCount}/4
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar size={12} />
                    {formatFecha(sala.fecha)}
                  </span>
                </div>
              </div>

              {/* Estado */}
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${config.dot}`} />
                  <span className={`text-xs font-bold ${config.color}`}>{config.label}</span>
                </div>
                
                {/* CTA */}
                <Button
                  variant={sala.estado === 'en_juego' || sala.estado === 'activa' ? 'primary' : 'secondary'}
                  className="text-xs px-3 py-1.5"
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenSala(sala);
                  }}
                >
                  {sala.estado === 'esperando' && (
                    <>
                      <Eye size={12} className="mr-1" />
                      Entrar
                    </>
                  )}
                  {(sala.estado === 'en_juego' || sala.estado === 'activa') && (
                    <>
                      <Play size={12} className="mr-1" />
                      Ver
                    </>
                  )}
                  {sala.estado === 'programada' && (
                    <>
                      <Play size={12} className="mr-1" />
                      Iniciar
                    </>
                  )}
                  {sala.estado === 'finalizada' && (
                    <>
                      <Eye size={12} className="mr-1" />
                      Ver
                    </>
                  )}
                </Button>
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
