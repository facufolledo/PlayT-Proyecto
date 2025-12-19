import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { 
  Trophy, MapPin, Target, Hand, ArrowLeft, User, Calendar,
  ChevronDown, ChevronUp, Flame, Award, Zap
} from 'lucide-react';
import Button from '../components/Button';
import { PartidoCardSkeleton } from '../components/SkeletonLoader';
import { PlayerLink } from '../components/UserLink';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface DetalleSet {
  set: number;
  juegos_eq1: number;
  juegos_eq2: number;
  tiebreak_eq1?: number;
  tiebreak_eq2?: number;
}

interface ResultadoPartido {
  sets_eq1: number;
  sets_eq2: number;
  detalle_sets: DetalleSet[];
  confirmado: boolean;
  desenlace: string;
}

interface JugadorPartido {
  id_usuario: number;
  nombre_usuario: string;
  nombre: string;
  apellido: string;
  equipo: number;
  rating: number;
}

interface HistorialRating {
  rating_antes: number;
  delta: number;
  rating_despues: number;
}

interface Partido {
  id_partido: number;
  fecha: string;
  estado: string;
  tipo?: string;
  jugadores: JugadorPartido[];
  resultado?: ResultadoPartido;
  historial_rating?: HistorialRating;
}

interface PerfilUsuario {
  id_usuario: number;
  nombre_usuario: string;
  nombre: string;
  apellido: string;
  nombre_completo: string;
  sexo: string;
  ciudad: string;
  pais: string;
  rating: number;
  partidos_jugados: number;
  categoria: string;
  posicion_preferida: string;
  mano_dominante: string;
  foto_perfil: string | null;
}

