import { motion } from 'framer-motion';
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
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: -20 }}
      transition={{ type: "spring", stiffness: 200 }}
      whileHover={{ y: -6, scale: 1.01 }}
      className="group"
    >
      <div className="relative bg-cardBg rounded-xl overflow-hidden border border-cardBorder group-hover:border-transparent transition-all duration-300">
        {/* Glow effect on hover */}
        <div className={`absolute -inset-[1px] bg-gradient-to-br ${estadoConfig.glow} opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl -z-10 blur-sm`} />
        <div className="p-6 relative">
          <div className="space-y-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-xl font-bold text-textPrimary mb-2 group-hover:text-primary transition-colors">
                  {sala.nombre}
                </h3>
                <div className="flex items-center gap-2 text-textSecondary text-sm">
                  <Calendar size={16} />
                  <span>{new Date(sala.fecha).toLocaleDateString('es-ES', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric'
                  })}</span>
                </div>
              </div>
              <motion.span
                className={`${estadoConfig.bg} text-white px-3 py-1 rounded-full text-xs font-black uppercase tracking-wide shadow-lg`}
                whileHover={{ scale: 1.05 }}
              >
                {getEstadoText(sala.estado)}
              </motion.span>
            </div>

            {/* Marcador o lista de jugadores */}
            {sala.estado === 'esperando' ? (
              <div className="relative bg-background/50 rounded-xl p-4 backdrop-blur-sm">
                <p className="text-textSecondary text-sm font-medium mb-3">
                  Jugadores: {sala.jugadores?.length || 0}/4
                </p>
                <div className="space-y-2">
                  {sala.jugadores?.map((jugador, index) => (
                    <div key={jugador.id} className="flex items-center gap-2 bg-cardBg rounded-lg p-2">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-sm font-bold">
                        {jugador.nombre.charAt(0).toUpperCase()}
                      </div>
                      <span className="text-textPrimary text-sm font-semibold">{jugador.nombre}</span>
                      {jugador.esCreador && (
                        <span className="ml-auto text-accent text-xs">👑</span>
                      )}
                    </div>
                  ))}
                </div>
                {sala.codigoInvitacion && (
                  <div className="mt-3 text-center">
                    <p className="text-textSecondary text-xs mb-1">Código:</p>
                    <p className="text-primary font-bold text-lg tracking-wider">{sala.codigoInvitacion}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="relative bg-background/50 rounded-xl p-4 backdrop-blur-sm">
                <div className="grid grid-cols-3 gap-4">
                  {/* Equipo A */}
                  <motion.div
                    className="text-center"
                    whileHover={{ scale: 1.05 }}
                  >
                    <div className="bg-primary/10 rounded-lg p-3 mb-2">
                      <p className="text-primary text-xs font-bold mb-2">EQUIPO A</p>
                      <p className="text-textPrimary font-semibold text-sm leading-tight">{sala.equipoA.jugador1.nombre}</p>
                      <p className="text-textPrimary font-semibold text-sm leading-tight">{sala.equipoA.jugador2.nombre}</p>
                    </div>
                    <motion.p
                      className="text-4xl font-black text-primary"
                      key={sala.equipoA.puntos}
                      initial={{ scale: 1.3, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ type: "spring", stiffness: 300 }}
                    >
                      {sala.equipoA.puntos}
                    </motion.p>
                  </motion.div>

                  {/* VS */}
                  <div className="flex items-center justify-center">
                    <motion.div
                      animate={{ rotate: [0, 5, -5, 0] }}
                      transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
                      className="bg-gradient-to-br from-primary/20 to-secondary/20 rounded-full w-12 h-12 flex items-center justify-center"
                    >
                      <span className="text-lg font-black text-textPrimary">VS</span>
                    </motion.div>
                  </div>

                  {/* Equipo B */}
                  <motion.div
                    className="text-center"
                    whileHover={{ scale: 1.05 }}
                  >
                    <div className="bg-secondary/10 rounded-lg p-3 mb-2">
                      <p className="text-secondary text-xs font-bold mb-2">EQUIPO B</p>
                      <p className="text-textPrimary font-semibold text-sm leading-tight">{sala.equipoB.jugador1.nombre}</p>
                      <p className="text-textPrimary font-semibold text-sm leading-tight">{sala.equipoB.jugador2.nombre}</p>
                    </div>
                    <motion.p
                      className="text-4xl font-black text-secondary"
                      key={sala.equipoB.puntos}
                      initial={{ scale: 1.3, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ type: "spring", stiffness: 300 }}
                    >
                      {sala.equipoB.puntos}
                    </motion.p>
                  </motion.div>
                </div>
              </div>
            )}

            {sala.ganador && (
              <div className="flex items-center justify-center gap-2 py-2 bg-accent/10 rounded-lg">
                <Trophy size={20} className="text-accent" />
                <span className="text-accent font-semibold">
                  Ganador: {sala.ganador === 'equipoA' ? 'Equipo A' : 'Equipo B'}
                </span>
              </div>
            )}

            <div className="flex gap-2 pt-2">
              {sala.estado === 'esperando' && (
                <Button
                  variant="primary"
                  onClick={() => onOpenMarcador(sala)}
                  className="flex-1 flex items-center justify-center gap-2"
                >
                  <Play size={18} />
                  Ver Sala de Espera
                </Button>
              )}
              {sala.estado !== 'finalizada' && sala.estado !== 'esperando' && (
                <Button
                  variant="primary"
                  onClick={() => onOpenMarcador(sala)}
                  className="flex-1 flex items-center justify-center gap-2"
                >
                  <Play size={18} />
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
                className="flex items-center justify-center gap-2"
              >
                <Trash2 size={18} />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
