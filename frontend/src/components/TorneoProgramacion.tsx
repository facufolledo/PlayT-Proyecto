import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Calendar, Clock, MapPin, Plus, Trash2, Play, 
  RefreshCw, AlertCircle, CheckCircle, X
} from 'lucide-react';
import Card from './Card';
import Button from './Button';
import torneoService from '../services/torneo.service';

interface Cancha {
  id: number;
  nombre: string;
  activa: boolean;
}

interface Slot {
  id: number;
  cancha_id: number;
  cancha_nombre: string;
  fecha_hora_inicio: string;
  fecha_hora_fin: string;
  ocupado: boolean;
  partido_id: number | null;
}

interface Props {
  torneoId: number;
  esOrganizador: boolean;
}

export default function TorneoProgramacion({ torneoId, esOrganizador }: Props) {
  const [canchas, setCanchas] = useState<Cancha[]>([]);
  const [slots, setSlots] = useState<Slot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Form states
  const [nuevaCancha, setNuevaCancha] = useState('');
  const [showSlotForm, setShowSlotForm] = useState(false);
  const [slotForm, setSlotForm] = useState({
    fecha: '',
    horaInicio: '09:00',
    horaFin: '21:00',
    duracion: 90
  });
  const [programando, setProgramando] = useState(false);
  const [fechaFiltro, setFechaFiltro] = useState('');

  useEffect(() => {
    cargarDatos();
  }, [torneoId]);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const [canchasData, slotsData] = await Promise.all([
        torneoService.listarCanchas(torneoId),
        torneoService.listarSlots(torneoId)
      ]);
      setCanchas(canchasData);
      setSlots(slotsData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar datos');
    } finally {
      setLoading(false);
    }
  };


  const crearCancha = async () => {
    if (!nuevaCancha.trim()) return;
    
    try {
      await torneoService.crearCancha(torneoId, nuevaCancha.trim());
      setNuevaCancha('');
      setSuccess('Cancha creada');
      cargarDatos();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear cancha');
    }
  };

  const eliminarCancha = async (canchaId: number) => {
    if (!confirm('¿Eliminar esta cancha?')) return;
    
    try {
      await torneoService.eliminarCancha(torneoId, canchaId);
      setSuccess('Cancha eliminada');
      cargarDatos();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar cancha');
    }
  };

  const crearSlots = async () => {
    if (!slotForm.fecha) {
      setError('Selecciona una fecha');
      return;
    }
    
    try {
      const result = await torneoService.crearSlots(
        torneoId,
        slotForm.fecha,
        slotForm.horaInicio,
        slotForm.horaFin,
        slotForm.duracion
      );
      setSuccess(result.message);
      setShowSlotForm(false);
      cargarDatos();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear slots');
    }
  };

  const programarPartidos = async () => {
    try {
      setProgramando(true);
      const result = await torneoService.programarPartidos(torneoId);
      setSuccess(`${result.message}. Sin programar: ${result.sin_programar}`);
      cargarDatos();
      setTimeout(() => setSuccess(null), 5000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al programar partidos');
    } finally {
      setProgramando(false);
    }
  };

  const slotsFiltrados = fechaFiltro 
    ? slots.filter(s => s.fecha_hora_inicio?.startsWith(fechaFiltro))
    : slots;

  // Agrupar slots por fecha
  const slotsPorFecha = slotsFiltrados.reduce((acc, slot) => {
    const fecha = slot.fecha_hora_inicio?.split('T')[0] || 'Sin fecha';
    if (!acc[fecha]) acc[fecha] = [];
    acc[fecha].push(slot);
    return acc;
  }, {} as Record<string, Slot[]>);

  if (loading) {
    return (
      <Card>
        <div className="p-6 text-center">
          <RefreshCw className="animate-spin mx-auto text-primary" size={32} />
          <p className="text-textSecondary mt-2">Cargando...</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Mensajes */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-center gap-3"
        >
          <AlertCircle className="text-red-500" size={20} />
          <span className="text-red-500 flex-1">{error}</span>
          <button onClick={() => setError(null)}>
            <X size={18} className="text-red-500" />
          </button>
        </motion.div>
      )}

      {success && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-green-500/10 border border-green-500/30 rounded-lg p-4 flex items-center gap-3"
        >
          <CheckCircle className="text-green-500" size={20} />
          <span className="text-green-500">{success}</span>
        </motion.div>
      )}

      {/* Canchas */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-textPrimary flex items-center gap-2">
              <MapPin size={20} className="text-primary" />
              Canchas ({canchas.length})
            </h3>
          </div>

          {esOrganizador && (
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={nuevaCancha}
                onChange={(e) => setNuevaCancha(e.target.value)}
                placeholder="Nombre de la cancha (ej: Cancha 1)"
                className="flex-1 px-4 py-2 bg-background border border-cardBorder rounded-lg text-textPrimary"
                onKeyPress={(e) => e.key === 'Enter' && crearCancha()}
              />
              <Button onClick={crearCancha} disabled={!nuevaCancha.trim()}>
                <Plus size={18} />
              </Button>
            </div>
          )}

          {canchas.length === 0 ? (
            <p className="text-textSecondary text-center py-4">
              No hay canchas configuradas
            </p>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {canchas.map((cancha) => (
                <div
                  key={cancha.id}
                  className="flex items-center justify-between p-3 bg-background rounded-lg"
                >
                  <span className="text-textPrimary font-medium">{cancha.nombre}</span>
                  {esOrganizador && (
                    <button
                      onClick={() => eliminarCancha(cancha.id)}
                      className="text-red-500 hover:text-red-400"
                    >
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>


      {/* Slots de Horarios */}
      <Card>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-textPrimary flex items-center gap-2">
              <Clock size={20} className="text-primary" />
              Horarios Disponibles
            </h3>
            {esOrganizador && (
              <Button
                variant="ghost"
                onClick={() => setShowSlotForm(!showSlotForm)}
                className="flex items-center gap-2"
              >
                <Plus size={18} />
                Agregar Horarios
              </Button>
            )}
          </div>

          {/* Formulario para crear slots */}
          {showSlotForm && esOrganizador && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="bg-background rounded-lg p-4 mb-4 space-y-4"
            >
              <h4 className="font-bold text-textPrimary">Crear Horarios</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-textSecondary mb-1">Fecha</label>
                  <input
                    type="date"
                    value={slotForm.fecha}
                    onChange={(e) => setSlotForm({ ...slotForm, fecha: e.target.value })}
                    className="w-full px-4 py-2 bg-card border border-cardBorder rounded-lg text-textPrimary"
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-textSecondary mb-1">Duración (min)</label>
                  <select
                    value={slotForm.duracion}
                    onChange={(e) => setSlotForm({ ...slotForm, duracion: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 bg-card border border-cardBorder rounded-lg text-textPrimary"
                  >
                    <option value={60}>60 minutos</option>
                    <option value={75}>75 minutos</option>
                    <option value={90}>90 minutos</option>
                    <option value={120}>120 minutos</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm text-textSecondary mb-1">Hora Inicio</label>
                  <input
                    type="time"
                    value={slotForm.horaInicio}
                    onChange={(e) => setSlotForm({ ...slotForm, horaInicio: e.target.value })}
                    className="w-full px-4 py-2 bg-card border border-cardBorder rounded-lg text-textPrimary"
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-textSecondary mb-1">Hora Fin</label>
                  <input
                    type="time"
                    value={slotForm.horaFin}
                    onChange={(e) => setSlotForm({ ...slotForm, horaFin: e.target.value })}
                    className="w-full px-4 py-2 bg-card border border-cardBorder rounded-lg text-textPrimary"
                  />
                </div>
              </div>

              <p className="text-xs text-textSecondary">
                Se crearán slots de {slotForm.duracion} minutos para todas las canchas activas
              </p>

              <div className="flex gap-2">
                <Button onClick={crearSlots} disabled={!slotForm.fecha}>
                  Crear Horarios
                </Button>
                <Button variant="ghost" onClick={() => setShowSlotForm(false)}>
                  Cancelar
                </Button>
              </div>
            </motion.div>
          )}

          {/* Filtro por fecha */}
          <div className="flex items-center gap-4 mb-4">
            <div className="flex items-center gap-2">
              <Calendar size={18} className="text-textSecondary" />
              <input
                type="date"
                value={fechaFiltro}
                onChange={(e) => setFechaFiltro(e.target.value)}
                className="px-3 py-1 bg-background border border-cardBorder rounded-lg text-textPrimary text-sm"
              />
              {fechaFiltro && (
                <button
                  onClick={() => setFechaFiltro('')}
                  className="text-textSecondary hover:text-textPrimary"
                >
                  <X size={16} />
                </button>
              )}
            </div>
            <span className="text-sm text-textSecondary">
              {slotsFiltrados.length} slots
            </span>
          </div>

          {/* Lista de slots agrupados por fecha */}
          {Object.keys(slotsPorFecha).length === 0 ? (
            <p className="text-textSecondary text-center py-4">
              No hay horarios configurados
            </p>
          ) : (
            <div className="space-y-4">
              {Object.entries(slotsPorFecha).map(([fecha, slotsDelDia]) => (
                <div key={fecha} className="border border-cardBorder rounded-lg overflow-hidden">
                  <div className="bg-background px-4 py-2 font-bold text-textPrimary">
                    {new Date(fecha + 'T12:00:00').toLocaleDateString('es-ES', {
                      weekday: 'long',
                      day: 'numeric',
                      month: 'long'
                    })}
                  </div>
                  <div className="p-4 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
                    {slotsDelDia.map((slot) => (
                      <div
                        key={slot.id}
                        className={`p-2 rounded-lg text-center text-sm ${
                          slot.ocupado
                            ? 'bg-red-500/10 border border-red-500/30'
                            : 'bg-green-500/10 border border-green-500/30'
                        }`}
                      >
                        <div className="font-bold text-textPrimary">
                          {new Date(slot.fecha_hora_inicio).toLocaleTimeString('es-ES', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </div>
                        <div className="text-xs text-textSecondary">
                          {slot.cancha_nombre}
                        </div>
                        <div className={`text-xs mt-1 ${slot.ocupado ? 'text-red-500' : 'text-green-500'}`}>
                          {slot.ocupado ? 'Ocupado' : 'Libre'}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>


      {/* Programación Automática */}
      {esOrganizador && (
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-textPrimary flex items-center gap-2">
                <Play size={20} className="text-accent" />
                Programación Automática
              </h3>
            </div>

            <p className="text-textSecondary mb-4">
              Asigna automáticamente los partidos pendientes a los horarios disponibles.
              El sistema considera:
            </p>

            <ul className="text-sm text-textSecondary mb-6 space-y-1">
              <li>• Disponibilidad de canchas y horarios</li>
              <li>• Bloqueos horarios de los jugadores</li>
              <li>• Descanso mínimo de 30 minutos entre partidos de una pareja</li>
            </ul>

            <div className="flex items-center gap-4">
              <Button
                variant="accent"
                onClick={programarPartidos}
                disabled={programando || canchas.length === 0 || slots.length === 0}
                className="flex items-center gap-2"
              >
                {programando ? (
                  <>
                    <RefreshCw className="animate-spin" size={18} />
                    Programando...
                  </>
                ) : (
                  <>
                    <Play size={18} />
                    Programar Partidos
                  </>
                )}
              </Button>

              {(canchas.length === 0 || slots.length === 0) && (
                <span className="text-sm text-yellow-500">
                  {canchas.length === 0 && 'Primero crea canchas. '}
                  {slots.length === 0 && 'Primero crea horarios.'}
                </span>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Resumen */}
      <Card>
        <div className="p-6">
          <h3 className="font-bold text-textPrimary mb-4">Resumen</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-background rounded-lg">
              <div className="text-2xl font-bold text-primary">{canchas.length}</div>
              <div className="text-sm text-textSecondary">Canchas</div>
            </div>
            <div className="text-center p-4 bg-background rounded-lg">
              <div className="text-2xl font-bold text-primary">{slots.length}</div>
              <div className="text-sm text-textSecondary">Slots Totales</div>
            </div>
            <div className="text-center p-4 bg-background rounded-lg">
              <div className="text-2xl font-bold text-green-500">
                {slots.filter(s => !s.ocupado).length}
              </div>
              <div className="text-sm text-textSecondary">Disponibles</div>
            </div>
            <div className="text-center p-4 bg-background rounded-lg">
              <div className="text-2xl font-bold text-red-500">
                {slots.filter(s => s.ocupado).length}
              </div>
              <div className="text-sm text-textSecondary">Ocupados</div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
