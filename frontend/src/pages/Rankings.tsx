import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Trophy, TrendingUp, TrendingDown, Minus, Medal, Filter, Search, BarChart3 } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { apiService } from '../services/api';
import { logger } from '../utils/logger';

// Categorías según la documentación
const CATEGORIAS = [
  { id: 1, nombre: '8va', descripcion: 'Principiante / Princ. avanzado', ratingMin: 0, ratingMax: 899, color: 'from-gray-500 to-gray-600' },
  { id: 2, nombre: '7ma', descripcion: 'Golpes más sólidos', ratingMin: 900, ratingMax: 1049, color: 'from-blue-500 to-blue-600' },
  { id: 3, nombre: '6ta', descripcion: 'Mejor dominio y estrategia', ratingMin: 1050, ratingMax: 1199, color: 'from-green-500 to-green-600' },
  { id: 4, nombre: '5ta', descripcion: 'Buenos jugadores, constancia', ratingMin: 1200, ratingMax: 1349, color: 'from-yellow-500 to-yellow-600' },
  { id: 5, nombre: '4ta', descripcion: 'Muy buenos, técnica + estrategia', ratingMin: 1350, ratingMax: 1499, color: 'from-orange-500 to-orange-600' },
  { id: 6, nombre: 'Libre', descripcion: 'Élite local (top provincia)', ratingMin: 1500, ratingMax: 9999, color: 'from-purple-500 to-pink-500' },
];

function getCategoriaInfo(rating: number) {
  return CATEGORIAS.find(cat => rating >= cat.ratingMin && rating <= cat.ratingMax) || CATEGORIAS[0];
}

