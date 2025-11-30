import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, MapPin, Trophy, Clock } from 'lucide-react';
import { torneoService } from '../services/torneo.service';
import Card from './Card';
import Button from './Button';
import SkeletonLoader from './SkeletonLoader';
import ModalCargarResultado from './ModalCargarResultado';

interface TorneoFixtureProps {
  torneoId: number;
  esOrganizador: boolean;
}

export default function TorneoFixture({ torneoId, esOrganizador }: TorneoFixtureProps) {
  const [partidos, setPartidos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generando, setGenerando] = useState(false);
  const [partidoSeleccionado, setPartidoSeleccionado] = useState<any>(null);
  const [modalResultadoOpen, setModalResultadoOpen] = useState(false);
  const [filtroZona, setFiltroZona] = useState<string>('todas');
  const [zonas, setZonas] = useState<any[]>([]);

  useEffect(() => {
    cargarDatos();
  }, [torneoId]);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const [partidosResponse, zonasData] = await Promise.all([
        torneoService.listarPartidos(torneoId),
        torneoService.listarZonas(torneoId)
      ]);
      // El endpoint retorna { total, partidos }, necesitamos solo el array
      const partidosArray = Array.isArray(partidosResponse) ? partidosResponse : partidosResponse.partidos || [];
      setPartidos(partidosArray);
      setZonas(zonasData);
    } catch (error) {
      console.error('Error al cargar datos:', error);
    } finally {
      setLoading(false);
    }
  };

  const generarFixture = async () => {
    try {
      setGenerando(true);
      await torneoService.generarFixture(torneoId);
      await cargarDatos();
    } catch (error: any) {
      console.error('Error al generar fixture:', error);
      alert(error.response?.data?.detail || 'Error al generar fixture');
    } finally {
      setGenerando(false);
    }
  };

  const abrirModalResultado = (partido: any) => {
    setPartidoSeleccionado(partido);
    setModalResultadoOpen(true);
  };

  const handleResultadoCargado = () => {
    setModalResultadoOpen(false);
    setPartidoSeleccionado(null);
    cargarDatos();
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <SkeletonLoader height="60px" />
        <SkeletonLoader height="300px" />
        <SkeletonLoader height="300px" />
      </div>
    );
  }

  if (partidos.length === 0) {
    return (
      <Card>
        <div className="p-6 text-center">
          <Calendar size={48} className="mx-auto text-textSecondary mb-4" />
          <h3 className="text-xl font-bold text-textPrimary mb-2">
            Aún no se generó el fixture
          </h3>
          <p className="text-textSecondary mb-6">
            El fixture se genera después de crear las zonas
          </p>
          {esOrganizador && (
            <Button
              onClick={generarFixture}
              disabled={generando}
              variant="accent"
            >
              {generando ? 'Generando...' : 'Generar Fixture'}
            </Button>
          )}
        </div>
      </Card>
    );
  }

  // Agrupar partidos por zona
  const partidosPorZona = partidos.reduce((acc: any, partido: any) => {
    const zonaId = partido.zona_id || 'sin_zona';
    if (!acc[zonaId]) {
      acc[zonaId] = [];
    }
    acc[zonaId].push(partido);
    return acc;
  }, {});

  const zonasConPartidos = Object.keys(partidosPorZona).map(zonaId => {
    const zona = zonas.find(z => z.id === parseInt(zonaId));
    return {
      id: zonaId,
      nombre: zona?.nombre || 'Sin zona',
      partidos: partidosPorZona[zonaId]
    };
  });

  return (
    <div className="space-y-6">
      {/* Filtros */}
      {zonas.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-2">
          <Button
            variant={filtroZona === 'todas' ? 'primary' : 'ghost'}
            onClick={() => setFiltroZona('todas')}
            size="sm"
          >
            Todas las zonas
          </Button>
          {zonas.map(zona => (
            <Button
              key={zona.id}
              variant={filtroZona === zona.id.toString() ? 'primary' : 'ghost'}
              onClick={() => setFiltroZona(zona.id.toString())}
              size="sm"
            >
              {zona.nombre}
            </Button>
          ))}
        </div>
      )}

      {/* Partidos por zona */}
      {zonasConPartidos
        .filter(zona => filtroZona === 'todas' || filtroZona === zona.id)
        .map((zona, index) => (
          <motion.div
            key={zona.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card>
              <div className="p-6">
                <h3 className="text-xl font-bold text-textPrimary mb-4 flex items-center gap-2">
                  <Trophy size={20} className="text-primary" />
                  {zona.nombre}
                </h3>

                <div className="space-y-3">
                  {zona.partidos.map((partido: any) => (
                    <div
                      key={partido.id_partido}
                      className="p-4 bg-background rounded-lg border border-cardBorder hover:border-primary/50 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2 text-sm text-textSecondary">
                          <Calendar size={14} />
                          <span>
                            {new Date(partido.fecha_hora).toLocaleDateString('es-ES', {
                              day: 'numeric',
                              month: 'short',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>
                        <div
                          className={`px-3 py-1 rounded-full text-xs font-bold ${
                            partido.estado === 'confirmado'
                              ? 'bg-green-500/10 text-green-500'
                              : partido.estado === 'reportado'
                              ? 'bg-yellow-500/10 text-yellow-500'
                              : 'bg-gray-500/10 text-gray-500'
                          }`}
                        >
                          {partido.estado === 'confirmado' && 'Finalizado'}
                          {partido.estado === 'reportado' && 'Reportado'}
                          {partido.estado === 'pendiente' && 'Pendiente'}
                        </div>
                      </div>

                      {/* Parejas */}
                      <div className="space-y-2 mb-3">
                        <div className="flex items-center justify-between">
                          <span className="text-textPrimary font-bold">
                            {partido.pareja1_nombre || `Pareja ${partido.pareja1_id}`}
                          </span>
                          {partido.resultado_padel && (
                            <span className="text-lg font-bold text-textPrimary">
                              {partido.resultado_padel.sets
                                .filter((s: any) => s.ganador === 'equipoA')
                                .length}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-textPrimary font-bold">
                            {partido.pareja2_nombre || `Pareja ${partido.pareja2_id}`}
                          </span>
                          {partido.resultado_padel && (
                            <span className="text-lg font-bold text-textPrimary">
                              {partido.resultado_padel.sets
                                .filter((s: any) => s.ganador === 'equipoB')
                                .length}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Detalle de sets */}
                      {partido.resultado_padel && (
                        <div className="flex gap-2 mb-3">
                          {partido.resultado_padel.sets.map((set: any, idx: number) => (
                            <div
                              key={idx}
                              className="px-2 py-1 bg-card rounded text-xs text-textSecondary"
                            >
                              {set.gamesEquipoA}-{set.gamesEquipoB}
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Acciones */}
                      {esOrganizador && partido.estado === 'pendiente' && (
                        <Button
                          variant="accent"
                          size="sm"
                          onClick={() => abrirModalResultado(partido)}
                          className="w-full"
                        >
                          Cargar Resultado
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          </motion.div>
        ))}

      {/* Modal Cargar Resultado */}
      {partidoSeleccionado && (
        <ModalCargarResultado
          isOpen={modalResultadoOpen}
          onClose={() => {
            setModalResultadoOpen(false);
            setPartidoSeleccionado(null);
          }}
          partido={partidoSeleccionado}
          torneoId={torneoId}
          onResultadoCargado={handleResultadoCargado}
        />
      )}
    </div>
  );
}
