import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Trophy, MapPin, Calendar, ChevronDown, ChevronUp, Target, Hand, 
  TrendingUp, TrendingDown, Flame, Award, Zap, ArrowLeft 
} from 'lucide-react';
import Button from './Button';
import { PartidoCardSkeleton } from './SkeletonLoader';
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

interface PerfilData {
  id_usuario: number;
  nombre_usuario: string;
  nombre: string;
  apellido: string;
  sexo?: string;
  ciudad?: string;
  pais?: string;
  rating: number;
  partidos_jugados?: number;
  categoria?: string;
  posicion_preferida?: string;
  mano_dominante?: string;
  foto_perfil?: string | null;
}

interface PerfilViewProps {
  perfil: PerfilData;
  esPropietario: boolean; // true = MiPerfil, false = perfil de otro
  mostrarBotonVolver?: boolean;
  mostrarBotonEditar?: boolean;
}

export default function PerfilView({ 
  perfil, 
  esPropietario, 
  mostrarBotonVolver = false,
  mostrarBotonEditar = false 
}: PerfilViewProps) {
  const navigate = useNavigate();
  const [filtro, setFiltro] = useState<'todos' | 'torneos' | 'amistosos'>('todos');
  const [mostrarTodos, setMostrarTodos] = useState(false);
  const [partidos, setPartidos] = useState<Partido[]>([]);
  const [loading, setLoading] = useState(true);
  const [detallesAbiertos, setDetallesAbiertos] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (perfil?.id_usuario) {
      cargarPartidos();
    }
  }, [perfil?.id_usuario]);

  const cargarPartidos = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const response = await axios.get(
        `${API_URL}/partidos/usuario/${perfil.id_usuario}`,
        { headers, params: { limit: 50 } }
      );
      
      const partidosUnicos = response.data.filter((partido: Partido, index: number, self: Partido[]) =>
        index === self.findIndex((p) => p.id_partido === partido.id_partido)
      );
      
      setPartidos(partidosUnicos);
    } catch {
      setPartidos([]);
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
    const miEquipo = partido.jugadores.find(j => j.id_usuario === perfil.id_usuario)?.equipo;
    return partido.jugadores.filter(j => j.equipo === miEquipo);
  };

  const obtenerEquipoRival = (partido: Partido): JugadorPartido[] => {
    const miEquipo = partido.jugadores.find(j => j.id_usuario === perfil.id_usuario)?.equipo;
    return partido.jugadores.filter(j => j.equipo !== miEquipo);
  };

  const esVictoria = (partido: Partido): boolean => {
    if (!partido.resultado) {
      if (partido.historial_rating) return partido.historial_rating.delta > 0;
      return false;
    }
    const miEquipo = partido.jugadores.find(j => j.id_usuario === perfil.id_usuario)?.equipo;
    if (miEquipo === 1) return partido.resultado.sets_eq1 > partido.resultado.sets_eq2;
    return partido.resultado.sets_eq2 > partido.resultado.sets_eq1;
  };

  const formatearSets = (partido: Partido): string => {
    if (!partido.resultado) {
      if (partido.historial_rating) return partido.historial_rating.delta > 0 ? 'W' : 'L';
      return '-';
    }
    const miEquipo = partido.jugadores.find(j => j.id_usuario === perfil.id_usuario)?.equipo;
    if (miEquipo === 1) return `${partido.resultado.sets_eq1}-${partido.resultado.sets_eq2}`;
    return `${partido.resultado.sets_eq2}-${partido.resultado.sets_eq1}`;
  };

  const formatearDetalleSets = (partido: Partido): string => {
    if (!partido.resultado?.detalle_sets) return '';
    const miEquipo = partido.jugadores.find(j => j.id_usuario === perfil.id_usuario)?.equipo;
    
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
