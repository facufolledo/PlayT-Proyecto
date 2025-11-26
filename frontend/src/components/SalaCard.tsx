import { forwardRef } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { Calendar, Trophy, Trash2, Play } from 'lucide-react';
import Button from './Button';
import { Sala } from '../utils/types';
import { useSalas } from '../context/SalasContext';
import { useAuth } from '../context/AuthContext';

interface SalaCardProps {
  sala: Sala;
  onOpenMarcador: (sala: Sala) => void;
}

const SalaCard = forwardRef<HTMLDivElement, SalaCardProps>(
  ({ sala, onOpenMarcador }, ref) => {
    const { deleteSala } = useSalas();
    const { usuario } = useAuth();
    const shouldReduceMotion = useReducedMotion();
    
    // Verificar si el usuario es participante
    const esParticipante = sala.jugadores?.some(j => j.id === usuario?.id_usuario?.toString());

  const getEstadoConfig = (estado: string) => {
    switch (estado) {
      case 'esperando':
        return {
          color: 'text-purple-500',
          bg: 'bg-gradient-to-r from-purple-500 to-pink-500',
          glow: 'from-purple-500 to-pink-500'
        };
      case 'activa':
      case 'en_juego':
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
      case 'en_juego': return 'En Juego';
      case 'finalizada': return 'Finalizada';
      case 'programada': return 'Programada';
      default: return estado;
    }
  };

  const estadoConfig = getEstadoConfig(sala.estado);

  return (
    <motion.div
      layout
      initial={shouldReduceMotion ? undefined : { opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={shouldReduceMotion ? undefined : { 
        opacity: 0, 
        scale: 0.8, 
        x: -100,
        transition: { duration: 0.3, ease: "easeInOut" }
      }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      whileHover={shouldReduceMotion ? undefined : { y: -4, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="group h-full"
    >
      <div className="relative bg-cardBg/95 backdrop-blur-sm rounded-lg md:rounded-xl overflow-hidden border border-cardBorder group-hover:border-transparent transition-all duration-200 h-full flex flex-col">
        {/* Glow effect on hover - solo desktop */}
        <div className={`hidden md:block absolute -inset-[1px] bg-gradient-to-br ${estadoConfig.glow} opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-lg md:rounded-xl -z-10 blur-sm`} />
        <div className="p-3 md:p-5 relative flex flex-col h-full">
          <div className="space-y-2 md:space-y-3 flex-1 flex flex-col">
            <div className="flex items-center justify-between gap-2 md:gap-3">
              <div className="flex-1 min-w-0">
                <h3 className="text-sm md:text-lg font-bold text-textPrimary mb-0.5 md:mb-1 group-hover:text-primary transition-colors truncate">
                  {sala.nombre}
                </h3>
                <div className="flex items-center gap-1 md:gap-1.5 text-textSecondary text-[10px] md:text-sm">
                  <Calendar size={10} className="md:w-4 md:h-4 flex-shrink-0" />
                  <span className="truncate">{new Date(sala.fecha).toLocaleDateString('es-ES', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric'
                  })}</span>
                </div>
              </div>
              <span
                className={`${estadoConfig.bg} text-white px-2 md:px-3 py-0.5 md:py-1 rounded-full text-[8px] md:text-xs font-black uppercase tracking-wide shadow-lg flex-shrink-0`}
              >
                {getEstadoText(sala.estado)}
              </span>
            </div>

            {/* Marcador o lista de jugadores */}
            {sala.estado === 'esperando' ? (
              <div className="relative bg-background/50 rounded-md md:rounded-lg p-2 md:p-3 backdrop-blur-sm flex-1">
                <p className="text-textSecondary text-[10px] md:text-sm font-medium mb-1.5 md:mb-2">
                  Jugadores: {sala.jugadores?.length || 0}/4
                </p>
                <div className="space-y-1 md:space-y-2">
                  {sala.jugadores?.map((jugador) => (
                    <div key={jugador.id} className="flex items-center gap-1.5 md:gap-2 bg-cardBg rounded p-1.5 md:p-2">
                      <div className="w-6 h-6 md:w-8 md:h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-[10px] md:text-sm font-bold flex-shrink-0">
                        {jugador.nombre.charAt(0).toUpperCase()}
                      </div>
                      <span className="text-textPrimary text-[10px] md:text-sm font-semibold truncate flex-1">{jugador.nombre}</span>
                      {jugador.esCreador && (
                        <span className="ml-auto text-accent text-xs md:text-base flex-shrink-0">👑</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="relative bg-background/50 rounded-md md:rounded-lg p-2 md:p-4 backdrop-blur-sm flex-1">
                <div className="grid grid-cols-3 gap-2 md:gap-4">
                  {/* Equipo A */}
                  <div className="text-center">
                    <div className="bg-primary/10 rounded p-1.5 md:p-2 mb-1 md:mb-2">
                      <p className="text-primary text-[8px] md:text-xs font-bold mb-0.5 md:mb-1">EQUIPO A</p>
                      <p className="text-textPrimary font-semibold text-[9px] md:text-sm leading-tight truncate">{sala.equipoA.jugador1.nombre}</p>
                      <p className="text-textPrimary font-semibold text-[9px] md:text-sm leading-tight truncate">{sala.equipoA.jugador2.nombre}</p>
                    </div>
                    <p className="text-2xl md:text-4xl font-black text-primary">
                      {(() => {
                        if (sala.resultado?.sets) {
                          return sala.resultado.sets.filter((s: any) => s.ganador === 'equipoA').length;
                        }
                        return sala.equipoA.puntos;
                      })()}
                    </p>
                  </div>

                  {/* VS */}
                  <div className="flex items-center justify-center">
                    <div className="bg-gradient-to-br from-primary/20 to-secondary/20 rounded-full w-8 h-8 md:w-12 md:h-12 flex items-center justify-center">
                      <span className="text-[10px] md:text-sm font-black text-textPrimary">VS</span>
                    </div>
                  </div>

                  {/* Equipo B */}
                  <div className="text-center">
                    <div className="bg-secondary/10 rounded p-1.5 md:p-2 mb-1 md:mb-2">
                      <p className="text-secondary text-[8px] md:text-xs font-bold mb-0.5 md:mb-1">EQUIPO B</p>
                      <p className="text-textPrimary font-semibold text-[9px] md:text-sm leading-tight truncate">{sala.equipoB.jugador1.nombre}</p>
                      <p className="text-textPrimary font-semibold text-[9px] md:text-sm leading-tight truncate">{sala.equipoB.jugador2.nombre}</p>
                    </div>
                    <p className="text-2xl md:text-4xl font-black text-secondary">
                      {(() => {
                        if (sala.resultado?.sets) {
                          return sala.resultado.sets.filter((s: any) => s.ganador === 'equipoB').length;
                        }
                        return sala.equipoB.puntos;
                      })()}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {sala.ganador && (
              <div className="flex items-center justify-center gap-1 md:gap-2 py-1.5 md:py-2 bg-accent/10 rounded">
                <Trophy size={12} className="text-accent md:w-4 md:h-4" />
                <span className="text-accent font-semibold text-[10px] md:text-sm">
                  Ganador: {sala.ganador === 'equipoA' ? 'Equipo A' : 'Equipo B'}
                </span>
              </div>
            )}

            <div className="flex gap-1.5 md:gap-2 pt-2 md:pt-3 mt-auto">
              {sala.estado === 'esperando' && esParticipante && (
                <Button
                  variant="primary"
                  onClick={() => onOpenMarcador(sala)}
                  className="flex-1 flex items-center justify-center gap-1 md:gap-2 text-[10px] md:text-sm py-2 md:py-2.5"
                >
                  <Play size={12} className="md:w-4 md:h-4" />
                  <span className="hidden sm:inline">Ver Sala de Espera</span>
                  <span className="sm:hidden">Ver</span>
                </Button>
              )}
              {sala.estado === 'esperando' && !esParticipante && (
                <div className="flex-1 bg-cardBorder/50 rounded p-1.5 md:p-2 text-center">
                  <p className="text-textSecondary text-[10px] md:text-sm">🔒 Sala Privada</p>
                </div>
              )}
              {sala.estado !== 'finalizada' && sala.estado !== 'esperando' && esParticipante && (
                <Button
                  variant="primary"
                  onClick={() => onOpenMarcador(sala)}
                  className="flex-1 flex items-center justify-center gap-1 md:gap-2 text-[10px] md:text-sm py-2 md:py-2.5"
                >
                  <Play size={12} className="md:w-4 md:h-4" />
                  {sala.estado === 'programada' ? 'Iniciar Partido' : 'Ver Marcador'}
                </Button>
              )}
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  variant="ghost"
                  onClick={async () => {
                    if (confirm('¿Estás seguro de eliminar esta sala?')) {
                      try {
                        await deleteSala(sala.id);
                      } catch (error: any) {
                        const errorMsg = error.message || 'Error al eliminar';
                        if (errorMsg.includes('Not authenticated') || errorMsg.includes('401')) {
                          alert('Tu sesión ha expirado. Por favor, vuelve a iniciar sesión.');
                          window.location.href = '/login';
                        } else {
                          alert(errorMsg);
                        }
                      }
                    }
                  }}
                  className="flex items-center justify-center px-2 md:px-3 py-2 md:py-2.5 hover:text-red-500 transition-colors"
                >
                  <Trash2 size={12} className="md:w-4 md:h-4" />
                </Button>
              </motion.div>
            </div>
          </div>
        </div>
        </div>
      </motion.div>
    );
  }
);

SalaCard.displayName = 'SalaCard';

export default SalaCard;
