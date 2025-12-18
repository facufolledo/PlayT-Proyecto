import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Clock, MapPin, Plus, Trash2, Zap, AlertCircle } from 'lucide-react';
import { torneoService } from '../services/torneo.service';
import Card from './Card';
import Button from './Button';
import SkeletonLoader from './SkeletonLoader';

interface TorneoProgramacionProps {
  torneoId: number;
  esOrganizador: boolean;
}

interface Cancha {
  id: number;
  nombre: string;
  activa: boolean;
}

interface Slot {
  id: number;
  cancha_id: number;
  cancha_nombre?: string;
  fecha_hora_inicio: string;
  fecha_hora_fin: string;
  ocupado: boolean;
  partido_id?: number;
}

export default function TorneoProgramacion({ torneoId, esOrganizador }: TorneoProgramacionProps) {
  const [canchas, setCanchas] = useState<Cancha[]>([]);
  const [slots, setSlots] = useState<Slot[]>([]);
  const [loading, setLoading] = useState(true);
  const [programando, setProgramando] = useState(false);
  const [error, setError] = useState('');
  
  // Modal crear cancha
  const [modalCanchaOpen, setModalCanchaOpen] = useState(false);
  const [nombreCancha, setNombreCancha] = useState('');
  
  // Programación automática
  const [fechaInicio, setFechaInicio] = useState('');
  const [fechaFin, setFechaFin] = useState('');
  const [duracionPartido, setDuracionPartido] = useState(90);

  useEffect(() => {
    cargarDatos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [torneoId]);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      setError('');
      const [canchasData, slotsData] = await Promise.all([
        torneoService.listarCanchas(torneoId),
        torneoService.listarSlots(torneoId)
      ]);
      
      // Asegurar que siempre sean arrays
      setCanchas(Array.isArray(canchasData) ? canchasData : []);
      setSlots(Array.isArray(slotsData) ? slotsData : []);
    } catch (error: any) {
      console.error('Error al cargar datos:', error);
      // Si es 404, probablemente no hay canchas aún
      if (error.response?.status === 404) {
        setCanchas([]);
        setSlots([]);
      } else {
        setError(error.response?.data?.detail || 'Error al cargar la programación');
      }
    } finally {
      setLoading(false);
    }
  };

  const crearCancha = async () => {
    if (!nombreCancha.trim()) {
      setError('El nombre de la cancha es requerido');
      return;
    }

    try {
      setError('');
      await torneoService.crearCancha(torneoId, { nombre: nombreCancha.trim(), activa: true });
      setNombreCancha('');
      setModalCanchaOpen(false);
      setError('');
      await cargarDatos();
    } catch (error: any) {
      console.error('Error al crear cancha:', error);
      setError(error.response?.data?.detail || error.message || 'Error al crear cancha');
    }
  };

  const eliminarCancha = async (canchaId: number) => {
    if (!confirm('¿Estás seguro de eliminar esta cancha? Se eliminarán todos los horarios asociados.')) return;

    try {
      setError('');
      await torneoService.eliminarCancha(torneoId, canchaId);
      await cargarDatos();
    } catch (error: any) {
      console.error('Error al eliminar cancha:', error);
      setError(error.response?.data?.detail || error.message || 'Error al eliminar cancha');
    }
  };

  const programarAutomaticamente = async () => {
    if (!fechaInicio || !fechaFin) {
      setError('Debes seleccionar las fechas de inicio y fin');
      return;
    }

    if (new Date(fechaInicio) > new Date(fechaFin)) {
      setError('La fecha de inicio debe ser anterior a la fecha de fin');
      return;
    }

    if (canchas.length === 0) {
      setError('Debes crear al menos una cancha antes de programar');
      return;
    }

    try {
      setProgramando(true);
      setError('');
      const resultado = await torneoService.programarPartidosAutomaticamente(torneoId, {
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
        duracion_partido_minutos: duracionPartido
      });
      await cargarDatos();
      
      // Mostrar resultado
      const mensaje = resultado.mensaje || 'Programación automática completada';
      const partidosProgramados = resultado.partidos_programados || 0;
      alert(`${mensaje}\n\nPartidos programados: ${partidosProgramados}`);
    } catch (error: any) {
      console.error('Error al programar:', error);
      setError(error.response?.data?.detail || error.message || 'Error al programar partidos');
    } finally {
      setProgramando(false);
    }
  };

  const agruparSlotsPorFecha = () => {
    const grupos: { [fecha: string]: Slot[] } = {};
    slots.forEach(slot => {
      const fecha = new Date(slot.fecha_hora_inicio).toLocaleDateString('es-ES');
      if (!grupos[fecha]) grupos[fecha] = [];
      grupos[fecha].push(slot);
    });
    return grupos;
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <SkeletonLoader height="200px" />
        <SkeletonLoader height="400px" />
      </div>
    );
  }

  const slotsPorFecha = agruparSlotsPorFecha();

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-textPrimary">Programación de Partidos</h2>
          <p className="text-xs md:text-sm text-textSecondary">Gestiona canchas y horarios</p>
        </div>
        {esOrganizador && (
          <Button
            variant="accent"
            onClick={() => setModalCanchaOpen(true)}
            className="text-sm md:text-base"
          >
            <Plus size={16} className="mr-1.5 md:mr-2" />
            Nueva Cancha
          </Button>
        )}
      </div>

      {/* Error */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg"
        >
          <AlertCircle size={18} className="text-red-500 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-500">{error}</p>
        </motion.div>
      )}

      {/* Canchas */}
      <Card>
        <div className="p-4 md:p-6">
          <h3 className="text-lg md:text-xl font-bold text-textPrimary mb-3 md:mb-4 flex items-center gap-2">
            <MapPin size={20} className="text-primary" />
            Canchas Disponibles
          </h3>

          {canchas.length === 0 ? (
            <div className="text-center py-8 text-textSecondary">
              <MapPin size={40} className="mx-auto mb-3 opacity-50" />
              <p className="text-sm md:text-base">No hay canchas configuradas</p>
              {esOrganizador && (
                <Button
                  variant="primary"
                  onClick={() => setModalCanchaOpen(true)}
                  className="mt-4 text-sm"
                >
                  Crear Primera Cancha
                </Button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 md:gap-3">
              {canchas.map((cancha, idx) => (
                <motion.div
                  key={cancha.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="p-3 md:p-4 bg-background rounded-lg border border-cardBorder flex items-center justify-between"
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <div className={`w-2 h-2 rounded-full ${cancha.activa ? 'bg-green-500' : 'bg-gray-500'}`} />
                    <span className="font-bold text-textPrimary text-sm md:text-base truncate">{cancha.nombre}</span>
                  </div>
                  {esOrganizador && (
                    <button
                      onClick={() => eliminarCancha(cancha.id)}
                      className="text-textSecondary hover:text-red-500 transition-colors p-1"
                    >
                      <Trash2 size={16} />
                    </button>
                  )}
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </Card>

      {/* Programación Automática */}
      {esOrganizador && canchas.length > 0 && (
        <Card>
          <div className="p-4 md:p-6">
            <h3 className="text-lg md:text-xl font-bold text-textPrimary mb-3 md:mb-4 flex items-center gap-2">
              <Zap size={20} className="text-accent" />
              Programación Automática
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4 mb-4">
              <div>
                <label className="block text-xs md:text-sm font-bold text-textSecondary mb-2">
                  Fecha Inicio
                </label>
                <input
                  type="date"
                  value={fechaInicio}
                  onChange={(e) => setFechaInicio(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-cardBorder rounded-lg text-textPrimary text-sm"
                />
              </div>

              <div>
                <label className="block text-xs md:text-sm font-bold text-textSecondary mb-2">
                  Fecha Fin
                </label>
                <input
                  type="date"
                  value={fechaFin}
                  onChange={(e) => setFechaFin(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-cardBorder rounded-lg text-textPrimary text-sm"
                />
              </div>

              <div>
                <label className="block text-xs md:text-sm font-bold text-textSecondary mb-2">
                  Duración (min)
                </label>
                <input
                  type="number"
                  value={duracionPartido}
                  onChange={(e) => setDuracionPartido(parseInt(e.target.value) || 90)}
                  min="30"
                  max="180"
                  step="15"
                  className="w-full px-3 py-2 bg-background border border-cardBorder rounded-lg text-textPrimary text-sm"
                />
              </div>
            </div>

            <Button
              variant="accent"
              onClick={programarAutomaticamente}
              disabled={programando || !fechaInicio || !fechaFin}
              className="w-full md:w-auto text-sm md:text-base"
            >
              {programando ? 'Programando...' : 'Programar Automáticamente'}
            </Button>
          </div>
        </Card>
      )}

      {/* Programación por Fecha */}
      {Object.keys(slotsPorFecha).length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg md:text-xl font-bold text-textPrimary flex items-center gap-2">
            <Calendar size={20} className="text-primary" />
            Horarios Programados
          </h3>

          {Object.entries(slotsPorFecha).map(([fecha, slotsDelDia]) => (
            <Card key={fecha}>
              <div className="p-4 md:p-6">
                <h4 className="font-bold text-textPrimary mb-3 text-sm md:text-base">{fecha}</h4>
                <div className="space-y-2">
                  {slotsDelDia.map((slot, idx) => (
                    <motion.div
                      key={slot.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.03 }}
                      className={`p-2 md:p-3 rounded-lg border flex flex-col sm:flex-row sm:items-center justify-between gap-2 ${
                        slot.ocupado
                          ? 'bg-green-500/10 border-green-500/30'
                          : 'bg-background border-cardBorder'
                      }`}
                    >
                      <div className="flex items-center gap-2 md:gap-3 flex-1 min-w-0">
                        <Clock size={14} className="text-textSecondary flex-shrink-0 md:w-4 md:h-4" />
                        <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2 flex-1 min-w-0">
                          <span className="text-xs md:text-sm text-textPrimary font-medium whitespace-nowrap">
                            {new Date(slot.fecha_hora_inicio).toLocaleTimeString('es-ES', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                            {' - '}
                            {new Date(slot.fecha_hora_fin).toLocaleTimeString('es-ES', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                          <span className="text-xs md:text-sm text-textSecondary truncate">
                            {slot.cancha_nombre || `Cancha ${slot.cancha_id}`}
                          </span>
                        </div>
                      </div>
                      <span
                        className={`text-xs font-bold px-2 py-1 rounded-full whitespace-nowrap self-start sm:self-auto ${
                          slot.ocupado
                            ? 'bg-green-500/20 text-green-500'
                            : 'bg-gray-500/20 text-gray-500'
                        }`}
                      >
                        {slot.ocupado ? 'Ocupado' : 'Libre'}
                      </span>
                    </motion.div>
                  ))}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Modal Crear Cancha */}
      {modalCanchaOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-3 md:p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-card rounded-xl max-w-md w-full p-4 md:p-6"
          >
            <h3 className="text-lg md:text-xl font-bold text-textPrimary mb-3 md:mb-4">Nueva Cancha</h3>

            <div className="mb-4">
              <label className="block text-xs md:text-sm font-bold text-textSecondary mb-2">
                Nombre de la Cancha *
              </label>
              <input
                type="text"
                value={nombreCancha}
                onChange={(e) => setNombreCancha(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    crearCancha();
                  }
                }}
                placeholder="Ej: Cancha 1"
                className="w-full px-3 md:px-4 py-2 md:py-3 bg-background border border-cardBorder rounded-lg text-textPrimary text-sm md:text-base focus:outline-none focus:border-primary"
                autoFocus
                maxLength={50}
              />
              <p className="text-xs text-textSecondary mt-1">
                {nombreCancha.length}/50 caracteres
              </p>
            </div>

            <div className="flex gap-2 md:gap-3">
              <Button
                variant="ghost"
                onClick={() => {
                  setModalCanchaOpen(false);
                  setNombreCancha('');
                  setError('');
                }}
                className="flex-1 text-sm md:text-base"
              >
                Cancelar
              </Button>
              <Button 
                variant="accent" 
                onClick={crearCancha} 
                className="flex-1 text-sm md:text-base"
                disabled={!nombreCancha.trim()}
              >
                Crear
              </Button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
