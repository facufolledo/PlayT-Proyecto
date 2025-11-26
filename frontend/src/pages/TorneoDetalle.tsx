import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Trophy, Calendar, Users, Edit, Trash2, Play, CheckCircle } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import BracketVisualization from '../components/BracketVisualization';
import ModalInscripcionTorneo from '../components/ModalInscripcionTorneo';
import { useTorneos } from '../context/TorneosContext';
import { useAuth } from '../context/AuthContext';
import { logger } from '../utils/logger';
import { Partido } from '../utils/bracketGenerator';

export default function TorneoDetalle() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { getTorneoById, getBracket, deleteTorneo, inscribirUsuario, iniciarTorneo } = useTorneos();
  const { usuario } = useAuth();
  const [modalInscripcionOpen, setModalInscripcionOpen] = useState(false);

  const torneo = id ? getTorneoById(id) : null;
  const bracket = id ? getBracket(id) : null;

  if (!torneo) {
    return (
      <div className="text-center py-12">
        <p className="text-textPrimary text-xl">Torneo no encontrado</p>
        <Button onClick={() => navigate('/torneos')} className="mt-4">
          Volver a Torneos
        </Button>
      </div>
    );
  }

  const handleEliminar = () => {
    if (window.confirm('¿Estás seguro de eliminar este torneo?')) {
      deleteTorneo(torneo.id);
      navigate('/torneos');
    }
  };

  const handleIniciar = () => {
    // Mock: Crear participantes de ejemplo
    const participantesMock = Array.from({ length: 8 }, (_, i) => ({
      id: `jugador-${i + 1}`,
      nombre: `Jugador ${i + 1}`,
      email: `jugador${i + 1}@email.com`,
      avatar: undefined,
      rol: 'jugador' as const,
      estadisticas: {
        partidosJugados: 0,
        partidosGanados: 0,
        torneosParticipados: 0,
        torneosGanados: 0,
      },
      createdAt: new Date().toISOString(),
    }));

    iniciarTorneo(torneo.id, participantesMock);
  };

  const handleInscribir = (torneoId: string) => {
    if (usuario) {
      inscribirUsuario(torneoId, usuario.id);
    }
  };

  const handlePartidoClick = (partido: Partido) => {
    logger.log('Partido seleccionado:', partido);
    // TODO: Abrir modal para registrar resultado
  };

  const getEstadoColor = () => {
    switch (torneo.estado) {
      case 'activo':
        return 'from-secondary to-pink-600';
      case 'finalizado':
        return 'from-accent to-yellow-500';
      case 'programado':
        return 'from-primary to-blue-600';
    }
  };

  const getEstadoLabel = () => {
    switch (torneo.estado) {
      case 'activo':
        return 'En Curso';
      case 'finalizado':
        return 'Finalizado';
      case 'programado':
        return 'Próximamente';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Button
          variant="ghost"
          onClick={() => navigate('/torneos')}
          className="mb-4"
        >
          <ArrowLeft size={20} className="mr-2" />
          Volver a Torneos
        </Button>

        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <div className={`bg-gradient-to-br ${getEstadoColor()} p-3 rounded-lg`}>
                <Trophy className="text-white" size={32} />
              </div>
              <div>
                <h1 className="text-5xl font-black text-textPrimary tracking-tight">
                  {torneo.nombre}
                </h1>
                <div className="flex items-center gap-3 mt-2">
                  <span className={`px-3 py-1 rounded-full bg-gradient-to-r ${getEstadoColor()} text-white text-sm font-bold`}>
                    {getEstadoLabel()}
                  </span>
                  <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-bold">
                    Categoría {torneo.categoria}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            {torneo.estado === 'programado' && (
              <>
                <Button
                  variant="primary"
                  onClick={handleIniciar}
                >
                  <Play size={20} className="mr-2" />
                  Iniciar Torneo
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => navigate(`/torneos/${torneo.id}/editar`)}
                >
                  <Edit size={20} />
                </Button>
                <Button
                  variant="ghost"
                  onClick={handleEliminar}
                  className="text-red-500 hover:text-red-400"
                >
                  <Trash2 size={20} />
                </Button>
              </>
            )}
            {torneo.estado === 'programado' && (
              <Button
                variant="accent"
                onClick={() => setModalInscripcionOpen(true)}
              >
                Inscribirse
              </Button>
            )}
          </div>
        </div>
      </motion.div>

      {/* Información del Torneo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <div className="flex items-center gap-3 mb-2">
            <Calendar className="text-primary" size={24} />
            <h3 className="text-lg font-bold text-textPrimary">Fechas</h3>
          </div>
          <p className="text-textSecondary text-sm">
            {new Date(torneo.fechaInicio).toLocaleDateString('es-ES', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
            })}
            {' - '}
            {new Date(torneo.fechaFin).toLocaleDateString('es-ES', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
            })}
          </p>
        </Card>

        <Card>
          <div className="flex items-center gap-3 mb-2">
            <Users className="text-secondary" size={24} />
            <h3 className="text-lg font-bold text-textPrimary">Participantes</h3>
          </div>
          <p className="text-textSecondary text-sm">
            {torneo.participantes} jugadores ({torneo.participantes / 2} parejas)
          </p>
        </Card>

        <Card>
          <div className="flex items-center gap-3 mb-2">
            <Trophy className="text-accent" size={24} />
            <h3 className="text-lg font-bold text-textPrimary">Formato</h3>
          </div>
          <p className="text-textSecondary text-sm">
            {torneo.formato === 'eliminacion-simple' && 'Eliminación Simple'}
            {torneo.formato === 'eliminacion-doble' && 'Eliminación Doble'}
            {torneo.formato === 'round-robin' && 'Round Robin'}
            {torneo.formato === 'grupos' && 'Por Grupos'}
          </p>
        </Card>
      </div>

      {/* Descripción */}
      {torneo.descripcion && (
        <Card>
          <h3 className="text-xl font-bold text-textPrimary mb-3">Descripción</h3>
          <p className="text-textSecondary">{torneo.descripcion}</p>
        </Card>
      )}

      {/* Bracket */}
      {bracket && torneo.estado === 'activo' ? (
        <Card>
          <BracketVisualization bracket={bracket} onPartidoClick={handlePartidoClick} />
        </Card>
      ) : torneo.estado === 'programado' ? (
        <Card>
          <div className="text-center py-12">
            <Trophy size={64} className="text-accent mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-textPrimary mb-2">
              Torneo Próximamente
            </h3>
            <p className="text-textSecondary mb-6">
              El bracket se generará cuando el torneo inicie
            </p>
            <Button variant="accent" onClick={() => setModalInscripcionOpen(true)}>
              Inscribirse Ahora
            </Button>
          </div>
        </Card>
      ) : (
        <Card>
          <div className="text-center py-12">
            <CheckCircle size={64} className="text-secondary mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-textPrimary mb-2">
              Torneo Finalizado
            </h3>
            <p className="text-textSecondary">
              Este torneo ha concluido
            </p>
          </div>
        </Card>
      )}

      {/* Modal */}
      <ModalInscripcionTorneo
        isOpen={modalInscripcionOpen}
        onClose={() => setModalInscripcionOpen(false)}
        torneo={torneo}
        onInscribir={handleInscribir}
      />
    </div>
  );
}
