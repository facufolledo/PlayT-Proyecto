import { motion } from 'framer-motion';
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
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -6, scale: 1.02 }}
      className="group cursor-pointer"
      onClick={() => navigate(`/torneos/${torneo.id}`)}
    >
      <div className="relative bg-cardBg rounded-xl p-6 border border-cardBorder group-hover:border-transparent transition-all duration-300 overflow-hidden">
        {/* Glow effect on hover */}
        <div className={`absolute -inset-[1px] bg-gradient-to-br ${getEstadoColor()} opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl -z-10 blur-sm`} />
        
        <div className="relative z-10">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className={`bg-gradient-to-br ${getEstadoColor()} p-3 rounded-lg`}>
                <Trophy className="text-white" size={24} />
              </div>
              <div>
                <h3 className="text-xl font-bold text-textPrimary group-hover:text-white transition-colors">
                  {torneo.nombre}
                </h3>
                <p className="text-textSecondary text-sm">{FORMATO_LABELS[torneo.formato]}</p>
              </div>
            </div>
            
            {/* Estado badge */}
            <div className={`flex items-center gap-1 px-3 py-1 rounded-full bg-gradient-to-r ${getEstadoColor()} text-white text-xs font-bold`}>
              {getEstadoIcon()}
              {getEstadoLabel()}
            </div>
          </div>

          {/* Info */}
          <div className="space-y-3 mb-4">
            <div className="flex items-center gap-2 text-textSecondary">
              <Calendar size={16} />
              <span className="text-sm">
                {new Date(torneo.fechaInicio).toLocaleDateString('es-ES', { 
                  day: 'numeric', 
                  month: 'short' 
                })} - {new Date(torneo.fechaFin).toLocaleDateString('es-ES', { 
                  day: 'numeric', 
                  month: 'short',
                  year: 'numeric'
                })}
              </span>
            </div>
            
            <div className="flex items-center gap-2 text-textSecondary">
              <Users size={16} />
              <span className="text-sm">
                {torneo.participantes} participantes ({torneo.participantes / 2} parejas)
              </span>
            </div>

            {/* Categoría y Género */}
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold">
                Categoría {torneo.categoria}
              </span>
              <span className={`px-3 py-1 rounded-full bg-gradient-to-r ${GENERO_LABELS[torneo.genero].color} text-white text-xs font-bold flex items-center gap-1`}>
                <span>{GENERO_LABELS[torneo.genero].icon}</span>
                <span>{GENERO_LABELS[torneo.genero].label}</span>
              </span>
            </div>
          </div>

          {/* Descripción */}
          {torneo.descripcion && (
            <p className="text-textSecondary text-sm mb-4 line-clamp-2">
              {torneo.descripcion}
            </p>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between pt-4 border-t border-cardBorder">
            <div className="text-textSecondary text-xs">
              {torneo.salasIds.length} {torneo.salasIds.length === 1 ? 'partido' : 'partidos'}
            </div>
            <Button
              variant="primary"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/torneos/${torneo.id}`);
              }}
            >
              Ver Detalles
            </Button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
