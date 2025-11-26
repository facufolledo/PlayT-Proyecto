import { motion, useReducedMotion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import { Trophy, Users, Calendar, Zap, Target, TrendingUp } from 'lucide-react';
import { useSalas } from '../context/SalasContext';
import { useTorneos } from '../context/TorneosContext';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const { salas } = useSalas();
  const { torneos } = useTorneos();
  const navigate = useNavigate();
  const shouldReduceMotion = useReducedMotion();

  const partidosJugados = salas.filter(s => s.estado === 'finalizada').length;
  const proximosPartidos = salas.filter(s => s.estado === 'programada').length;
  const partidosActivos = salas.filter(s => s.estado === 'activa').length;
  const torneosActivos = torneos.filter(t => t.estado === 'activo').length;

  const ultimosPartidos = salas
    .filter(s => s.estado === 'finalizada')
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 5);

  // Datos para gráficos
  const actividadSemanal = [
    { dia: 'Lun', partidos: 3, victorias: 2 },
    { dia: 'Mar', partidos: 5, victorias: 3 },
    { dia: 'Mié', partidos: 2, victorias: 1 },
    { dia: 'Jue', partidos: 4, victorias: 3 },
    { dia: 'Vie', partidos: 6, victorias: 4 },
    { dia: 'Sáb', partidos: 8, victorias: 5 },
    { dia: 'Dom', partidos: 4, victorias: 2 },
  ];

  const rendimientoPorCategoria = [
    { categoria: '8va', partidos: 5, victorias: 3 },
    { categoria: '7ma', partidos: 8, victorias: 5 },
    { categoria: '6ta', partidos: 12, victorias: 8 },
    { categoria: '5ta', partidos: 6, victorias: 4 },
  ];

  const distribucionResultados = [
    { name: 'Victorias', value: partidosJugados > 0 ? Math.floor(partidosJugados * 0.6) : 0, color: '#FF006E' },
    { name: 'Derrotas', value: partidosJugados > 0 ? Math.floor(partidosJugados * 0.4) : 0, color: '#94A3B8' },
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
              {ultimosPartidos.map((sala, index) => (
                <motion.div
                  key={sala.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.02, x: 5 }}
                  className="bg-gradient-to-r from-background to-cardBg rounded-xl p-4 border border-cardBorder hover:border-primary/50 transition-all cursor-pointer group"
                  onClick={() => navigate('/salas')}
                >
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-textPrimary font-bold group-hover:text-primary transition-colors">{sala.nombre}</p>
                    <p className="text-textSecondary text-xs bg-cardBorder px-2 py-1 rounded-full">
                      {new Date(sala.fecha).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })}
                    </p>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2 flex-1">
                      <span className={`${sala.ganador === 'equipoA' ? 'text-primary font-black' : 'text-textSecondary'} truncate`}>
                        {sala.equipoA.jugador1.nombre} / {sala.equipoA.jugador2.nombre}
                      </span>
                      <span className={`${sala.ganador === 'equipoA' ? 'text-primary' : 'text-textPrimary'} font-bold text-lg`}>
                        {sala.equipoA.puntos}
                      </span>
                    </div>
                    <span className="text-textSecondary mx-3 font-bold">VS</span>
                    <div className="flex items-center gap-2 flex-1 justify-end">
                      <span className={`${sala.ganador === 'equipoB' ? 'text-secondary' : 'text-textPrimary'} font-bold text-lg`}>
                        {sala.equipoB.puntos}
                      </span>
                      <span className={`${sala.ganador === 'equipoB' ? 'text-secondary font-black' : 'text-textSecondary'} truncate text-right`}>
                        {sala.equipoB.jugador1.nombre} / {sala.equipoB.jugador2.nombre}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
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

      {/* Gráfico de Rendimiento por Categoría */}
      <Card gradient>
        <div className="flex items-center gap-2 mb-6">
          <Target className="text-accent" size={28} />
          <h2 className="text-2xl font-bold text-textPrimary">Rendimiento por Categoría</h2>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={rendimientoPorCategoria}>
            <CartesianGrid strokeDasharray="3 3" stroke="#3A4558" />
            <XAxis dataKey="categoria" stroke="#94A3B8" />
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
