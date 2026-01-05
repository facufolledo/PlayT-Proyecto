import { motion } from 'framer-motion';
import { Play, Users, Clock, Eye } from 'lucide-react';
import Button from '../Button';

interface SalaEnJuego {
  id: string;
  nombre: string;
  jugadores_actuales: number;
  jugadores_maximos: number;
  tiempo_transcurrido?: string;
  estado_juego?: string;
}

interface SalasEnJuegoSectionProps {
  salas: any[];
  onVerSala: (salaId: number) => void;
  loading?: boolean;
}

export default function SalasEnJuegoSection({ salas, onVerSala, loading }: SalasEnJuegoSectionProps) {
  // Filtrar solo salas en juego y convertir formato
  const salasEnJuego: SalaEnJuego[] = salas
    .filter(sala => sala.estado === 'activa' || sala.estado === 'en_juego')
    .map(sala => ({
      id: sala.id,
      nombre: sala.nombre || `Sala #${sala.id}`,
      jugadores_actuales: sala.jugadores?.length || 0,
      jugadores_maximos: 4,
      tiempo_transcurrido: sala.estado === 'en_juego' ? '2do set' : 'Ahora',
      estado_juego: sala.estado === 'en_juego' ? '2do set' : 'Iniciando'
    }));

  if (loading) {
    return (
      <div className="mb-8">
        <h2 className="text-xl font-bold text-textPrimary mb-4 flex items-center gap-2">
          <Play size={20} className="text-green-400" />
          En juego / Hoy
        </h2>
        <div className="space-y-3">
          {[1, 2].map(i => (
            <div key={i} className="bg-cardBg border border-cardBorder rounded-lg p-4">
              <div className="animate-pulse">
                <div className="h-4 bg-cardBorder/30 rounded w-1/3 mb-2"></div>
                <div className="h-3 bg-cardBorder/30 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (salasEnJuego.length === 0) {
    return null; // No mostrar sección si no hay salas en juego
  }

  return (
    <div className="mb-8">
      <h2 className="text-xl font-bold text-textPrimary mb-4 flex items-center gap-2">
        <Play size={20} className="text-green-400" />
        En juego / Hoy ({salasEnJuego.length})
      </h2>
      
      <div className="space-y-3">
        {salasEnJuego.slice(0, 3).map((sala, index) => (
          <motion.div
            key={sala.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-gradient-to-r from-green-500/10 to-green-400/5 border border-green-400/30 rounded-lg p-4"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="font-bold text-textPrimary text-base">
                    {sala.nombre}
                  </h3>
                  <span className="px-2 py-1 rounded-full text-xs font-bold text-green-400 bg-green-400/20">
                    <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse inline-block mr-1"></div>
                    EN JUEGO
                  </span>
                </div>
                
                <div className="flex items-center gap-4 text-sm text-textSecondary">
                  <div className="flex items-center gap-1">
                    <Users size={14} />
                    <span>{sala.jugadores_actuales} / {sala.jugadores_maximos} jugadores</span>
                  </div>
                  
                  <div className="flex items-center gap-1">
                    <Clock size={14} />
                    <span>{sala.tiempo_transcurrido}</span>
                  </div>

                  {sala.estado_juego && (
                    <div className="text-green-400 font-semibold">
                      {sala.estado_juego}
                    </div>
                  )}
                </div>
              </div>

              <Button
                variant="secondary"
                onClick={() => onVerSala(parseInt(sala.id))}
                className="text-xs px-4 py-2"
              >
                <Eye size={12} className="mr-1" />
                Ver
              </Button>
            </div>
          </motion.div>
        ))}
      </div>

      {salasEnJuego.length > 3 && (
        <div className="mt-4 text-center">
          <Button variant="ghost" className="text-sm">
            Ver todas en juego ({salasEnJuego.length - 3} más)
          </Button>
        </div>
      )}
    </div>
  );
}