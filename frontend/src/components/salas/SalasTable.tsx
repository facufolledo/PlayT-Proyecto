import { motion } from 'framer-motion';
import { Users, Clock, Calendar, Play, Eye, UserPlus } from 'lucide-react';
import Button from '../Button';
import { useState } from 'react';

interface SalaTabla {
  id: number;
  nombre: string;
  jugadores_actuales: number;
  jugadores_maximos: number;
  estado: 'esperando' | 'en_juego' | 'finalizada';
  fecha: string;
  organizador: string;
  puede_unirse: boolean;
}

interface SalasTableProps {
  salas: SalaTabla[];
  loading?: boolean;
  onUnirse: (salaId: number) => void;
  onVer: (salaId: number) => void;
}

export default function SalasTable({ salas, loading = false, onUnirse, onVer }: SalasTableProps) {
  const [paginaActual, setPaginaActual] = useState(1);
  const ITEMS_POR_PAGINA = 10;

  const getEstadoColor = (estado: string) => {
    switch (estado) {
      case 'esperando': return 'text-yellow-400 bg-yellow-400/20';
      case 'en_juego': return 'text-green-400 bg-green-400/20';
      case 'finalizada': return 'text-gray-400 bg-gray-400/20';
      default: return 'text-gray-400 bg-gray-400/20';
    }
  };

  const getEstadoTexto = (estado: string) => {
    switch (estado) {
      case 'esperando': return 'Esperando';
      case 'en_juego': return 'En juego';
      case 'finalizada': return 'Finalizada';
      default: return estado;
    }
  };

  const formatearFecha = (fecha: string) => {
    const fechaObj = new Date(fecha);
    const hoy = new Date();
    const manana = new Date(hoy);
    manana.setDate(hoy.getDate() + 1);

    if (fechaObj.toDateString() === hoy.toDateString()) {
      return `Hoy ${fechaObj.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}`;
    } else if (fechaObj.toDateString() === manana.toDateString()) {
      return `Mañana ${fechaObj.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}`;
    } else {
      return fechaObj.toLocaleDateString('es-ES', { 
        day: 'numeric', 
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  };

  const salasActuales = salas.slice(
    (paginaActual - 1) * ITEMS_POR_PAGINA,
    paginaActual * ITEMS_POR_PAGINA
  );

  const totalPaginas = Math.ceil(salas.length / ITEMS_POR_PAGINA);

  if (loading) {
    return (
      <div className="bg-cardBg border border-cardBorder rounded-lg overflow-hidden">
        <div className="p-4 border-b border-cardBorder">
          <div className="h-6 bg-cardBorder animate-pulse rounded w-32"></div>
        </div>
        <div className="p-4 space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-12 bg-cardBorder animate-pulse rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-cardBg border border-cardBorder rounded-lg overflow-hidden">
      {/* Header de tabla */}
      <div className="bg-cardBorder/30 px-4 py-3 border-b border-cardBorder">
        <div className="grid grid-cols-12 gap-4 text-xs font-bold text-textSecondary uppercase tracking-wider">
          <div className="col-span-3">Nombre</div>
          <div className="col-span-2 text-center">Jugadores</div>
          <div className="col-span-2 text-center">Estado</div>
          <div className="col-span-3">Fecha</div>
          <div className="col-span-2 text-center">Acción</div>
        </div>
      </div>

      {/* Filas de datos */}
      <div className="divide-y divide-cardBorder">
        {salasActuales.length === 0 ? (
          <div className="p-8 text-center">
            <Users size={32} className="mx-auto mb-3 text-textSecondary opacity-50" />
            <p className="text-textSecondary">No hay salas disponibles</p>
          </div>
        ) : (
          salasActuales.map((sala, index) => (
            <motion.div
              key={sala.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="px-4 py-3 hover:bg-cardBorder/20 transition-colors"
            >
              <div className="grid grid-cols-12 gap-4 items-center">
                {/* Nombre */}
                <div className="col-span-3">
                  <div className="font-semibold text-textPrimary text-sm truncate">
                    {sala.nombre}
                  </div>
                  <div className="text-xs text-textSecondary truncate">
                    por {sala.organizador}
                  </div>
                </div>

                {/* Jugadores */}
                <div className="col-span-2 text-center">
                  <div className="flex items-center justify-center gap-1">
                    <Users size={14} className="text-textSecondary" />
                    <span className="text-sm font-semibold text-textPrimary">
                      {sala.jugadores_actuales} / {sala.jugadores_maximos}
                    </span>
                  </div>
                </div>

                {/* Estado */}
                <div className="col-span-2 text-center">
                  <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold ${getEstadoColor(sala.estado)}`}>
                    {sala.estado === 'en_juego' && <div className="w-1.5 h-1.5 bg-current rounded-full animate-pulse"></div>}
                    {getEstadoTexto(sala.estado)}
                  </span>
                </div>

                {/* Fecha */}
                <div className="col-span-3">
                  <div className="flex items-center gap-1 text-sm text-textSecondary">
                    <Calendar size={14} />
                    <span>{formatearFecha(sala.fecha)}</span>
                  </div>
                </div>

                {/* Acción */}
                <div className="col-span-2 text-center">
                  {sala.estado === 'esperando' && sala.puede_unirse ? (
                    <Button
                      variant="primary"
                      onClick={() => onUnirse(sala.id)}
                      className="text-xs px-3 py-1.5"
                    >
                      <UserPlus size={12} className="mr-1" />
                      Unirse
                    </Button>
                  ) : sala.estado === 'en_juego' ? (
                    <Button
                      variant="secondary"
                      onClick={() => onVer(sala.id)}
                      className="text-xs px-3 py-1.5"
                    >
                      <Eye size={12} className="mr-1" />
                      Ver
                    </Button>
                  ) : sala.estado === 'esperando' ? (
                    <span className="text-xs text-textSecondary">Llena</span>
                  ) : (
                    <Button
                      variant="ghost"
                      onClick={() => onVer(sala.id)}
                      className="text-xs px-3 py-1.5"
                    >
                      <Eye size={12} className="mr-1" />
                      Ver
                    </Button>
                  )}
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* Paginación */}
      {totalPaginas > 1 && (
        <div className="px-4 py-3 border-t border-cardBorder bg-cardBorder/10">
          <div className="flex items-center justify-between">
            <div className="text-xs text-textSecondary">
              Mostrando {((paginaActual - 1) * ITEMS_POR_PAGINA) + 1} - {Math.min(paginaActual * ITEMS_POR_PAGINA, salas.length)} de {salas.length} salas
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                onClick={() => setPaginaActual(prev => Math.max(1, prev - 1))}
                disabled={paginaActual === 1}
                className="text-xs px-3 py-1"
              >
                Anterior
              </Button>
              
              <span className="text-xs text-textSecondary">
                {paginaActual} / {totalPaginas}
              </span>
              
              <Button
                variant="ghost"
                onClick={() => setPaginaActual(prev => Math.min(totalPaginas, prev + 1))}
                disabled={paginaActual === totalPaginas}
                className="text-xs px-3 py-1"
              >
                Siguiente
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