export default function PerfilPublico() {
  const { username, id } = useParams<{ username?: string; id?: string }>();
  const navigate = useNavigate();
  const { usuario: usuarioActual } = useAuth();
  
  const [perfil, setPerfil] = useState<PerfilUsuario | null>(null);
  const [partidos, setPartidos] = useState<Partido[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filtro, setFiltro] = useState<'todos' | 'torneos' | 'amistosos'>('todos');
  const [mostrarTodos, setMostrarTodos] = useState(false);
  const [detallesAbiertos, setDetallesAbiertos] = useState<Set<number>>(new Set());

  // Determinar si puede ver datos privados (puntos Elo)
  // Solo el dueño del perfil o un admin pueden ver los puntos
  const puedeVerDatosPrivados = usuarioActual && (
    usuarioActual.nombre_usuario === username || 
    (id && usuarioActual.id_usuario === parseInt(id)) ||
    usuarioActual.es_administrador === true
  );

  // Si es el usuario actual, redirigir a MiPerfil
  useEffect(() => {
    if (usuarioActual) {
      if (username && username === usuarioActual.nombre_usuario) {
        navigate('/perfil', { replace: true });
      } else if (id && parseInt(id) === usuarioActual.id_usuario) {
        navigate('/perfil', { replace: true });
      }
    }
  }, [username, id, usuarioActual, navigate]);

  useEffect(() => {
    if (username || id) {
      cargarDatos();
    }
  }, [username, id]);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      let perfilRes;
      if (id) {
        // Buscar por ID
        perfilRes = await axios.get(`${API_URL}/usuarios/${id}/perfil`, { headers });
      } else if (username) {
        // Buscar por username
        perfilRes = await axios.get(`${API_URL}/usuarios/@${username}/perfil`, { headers });
      } else {
        throw new Error('No se especificó usuario');
      }
      setPerfil(perfilRes.data);

      const userId = perfilRes.data.id_usuario;

      try {
        const partidosRes = await axios.get(
          `${API_URL}/partidos/usuario/${userId}`,
          { headers, params: { limit: 50 } }
        );
        const partidosUnicos = partidosRes.data.filter((partido: Partido, index: number, self: Partido[]) =>
          index === self.findIndex((p) => p.id_partido === partido.id_partido)
        );
        setPartidos(partidosUnicos);
      } catch {
        setPartidos([]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar el perfil');
    } finally {
      setLoading(false);
    }
  };

  const toggleDetalles = (partidoId: number) => {
    setDetallesAbiertos(prev => {
      const newSet = new Set(prev);
      if (newSet.has(partidoId)) {
        newSet.delete(partidoId);
      } else {
        newSet.add(partidoId);
      }
      return newSet;
    });
  };

  const obtenerEquipoUsuario = (partido: Partido): JugadorPartido[] => {
    const miEquipo = partido.jugadores.find(j => j.id_usuario === perfil?.id_usuario)?.equipo;
    return partido.jugadores.filter(j => j.equipo === miEquipo);
  };

  const obtenerEquipoRival = (partido: Partido): JugadorPartido[] => {
    const miEquipo = partido.jugadores.find(j => j.id_usuario === perfil?.id_usuario)?.equipo;
    return partido.jugadores.filter(j => j.equipo !== miEquipo);
  };

  const esVictoria = (partido: Partido): boolean => {
    if (!partido.resultado) {
      if (partido.historial_rating) return partido.historial_rating.delta > 0;
      return false;
    }
    const miEquipo = partido.jugadores.find(j => j.id_usuario === perfil?.id_usuario)?.equipo;
    if (miEquipo === 1) return partido.resultado.sets_eq1 > partido.resultado.sets_eq2;
    return partido.resultado.sets_eq2 > partido.resultado.sets_eq1;
  };

  const formatearSets = (partido: Partido): string => {
    if (!partido.resultado) {
      if (partido.historial_rating) return partido.historial_rating.delta > 0 ? 'W' : 'L';
      return '-';
    }
    const miEquipo = partido.jugadores.find(j => j.id_usuario === perfil?.id_usuario)?.equipo;
    if (miEquipo === 1) return `${partido.resultado.sets_eq1}-${partido.resultado.sets_eq2}`;
    return `${partido.resultado.sets_eq2}-${partido.resultado.sets_eq1}`;
  };

  const formatearDetalleSets = (partido: Partido): string => {
    if (!partido.resultado?.detalle_sets) return '';
    const miEquipo = partido.jugadores.find(j => j.id_usuario === perfil?.id_usuario)?.equipo;
    
    return partido.resultado.detalle_sets.map(set => {
      const misJuegos = miEquipo === 1 ? set.juegos_eq1 : set.juegos_eq2;
      const rivalJuegos = miEquipo === 1 ? set.juegos_eq2 : set.juegos_eq1;
      if (set.tiebreak_eq1 !== undefined && set.tiebreak_eq1 !== null) {
        const miTiebreak = miEquipo === 1 ? set.tiebreak_eq1 : set.tiebreak_eq2;
        return `${misJuegos}-${rivalJuegos}(${miTiebreak})`;
      }
      return `${misJuegos}-${rivalJuegos}`;
    }).join(' / ');
  };

  const formatearFecha = (fecha: string): string => {
    const fechaPartido = new Date(fecha);
    const ahora = new Date();
    const diffMs = ahora.getTime() - fechaPartido.getTime();
    const diffHoras = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDias = Math.floor(diffHoras / 24);
    if (diffHoras < 1) return 'hace menos de 1 hora';
    if (diffHoras < 24) return `hace ${diffHoras} hora${diffHoras > 1 ? 's' : ''}`;
    if (diffDias < 7) return `hace ${diffDias} día${diffDias > 1 ? 's' : ''}`;
    return fechaPartido.toLocaleDateString();
  };

  // Filtros y estadísticas
  const partidosFiltrados = partidos.filter(partido => {
    if (filtro === 'todos') return true;
    if (filtro === 'torneos') return partido.tipo === 'torneo';
    if (filtro === 'amistosos') return partido.tipo === 'amistoso';
    return true;
  });
  
  const partidosMostrados = mostrarTodos ? partidosFiltrados : partidosFiltrados.slice(0, 10);

  const totalPartidos = partidos.filter(p => p.resultado || p.historial_rating).length;
  const partidosTorneos = partidos.filter(p => p.tipo === 'torneo').length;
  const partidosAmistosos = partidos.filter(p => p.tipo === 'amistoso' || !p.tipo).length;
  
  const victorias = partidos.filter(p => (p.resultado || p.historial_rating) && esVictoria(p)).length;
  const derrotas = totalPartidos - victorias;
  const winrate = totalPartidos > 0 ? Math.round((victorias / totalPartidos) * 100) : 0;

  // Estadísticas avanzadas
  const calcularEstadisticasAvanzadas = () => {
    const torneos = partidos.filter(p => p.tipo === 'torneo');
    const amistosos = partidos.filter(p => p.tipo === 'amistoso' || !p.tipo);
    
    const victoriasTorneos = torneos.filter(p => (p.resultado || p.historial_rating) && esVictoria(p)).length;
    const victoriaAmistosos = amistosos.filter(p => (p.resultado || p.historial_rating) && esVictoria(p)).length;
    
    const winrateTorneos = torneos.length > 0 ? Math.round((victoriasTorneos / torneos.length) * 100) : 0;
    const winrateAmistosos = amistosos.length > 0 ? Math.round((victoriaAmistosos / amistosos.length) * 100) : 0;

    let rachaActual = 0;
    let rachaVictorias = true;
    const partidosOrdenados = [...partidos].sort((a, b) => 
      new Date(b.fecha).getTime() - new Date(a.fecha).getTime()
    );
    
    for (const partido of partidosOrdenados) {
      if (!partido.resultado && !partido.historial_rating) continue;
      const victoria = esVictoria(partido);
      if (rachaActual === 0) {
        rachaVictorias = victoria;
        rachaActual = 1;
      } else if (victoria === rachaVictorias) {
        rachaActual++;
      } else {
        break;
      }
    }

    let mejorRacha = 0;
    let rachaTemp = 0;
    for (const partido of partidosOrdenados.reverse()) {
      if (!partido.resultado && !partido.historial_rating) continue;
      if (esVictoria(partido)) {
        rachaTemp++;
        mejorRacha = Math.max(mejorRacha, rachaTemp);
      } else {
        rachaTemp = 0;
      }
    }

    let setsGanados = 0;
    let setsPerdidos = 0;
    let gamesGanados = 0;
    let gamesPerdidos = 0;

    for (const partido of partidos) {
      if (!partido.resultado) continue;
      const miEquipo = partido.jugadores.find(j => j.id_usuario === perfil?.id_usuario)?.equipo;
      
      if (miEquipo === 1) {
        setsGanados += partido.resultado.sets_eq1;
        setsPerdidos += partido.resultado.sets_eq2;
      } else {
        setsGanados += partido.resultado.sets_eq2;
        setsPerdidos += partido.resultado.sets_eq1;
      }

      if (partido.resultado.detalle_sets) {
        for (const set of partido.resultado.detalle_sets) {
          if (miEquipo === 1) {
            gamesGanados += set.juegos_eq1;
            gamesPerdidos += set.juegos_eq2;
          } else {
            gamesGanados += set.juegos_eq2;
            gamesPerdidos += set.juegos_eq1;
          }
        }
      }
    }

    return {
      winrateTorneos,
      winrateAmistosos,
      victoriasTorneos,
      victoriaAmistosos,
      derrotasTorneos: torneos.length - victoriasTorneos,
      derrotasAmistosos: amistosos.length - victoriaAmistosos,
      rachaActual,
      rachaVictorias,
      mejorRacha,
      setsGanados,
      setsPerdidos,
      gamesGanados,
      gamesPerdidos
    };
  };

  const stats = perfil ? calcularEstadisticasAvanzadas() : null;

  if (loading) {
    return (
      <div className="min-h-screen p-4 md:p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-cardBorder rounded w-32 mb-6" />
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-4 space-y-4">
                <div className="bg-cardBg rounded-xl p-6 border border-cardBorder h-80" />
                <div className="bg-cardBg rounded-xl p-6 border border-cardBorder h-40" />
              </div>
              <div className="lg:col-span-8">
                <div className="bg-cardBg rounded-xl p-6 border border-cardBorder">
                  <PartidoCardSkeleton />
                  <PartidoCardSkeleton />
                  <PartidoCardSkeleton />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !perfil) {
    return (
      <div className="min-h-screen p-4 md:p-6 flex items-center justify-center">
        <div className="text-center">
          <User size={64} className="mx-auto mb-4 text-textSecondary opacity-50" />
          <h2 className="text-xl font-bold text-textPrimary mb-2">Usuario no encontrado</h2>
          <p className="text-textSecondary mb-4">{error || 'El perfil que buscas no existe'}</p>
          <Button onClick={() => navigate(-1)}>Volver</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header con botón volver */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-textSecondary hover:text-primary transition-colors"
          >
            <ArrowLeft size={20} />
            <span>Volver</span>
          </button>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 md:gap-6">
          {/* Panel Izquierdo - Perfil */}
          <div className="lg:col-span-4 space-y-4">
            {/* Card de Perfil */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-cardBg rounded-xl p-3 md:p-6 border border-cardBorder"
            >
              <div className="flex items-center justify-between mb-4 md:mb-6">
                <h2 className="text-lg md:text-xl font-bold text-textPrimary flex items-center gap-2">
                  <div className="h-0.5 md:h-1 w-6 md:w-8 bg-gradient-to-r from-primary to-secondary rounded-full" />
                  Perfil
                </h2>
              </div>

              {/* Avatar y Nombre */}
              <div className="flex flex-col items-center mb-3">
                <div className="w-20 h-20 md:w-32 md:h-32 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-2xl md:text-4xl font-black mb-2 overflow-hidden">
                  {perfil.foto_perfil ? (
                    <img src={perfil.foto_perfil} alt={perfil.nombre_completo} className="w-full h-full object-cover" />
                  ) : (
                    <span>{perfil.nombre?.charAt(0)}{perfil.apellido?.charAt(0)}</span>
                  )}
                </div>
                <h3 className="text-lg md:text-2xl font-black text-textPrimary text-center">
                  {perfil.nombre} {perfil.apellido}
                </h3>
                <p className="text-textSecondary text-[10px] md:text-sm">@{perfil.nombre_usuario}</p>
              </div>

              {/* Rating */}
              <div className="text-center mb-3 p-2 md:p-4 bg-primary/10 rounded-lg">
                <p className="text-textSecondary text-[10px] md:text-sm mb-0.5">Rating</p>
                <p className="text-2xl md:text-4xl font-black text-primary">{perfil.rating}</p>
                {perfil.categoria && <p className="text-[9px] md:text-xs text-textSecondary mt-0.5">Categoría {perfil.categoria}</p>}
              </div>

              {/* Info Adicional */}
              <div className="space-y-1.5 text-[10px] md:text-sm">
                {perfil.posicion_preferida && (
                  <div className="flex items-center gap-1.5 text-textSecondary">
                    <Target size={12} className="text-primary md:w-3.5 md:h-3.5" />
                    <span className="capitalize">{perfil.posicion_preferida}</span>
                  </div>
                )}
                {perfil.mano_dominante && (
                  <div className="flex items-center gap-1.5 text-textSecondary">
                    <Hand size={12} className="text-secondary md:w-3.5 md:h-3.5" />
                    <span className="capitalize">{perfil.mano_dominante}</span>
                  </div>
                )}
                {perfil.ciudad && perfil.pais && (
                  <div className="flex items-center gap-1.5 text-textSecondary">
                    <MapPin size={12} className="text-primary md:w-3.5 md:h-3.5" />
                    <span>{perfil.ciudad}, {perfil.pais}</span>
                  </div>
                )}
                <div className="flex items-center gap-1.5 text-textSecondary">
                  <Calendar size={12} className="text-primary md:w-3.5 md:h-3.5" />
                  <span>Miembro desde {new Date().getFullYear()}</span>
                </div>
              </div>
            </motion.div>

            {/* Card de Estadísticas */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-gradient-to-br from-primary/20 to-secondary/20 rounded-xl p-3 md:p-6 border border-primary/30"
            >
              <h3 className="text-sm md:text-lg font-bold text-textPrimary mb-2 md:mb-4">Estadísticas</h3>
              
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-primary/20 rounded-lg p-2 text-center">
                  <Trophy size={16} className="text-primary mx-auto mb-1 md:w-5 md:h-5" />
                  <p className="text-xl md:text-2xl font-black text-primary">{victorias}</p>
                  <p className="text-[9px] md:text-xs text-textSecondary">Victorias</p>
                </div>
                <div className="bg-red-500/20 rounded-lg p-2 text-center">
                  <Trophy size={16} className="text-red-500 mx-auto mb-1 md:w-5 md:h-5" />
                  <p className="text-xl md:text-2xl font-black text-red-500">{derrotas}</p>
                  <p className="text-[9px] md:text-xs text-textSecondary">Derrotas</p>
                </div>
              </div>

              <div className="mt-2 bg-accent/20 rounded-lg p-2 text-center">
                <p className="text-[9px] md:text-xs text-textSecondary mb-0.5">Winrate General</p>
                <p className="text-2xl md:text-3xl font-black text-accent">{winrate}%</p>
              </div>
            </motion.div>

            {/* Card de Estadísticas Avanzadas */}
            {stats && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-cardBg rounded-xl p-3 md:p-6 border border-cardBorder"
              >
                <h3 className="text-sm md:text-lg font-bold text-textPrimary mb-3 md:mb-4 flex items-center gap-2">
                  <Zap size={16} className="text-accent" />
                  Estadísticas Avanzadas
                </h3>
                
                {/* Winrate por tipo */}
                <div className="space-y-3 mb-4">
                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-[10px] md:text-xs text-textSecondary flex items-center gap-1">
                        <Award size={12} className="text-accent" />
                        Torneos
                      </span>
                      <span className="text-[10px] md:text-xs font-bold text-accent">{stats.winrateTorneos}%</span>
                    </div>
                    <div className="h-2 bg-cardBorder rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-accent to-accent/60 rounded-full transition-all duration-500"
                        style={{ width: `${stats.winrateTorneos}%` }}
                      />
                    </div>
                    <p className="text-[9px] text-textSecondary mt-0.5">{stats.victoriasTorneos}V - {stats.derrotasTorneos}D</p>
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-[10px] md:text-xs text-textSecondary flex items-center gap-1">
                        <Target size={12} className="text-primary" />
                        Amistosos
                      </span>
                      <span className="text-[10px] md:text-xs font-bold text-primary">{stats.winrateAmistosos}%</span>
                    </div>
                    <div className="h-2 bg-cardBorder rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-primary to-primary/60 rounded-full transition-all duration-500"
                        style={{ width: `${stats.winrateAmistosos}%` }}
                      />
                    </div>
                    <p className="text-[9px] text-textSecondary mt-0.5">{stats.victoriaAmistosos}V - {stats.derrotasAmistosos}D</p>
                  </div>
                </div>

                {/* Racha */}
                <div className="grid grid-cols-2 gap-2 mb-3">
                  <div className={`rounded-lg p-2 text-center ${stats.rachaVictorias ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                    <Flame size={14} className={`mx-auto mb-1 ${stats.rachaVictorias ? 'text-green-400' : 'text-red-400'}`} />
                    <p className={`text-lg md:text-xl font-black ${stats.rachaVictorias ? 'text-green-400' : 'text-red-400'}`}>
                      {stats.rachaActual}
                    </p>
                    <p className="text-[9px] md:text-xs text-textSecondary">
                      Racha {stats.rachaVictorias ? 'Victorias' : 'Derrotas'}
                    </p>
                  </div>
                  <div className="bg-yellow-500/20 rounded-lg p-2 text-center">
                    <Trophy size={14} className="text-yellow-400 mx-auto mb-1" />
                    <p className="text-lg md:text-xl font-black text-yellow-400">{stats.mejorRacha}</p>
                    <p className="text-[9px] md:text-xs text-textSecondary">Mejor Racha</p>
                  </div>
                </div>

                {/* Sets y Games */}
                <div className="border-t border-cardBorder pt-3">
                  <p className="text-[10px] md:text-xs text-textSecondary mb-2">Rendimiento en Sets/Games</p>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="text-center">
                      <p className="text-[9px] text-textSecondary">Sets</p>
                      <p className="text-sm font-bold">
                        <span className="text-green-400">{stats.setsGanados}</span>
                        <span className="text-textSecondary mx-1">-</span>
                        <span className="text-red-400">{stats.setsPerdidos}</span>
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-[9px] text-textSecondary">Games</p>
                      <p className="text-sm font-bold">
                        <span className="text-green-400">{stats.gamesGanados}</span>
                        <span className="text-textSecondary mx-1">-</span>
                        <span className="text-red-400">{stats.gamesPerdidos}</span>
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Panel Derecho - Historial */}
          <div className="lg:col-span-8">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-cardBg rounded-xl p-4 md:p-6 border border-cardBorder"
            >
              {/* Header */}
              <div className="mb-4 md:mb-6">
                <h2 className="text-xl md:text-2xl font-black text-textPrimary mb-3 md:mb-4">Historial de Partidos</h2>
                
                {/* Estadísticas */}
                <div className="grid grid-cols-4 gap-2 md:gap-4 mb-4 md:mb-6">
                  <div>
                    <p className="text-textSecondary text-[10px] md:text-sm">Total</p>
                    <p className="text-xl md:text-2xl font-black text-textPrimary">{totalPartidos}</p>
                  </div>
                  <div>
                    <p className="text-textSecondary text-[10px] md:text-sm">Ganados</p>
                    <p className="text-xl md:text-2xl font-black text-secondary">{victorias}</p>
                  </div>
                  <div>
                    <p className="text-textSecondary text-[10px] md:text-sm">Perdidos</p>
                    <p className="text-xl md:text-2xl font-black text-red-500">{derrotas}</p>
                  </div>
                  <div>
                    <p className="text-textSecondary text-[10px] md:text-sm">Winrate</p>
                    <p className="text-xl md:text-2xl font-black text-accent">{winrate}%</p>
                  </div>
                </div>

                {/* Filtros */}
                <div className="flex gap-1 md:gap-2 flex-wrap">
                  <Button
                    variant={filtro === 'todos' ? 'primary' : 'ghost'}
                    onClick={() => setFiltro('todos')}
                    className="text-[10px] md:text-sm px-2 md:px-4 py-1 md:py-2"
                  >
                    TODOS ({totalPartidos})
                  </Button>
                  <Button
                    variant={filtro === 'torneos' ? 'primary' : 'ghost'}
                    onClick={() => setFiltro('torneos')}
                    className="text-[10px] md:text-sm px-2 md:px-4 py-1 md:py-2"
                  >
                    TORNEOS ({partidosTorneos})
                  </Button>
                  <Button
                    variant={filtro === 'amistosos' ? 'primary' : 'ghost'}
                    onClick={() => setFiltro('amistosos')}
                    className="text-[10px] md:text-sm px-2 md:px-4 py-1 md:py-2"
                  >
                    AMISTOSOS ({partidosAmistosos})
                  </Button>
                </div>
              </div>

              {/* Lista de Partidos */}
              <div className="space-y-3">
                {partidosMostrados.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="bg-cardBorder/30 rounded-lg p-8">
                      <Trophy size={48} className="mx-auto mb-4 text-textSecondary opacity-50" />
                      <p className="text-textPrimary font-bold mb-2">Sin partidos registrados</p>
                      <p className="text-textSecondary text-sm">
                        Los partidos aparecerán aquí una vez que juegue
                      </p>
                    </div>
                  </div>
                ) : (
                  partidosMostrados.map((partido, index) => {
                    const victoria = esVictoria(partido);
                    const miEquipo = obtenerEquipoUsuario(partido);
                    const rivalEquipo = obtenerEquipoRival(partido);
                    const detallesVisible = detallesAbiertos.has(partido.id_partido);

                    return (
                      <motion.div
                        key={partido.id_partido}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className={`relative rounded-lg p-3 md:p-4 border-l-4 ${
                          victoria
                            ? 'bg-green-500/20 border-green-500 shadow-green-500/20 shadow-lg'
                            : 'bg-red-500/20 border-red-500 shadow-red-500/20 shadow-lg'
                        }`}
                      >
                        {/* Tipo y Fecha */}
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-3">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className={`px-2 md:px-3 py-0.5 md:py-1 rounded-full text-[10px] md:text-xs font-bold ${
                              partido.tipo === 'torneo' 
                                ? 'bg-accent/20 text-accent' 
                                : 'bg-primary/20 text-primary'
                            }`}>
                              {partido.tipo === 'torneo' ? 'TORNEO' : 'AMISTOSO'}
                            </span>
                            <span className="text-textSecondary text-[10px] md:text-xs">
                              {formatearFecha(partido.fecha)}
                            </span>
                          </div>
                          {/* Solo mostrar puntos Elo si es propietario o admin */}
                          {puedeVerDatosPrivados && partido.historial_rating && (
                            <span className={`text-base md:text-lg font-black ${
                              partido.historial_rating.delta > 0 ? 'text-green-400' : 'text-red-400'
                            }`}>
                              {partido.historial_rating.delta > 0 ? '+' : ''}{partido.historial_rating.delta}
                            </span>
                          )}
                        </div>

                        {/* Equipos y Resultado */}
                        <div className="grid grid-cols-12 gap-2 md:gap-4 items-center mb-2">
                          {/* Mi Equipo */}
                          <div className="col-span-5">
                            {miEquipo.map((jugador, i) => (
                              <div key={i} className="truncate">
                                <PlayerLink 
                                  id={jugador.id_usuario} 
                                  nombre={`${jugador.nombre} ${jugador.apellido}`}
                                  nombreUsuario={jugador.nombre_usuario}
                                  size="sm" 
                                />
                              </div>
                            ))}
                          </div>

                          {/* Resultado */}
                          <div className="col-span-2 text-center">
                            <p className={`text-2xl md:text-3xl font-black ${
                              victoria ? 'text-green-400' : 'text-red-400'
                            }`}>
                              {formatearSets(partido)}
                            </p>
                            <p className="text-textSecondary text-[9px] md:text-xs hidden sm:block">
                              {formatearDetalleSets(partido)}
                            </p>
                          </div>

                          {/* Equipo Rival */}
                          <div className="col-span-5 text-right">
                            {rivalEquipo.map((jugador, i) => (
                              <div key={i} className="truncate">
                                <PlayerLink 
                                  id={jugador.id_usuario} 
                                  nombre={`${jugador.nombre} ${jugador.apellido}`}
                                  nombreUsuario={jugador.nombre_usuario}
                                  size="sm" 
                                />
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Detalles Expandibles */}
                        <AnimatePresence>
                          {detallesVisible && partido.resultado?.detalle_sets && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              transition={{ duration: 0.2 }}
                              className="overflow-hidden"
                            >
                              <div className="mt-3 md:mt-4 pt-3 md:pt-4 border-t border-cardBorder">
                                <h4 className="text-[10px] md:text-xs font-bold text-textSecondary mb-2">Detalle por Set</h4>
                                <div className="space-y-1 md:space-y-2">
                                  {partido.resultado.detalle_sets.map((set, idx) => {
                                    const miEquipoNum = partido.jugadores.find(j => j.id_usuario === perfil?.id_usuario)?.equipo;
                                    const misJuegos = miEquipoNum === 1 ? set.juegos_eq1 : set.juegos_eq2;
                                    const rivalJuegos = miEquipoNum === 1 ? set.juegos_eq2 : set.juegos_eq1;
                                    const ganeSet = misJuegos > rivalJuegos;

                                    return (
                                      <div key={idx} className={`flex items-center justify-between p-1.5 md:p-2 rounded ${
                                        ganeSet ? 'bg-green-500/10' : 'bg-red-500/10'
                                      }`}>
                                        <span className="text-textSecondary text-[10px] md:text-xs">Set {set.set}</span>
                                        <span className={`font-bold text-xs md:text-sm ${
                                          ganeSet ? 'text-green-400' : 'text-red-400'
                                        }`}>
                                          {misJuegos} - {rivalJuegos}
                                          {set.tiebreak_eq1 !== undefined && set.tiebreak_eq1 !== null && 
                                           set.tiebreak_eq2 !== undefined && set.tiebreak_eq2 !== null && (
                                            <span className="text-[10px] md:text-xs ml-1">
                                              ({miEquipoNum === 1 ? set.tiebreak_eq1 : set.tiebreak_eq2})
                                            </span>
                                          )}
                                        </span>
                                      </div>
                                    );
                                  })}
                                </div>
                                {/* Solo mostrar historial de rating si es propietario o admin */}
                                {puedeVerDatosPrivados && partido.historial_rating && (
                                  <div className="mt-2 md:mt-3 text-[10px] md:text-xs text-textSecondary space-y-0.5">
                                    <p>Rating antes: {partido.historial_rating.rating_antes}</p>
                                    <p>Rating después: {partido.historial_rating.rating_despues}</p>
                                  </div>
                                )}
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>

                        {/* Botón Ver Detalles */}
                        {partido.resultado && (
                          <button 
                            onClick={() => toggleDetalles(partido.id_partido)}
                            className="absolute bottom-1 md:bottom-2 right-1 md:right-2 text-textSecondary hover:text-primary text-[10px] md:text-xs flex items-center gap-1 transition-colors"
                          >
                            {detallesVisible ? 'ocultar' : 'detalles'}
                            {detallesVisible ? <ChevronUp size={10} className="md:w-3 md:h-3" /> : <ChevronDown size={10} className="md:w-3 md:h-3" />}
                          </button>
                        )}
                      </motion.div>
                    );
                  })
                )}
              </div>

              {/* Botón Cargar Más */}
              {!mostrarTodos && partidosFiltrados.length > 10 && (
                <div className="mt-6 text-center">
                  <Button
                    variant="ghost"
                    onClick={() => setMostrarTodos(true)}
                    className="w-full"
                  >
                    cargar más
                  </Button>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
