import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, UserPlus, ChevronDown, ChevronUp, Users, Calendar } from 'lucide-react';
import Button from './Button';
import { Sala } from '../utils/types';

interface SalasTableProps {
  salas: Sala[];
  onOpenSala: (sala: Sala) => void;
  onUnirse?: (sala: Sala) => void;
  usuarioId?: string;
  titulo?: string;
  mostrarAccionUnirse?: boolean;
  colapsable?: boolean;
  inicialmenteColapsado?: boolean;
}

const getEstadoConfig = (estado: string) => {
  switch (estado) {
    case 'esperando':
      return { color: 'text-purple-400', bg: 'bg-purple-500/20', label: 'Esperando' };
    case 'activa':
    case 'en_juego':
      return { color: 'text-green-400', bg: 'bg-green-500/20', label: 'En juego' };
    case 'finalizada':
      return { color: 'text-amber-400', bg: 'bg-amber-500/20', label: 'Finalizada' };
    case 'programada':
      return { color: 'text-blue-400', bg: 'bg-blue-500/20', label: 'Programada' };
    default:
      return { color: 'text-gray-400', bg: 'bg-gray-500/20', label: estado };
  }
};

const formatFecha = (fecha: string) => {
  const date = new Date(fecha);
  const hoy = new Date();
  const ayer = new Date(hoy);
  ayer.setDate(ayer.getDate() - 1);
  
  if (date.toDateString() === hoy.toDateString()) {
    return 'Hoy';
  }
  if (date.toDateString() === ayer.toDateString()) {
    return 'Ayer';
  }
  return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
};

export default function SalasTable({ 
  salas, 
  onOpenSala, 
  onUnirse,
  usuarioId,
  titulo = 'Explorar salas',
  mostrarAccionUnirse = true,
  colapsable = false,
  inicialmenteColapsado = false
}: SalasTableProps) {
  const [colapsado, setColapsado] = useState(inicialmenteColapsado);
  const [pagina, setPagina] = useState(1);
  const ITEMS_POR_PAGINA = 10;

  const salasVisibles = salas.slice(0, pagina * ITEMS_POR_PAGINA);
  const hayMas = salas.length > salasVisibles.length;

  if (salas.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      {/* Header */}
      <div 
        className={`flex items-center justify-between ${colapsable ? 'cursor-pointer' : ''}`}
        onClick={() => colapsable && setColapsado(!colapsado)}
      >
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-bold text-textPrimary">{titulo}</h2>
          <span className="text-textSecondary text-sm">({salas.length})</span>
        </div>
        {colapsable && (
          <button className="text-textSecondary hover:text-textPrimary transition-colors">
            {colapsado ? <ChevronDown size={20} /> : <ChevronUp size={20} />}
          </button>
        )}
      </div>

      <AnimatePresence>
        {!colapsado && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {/* Tabla Desktop */}
            <div className="hidden md:block bg-cardBg border border-cardBorder rounded-xl overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-cardBorder bg-background/50">
                    <th className="text-left text-xs font-bold text-textSecondary uppercase tracking-wider px-4 py-3">Nombre</th>
                    <th className="text-center text-xs font-bold text-textSecondary uppercase tracking-wider px-4 py-3">Jugadores</th>
                    <th className="text-center text-xs font-bold text-textSecondary uppercase tracking-wider px-4 py-3">Estado</th>
                    <th className="text-center text-xs font-bold text-textSecondary uppercase tracking-wider px-4 py-3">Fecha</th>
                    <th className="text-right text-xs font-bold text-textSecondary uppercase tracking-wider px-4 py-3">Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {salasVisibles.map((sala, index) => {
                    const config = getEstadoConfig(sala.estado);
                    const jugadoresCount = sala.jugadores?.length || 0;
                    const esParticipante = sala.jugadores?.some(j => j.id === usuarioId);
                    const puedeUnirse = sala.estado === 'esperando' && jugadoresCount < 4 && !esParticipante;

                    return (
                      <motion.tr
                        key={sala.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: index * 0.02 }}
                        className="border-b border-cardBorder/50 last:border-0 hover:bg-background/30 transition-colors"
                      >
                        <td className="px-4 py-3">
                          <span className="font-medium text-textPrimary">{sala.nombre}</span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className="text-textSecondary text-sm">{jugadoresCount}/4</span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
                            {(sala.estado === 'en_juego' || sala.estado === 'activa') && (
                              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                            )}
                            {config.label}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className="text-textSecondary text-sm">{formatFecha(sala.fecha)}</span>
                        </td>
                        <td className="px-4 py-3 text-right">
                          {puedeUnirse && mostrarAccionUnirse ? (
                            <Button
                              variant="primary"
                              className="text-xs px-3 py-1.5"
                              onClick={() => onUnirse?.(sala)}
                            >
                              <UserPlus size={12} className="mr-1" />
                              Unirse
                            </Button>
                          ) : (
                            <Button
                              variant="secondary"
                              className="text-xs px-3 py-1.5"
                              onClick={() => onOpenSala(sala)}
                            >
                              <Eye size={12} className="mr-1" />
                              Ver
                            </Button>
                          )}
                        </td>
                      </motion.tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Lista Mobile */}
            <div className="md:hidden space-y-2">
              {salasVisibles.map((sala, index) => {
                const config = getEstadoConfig(sala.estado);
                const jugadoresCount = sala.jugadores?.length || 0;
                const esParticipante = sala.jugadores?.some(j => j.id === usuarioId);
                const puedeUnirse = sala.estado === 'esperando' && jugadoresCount < 4 && !esParticipante;

                return (
                  <motion.div
                    key={sala.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.02 }}
                    className="bg-cardBg border border-cardBorder rounded-lg p-3"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-textPrimary text-sm truncate flex-1">{sala.nombre}</span>
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium ${config.bg} ${config.color}`}>
                        {(sala.estado === 'en_juego' || sala.estado === 'activa') && (
                          <span className="w-1 h-1 rounded-full bg-green-400 animate-pulse" />
                        )}
                        {config.label}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
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
                      {puedeUnirse && mostrarAccionUnirse ? (
                        <Button
                          variant="primary"
                          className="text-[10px] px-2 py-1"
                          onClick={() => onUnirse?.(sala)}
                        >
                          Unirse
                        </Button>
                      ) : (
                        <Button
                          variant="secondary"
                          className="text-[10px] px-2 py-1"
                          onClick={() => onOpenSala(sala)}
                        >
                          Ver
                        </Button>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>

            {/* Cargar más */}
            {hayMas && (
              <div className="mt-4 text-center">
                <Button
                  variant="ghost"
                  className="text-sm"
                  onClick={() => setPagina(p => p + 1)}
                >
                  Cargar más ({salas.length - salasVisibles.length} restantes)
                </Button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
