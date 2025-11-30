import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Plus, Filter, Calendar, MapPin, Users, Award } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import { torneoService, Torneo } from '../services/torneo.service';
import { useAuth } from '../context/AuthContext';

export default function TorneosNuevo() {
  const navigate = useNavigate();
  const { usuario } = useAuth();
  const [torneos, setTorneos] = useState<Torneo[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroEstado, setFiltroEstado] = useState<string>('todos');
  const [filtroCategoria, setFiltroCategoria] = useState<string>('todos');

  useEffect(() => {
    cargarTorneos();
  }, [filtroEstado, filtroCategoria]);

  const cargarTorneos = async () => {
    try {
      setLoading(true);
      const params: any = {};
      
      if (filtroEstado !== 'todos') {
        params.estado = filtroEstado;
      }
      
      if (filtroCategoria !== 'todos') {
        params.categoria = filtroCategoria;
      }

      const data = await torneoService.listarTorneos(params);
      setTorneos(data);
    } catch (error) {
      console.error('Error al cargar torneos:', error);
      setTorneos([]);
    } finally {
      setLoading(false);
    }
  };

  const getEstadoBadge = (estado: string) => {
    const badges = {
      inscripcion: { color: 'bg-green-500/20 text-green-500', text: 'Inscripción Abierta' },
      armando_zonas: { color: 'bg-blue-500/20 text-blue-500', text: 'Armando Zonas' },
      fase_grupos: { color: 'bg-yellow-500/20 text-yellow-500', text: 'Fase de Grupos' },
      fase_eliminacion: { color: 'bg-orange-500/20 text-orange-500', text: 'Eliminación' },
      finalizado: { color: 'bg-gray-500/20 text-gray-500', text: 'Finalizado' },
    };
    return badges[estado as keyof typeof badges] || badges.inscripcion;
  };

  const formatearFecha = (fecha: string) => {
    return new Date(fecha).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
      >
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="h-1 w-12 bg-gradient-to-r from-accent to-yellow-500 rounded-full" />
            <h1 className="text-4xl md:text-5xl font-black text-textPrimary">Torneos</h1>
          </div>
          <p className="text-textSecondary ml-15">Competiciones oficiales de pádel</p>
        </div>

        <Button
          variant="primary"
          onClick={() => navigate('/torneos/crear')}
          className="flex items-center gap-2"
        >
          <Plus size={20} />
          Crear Torneo
        </Button>
      </motion.div>

      {/* Filtros */}
      <Card>
        <div className="p-4 space-y-4">
          {/* Filtro por Estado */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Filter size={18} className="text-textSecondary" />
              <span className="text-sm font-bold text-textSecondary">Estado:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {['todos', 'inscripcion', 'fase_grupos', 'fase_eliminacion', 'finalizado'].map((estado) => (
                <Button
                  key={estado}
                  variant={filtroEstado === estado ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => setFiltroEstado(estado)}
                >
                  {estado === 'todos' ? 'Todos' : estado.replace('_', ' ')}
                </Button>
              ))}
            </div>
          </div>

          {/* Filtro por Categoría */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Award size={18} className="text-textSecondary" />
              <span className="text-sm font-bold text-textSecondary">Categoría:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {['todos', '8va', '7ma', '6ta', '5ta', '4ta', 'Libre'].map((cat) => (
                <Button
                  key={cat}
                  variant={filtroCategoria === cat ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => setFiltroCategoria(cat)}
                >
                  {cat === 'todos' ? 'Todas' : cat}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Lista de Torneos */}
      {loading ? (
        <div className="text-center py-12">
          <p className="text-textSecondary">Cargando torneos...</p>
        </div>
      ) : torneos.length === 0 ? (
        <Card>
          <div className="p-12 text-center">
            <Trophy size={64} className="mx-auto mb-4 text-textSecondary opacity-50" />
            <h3 className="text-xl font-bold text-textPrimary mb-2">No hay torneos disponibles</h3>
            <p className="text-textSecondary mb-6">
              {filtroEstado !== 'todos' || filtroCategoria !== 'todos'
                ? 'Intenta con otros filtros'
                : 'Sé el primero en crear un torneo'}
            </p>
            <Button variant="primary" onClick={() => navigate('/torneos/crear')}>
              <Plus size={20} className="mr-2" />
              Crear Torneo
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {torneos.map((torneo, index) => (
            <motion.div
              key={torneo.id_torneo}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card
                className="hover:border-primary/50 transition-all cursor-pointer h-full"
                onClick={() => navigate(`/torneos/${torneo.id_torneo}`)}
              >
                <div className="p-4 space-y-3">
                  {/* Header */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-bold text-textPrimary truncate">
                        {torneo.nombre}
                      </h3>
                      <p className="text-xs text-textSecondary line-clamp-2">
                        {torneo.descripcion}
                      </p>
                    </div>
                    <Trophy size={24} className="text-accent flex-shrink-0" />
                  </div>

                  {/* Estado */}
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-bold ${
                        getEstadoBadge(torneo.estado).color
                      }`}
                    >
                      {getEstadoBadge(torneo.estado).text}
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-primary/20 text-primary">
                      {torneo.categoria}
                    </span>
                  </div>

                  {/* Info */}
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-textSecondary">
                      <Calendar size={16} />
                      <span>
                        {formatearFecha(torneo.fecha_inicio)} - {formatearFecha(torneo.fecha_fin)}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-textSecondary">
                      <MapPin size={16} />
                      <span className="truncate">{torneo.ubicacion}</span>
                    </div>
                    <div className="flex items-center gap-2 text-textSecondary">
                      <Users size={16} />
                      <span>
                        {torneo.parejas_inscritas || 0} / {torneo.max_parejas} parejas
                      </span>
                    </div>
                  </div>

                  {/* Premio */}
                  {torneo.premio && (
                    <div className="pt-3 border-t border-cardBorder">
                      <p className="text-xs text-textSecondary">Premio</p>
                      <p className="text-lg font-black text-accent">${torneo.premio}</p>
                    </div>
                  )}

                  {/* Progreso */}
                  <div className="pt-2">
                    <div className="h-2 bg-background rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-primary to-accent transition-all"
                        style={{
                          width: `${
                            ((torneo.parejas_inscritas || 0) / torneo.max_parejas) * 100
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
