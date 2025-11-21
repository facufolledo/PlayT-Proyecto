import { motion, useReducedMotion } from 'framer-motion';
import { Calendar, Trophy, Trash2, Play } from 'lucide-react';
import Button from './Button';
import { Sala } from '../utils/types';
import { useSalas } from '../context/SalasContext';

interface SalaCardProps {
  sala: Sala;
  onOpenMarcador: (sala: Sala) => void;
}

export default function SalaCard({ sala, onOpenMarcador }: SalaCardProps) {
  const { deleteSala } = useSalas();
  const shouldReduceMotion = useReducedMotion();

  const getEstadoConfig = (estado: string) => {
    switch (estado) {
      case 'esperando':
        return {
          color: 'text-purple-500',
          bg: 'bg-gradient-to-r from-purple-500 to-pink-500',
          glow: 'from-purple-500 to-pink-500'
        };
      case 'activa':
        return {
          color: 'text-secondary',
          bg: 'bg-gradient-to-r from-secondary to-pink-600',
          glow: 'from-secondary to-pink-600'
        };
      case 'finalizada':
        return {
          color: 'text-accent',
          bg: 'bg-gradient-to-r from-accent to-yellow-500',
          glow: 'from-accent to-yellow-500'
        };
      case 'programada':
        return {
          color: 'text-primary',
          bg: 'bg-gradient-to-r from-primary to-blue-600',
          glow: 'from-primary to-blue-600'
        };
      default:
        return {
          color: 'text-textSecondary',
          bg: 'bg-textSecondary',
          glow: 'from-textSecondary to-textSecondary'
        };
    }
  };

  const getEstadoText = (estado: string) => {
    switch (estado) {
      case 'esperando': return 'Esperando';
      case 'activa': return 'En Juego';
      case 'finalizada': return 'Finalizada';
      case 'programada': return 'Programada';
      default: return estado;
    }
  };

  const estadoConfig = getEstadoConfig(sala.estado);

  return (
    <motion.div
      initial={shouldReduceMotion ? undefined : { opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={shouldReduceMotion ? undefined : { opacity: 0, y: -10 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      whileHover={shouldReduceMotion ? undefined : { y: -4, scale: 1.005 }}
      whileTap={{ scale: 0.98 }}
      className="group"
    >
      <div className="relative bg-cardBg/95 backdrop-blur-sm rounded-lg md:rounded-xl overflow-hidden border border-cardBorder group-hover:border-transparent transition-all duration-200 active:scale-[0.98]">
        {/* Glow effect on hover - solo desktop */}
        <div className={`hidden md:block absolute -inset-[1px] bg-gradient-to-br ${estadoConfig.glow} opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-lg -z-10 blur-sm`} />
        <div className="p-2 md:p-5 relative">
          <div className="space-y-2 md:space-y-3">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <h3 className="text-base md:text-lg font-bold text-textPrimary mb-0.5 md:mb-1 group-hover:text-primary transition-colors truncate">
                  {sala.nombre}
                </h3>
                <div className="flex items-center gap-1.5 text-textSecondary text-xs md:text-sm">
                  <Calendar size={12} className="md:w-4 md:h-4 flex-shrink-0" />
                  <span className="truncate">{new Date(sala.fecha).toLocaleDateString('es-ES', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric'
                  })}</span>
                </div>
              </div>
              <motion.span
                className={`${estadoConfig.bg} text-white px-1.5 md:px-2.5 py-0.5 md:py-1 rounded-full text-[8px] md:text-[10px] font-black uppercase tracking-wide shadow-lg flex-shrink-0`}
                whileHover={shouldReduceMotion ? {} : { scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {getEstadoText(sala.estado)}
              </motion.span>
            </div>

            {/* Marcador o lista de jugadores */}
            {sala.estado === 'esperando' ? (
              <div className="relative bg-background/50 rounded-md md:rounded-lg p-2 md:p-3 backdrop-blur-sm">
                <p className="text-textSecondary text-xs md:text-sm font-medium mb-2">
                  Jugadores: {sala.jugadores?.length || 0}/4
                </p>
                <div className="space-y-1.5 md:space-y-2">
                  {sala.jugadores?.map((jugador) => (
                    <div key={jugador.id} className="flex items-center gap-2 bg-cardBg rounded-md p-2">
                      <div className="w-7 h-7 md:w-8 md:h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xs md:text-sm font-bold flex-shrink-0">
                        {jugador.nombre.charAt(0).toUpperCase()}
                      </div>
                      <span className="text-textPrimary text-xs md:text-sm font-semibold truncate flex-1">{jugador.nombre}</span>
                      {jugador.esCreador && (
                        <span className="ml-auto text-accent text-sm flex-shrink-0">👑</span>
                      )}
                    </div>
                  ))}
                </div>
                {sala.codigoInvitacion && (
                  <div className="mt-2 md:mt-3 text-center">
                    <p className="text-textSecondary text-[10px] md:text-xs mb-1">Código:</p>
                    <p className="text-primary font-bold text-base md:text-lg tracking-wider">{sala.codigoInvitacion}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="relative bg-background/50 rounded-md md:rounded-lg p-2 md:p-3 backdrop-blur-sm">
                <div className="grid grid-cols-3 gap-1.5 md:gap-3">
                  {/* Equipo A */}
                  <motion.div
                    className="text-center"
                    whileHover={shouldReduceMotion ? {} : { scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="bg-primary/10 rounded-md p-1.5 md:p-2 mb-1">
                      <p className="text-primary text-[10px] md:text-xs font-bold mb-0.5 md:mb-1">EQUIPO A</p>
                      <p className="text-textPrimary font-semibold text-[10px] md:text-xs leading-tight truncate">{sala.equipoA.jugador1.nombre}</p>
                      <p className="text-textPrimary font-semibold text-[10px] md:text-xs leading-tight truncate">{sala.equipoA.jugador2.nombre}</p>
                    </div>
                    <motion.p
                      className="text-2xl md:text-3xl font-black text-primary"
                      key={sala.equipoA.puntos}
                      initial={shouldReduceMotion ? false : { scale: 1.1, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ type: "spring", stiffness: 300, damping: 20 }}
                    >
                      {sala.equipoA.puntos}
                    </motion.p>
                  </motion.div>

                  {/* VS */}
                  <div className="flex items-center justify-center">
                    <motion.div
                      animate={shouldReduceMotion ? {} : { rotate: [0, 5, -5, 0] }}
                      transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
                      className="bg-gradient-to-br from-primary/20 to-secondary/20 rounded-full w-9 h-9 md:w-10 md:h-10 flex items-center justify-center"
                    >
                      <span className="text-xs md:text-sm font-black text-textPrimary">VS</span>
                    </motion.div>
                  </div>

                  {/* Equipo B */}
                  <motion.div
                    className="text-center"
                    whileHover={shouldReduceMotion ? {} : { scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="bg-secondary/10 rounded-md p-1.5 md:p-2 mb-1">
                      <p className="text-secondary text-[10px] md:text-xs font-bold mb-0.5 md:mb-1">EQUIPO B</p>
                      <p className="text-textPrimary font-semibold text-[10px] md:text-xs leading-tight truncate">{sala.equipoB.jugador1.nombre}</p>
                      <p className="text-textPrimary font-semibold text-[10px] md:text-xs leading-tight truncate">{sala.equipoB.jugador2.nombre}</p>
                    </div>
                    <motion.p
                      className="text-2xl md:text-3xl font-black text-secondary"
                      key={sala.equipoB.puntos}
                      initial={shouldReduceMotion ? false : { scale: 1.1, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ type: "spring", stiffness: 300, damping: 20 }}
                    >
                      {sala.equipoB.puntos}
                    </motion.p>
                  </motion.div>
                </div>
              </div>
            )}

            {sala.ganador && (
              <div className="flex items-center justify-center gap-1.5 md:gap-2 py-2 bg-accent/10 rounded-md">
                <Trophy size={14} className="text-accent md:w-4 md:h-4" />
                <span className="text-accent font-semibold text-xs md:text-sm">
                  Ganador: {sala.ganador === 'equipoA' ? 'Equipo A' : 'Equipo B'}
                </span>
              </div>
            )}

            <div className="flex gap-2 pt-2">
              {sala.estado === 'esperando' && (
                <Button
                  variant="primary"
                  onClick={() => onOpenMarcador(sala)}
                  className="flex-1 flex items-center justify-center gap-1.5 text-xs md:text-sm py-2 md:py-2.5"
                >
                  <Play size={14} className="md:w-4 md:h-4" />
                  <span className="hidden sm:inline">Ver Sala de Espera</span>
                  <span className="sm:hidden">Ver Sala</span>
                </Button>
              )}
              {sala.estado !== 'finalizada' && sala.estado !== 'esperando' && (
                <Button
                  variant="primary"
                  onClick={() => onOpenMarcador(sala)}
                  className="flex-1 flex items-center justify-center gap-1.5 text-xs md:text-sm py-2 md:py-2.5"
                >
                  <Play size={14} className="md:w-4 md:h-4" />
                  {sala.estado === 'programada' ? 'Iniciar' : 'Marcador'}
                </Button>
              )}
              <Button
                variant="ghost"
                onClick={() => {
                  if (confirm('¿Estás seguro de eliminar esta sala?')) {
                    deleteSala(sala.id);
                  }
                }}
                className="flex items-center justify-center gap-1.5 px-3 py-2 md:py-2.5"
              >
                <Trash2 size={14} className="md:w-4 md:h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
