import { motion } from 'framer-motion';
import { Trophy, Clock, CheckCircle } from 'lucide-react';
import { Bracket, Partido } from '../utils/bracketGenerator';

interface BracketVisualizationProps {
  bracket: Bracket;
  onPartidoClick?: (partido: Partido) => void;
}

export default function BracketVisualization({ bracket, onPartidoClick }: BracketVisualizationProps) {
  const getEstadoColor = (estado: Partido['estado']) => {
    switch (estado) {
      case 'finalizado':
        return 'border-secondary';
      case 'en-curso':
        return 'border-primary';
      case 'pendiente':
        return 'border-cardBorder';
    }
  };

  const getEstadoIcon = (estado: Partido['estado']) => {
    switch (estado) {
      case 'finalizado':
        return <CheckCircle size={14} className="text-secondary" />;
      case 'en-curso':
        return <Clock size={14} className="text-primary" />;
      case 'pendiente':
        return <Clock size={14} className="text-textSecondary" />;
    }
  };

  return (
    <div className="relative">
      {/* Header */}
      <div className="mb-6 text-center">
        <div className="flex items-center justify-center gap-2 mb-2">
          <Trophy className="text-accent" size={28} />
          <h3 className="text-2xl font-bold text-textPrimary">Bracket del Torneo</h3>
        </div>
        <p className="text-textSecondary text-sm">
          {bracket.tipo === 'eliminacion-simple' && 'Eliminación Simple'}
        </p>
      </div>

      {/* Bracket Grid */}
      <div className="overflow-x-auto pb-4">
        <div className="flex gap-8 min-w-max">
          {bracket.rondas.map((ronda, rondaIndex) => (
            <div key={ronda.numero} className="flex flex-col">
              {/* Nombre de la ronda */}
              <div className="mb-4 text-center">
                <h4 className="text-lg font-bold text-textPrimary">{ronda.nombre}</h4>
                <p className="text-xs text-textSecondary">Ronda {ronda.numero}</p>
              </div>

              {/* Partidos de la ronda */}
              <div className="flex flex-col justify-around flex-1 gap-4">
                {ronda.partidos.map((partido, partidoIndex) => (
                  <motion.div
                    key={partido.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: (rondaIndex * 0.1) + (partidoIndex * 0.05) }}
                    whileHover={{ scale: 1.02 }}
                    onClick={() => onPartidoClick?.(partido)}
                    className={`relative bg-cardBg rounded-lg border-2 ${getEstadoColor(partido.estado)} p-3 cursor-pointer transition-all hover:shadow-lg min-w-[200px]`}
                    style={{
                      marginTop: rondaIndex > 0 ? `${Math.pow(2, rondaIndex - 1) * 40}px` : '0',
                    }}
                  >
                    {/* Estado del partido */}
                    <div className="absolute -top-2 -right-2 bg-cardBg rounded-full p-1 border border-cardBorder">
                      {getEstadoIcon(partido.estado)}
                    </div>

                    {/* Jugador 1 */}
                    <div className={`flex items-center justify-between p-2 rounded ${
                      partido.ganador?.id === partido.jugador1?.id 
                        ? 'bg-secondary/10 border-l-2 border-secondary' 
                        : 'bg-background'
                    }`}>
                      <span className={`text-sm font-bold ${
                        partido.ganador?.id === partido.jugador1?.id 
                          ? 'text-secondary' 
                          : 'text-textPrimary'
                      }`}>
                        {partido.jugador1?.nombre || 'TBD'}
                      </span>
                      {partido.puntos1 !== undefined && (
                        <span className="text-lg font-black text-textPrimary ml-2">
                          {partido.puntos1}
                        </span>
                      )}
                    </div>

                    {/* VS */}
                    <div className="text-center text-xs text-textSecondary my-1">VS</div>

                    {/* Jugador 2 */}
                    <div className={`flex items-center justify-between p-2 rounded ${
                      partido.ganador?.id === partido.jugador2?.id 
                        ? 'bg-secondary/10 border-l-2 border-secondary' 
                        : 'bg-background'
                    }`}>
                      <span className={`text-sm font-bold ${
                        partido.ganador?.id === partido.jugador2?.id 
                          ? 'text-secondary' 
                          : 'text-textPrimary'
                      }`}>
                        {partido.jugador2?.nombre || 'TBD'}
                      </span>
                      {partido.puntos2 !== undefined && (
                        <span className="text-lg font-black text-textPrimary ml-2">
                          {partido.puntos2}
                        </span>
                      )}
                    </div>

                    {/* Línea conectora a la siguiente ronda */}
                    {rondaIndex < bracket.rondas.length - 1 && (
                      <div className="absolute top-1/2 -right-8 w-8 h-0.5 bg-cardBorder" />
                    )}
                  </motion.div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Leyenda */}
      <div className="mt-6 flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-secondary" />
          <span className="text-textSecondary">Finalizado</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-primary" />
          <span className="text-textSecondary">En Curso</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-cardBorder" />
          <span className="text-textSecondary">Pendiente</span>
        </div>
      </div>
    </div>
  );
}
