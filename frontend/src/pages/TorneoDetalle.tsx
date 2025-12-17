import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Calendar, MapPin, Trophy, Users, Settings } from 'lucide-react';
import { useTorneos } from '../context/TorneosContext';
import { useAuth } from '../context/AuthContext';
import Card from '../components/Card';
import Button from '../components/Button';
import SkeletonLoader from '../components/SkeletonLoader';
import ModalInscribirTorneo from '../components/ModalInscribirTorneo';
import TorneoZonas from '../components/TorneoZonas';
import TorneoFixture from '../components/TorneoFixture';
import TorneoPlayoffs from '../components/TorneoPlayoffs';
import TorneoProgramacion from '../components/TorneoProgramacion';
import TorneoParejas from '../components/TorneoParejas';

export default function TorneoDetalle() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { torneoActual, cargarTorneo, cargarParejas, parejas, loading } = useTorneos();
  const { usuario } = useAuth();
  const [tab, setTab] = useState<'info' | 'parejas' | 'zonas' | 'partidos' | 'playoffs' | 'programacion'>('info');
  const [modalInscripcionOpen, setModalInscripcionOpen] = useState(false);

  useEffect(() => {
    if (id) {
      cargarTorneo(parseInt(id));
      cargarParejas(parseInt(id));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  // Escuchar evento para cambiar tab
  useEffect(() => {
    const handleCambiarTab = (event: any) => {
      setTab(event.detail);
    };
    window.addEventListener('cambiarTab', handleCambiarTab);
    return () => window.removeEventListener('cambiarTab', handleCambiarTab);
  }, []);

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

  // Verificar si el usuario es el creador del torneo
  const esCreadorTorneo = usuario?.id_usuario === (torneoActual as any).creado_por;
  // El organizador es quien creó el torneo
  const esOrganizador = esCreadorTorneo;
  
  // Permitir inscripción:
  // - Usuarios normales: solo cuando está en inscripción
  // - Creador del torneo: siempre (puede agregar parejas en cualquier momento)
  const torneoEnInscripcion = torneoActual.estado === 'programado' || 
                              (torneoActual as any).estado_original === 'inscripcion';
  const puedeInscribirse = torneoEnInscripcion || esCreadorTorneo;

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

          {/* Botón de inscripción - visible para todos cuando está en inscripción */}
          {puedeInscribirse && (
            <div className="border-t border-cardBorder pt-6">
              <Button
                variant="accent"
                onClick={() => setModalInscripcionOpen(true)}
                className="w-full md:w-auto"
              >
                Inscribir Pareja
              </Button>
            </div>
          )}
        </div>
      </Card>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-cardBorder overflow-x-auto">
        <button
          onClick={() => setTab('info')}
          className={`px-4 py-2 font-bold transition-colors whitespace-nowrap ${
            tab === 'info'
              ? 'text-primary border-b-2 border-primary'
              : 'text-textSecondary hover:text-textPrimary'
          }`}
        >
          Información
        </button>
        <button
          onClick={() => setTab('parejas')}
          className={`px-4 py-2 font-bold transition-colors whitespace-nowrap ${
            tab === 'parejas'
              ? 'text-primary border-b-2 border-primary'
              : 'text-textSecondary hover:text-textPrimary'
          }`}
        >
          Parejas ({parejas.length})
        </button>
        <button
          onClick={() => setTab('zonas')}
          className={`px-4 py-2 font-bold transition-colors whitespace-nowrap ${
            tab === 'zonas'
              ? 'text-primary border-b-2 border-primary'
              : 'text-textSecondary hover:text-textPrimary'
          }`}
        >
          Zonas
        </button>
        <button
          onClick={() => setTab('partidos')}
          className={`px-4 py-2 font-bold transition-colors whitespace-nowrap ${
            tab === 'partidos'
              ? 'text-primary border-b-2 border-primary'
              : 'text-textSecondary hover:text-textPrimary'
          }`}
        >
          Fixture
        </button>
        <button
          onClick={() => setTab('programacion')}
          className={`px-4 py-2 font-bold transition-colors whitespace-nowrap flex items-center gap-2 ${
            tab === 'programacion'
              ? 'text-primary border-b-2 border-primary'
              : 'text-textSecondary hover:text-textPrimary'
          }`}
        >
          <Calendar size={16} />
          Programación
        </button>
        <button
          onClick={() => setTab('playoffs')}
          className={`px-4 py-2 font-bold transition-colors whitespace-nowrap flex items-center gap-2 ${
            tab === 'playoffs'
              ? 'text-accent border-b-2 border-accent'
              : 'text-textSecondary hover:text-textPrimary'
          }`}
        >
          <Trophy size={16} />
          Playoffs
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
        <TorneoParejas 
          torneoId={parseInt(id!)} 
          parejas={parejas} 
          esOrganizador={esOrganizador}
          onUpdate={() => cargarParejas(parseInt(id!))}
        />
      )}

      {tab === 'zonas' && (
        <TorneoZonas torneoId={parseInt(id!)} esOrganizador={esOrganizador} />
      )}

      {tab === 'partidos' && (
        <TorneoFixture torneoId={parseInt(id!)} esOrganizador={esOrganizador} />
      )}

      {tab === 'programacion' && (
        <TorneoProgramacion torneoId={parseInt(id!)} esOrganizador={esOrganizador} />
      )}

      {tab === 'playoffs' && (
        <TorneoPlayoffs torneoId={parseInt(id!)} esOrganizador={esOrganizador} />
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
