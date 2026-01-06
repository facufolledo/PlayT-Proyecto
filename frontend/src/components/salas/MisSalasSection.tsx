import { motion } from 'framer-motion';
import { Crown, Users, Clock, Calendar, ChevronDown } from 'lucide-react';
import Button from '../Button';
import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';

interface MiSala {
  id: number;
  nombre: string;
  estado: 'esperando' | 'en_juego' | 'finalizada';
  jugadores_actuales: number;
  jugadores_maximos: number;
  fecha: string;
  hora: string;
  es_organizador: boolean;
  tiempo_transcurrido?: string;
}

interface MisSalasSectionProps {
  salas: any[];
  onEntrarSala: (salaId: number) => void;
  onVerPartido: (salaId: number) => void;
  loading?: boolean;
}

export default function MisSalasSection({ salas, onEntrarSala, onVerPartido, loading }: MisSalasSectionProps) {
  const { usuario } = useAuth();
  const [expandido, setExpandido] = useState(false);

  // Convertir salas del formato actual al formato esperado
  const misSalasFormateadas: MiSala[] = salas.map(sala => {
    // Mapear estados correctamente
    let estadoMapeado: 'esperando' | 'en_juego' | 'finalizada';
    
    switch (sala.estado) {
      case 'esperando':
      case 'pendiente':
        estadoMapeado = 'esperando';
        break;
      case 'activa':
      case 'en_juego':
      case 'jugando':
        estadoMapeado = 'en_juego';
        break;
      case 'finalizada':
      case 'terminada':
      case 'completada':
        estadoMapeado = 'finalizada';
        break;
      default:
        // Si no reconocemos el estado, usar el estado original o 'esperando' por defecto
        estadoMapeado = sala.estado === 'finalizada' ? 'finalizada' : 'esperando';
    }

    return {
      id: parseInt(sala.id),
      nombre: sala.nombre || `Sala #${sala.id}`,
      estado: estadoMapeado,
      jugadores_actuales: sala.jugadores?.length || 0,
      jugadores_maximos: sala.max_jugadores || 4,
      fecha: new Date(sala.fecha_creacion || Date.now()).toLocaleDateString('es-AR', { 
        day: '2-digit', 
        month: 'short' 
      }),
      hora: new Date(sala.fecha_creacion || Date.now()).toLocaleTimeString('es-AR', { 
        hour: '2-digit', 
        minute: '2-digit' 
      }),
      es_organizador: sala.creador_id === usuario?.id_usuario?.toString() || sala.creador_id === usuario?.id_usuario,
      tiempo_transcurrido: estadoMapeado === 'en_juego' ? 'En curso' : undefined
    };
  });

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
      case 'esperando': return 'ESPERANDO';
      case 'en_juego': return 'EN JUEGO';
      case 'finalizada': return 'FINALIZADA';
      default: return estado.toUpperCase();
    }
  };

  const getAccionButton = (sala: MiSala) => {
    const salaOriginal = salas.find(s => parseInt(s.id) === sala.id);
    
    // Si la sala está finalizada, solo mostrar "Ver"
    if (sala.estado === 'finalizada') {
      return (
        <Button
          variant="ghost"
          onClick={() => onVerPartido(sala.id)}
          className="text-xs px-2 md:px-4 py-1.5 md:py-2"
        >
          Ver
        </Button>
      );
    }
    
    // Si la sala está en juego, mostrar "Ver Partido"
    if (sala.estado === 'en_juego') {
      return (
        <Button
          variant="secondary"
          onClick={() => onVerPartido(sala.id)}
          className="text-xs px-2 md:px-4 py-1.5 md:py-2"
        >
          <span className="hidden sm:inline">Ver Partido</span>
          <span className="sm:hidden">Ver</span>
        </Button>
      );
    }
    
    // Si la sala está esperando
    if (sala.estado === 'esperando') {
      // Si soy el organizador o ya estoy en la sala, mostrar "Entrar"
      if (sala.es_organizador || salaOriginal?.jugadores?.some(j => j.id === usuario?.id_usuario?.toString())) {
        return (
          <Button
            variant="primary"
            onClick={() => onEntrarSala(sala.id)}
            className="text-xs px-2 md:px-4 py-1.5 md:py-2"
          >
            Entrar
          </Button>
        );
      } else {
        // Si no estoy en la sala, mostrar "Unirse"
        return (
          <Button
            variant="primary"
            onClick={() => onEntrarSala(sala.id)}
            className="text-xs px-2 md:px-4 py-1.5 md:py-2"
          >
            Unirse
          </Button>
        );
      }
    }
    
    // Fallback
    return (
      <Button
        variant="ghost"
        onClick={() => onVerPartido(sala.id)}
        className="text-xs px-2 md:px-4 py-1.5 md:py-2"
      >
        Ver
      </Button>
    );
  };

  if (loading) {
    return (
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-textPrimary flex items-center gap-2">
            <Crown size={20} className="text-primary" />
            Mis Salas
          </h2>
        </div>
        <div className="bg-cardBg border border-cardBorder rounded-lg p-6">
          <div className="animate-pulse space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-16 bg-cardBorder/30 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (misSalasFormateadas.length === 0) {
    return (
      <div className="mb-8">
        <h2 className="text-xl font-bold text-textPrimary mb-4 flex items-center gap-2">
          <Crown size={20} className="text-primary" />
          Mis Salas (0)
        </h2>
        <div className="bg-cardBg/50 border border-cardBorder rounded-lg p-6 text-center">
          <Users size={32} className="mx-auto mb-3 text-textSecondary opacity-50" />
          <p className="text-textSecondary text-sm mb-3">No tienes salas creadas</p>
          <p className="text-textSecondary text-xs">Crea una sala para comenzar a jugar</p>
        </div>
      </div>
    );
  }

  const salasVisibles = expandido ? misSalasFormateadas : misSalasFormateadas.slice(0, 3);

  return (
    <div className="mb-8">
      {/* Header con info del usuario */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Crown size={20} className="text-primary" />
          <div>
            <h2 className="text-xl font-bold text-textPrimary">
              Mis Salas ({misSalasFormateadas.length})
            </h2>
            <p className="text-textSecondary text-sm">
              {usuario?.nombre} {usuario?.apellido} • Rating: {usuario?.rating || 1000}
            </p>
          </div>
        </div>
        
        {misSalasFormateadas.length > 3 && (
          <Button
            variant="ghost"
            onClick={() => setExpandido(!expandido)}
            className="flex items-center gap-2 text-sm"
          >
            {expandido ? 'Contraer' : `Expandir (${misSalasFormateadas.length - 3} más)`}
            <ChevronDown 
              size={16} 
              className={`transform transition-transform ${expandido ? 'rotate-180' : ''}`} 
            />
          </Button>
        )}
      </div>
      
      {/* Lista de salas estilo tabla compacta */}
      <div className="bg-cardBg border border-cardBorder rounded-lg overflow-hidden">
        {/* Header de la tabla - Oculto en móvil */}
        <div className="bg-cardBorder/20 px-3 md:px-4 py-2 md:py-3 border-b border-cardBorder hidden md:block">
          <div className="grid grid-cols-12 gap-2 md:gap-4 text-xs font-bold text-textSecondary uppercase tracking-wider">
            <div className="col-span-4">Sala</div>
            <div className="col-span-2">Jugadores</div>
            <div className="col-span-2">Estado</div>
            <div className="col-span-2">Fecha</div>
            <div className="col-span-2 text-right">Acción</div>
          </div>
        </div>

        {/* Filas de salas */}
        <div className="divide-y divide-cardBorder">
          {salasVisibles.map((sala, index) => (
            <motion.div
              key={sala.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="px-3 md:px-4 py-3 hover:bg-cardBorder/10 transition-colors"
            >
              {/* Layout móvil */}
              <div className="block md:hidden">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-textPrimary text-sm truncate">{sala.nombre}</p>
                    {/* Debug info - remover en producción */}
                    <p className="text-[8px] text-gray-400">Estado: {salas.find(s => parseInt(s.id) === sala.id)?.estado}</p>
                    {sala.es_organizador && (
                      <div className="flex items-center gap-1 mt-1">
                        <Crown size={10} className="text-yellow-400" />
                        <span className="text-[10px] text-yellow-400">Organizador</span>
                      </div>
                    )}
                  </div>
                  <div className="ml-2 flex-shrink-0">
                    {getAccionButton(sala)}
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-xs text-textSecondary">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1">
                      <Users size={12} />
                      <span>{sala.jugadores_actuales}/{sala.jugadores_maximos}</span>
                    </div>
                    
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${getEstadoColor(sala.estado)}`}>
                      ● {getEstadoTexto(sala.estado)}
                    </span>
                  </div>
                  
                  <div className="text-right">
                    {sala.estado === 'esperando' && (
                      <div className="flex items-center gap-1">
                        <Calendar size={10} />
                        <span className="text-[10px]">{sala.fecha}</span>
                      </div>
                    )}
                    {sala.estado === 'en_juego' && sala.tiempo_transcurrido && (
                      <div className="flex items-center gap-1">
                        <Clock size={10} />
                        <span className="text-[10px]">{sala.tiempo_transcurrido}</span>
                      </div>
                    )}
                    {sala.estado === 'finalizada' && (
                      <span className="text-[10px]">{sala.fecha}</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Layout desktop */}
              <div className="hidden md:grid grid-cols-12 gap-4 items-center">
                {/* Nombre de la sala */}
                <div className="col-span-4 flex items-center gap-2">
                  <div>
                    <p className="font-bold text-textPrimary text-sm">{sala.nombre}</p>
                    {/* Debug info - remover en producción */}
                    <p className="text-[8px] text-gray-400">Estado original: {salas.find(s => parseInt(s.id) === sala.id)?.estado}</p>
                    {sala.es_organizador && (
                      <div className="flex items-center gap-1 mt-1">
                        <Crown size={12} className="text-yellow-400" />
                        <span className="text-xs text-yellow-400">Organizador</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Jugadores */}
                <div className="col-span-2">
                  <div className="flex items-center gap-1 text-sm text-textSecondary">
                    <Users size={14} />
                    <span>{sala.jugadores_actuales} / {sala.jugadores_maximos}</span>
                  </div>
                </div>

                {/* Estado */}
                <div className="col-span-2">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-bold ${getEstadoColor(sala.estado)}`}>
                      ● {getEstadoTexto(sala.estado)}
                    </span>
                    {sala.estado === 'en_juego' && (
                      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    )}
                  </div>
                </div>

                {/* Fecha */}
                <div className="col-span-2">
                  <div className="text-sm text-textSecondary">
                    {sala.estado === 'esperando' && (
                      <div className="flex items-center gap-1">
                        <Calendar size={12} />
                        <span>{sala.fecha} {sala.hora}</span>
                      </div>
                    )}
                    {sala.estado === 'en_juego' && sala.tiempo_transcurrido && (
                      <div className="flex items-center gap-1">
                        <Clock size={12} />
                        <span>{sala.tiempo_transcurrido}</span>
                      </div>
                    )}
                    {sala.estado === 'finalizada' && (
                      <span>{sala.fecha}</span>
                    )}
                  </div>
                </div>

                {/* Acción */}
                <div className="col-span-2 text-right">
                  {getAccionButton(sala)}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
