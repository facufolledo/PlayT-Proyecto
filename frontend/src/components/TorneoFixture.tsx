import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Trophy, AlertCircle, X, MapPin, Clock, Camera, Filter } from 'lucide-react';
import { torneoService, Categoria } from '../services/torneo.service';
import Card from './Card';
import Button from './Button';
import SkeletonLoader from './SkeletonLoader';
import ModalCargarResultado from './ModalCargarResultado';
import html2canvas from 'html2canvas';

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
  const [canchas, setCanchas] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [capturando, setCapturando] = useState(false);
  const fixtureRef = useRef<HTMLDivElement>(null);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [categoriaFiltro, setCategoriaFiltro] = useState<number | null>(null);

  useEffect(() => {
    cargarDatos();
  }, [torneoId]);

  // Escuchar evento de cambio de tab con filtros
  useEffect(() => {
    const handleCambiarTabConFiltros = (event: any) => {
      if (event.detail.zonaId) {
        setFiltroZona(event.detail.zonaId.toString());
      }
      if (event.detail.categoriaId) {
        setCategoriaFiltro(event.detail.categoriaId);
      }
    };
    window.addEventListener('cambiarTab', handleCambiarTabConFiltros);
    return () => window.removeEventListener('cambiarTab', handleCambiarTabConFiltros);
  }, []);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const [partidosResponse, zonasData, canchasData, categoriasData] = await Promise.all([
        torneoService.listarPartidos(torneoId),
        torneoService.listarZonas(torneoId),
        torneoService.listarCanchas(torneoId).catch(() => []),
        torneoService.listarCategorias(torneoId).catch(() => [])
      ]);
      // El endpoint retorna { total, partidos }, necesitamos solo el array
      const partidosArray = Array.isArray(partidosResponse) 
        ? partidosResponse 
        : (partidosResponse as any).partidos || [];
      setPartidos(partidosArray);
      setZonas(zonasData);
      setCanchas(canchasData);
      setCategorias(categoriasData);
    } catch (error) {
      console.error('Error al cargar datos:', error);
    } finally {
      setLoading(false);
    }
  };

  // Función para capturar el fixture como imagen
  const capturarFixture = async () => {
    if (!fixtureRef.current) return;
    
    try {
      setCapturando(true);
      const canvas = await html2canvas(fixtureRef.current, {
        backgroundColor: '#1a1a2e',
        scale: 2,
        useCORS: true,
      });
      
      // Crear link de descarga
      const link = document.createElement('a');
      link.download = `fixture-torneo-${torneoId}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    } catch (error) {
      console.error('Error al capturar fixture:', error);
    } finally {
      setCapturando(false);
    }
  };

  // Obtener nombre de cancha por ID
  const getNombreCancha = (canchaId: number | null) => {
    if (!canchaId) return null;
    const cancha = canchas.find(c => c.id === canchaId);
    return cancha?.nombre || `Cancha ${canchaId}`;
  };

  const generarFixture = async () => {
    try {
      setGenerando(true);
      setError(null);
      await torneoService.generarFixture(torneoId);
      await cargarDatos();
    } catch (error: any) {
      console.error('Error al generar fixture:', error);
      setError(error.response?.data?.detail || 'Error al generar fixture');
    } finally {
      setGenerando(false);
    }
  };

  const eliminarFixture = async () => {
    if (!confirm('⚠️ ¿Estás seguro de eliminar el fixture?\n\nSe eliminarán todos los partidos de fase de grupos.\n\nEsta acción NO se puede deshacer.')) {
      return;
    }
    
    try {
      setGenerando(true);
      setError(null);
      await torneoService.eliminarFixture(torneoId);
      await cargarDatos();
    } catch (error: any) {
      console.error('Error al eliminar fixture:', error);
      setError(error.response?.data?.detail || 'Error al eliminar fixture');
    } finally {
      setGenerando(false);
    }
  };

  const abrirModalResultado = (partido: any) => {
    setPartidoSeleccionado(partido);
    setModalResultadoOpen(true);
  };

  const handleResultadoCargado = (partidoActualizado?: any) => {
    setModalResultadoOpen(false);
    
    // Actualizar solo el partido modificado en lugar de recargar todo
    if (partidoActualizado) {
      setPartidos(prev => prev.map(p => 
        p.id_partido === partidoActualizado.id_partido ? partidoActualizado : p
      ));
    } else {
      // Si no tenemos el partido actualizado, recargar todo
      cargarDatos();
    }
    
    setPartidoSeleccionado(null);
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
          
          {/* Mensaje de error */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-3"
            >
              <AlertCircle size={20} className="text-red-500 flex-shrink-0 mt-0.5" />
              <div className="flex-1 text-left">
                <p className="text-red-500 font-medium text-sm">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-500/70 hover:text-red-500 transition-colors"
              >
                <X size={18} />
              </button>
            </motion.div>
          )}
          
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

  // Filtrar partidos por categoría
  const partidosFiltrados = categoriaFiltro
    ? partidos.filter((p: any) => p.categoria_id === categoriaFiltro)
    : partidos;

  // Agrupar partidos por zona
  const partidosPorZona = partidosFiltrados.reduce((acc: any, partido: any) => {
    const zonaId = partido.zona_id || 'sin_zona';
    if (!acc[zonaId]) {
      acc[zonaId] = [];
    }
    acc[zonaId].push(partido);
    return acc;
  }, {});

  const zonasConPartidos = Object.keys(partidosPorZona).map(zonaId => {
    const zona = zonas.find(z => z.id === parseInt(zonaId));
    // Si no hay zona, mostrar la fase del partido (playoffs)
    let nombre = zona?.nombre || 'Sin zona';
    if (!zona && partidosPorZona[zonaId]?.length > 0) {
      const fase = partidosPorZona[zonaId][0]?.fase;
      if (fase) {
        const fasesNombres: Record<string, string> = {
          'semifinal': 'Semifinales',
          'semis': 'Semifinales',
          'final': 'Final',
          'cuartos': 'Cuartos de Final',
          '4tos': 'Cuartos de Final',
          '8vos': 'Octavos de Final',
          '16avos': 'Dieciseisavos de Final'
        };
        nombre = fasesNombres[fase] || fase.charAt(0).toUpperCase() + fase.slice(1);
      }
    }
    return {
      id: zonaId,
      nombre,
      partidos: partidosPorZona[zonaId]
    };
  });

  return (
    <div className="space-y-6">
      {/* Filtro por categoría */}
      {categorias.length > 0 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          <Filter size={14} className="text-textSecondary flex-shrink-0" />
          <button
            onClick={() => setCategoriaFiltro(null)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition-all ${
              categoriaFiltro === null
                ? 'bg-accent text-white'
                : 'bg-cardBorder text-textSecondary hover:bg-accent/20'
            }`}
          >
            Todas
          </button>
          {categorias.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setCategoriaFiltro(cat.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition-all ${
                categoriaFiltro === cat.id
                  ? 'bg-accent text-white'
                  : 'bg-cardBorder text-textSecondary hover:bg-accent/20'
              }`}
            >
              {cat.nombre}
            </button>
          ))}
        </div>
      )}

      {/* Header con filtros de zona y botón de captura */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2 overflow-x-auto">
          {/* Filtros por zona */}
          {zonas.length > 1 && (
            <div className="flex gap-2 pb-2 sm:pb-0">
              <Button
                variant={filtroZona === 'todas' ? 'primary' : 'ghost'}
                onClick={() => setFiltroZona('todas')}
                size="sm"
                className="whitespace-nowrap text-xs"
              >
                Todas
              </Button>
              {zonas.map(zona => (
                <Button
                  key={zona.id}
                  variant={filtroZona === zona.id.toString() ? 'primary' : 'ghost'}
                  onClick={() => setFiltroZona(zona.id.toString())}
                  size="sm"
                  className="whitespace-nowrap text-xs"
                >
                  {zona.nombre}
                </Button>
              ))}
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-2 self-end sm:self-auto">
          {/* Botón eliminar fixture (solo organizador) */}
          {esOrganizador && (
            <Button
              onClick={eliminarFixture}
              disabled={generando}
              variant="ghost"
              size="sm"
              className="flex items-center gap-1.5 text-xs text-red-500 hover:text-red-600 hover:bg-red-500/10 border border-red-500/30"
            >
              <X size={14} />
              Eliminar Fixture
            </Button>
          )}
          
          {/* Botón capturar para Instagram */}
          <Button
            variant="ghost"
            size="sm"
            onClick={capturarFixture}
            disabled={capturando}
            className="flex items-center gap-2 text-xs"
          >
            <Camera size={14} />
            {capturando ? 'Capturando...' : 'Capturar'}
          </Button>
        </div>
      </div>

      {/* Partidos por zona */}
      <div ref={fixtureRef} className="space-y-6">
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
              <div className="p-4 md:p-6">
                <h3 className="text-lg md:text-xl font-bold text-textPrimary mb-3 md:mb-4 flex items-center gap-2">
                  <Trophy size={18} className="text-primary md:w-5 md:h-5" />
                  {zona.nombre}
                </h3>

                <div className="space-y-2 md:space-y-3">
                  {zona.partidos.map((partido: any, idx: number) => {
                    const setsEquipoA = partido.resultado_padel?.sets.filter((s: any) => s.ganador === 'equipoA').length || 0;
                    const setsEquipoB = partido.resultado_padel?.sets.filter((s: any) => s.ganador === 'equipoB').length || 0;
                    const ganadorA = setsEquipoA > setsEquipoB;
                    const ganadorB = setsEquipoB > setsEquipoA;
                    
                    return (
                      <motion.div
                        key={partido.id_partido}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className="p-3 md:p-4 bg-background rounded-lg border border-cardBorder hover:border-primary/50 transition-all hover:shadow-md"
                      >
                        {/* Header del partido con fecha, hora y cancha */}
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-3 md:mb-4">
                          <div className="flex flex-wrap items-center gap-2 md:gap-3 text-xs md:text-sm text-textSecondary">
                            {/* Fecha y hora */}
                            <div className="flex items-center gap-1.5">
                              <div className="bg-primary/10 p-1 md:p-1.5 rounded">
                                <Calendar size={12} className="text-primary md:w-[14px] md:h-[14px]" />
                              </div>
                              <span className="font-medium">
                                {partido.fecha_hora ? new Date(partido.fecha_hora).toLocaleDateString('es-ES', {
                                  weekday: 'short',
                                  day: 'numeric',
                                  month: 'short'
                                }).toUpperCase() : 'Sin fecha'}
                              </span>
                            </div>
                            {/* Hora */}
                            {partido.fecha_hora && (
                              <div className="flex items-center gap-1">
                                <Clock size={12} className="text-accent md:w-[14px] md:h-[14px]" />
                                <span className="font-bold text-accent">
                                  {new Date(partido.fecha_hora).toLocaleTimeString('es-ES', {
                                    hour: '2-digit',
                                    minute: '2-digit'
                                  })}
                                </span>
                              </div>
                            )}
                            {/* Cancha */}
                            {partido.cancha_id && (
                              <div className="flex items-center gap-1 bg-accent/10 px-2 py-0.5 rounded">
                                <MapPin size={12} className="text-accent md:w-[14px] md:h-[14px]" />
                                <span className="font-bold text-accent text-[10px] md:text-xs">
                                  {getNombreCancha(partido.cancha_id)}
                                </span>
                              </div>
                            )}
                          </div>
                          <div
                            className={`px-2 md:px-3 py-0.5 md:py-1 rounded-full text-[10px] md:text-xs font-bold flex items-center gap-1 md:gap-1.5 ${
                              partido.estado === 'confirmado'
                                ? 'bg-green-500/10 text-green-500'
                                : partido.estado === 'reportado'
                                ? 'bg-yellow-500/10 text-yellow-500'
                                : 'bg-gray-500/10 text-gray-500'
                            }`}
                          >
                            <span className={`w-1 h-1 md:w-1.5 md:h-1.5 rounded-full ${
                              partido.estado === 'confirmado' ? 'bg-green-500' :
                              partido.estado === 'reportado' ? 'bg-yellow-500' : 'bg-gray-500'
                            }`} />
                            {partido.estado === 'confirmado' && 'Finalizado'}
                            {partido.estado === 'reportado' && 'Reportado'}
                            {partido.estado === 'pendiente' && 'Pendiente'}
                          </div>
                        </div>

                        {/* Parejas con resultado */}
                        <div className="space-y-2 md:space-y-3 mb-2 md:mb-3">
                          {/* Pareja 1 */}
                          <div className={`flex items-center justify-between p-2 md:p-3 rounded-lg transition-colors ${
                            ganadorA ? 'bg-green-500/10 border border-green-500/20' : 'bg-card'
                          }`}>
                            <div className="flex items-center gap-1.5 md:gap-2 flex-1 min-w-0">
                              {ganadorA && <Trophy size={12} className="text-green-500 flex-shrink-0 md:w-4 md:h-4" />}
                              <span className={`font-bold text-xs md:text-base truncate ${ganadorA ? 'text-green-500' : 'text-textPrimary'}`}>
                                {partido.pareja1_nombre || `Pareja ${partido.pareja1_id}`}
                              </span>
                            </div>
                            {partido.resultado_padel && (
                              <span className={`text-xl md:text-2xl font-bold ml-2 ${ganadorA ? 'text-green-500' : 'text-textSecondary'}`}>
                                {setsEquipoA}
                              </span>
                            )}
                          </div>

                          {/* Pareja 2 */}
                          <div className={`flex items-center justify-between p-2 md:p-3 rounded-lg transition-colors ${
                            ganadorB ? 'bg-green-500/10 border border-green-500/20' : 'bg-card'
                          }`}>
                            <div className="flex items-center gap-1.5 md:gap-2 flex-1 min-w-0">
                              {ganadorB && <Trophy size={12} className="text-green-500 flex-shrink-0 md:w-4 md:h-4" />}
                              <span className={`font-bold text-xs md:text-base truncate ${ganadorB ? 'text-green-500' : 'text-textPrimary'}`}>
                                {partido.pareja2_nombre || `Pareja ${partido.pareja2_id}`}
                              </span>
                            </div>
                            {partido.resultado_padel && (
                              <span className={`text-xl md:text-2xl font-bold ml-2 ${ganadorB ? 'text-green-500' : 'text-textSecondary'}`}>
                                {setsEquipoB}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Detalle de sets */}
                        {partido.resultado_padel && (
                          <div className="flex gap-1.5 md:gap-2 mb-2 md:mb-3 justify-center">
                            {partido.resultado_padel.sets.map((set: any, idx: number) => (
                              <div
                                key={idx}
                                className="px-2 md:px-3 py-1 md:py-2 bg-card rounded-lg border border-cardBorder"
                              >
                                <span className="text-xs md:text-sm font-bold text-textPrimary">
                                  {set.gamesEquipoA}
                                </span>
                                <span className="text-[10px] md:text-xs text-textSecondary mx-0.5 md:mx-1">-</span>
                                <span className="text-xs md:text-sm font-bold text-textPrimary">
                                  {set.gamesEquipoB}
                                </span>
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
                            className="w-full mt-2 text-xs md:text-sm py-2"
                          >
                            Cargar Resultado
                          </Button>
                        )}
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

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
