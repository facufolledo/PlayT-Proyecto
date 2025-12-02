import { motion, useReducedMotion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect, useMemo } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import { Trophy, Users, Calendar, Zap, Target, TrendingUp } from 'lucide-react';
import { useSalas } from '../context/SalasContext';
import { useTorneos } from '../context/TorneosContext';
import { useAuth } from '../context/AuthContext';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface PartidoHistorial {
  id_partido: number;
  fecha: string;
  tipo: string;
  jugadores: { id_usuario: number; equipo: number; nombre: string; apellido: string }[];
  resultado?: { sets_eq1: number; sets_eq2: number };
  historial_rating?: { delta: number };
}

export default function Dashboard() {
  const { salas } = useSalas();
  const { torneos } = useTorneos();
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const shouldReduceMotion = useReducedMotion();
  const [partidos, setPartidos] = useState<PartidoHistorial[]>([]);

  // Cargar partidos del usuario
  useEffect(() => {
    const cargarPartidos = async () => {
      if (!usuario?.id_usuario) return;
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `${API_URL}/partidos/usuario/${usuario.id_usuario}`,
          { headers: { Authorization: `Bearer ${token}` }, params: { limit: 100 } }
        );
        setPartidos(response.data);
      } catch (error) {
        console.error('Error cargando partidos:', error);
      }
    };
    cargarPartidos();
  }, [usuario]);

  // Calcular estadísticas reales
  const estadisticas = useMemo(() => {
    const esVictoria = (p: PartidoHistorial) => {
      if (p.historial_rating) return p.historial_rating.delta > 0;
      if (!p.resultado) return false;
      const miEquipo = p.jugadores.find(j => j.id_usuario === usuario?.id_usuario)?.equipo;
      return miEquipo === 1 ? p.resultado.sets_eq1 > p.resultado.sets_eq2 : p.resultado.sets_eq2 > p.resultado.sets_eq1;
    };

    const partidosConResultado = partidos.filter(p => p.resultado || p.historial_rating);
    const victorias = partidosConResultado.filter(esVictoria).length;
    const derrotas = partidosConResultado.length - victorias;

    // Actividad semanal (últimos 7 días)
    const hoy = new Date();
    const dias = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    const actividadSemanal = [];
    
    for (let i = 6; i >= 0; i--) {
      const fecha = new Date(hoy);
      fecha.setDate(hoy.getDate() - i);
      const diaStr = dias[fecha.getDay()];
      
      const partidosDia = partidos.filter(p => {
        const fechaPartido = new Date(p.fecha);
        return fechaPartido.toDateString() === fecha.toDateString();
      });
      
      const victoriasDia = partidosDia.filter(esVictoria).length;
      
      actividadSemanal.push({
        dia: diaStr,
        partidos: partidosDia.length,
        victorias: victoriasDia
      });
    }

    // Distribución por tipo
    const torneoPartidos = partidos.filter(p => p.tipo === 'torneo');
    const amistososPartidos = partidos.filter(p => p.tipo === 'amistoso' || !p.tipo);
    
    const victoriasTorneo = torneoPartidos.filter(esVictoria).length;
    const victoriasAmistoso = amistososPartidos.filter(esVictoria).length;

    const rendimientoPorTipo = [
      { tipo: 'Torneos', partidos: torneoPartidos.length, victorias: victoriasTorneo },
      { tipo: 'Amistosos', partidos: amistososPartidos.length, victorias: victoriasAmistoso },
    ];

    return { victorias, derrotas, actividadSemanal, rendimientoPorTipo, totalPartidos: partidosConResultado.length };
  }, [partidos, usuario]);

  const partidosJugados = estadisticas.totalPartidos;
  const proximosPartidos = salas.filter(s => s.estado === 'programada' || s.estado === 'esperando').length;
  const partidosActivos = salas.filter(s => s.estado === 'activa' || s.estado === 'en_juego').length;
  const torneosActivos = torneos.filter(t => 
    t.estado === 'activo' || t.estado === 'programado' || 
    (t.estado as string) === 'inscripcion' || (t.estado as string) === 'fase_grupos' || (t.estado as string) === 'fase_eliminacion'
  ).length;

  // Últimos partidos desde el endpoint real
  const ultimosPartidos = partidos
    .filter(p => p.resultado || p.historial_rating)
    .sort((a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime())
    .slice(0, 5);

  // Datos para gráficos - ahora con datos reales
  const actividadSemanal = estadisticas.actividadSemanal;
  const rendimientoPorTipo = estadisticas.rendimientoPorTipo;

  const distribucionResultados = [
    { name: 'Victorias', value: estadisticas.victorias, color: '#FF006E' },
    { name: 'Derrotas', value: estadisticas.derrotas, color: '#94A3B8' },
  ];

  const stats = [
    { 
      icon: Trophy, 
      label: 'Torneos Activos', 
      value: torneosActivos.toString(), 
      color: 'from-primary to-blue-500',
      iconBg: 'bg-primary/10',
      iconColor: 'text-primary',
      glowColor: 'primary'
    },
    { 
      icon: Users, 
      label: 'Partidos Jugados', 
      value: partidosJugados.toString(), 
      color: 'from-secondary to-pink-500',
      iconBg: 'bg-secondary/10',
      iconColor: 'text-secondary',
      glowColor: 'secondary'
    },
    { 
      icon: Zap, 
      label: 'Partidos Activos', 
      value: partidosActivos.toString(), 
      color: 'from-accent to-yellow-400',
      iconBg: 'bg-accent/10',
      iconColor: 'text-accent',
      glowColor: 'accent'
    },
    { 
      icon: Calendar, 
      label: 'Próximos Partidos', 
      value: proximosPartidos.toString(), 
      color: 'from-cyan-400 to-blue-500',
      iconBg: 'bg-cyan-400/10',
      iconColor: 'text-cyan-400',
      glowColor: 'cyan'
    },
  ];

  return (
    <div className="space-y-8">
        {/* Header estilo gaming */}
        <motion.div
          initial={shouldReduceMotion ? false : { opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={shouldReduceMotion ? { duration: 0 } : { duration: 0.4, ease: "easeOut" }}
          className="relative mb-2"
        >
          <div className="flex items-center gap-2 md:gap-3 mb-2 md:mb-3">
            <div className="h-0.5 md:h-1 w-8 md:w-12 bg-gradient-to-r from-primary to-secondary rounded-full" />
            <h1 className="text-2xl md:text-5xl font-black text-textPrimary tracking-tight">
              Bienvenido de vuelta
            </h1>
          </div>
          <p className="text-textSecondary text-xs md:text-base ml-10 md:ml-15">Aquí está tu resumen de rendimiento</p>
        </motion.div>

      {/* Stats Cards estilo eSports */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={shouldReduceMotion ? false : { opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={shouldReduceMotion ? { duration: 0 } : { 
                delay: index * 0.05,
                duration: 0.3
              }}
              whileHover={shouldReduceMotion ? {} : { y: -4, scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="group cursor-pointer"
            >
              <div className="relative bg-cardBg rounded-lg md:rounded-xl p-3 md:p-6 border border-cardBorder group-hover:border-transparent transition-all duration-200 overflow-hidden">
                {/* Glow effect on hover - solo desktop */}
                <div className={`hidden md:block absolute inset-0 bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-10 transition-opacity duration-200`} />
                <div className={`hidden md:block absolute -inset-[1px] bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-xl -z-10 blur-sm`} />
                
                <div className="relative z-10">
                  <div className="flex items-center justify-between mb-2 md:mb-4">
                    <div className={`${stat.iconBg} p-2 md:p-3 rounded-lg relative`}>
                      <Icon size={20} className={`${stat.iconColor} md:w-7 md:h-7`} strokeWidth={2.5} />
                    </div>
                    <div className="text-right">
                      <p className="text-3xl md:text-5xl font-black text-textPrimary tracking-tight">
                        {stat.value}
                      </p>
                    </div>
                  </div>
                  <p className="text-textSecondary text-[10px] md:text-xs font-bold uppercase tracking-wider">{stat.label}</p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Sección de últimos partidos y torneos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card gradient>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-textPrimary flex items-center gap-2">
              <Target className="text-primary" size={28} />
              Últimos Partidos
            </h2>
            {ultimosPartidos.length > 0 && (
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button variant="ghost" onClick={() => navigate('/salas')} className="text-sm">
                  Ver todos →
                </Button>
              </motion.div>
            )}
          </div>
          {ultimosPartidos.length === 0 ? (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12 text-textSecondary"
            >
              <div className="bg-primary/10 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
                <Users size={40} className="text-primary" />
              </div>
              <p className="mb-4 text-lg">No hay partidos registrados aún</p>
              <Button variant="primary" onClick={() => navigate('/salas')}>
                Crear primera sala
              </Button>
            </motion.div>
          ) : (
            <div className="space-y-3">
              {ultimosPartidos.map((partido, index) => {
                const miEquipo = partido.jugadores.find(j => j.id_usuario === usuario?.id_usuario)?.equipo;
                const equipoA = partido.jugadores.filter(j => j.equipo === 1);
                const equipoB = partido.jugadores.filter(j => j.equipo === 2);
                const setsA = partido.resultado?.sets_eq1 || 0;
                const setsB = partido.resultado?.sets_eq2 || 0;
                const esVictoria = partido.historial_rating ? partido.historial_rating.delta > 0 : 
                  (miEquipo === 1 ? setsA > setsB : setsB > setsA);
                const ganadorEquipo = setsA > setsB ? 1 : 2;

                return (
                  <motion.div
                    key={partido.id_partido}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ scale: 1.02, x: 5 }}
                    className={`bg-gradient-to-r ${esVictoria ? 'from-green-500/10' : 'from-red-500/10'} to-cardBg rounded-xl p-4 border ${esVictoria ? 'border-green-500/30' : 'border-red-500/30'} hover:border-primary/50 transition-all cursor-pointer group`}
                    onClick={() => navigate('/perfil')}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          partido.tipo === 'torneo' ? 'bg-accent/20 text-accent' : 'bg-primary/20 text-primary'
                        }`}>
                          {partido.tipo === 'torneo' ? 'TORNEO' : 'AMISTOSO'}
                        </span>
                        {partido.historial_rating && (
                          <span className={`text-sm font-bold ${esVictoria ? 'text-green-400' : 'text-red-400'}`}>
                            {partido.historial_rating.delta > 0 ? '+' : ''}{partido.historial_rating.delta}
                          </span>
                        )}
                      </div>
                      <p className="text-textSecondary text-xs bg-cardBorder px-2 py-1 rounded-full">
                        {new Date(partido.fecha).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })}
                      </p>
                    </div>
                    <div className="grid grid-cols-7 items-center text-sm gap-2">
                      {/* Equipo A - nombres */}
                      <div className="col-span-2 text-left">
                        <span className={`${ganadorEquipo === 1 ? 'text-green-400 font-black' : 'text-red-400'} truncate block`}>
                          {equipoA.map(j => j.nombre || j.apellido).join(' / ') || 'Equipo A'}
                        </span>
                      </div>
                      {/* Resultado centrado */}
                      <div className="col-span-3 flex items-center justify-center gap-2">
                        <span className={`${ganadorEquipo === 1 ? 'text-green-400' : 'text-red-400'} font-black text-2xl`}>
                          {setsA}
                        </span>
                        <span className="text-textSecondary font-bold text-lg">-</span>
                        <span className={`${ganadorEquipo === 2 ? 'text-green-400' : 'text-red-400'} font-black text-2xl`}>
                          {setsB}
                        </span>
                      </div>
                      {/* Equipo B - nombres */}
                      <div className="col-span-2 text-right">
                        <span className={`${ganadorEquipo === 2 ? 'text-green-400 font-black' : 'text-red-400'} truncate block`}>
                          {equipoB.map(j => j.nombre || j.apellido).join(' / ') || 'Equipo B'}
                        </span>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </Card>

        <Card gradient>
          <h2 className="text-2xl font-bold text-textPrimary mb-6 flex items-center gap-2">
            <Trophy className="text-accent" size={28} />
            Próximos Torneos
          </h2>
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12 text-textSecondary"
          >
            <div className="bg-accent/10 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
              <Trophy size={40} className="text-accent" />
            </div>
            <p className="mb-4 text-lg">No hay torneos programados</p>
            <Button variant="accent" onClick={() => navigate('/torneos')}>
              Crear primer torneo
            </Button>
          </motion.div>
        </Card>
      </div>

      {/* Gráficos de Estadísticas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de Actividad Semanal */}
        <Card gradient>
          <div className="flex items-center gap-2 mb-6">
            <TrendingUp className="text-primary" size={28} />
            <h2 className="text-2xl font-bold text-textPrimary">Actividad Semanal</h2>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={actividadSemanal}>
              <CartesianGrid strokeDasharray="3 3" stroke="#3A4558" />
              <XAxis dataKey="dia" stroke="#94A3B8" />
              <YAxis stroke="#94A3B8" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#242B3D', 
                  border: '1px solid #3A4558',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="partidos" 
                stroke="#0055FF" 
                strokeWidth={3}
                name="Partidos"
                dot={{ fill: '#0055FF', r: 5 }}
              />
              <Line 
                type="monotone" 
                dataKey="victorias" 
                stroke="#FF006E" 
                strokeWidth={3}
                name="Victorias"
                dot={{ fill: '#FF006E', r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Gráfico de Distribución de Resultados */}
        <Card gradient>
          <div className="flex items-center gap-2 mb-6">
            <Trophy className="text-secondary" size={28} />
            <h2 className="text-2xl font-bold text-textPrimary">Distribución de Resultados</h2>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={distribucionResultados}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${((percent || 0) * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {distribucionResultados.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#242B3D', 
                  border: '1px solid #3A4558',
                  borderRadius: '8px'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Gráfico de Rendimiento por Tipo */}
      <Card gradient>
        <div className="flex items-center gap-2 mb-6">
          <Target className="text-accent" size={28} />
          <h2 className="text-2xl font-bold text-textPrimary">Rendimiento por Tipo de Partido</h2>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={rendimientoPorTipo}>
            <CartesianGrid strokeDasharray="3 3" stroke="#3A4558" />
            <XAxis dataKey="tipo" stroke="#94A3B8" />
            <YAxis stroke="#94A3B8" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#242B3D', 
                border: '1px solid #3A4558',
                borderRadius: '8px'
              }}
            />
            <Legend />
            <Bar dataKey="partidos" fill="#0055FF" name="Partidos" radius={[8, 8, 0, 0]} />
            <Bar dataKey="victorias" fill="#FF006E" name="Victorias" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
}
