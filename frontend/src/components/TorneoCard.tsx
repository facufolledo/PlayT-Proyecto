import { motion, useReducedMotion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Trophy, Calendar, Users, Play, CheckCircle, Clock } from 'lucide-react';
import { Torneo } from '../utils/types';
import Button from './Button';

interface TorneoCardProps {
  torneo: Torneo;
}

const FORMATO_LABELS = {
  'eliminacion-simple': 'Eliminación Simple',
  'eliminacion-doble': 'Eliminación Doble',
  'round-robin': 'Round Robin',
  'grupos': 'Por Grupos',
  'por-puntos': 'Por Puntos',
};

const GENERO_LABELS = {
  'masculino': { label: 'Masculino', icon: '♂', color: 'from-blue-500 to-blue-600' },
  'femenino': { label: 'Femenino', icon: '♀', color: 'from-pink-500 to-pink-600' },
  'mixto': { label: 'Mixto', icon: '⚥', color: 'from-purple-500 to-purple-600' },
};

export default function TorneoCard({ torneo }: TorneoCardProps) {
  const navigate = useNavigate();
  const shouldReduceMotion = useReducedMotion();
  const getEstadoColor = () => {
    switch (torneo.estado) {
      case 'activo':
        return 'from-secondary to-pink-600';
      case 'finalizado':
        return 'from-accent to-yellow-500';
      case 'programado':
        return 'from-primary to-blue-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const getEstadoIcon = () => {
    switch (torneo.estado) {
      case 'activo':
        return <Play size={16} />;
      case 'finalizado':
        return <CheckCircle size={16} />;
      case 'programado':
        return <Clock size={16} />;
    }
  };

  const getEstadoLabel = () => {
    switch (torneo.estado) {
      case 'activo':
        return 'En Curso';
      case 'finalizado':
        return 'Finalizado';
      case 'programado':
        return 'Próximamente';
    }
  };

  return (
    <motion.div
      initial={shouldReduceMotion ? false : { opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={shouldReduceMotion ? {} : { y: -2 }}
      whileTap={{ scale: 0.98 }}
      className="group cursor-pointer"
      onClick={() => navigate(`/torneos/${torneo.id}`)}
    >
      <div className="relative bg-cardBg/95 backdrop-blur-sm rounded-lg p-3 border border-cardBorder group-hover:border-transparent transition-all duration-200 overflow-hidden h-full">
        {/* Glow effect on hover - solo desktop */}
        <div className={`hidden md:block absolute -inset-[1px] bg-gradient-to-br ${getEstadoColor()} opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-lg -z-10 blur-sm`} />
        
        <div className="relative z-10 flex flex-col h-full">
          {/* Header compacto */}
          <div className="flex items-center justify-between mb-2 gap-2">
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <div className={`bg-gradient-to-br ${getEstadoColor()} p-1.5 rounded flex-shrink-0`}>
                <Trophy className="text-white" size={16} />
              </div>
              <h3 className="text-sm font-bold text-textPrimary group-hover:text-white transition-colors truncate">
                {torneo.nombre}
              </h3>
            </div>
            
            {/* Estado badge compacto */}
            <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full bg-gradient-to-r ${getEstadoColor()} text-white flex-shrink-0`}>
              <span className="w-3 h-3">{getEstadoIcon()}</span>
            </div>
          </div>

          {/* Info compacta */}
          <div className="space-y-1.5 mb-2 flex-1">
            <div className="flex items-center gap-1.5 text-textSecondary">
              <Calendar size={12} className="flex-shrink-0" />
              <span className="text-[10px] truncate">
                {new Date(torneo.fechaInicio).toLocaleDateString('es-ES', { 
                  day: 'numeric', 
                  month: 'short' 
                })} - {new Date(torneo.fechaFin).toLocaleDateString('es-ES', { 
                  day: 'numeric', 
                  month: 'short'
                })}
              </span>
            </div>
            
            <div className="flex items-center gap-1.5 text-textSecondary">
              <Users size={12} className="flex-shrink-0" />
              <span className="text-[10px]">
                {torneo.participantes} jugadores
              </span>
            </div>

            {/* Categoría y Género en una línea */}
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-[9px] font-bold">
                {torneo.categoria}
              </span>
              <span className={`px-2 py-0.5 rounded-full bg-gradient-to-r ${GENERO_LABELS[torneo.genero].color} text-white text-[9px] font-bold`}>
                {GENERO_LABELS[torneo.genero].icon}
              </span>
              <span className="text-[9px] text-textSecondary">
                {FORMATO_LABELS[torneo.formato]}
              </span>
            </div>
          </div>

          {/* Footer compacto */}
          <div className="flex items-center justify-between pt-2 border-t border-cardBorder mt-auto">
            <div className="text-textSecondary text-[10px]">
              {torneo.salasIds.length} {torneo.salasIds.length === 1 ? 'partido' : 'partidos'}
            </div>
            <Button
              variant="primary"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/torneos/${torneo.id}`);
              }}
              className="text-[10px] px-2 py-1"
            >
              Ver
            </Button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
