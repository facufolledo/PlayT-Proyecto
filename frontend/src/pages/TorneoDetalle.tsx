import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Calendar, MapPin, Trophy, Users, Settings } from 'lucide-react';
import { useTorneos } from '../context/TorneosContext';
import Card from '../components/Card';
import Button from '../components/Button';
import SkeletonLoader from '../components/SkeletonLoader';
import ModalInscribirTorneo from '../components/ModalInscribirTorneo';

export default function TorneoDetalle() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { torneoActual, cargarTorneo, cargarParejas, parejas, loading, esAdministrador } = useTorneos();
  const [tab, setTab] = useState<'info' | 'parejas' | 'partidos'>('info');
  const [modalInscripcionOpen, setModalInscripcionOpen] = useState(false);

  useEffect(() => {
    if (id) {
      cargarTorneo(parseInt(id));
      cargarParejas(parseInt(id));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (loading && !torneoActual) {
    return (
      <div className="space-y-4">
        <SkeletonLoader height="200px" />
        <SkeletonLoader height="400px" />
      </div>
    );
  }

  if (!torneoActual) {
    return (
      <Card>
        <div className="text-center py-12">
          <Trophy size={48} className="mx-auto text-textSecondary mb-4" />
          <h2 className="text-xl font-bold text-textPrimary mb-2">Torneo no encontrado</h2>
          <p className="text-textSecondary mb-4">El torneo que buscas no existe o fue eliminado</p>
          <Button onClick={() => navigate('/torneos')}>
            Volver a Torneos
          </Button>
        </div>
      </Card>
    );
  }

  const esOrganizador = esAdministrador;
  const puedeInscribirse = torneoActual.estado === 'programado';

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-4"
      >
        <Button
          variant="ghost"
          onClick={() => navigate('/torneos')}
          className="flex items-center gap-2"
        >
          <ArrowLeft size={20} />
          Volver
        </Button>
      </motion.div>

      {/* Información del Torneo */}
      <Card>
        <div className="p-6">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-accent/10 p-3 rounded-lg">
                  <Trophy className="text-accent" size={32} />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-textPrimary">{torneoActual.nombre}</h1>
                  <p className="text-textSecondary">Categoría {torneoActual.categoria}</p>
                </div>
              </div>
            </div>
            
            {esOrganizador && (
              <Button variant="ghost" className="flex items-center gap-2">
                <Settings size={18} />
                Gestionar
              </Button>
            )}
          </div>

          {/* Estado */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary mb-6">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span className="font-bold text-sm">
              {torneoActual.estado === 'programado' && 'Inscripciones Abiertas'}
              {torneoActual.estado === 'activo' && 'En Curso'}
              {torneoActual.estado === 'finalizado' && 'Finalizado'}
            </span>
          </div>

          {/* Información básica */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="flex items-center gap-3 p-4 bg-background rounded-lg">
              <Calendar className="text-primary" size={24} />
              <div>
                <p className="text-xs text-textSecondary">Fechas</p>
                <p className="font-bold text-textPrimary">
                  {new Date(torneoActual.fechaInicio).toLocaleDateString('es-ES', { 
                    day: 'numeric', 
                    month: 'short' 
                  })} - {new Date(torneoActual.fechaFin).toLocaleDateString('es-ES', { 
                    day: 'numeric', 
                    month: 'short',
                    year: 'numeric'
                  })}
                </p>
              </div>
            </div>

            {torneoActual.lugar && (
              <div className="flex items-center gap-3 p-4 bg-background rounded-lg">
                <MapPin className="text-primary" size={24} />
                <div>
                  <p className="text-xs text-textSecondary">Lugar</p>
                  <p className="font-bold text-textPrimary">{torneoActual.lugar}</p>
                </div>
              </div>
            )}

            <div className="flex items-center gap-3 p-4 bg-background rounded-lg">
              <Users className="text-primary" size={24} />
              <div>
                <p className="text-xs text-textSecondary">Parejas Inscritas</p>
                <p className="font-bold text-textPrimary">{parejas.length}</p>
              </div>
            </div>
          </div>

          {/* Descripción */}
          <div className="mb-6">
            <h3 className="font-bold text-textPrimary mb-2">Descripción</h3>
            <p className="text-textSecondary">{torneoActual.descripcion || 'Sin descripción'}</p>
          </div>

          {/* Botón de inscripción */}
          {puedeInscribirse && !esOrganizador && (
            <div className="border-t border-cardBorder pt-6">
              <Button
                variant="accent"
                onClick={() => setModalInscripcionOpen(true)}
                className="w-full md:w-auto"
              >
                Inscribirse al Torneo
              </Button>
            </div>
          )}
        </div>
      </Card>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-cardBorder">
        <button
          onClick={() => setTab('info')}
          className={`px-4 py-2 font-bold transition-colors ${
            tab === 'info'
              ? 'text-primary border-b-2 border-primary'
              : 'text-textSecondary hover:text-textPrimary'
          }`}
        >
          Información
        </button>
        <button
          onClick={() => setTab('parejas')}
          className={`px-4 py-2 font-bold transition-colors ${
            tab === 'parejas'
              ? 'text-primary border-b-2 border-primary'
              : 'text-textSecondary hover:text-textPrimary'
          }`}
        >
          Parejas ({parejas.length})
        </button>
        <button
          onClick={() => setTab('partidos')}
          className={`px-4 py-2 font-bold transition-colors ${
            tab === 'partidos'
              ? 'text-primary border-b-2 border-primary'
              : 'text-textSecondary hover:text-textPrimary'
          }`}
        >
          Partidos
        </button>
      </div>

      {/* Contenido de tabs */}
      {tab === 'info' && (
        <Card>
          <div className="p-6">
            <h3 className="font-bold text-textPrimary mb-4">Información del Torneo</h3>
            <div className="space-y-2 text-textSecondary">
              <p>• Formato: {torneoActual.formato || 'Eliminación simple'}</p>
              <p>• Género: {torneoActual.genero || 'Mixto'}</p>
              <p>• Categoría: {torneoActual.categoria}</p>
            </div>
          </div>
        </Card>
      )}

      {tab === 'parejas' && (
        <Card>
          <div className="p-6">
            {parejas.length === 0 ? (
              <div className="text-center py-12">
                <Users size={48} className="mx-auto text-textSecondary mb-4" />
                <p className="text-textSecondary">Aún no hay parejas inscritas</p>
              </div>
            ) : (
              <div className="space-y-3">
                {parejas.map((pareja) => (
                  <div
                    key={pareja.id}
                    className="flex items-center justify-between p-4 bg-background rounded-lg"
                  >
                    <div>
                      <p className="font-bold text-textPrimary">
                        {pareja.nombre_pareja}
                      </p>
                      <p className="text-xs text-textSecondary">
                        Jugadores: {pareja.jugador1_id} / {pareja.jugador2_id}
                      </p>
                    </div>
                    <div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-bold ${
                          pareja.estado === 'confirmada'
                            ? 'bg-green-500/10 text-green-500'
                            : pareja.estado === 'inscripta'
                            ? 'bg-yellow-500/10 text-yellow-500'
                            : 'bg-red-500/10 text-red-500'
                        }`}
                      >
                        {pareja.estado === 'confirmada' && 'Confirmada'}
                        {pareja.estado === 'inscripta' && 'Pendiente'}
                        {pareja.estado === 'baja' && 'Baja'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      )}

      {tab === 'partidos' && (
        <Card>
          <div className="p-6">
            <div className="text-center py-12">
              <Trophy size={48} className="mx-auto text-textSecondary mb-4" />
              <p className="text-textSecondary">Los partidos se generarán cuando comience el torneo</p>
            </div>
          </div>
        </Card>
      )}

      {/* Modal de Inscripción */}
      <ModalInscribirTorneo
        isOpen={modalInscripcionOpen}
        onClose={() => setModalInscripcionOpen(false)}
        torneoId={parseInt(id!)}
        torneoNombre={torneoActual?.nombre || ''}
      />
    </div>
  );
}