export default function Rankings() {
  const [filtroCategoria, setFiltroCategoria] = useState<string>('todas');
  const [filtroGenero, setFiltroGenero] = useState<string>('todos');
  const [busqueda, setBusqueda] = useState('');
  const [jugadorSeleccionado, setJugadorSeleccionado] = useState<any | null>(null);
  const [jugadores, setJugadores] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [categorias, setCategorias] = useState<any[]>([]);

  // Cargar categorías y jugadores al montar
  useEffect(() => {
    const cargarDatos = async () => {
      try {
        setIsLoading(true);
        
        // Cargar categorías
        const categoriasData = await apiService.getCategorias();
        setCategorias(categoriasData);
        
        // Cargar ranking general (100 jugadores)
        const rankingData = await apiService.getRankingGeneral(100, 0);
        setJugadores(rankingData);
      } catch (error) {
        logger.error('Error al cargar datos:', error);
        // Si falla, mostrar array vacío
        setJugadores([]);
      } finally {
        setIsLoading(false);
      }
    };

    cargarDatos();
  }, []);

  // Recargar cuando cambie el filtro de categoría
  useEffect(() => {
    const cargarRanking = async () => {
      if (filtroCategoria === 'todas') {
        try {
          setIsLoading(true);
          const rankingData = await apiService.getRankingGeneral(100, 0);
          setJugadores(rankingData);
        } catch (error) {
          logger.error('Error al cargar ranking:', error);
          setJugadores([]);
        } finally {
          setIsLoading(false);
        }
      } else {
        // Buscar la categoría por nombre
        const categoria = CATEGORIAS.find(c => c.nombre === filtroCategoria);
        if (categoria) {
          try {
            setIsLoading(true);
            const categoriaData = await apiService.getRankingPorCategoria(categoria.id || 1);
            setJugadores(categoriaData.jugadores || []);
          } catch (error) {
            logger.error('Error al cargar ranking por categoría:', error);
            setJugadores([]);
          } finally {
            setIsLoading(false);
          }
        }
      }
    };

    cargarRanking();
  }, [filtroCategoria]);

  // Datos de progresión de rating (mock)
  const progresionRating = [
    { mes: 'Ene', rating: 1200 },
    { mes: 'Feb', rating: 1250 },
    { mes: 'Mar', rating: 1280 },
    { mes: 'Abr', rating: 1320 },
    { mes: 'May', rating: 1380 },
    { mes: 'Jun', rating: 1450 },
  ];

  // Filtrar jugadores localmente por búsqueda y género
  const jugadoresFiltrados = jugadores.filter(jugador => {
    const nombreCompleto = `${jugador.nombre || ''} ${jugador.apellido || ''}`.toLowerCase();
    const cumpleBusqueda = nombreCompleto.includes(busqueda.toLowerCase()) || 
                          (jugador.nombre_usuario || '').toLowerCase().includes(busqueda.toLowerCase());
    
    // Filtro por género
    const cumpleGenero = filtroGenero === 'todos' || 
                        (filtroGenero === 'masculino' && jugador.sexo === 'M') ||
                        (filtroGenero === 'femenino' && jugador.sexo === 'F');
    
    return cumpleBusqueda && cumpleGenero;
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="h-1 w-12 bg-gradient-to-r from-primary to-secondary rounded-full" />
          <h1 className="text-5xl font-black text-textPrimary tracking-tight">
            Rankings
          </h1>
        </div>
        <p className="text-textSecondary text-base ml-15">Tabla general de jugadores</p>
      </motion.div>

      {/* Información del sistema de categorías */}
      <Card gradient>
        <div className="mb-4">
          <h2 className="text-xl font-bold text-textPrimary mb-2">Sistema de Categorías</h2>
          <p className="text-textSecondary text-sm">
            El rating se calcula con el algoritmo ELO adaptado para pádel 2vs2. 
            Tu categoría se actualiza automáticamente según tu rating.
          </p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {CATEGORIAS.map((cat, index) => (
            <motion.div
              key={cat.nombre}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`bg-gradient-to-br ${cat.color} p-3 rounded-lg text-center`}
            >
              <p className="text-white font-black text-lg">{cat.nombre}</p>
              <p className="text-white/80 text-xs mt-1">{cat.ratingMin}+</p>
            </motion.div>
          ))}
        </div>
      </Card>

      {/* Filtros y Búsqueda */}
      <div className="space-y-4">
        {/* Búsqueda */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" size={20} />
          <Input
            type="text"
            placeholder="Buscar jugador..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Filtro por Categoría */}
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-2 text-textSecondary">
            <Filter size={18} />
            <span className="text-sm font-bold">Categoría:</span>
          </div>
          {['todas', ...CATEGORIAS.map(c => c.nombre)].map((cat) => (
            <Button
              key={cat}
              variant={filtroCategoria === cat ? 'primary' : 'secondary'}
              onClick={() => setFiltroCategoria(cat)}
              size="sm"
            >
              {cat === 'todas' ? 'Todas' : cat}
            </Button>
          ))}
        </div>

        {/* Filtro por Género */}
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-2 text-textSecondary">
            <Filter size={18} />
            <span className="text-sm font-bold">Género:</span>
          </div>
          {[
            { value: 'todos', label: 'Todos', icon: '🏆' },
            { value: 'masculino', label: 'Masculino', icon: '♂' },
            { value: 'femenino', label: 'Femenino', icon: '♀' }
          ].map((g) => (
            <Button
              key={g.value}
              variant={filtroGenero === g.value ? 'primary' : 'secondary'}
              onClick={() => setFiltroGenero(g.value)}
              size="sm"
              className="flex items-center gap-1.5"
            >
              <span>{g.icon}</span>
              <span>{g.label}</span>
            </Button>
          ))}
        </div>
      </div>

      {/* Tabla de Rankings */}
      <Card>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-textPrimary flex items-center gap-2">
            <Trophy className="text-accent" size={28} />
            Top Jugadores
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-cardBorder">
                <th className="text-left py-3 px-4 text-textSecondary text-sm font-bold uppercase tracking-wider">Pos</th>
                <th className="text-left py-3 px-4 text-textSecondary text-sm font-bold uppercase tracking-wider">Jugador</th>
                <th className="text-center py-3 px-4 text-textSecondary text-sm font-bold uppercase tracking-wider">Género</th>
                <th className="text-center py-3 px-4 text-textSecondary text-sm font-bold uppercase tracking-wider">Rating</th>
                <th className="text-center py-3 px-4 text-textSecondary text-sm font-bold uppercase tracking-wider">Categoría</th>
                <th className="text-center py-3 px-4 text-textSecondary text-sm font-bold uppercase tracking-wider">Partidos</th>
                <th className="text-center py-3 px-4 text-textSecondary text-sm font-bold uppercase tracking-wider">Victorias</th>
                <th className="text-center py-3 px-4 text-textSecondary text-sm font-bold uppercase tracking-wider">% Victoria</th>
                <th className="text-center py-3 px-4 text-textSecondary text-sm font-bold uppercase tracking-wider">Tendencia</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-textSecondary">
                    Cargando rankings...
                  </td>
                </tr>
              ) : jugadoresFiltrados.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-textSecondary">
                    No se encontraron jugadores
                  </td>
                </tr>
              ) : (
                jugadoresFiltrados.map((jugador, index) => {
                  const catInfo = getCategoriaInfo(jugador.rating);
                  const nombreCompleto = `${jugador.nombre || ''} ${jugador.apellido || ''}`.trim() || jugador.nombre_usuario;
                  const partidosJugados = jugador.partidos_jugados || jugador.partidosJugados || 0;
                  const partidosGanados = jugador.partidos_ganados || jugador.partidosGanados || 0;
                  const porcentaje = partidosJugados > 0 ? ((partidosGanados / partidosJugados) * 100).toFixed(0) : '0';
                  
                  return (
                    <motion.tr
                      key={jugador.id_usuario || jugador.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      onClick={() => setJugadorSeleccionado(jugador)}
                      className="border-b border-cardBorder hover:bg-cardBorder transition-colors cursor-pointer"
                    >
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          {index === 0 && <Medal className="text-accent" size={20} />}
                          {index === 1 && <Medal className="text-gray-400" size={20} />}
                          {index === 2 && <Medal className="text-orange-400" size={20} />}
                          <span className="text-textPrimary font-bold text-lg">#{index + 1}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <p className="text-textPrimary font-bold">{nombreCompleto}</p>
                        <p className="text-textSecondary text-xs">@{jugador.nombre_usuario}</p>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className={`inline-block px-3 py-1 rounded-full text-white font-bold text-sm ${
                          jugador.sexo === 'M' 
                            ? 'bg-gradient-to-r from-blue-500 to-blue-600' 
                            : 'bg-gradient-to-r from-pink-500 to-pink-600'
                        }`}>
                          {jugador.sexo === 'M' ? '♂' : '♀'}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className="text-2xl font-black text-primary">{jugador.rating}</span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className={`inline-block px-3 py-1 rounded-full text-white font-bold text-sm bg-gradient-to-r ${catInfo.color}`}>
                          {catInfo.nombre}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className="text-textPrimary font-semibold">{partidosJugados}</span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className="text-secondary font-semibold">{partidosGanados}</span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className="text-textPrimary font-semibold">{porcentaje}%</span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <Minus className="text-textSecondary" size={20} />
                          <span className="text-textSecondary font-bold text-sm">-</span>
                        </div>
                      </td>
                    </motion.tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Información adicional */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <h3 className="text-lg font-bold text-textPrimary mb-3">¿Cómo funciona?</h3>
          <ul className="space-y-2 text-textSecondary text-sm">
            <li>• El rating inicial depende de tu categoría declarada</li>
            <li>• Ganas puntos al vencer rivales de mayor nivel</li>
            <li>• El margen de victoria afecta los puntos ganados</li>
            <li>• Tu categoría se actualiza automáticamente</li>
          </ul>
        </Card>

        <Card>
          <h3 className="text-lg font-bold text-textPrimary mb-3">Factor K</h3>
          <ul className="space-y-2 text-textSecondary text-sm">
            <li>• Nuevo (&lt;15 partidos): K = 32</li>
            <li>• Intermedio (15-59): K = 24</li>
            <li>• Experto (≥60): K = 18</li>
            <li>• Más partidos = cambios más estables</li>
          </ul>
        </Card>

        <Card>
          <h3 className="text-lg font-bold text-textPrimary mb-3">Caps de Rating</h3>
          <ul className="space-y-2 text-textSecondary text-sm">
            <li>• Ganador favorito: +22 máx</li>
            <li>• Ganador no favorito: +40 máx</li>
            <li>• Perdedor favorito: -40 mín</li>
            <li>• Perdedor no favorito: -18 mín</li>
          </ul>
        </Card>
      </div>

      {/* Gráfico de Progresión de Rating */}
      {jugadorSeleccionado && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card gradient>
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <BarChart3 className="text-primary" size={28} />
                <h2 className="text-2xl font-bold text-textPrimary">
                  Progresión de Rating - {jugadorSeleccionado.nombre}
                </h2>
              </div>
              <Button
                variant="ghost"
                onClick={() => setJugadorSeleccionado(null)}
                size="sm"
              >
                Cerrar
              </Button>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={progresionRating}>
                <CartesianGrid strokeDasharray="3 3" stroke="#3A4558" />
                <XAxis dataKey="mes" stroke="#94A3B8" />
                <YAxis stroke="#94A3B8" domain={[1000, 1500]} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#242B3D', 
                    border: '1px solid #3A4558',
                    borderRadius: '8px'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="rating" 
                  stroke="#0055FF" 
                  strokeWidth={3}
                  name="Rating"
                  dot={{ fill: '#0055FF', r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-background rounded-lg p-3">
                <p className="text-textSecondary text-xs mb-1">Rating Actual</p>
                <p className="text-2xl font-black text-primary">{jugadorSeleccionado.rating}</p>
              </div>
              <div className="bg-background rounded-lg p-3">
                <p className="text-textSecondary text-xs mb-1">Cambio Reciente</p>
                <p className={`text-2xl font-black ${jugadorSeleccionado.cambioReciente > 0 ? 'text-secondary' : 'text-red-500'}`}>
                  {jugadorSeleccionado.cambioReciente > 0 ? '+' : ''}{jugadorSeleccionado.cambioReciente}
                </p>
              </div>
              <div className="bg-background rounded-lg p-3">
                <p className="text-textSecondary text-xs mb-1">Partidos</p>
                <p className="text-2xl font-black text-textPrimary">{jugadorSeleccionado.partidosJugados}</p>
              </div>
              <div className="bg-background rounded-lg p-3">
                <p className="text-textSecondary text-xs mb-1">% Victoria</p>
                <p className="text-2xl font-black text-accent">
                  {((jugadorSeleccionado.partidosGanados / jugadorSeleccionado.partidosJugados) * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
