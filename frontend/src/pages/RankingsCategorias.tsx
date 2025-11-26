import { useState } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Medal, Award, TrendingUp, Users } from 'lucide-react';
import Card from '../components/Card';
import RatingProgressBar from '../components/RatingProgressBar';

type Categoria = '8va' | '7ma' | '6ta' | '5ta' | '4ta' | 'Libre';
type Genero = 'masculino' | 'femenino' | 'mixto';

interface Jugador {
  posicion: number;
  nombre: string;
  rating: number;
  partidosJugados: number;
  partidosGanados: number;
  winRate: number;
  cambioSemanal: number;
}

export default function RankingsCategorias() {
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState<Categoria>('6ta');
  const [generoSeleccionado, setGeneroSeleccionado] = useState<Genero>('masculino');
  const [mostrarTodos, setMostrarTodos] = useState(false);
  const LIMITE_INICIAL = 20; // Solo cargar 20 jugadores inicialmente

  // Datos de ejemplo - reemplazar con datos reales del backend
  const jugadoresPorCategoria: Record<Categoria, Jugador[]> = {
    '8va': [
      { posicion: 1, nombre: 'Carlos Ruiz', rating: 895, partidosJugados: 15, partidosGanados: 12, winRate: 80, cambioSemanal: +25 },
      { posicion: 2, nombre: 'Ana Torres', rating: 880, partidosJugados: 18, partidosGanados: 13, winRate: 72, cambioSemanal: +18 },
      { posicion: 3, nombre: 'Luis Gómez', rating: 865, partidosJugados: 20, partidosGanados: 14, winRate: 70, cambioSemanal: +12 },
    ],
    '7ma': [
      { posicion: 1, nombre: 'María López', rating: 1095, partidosJugados: 25, partidosGanados: 18, winRate: 72, cambioSemanal: +30 },
      { posicion: 2, nombre: 'Pedro Sánchez', rating: 1080, partidosJugados: 22, partidosGanados: 16, winRate: 73, cambioSemanal: +22 },
      { posicion: 3, nombre: 'Laura Martín', rating: 1065, partidosJugados: 28, partidosGanados: 19, winRate: 68, cambioSemanal: +15 },
    ],
    '6ta': [
      { posicion: 1, nombre: 'Juan Pérez', rating: 1295, partidosJugados: 35, partidosGanados: 26, winRate: 74, cambioSemanal: +35 },
      { posicion: 2, nombre: 'Carmen García', rating: 1280, partidosJugados: 32, partidosGanados: 24, winRate: 75, cambioSemanal: +28 },
      { posicion: 3, nombre: 'Diego Fernández', rating: 1265, partidosJugados: 30, partidosGanados: 22, winRate: 73, cambioSemanal: +20 },
    ],
    '5ta': [
      { posicion: 1, nombre: 'Roberto Silva', rating: 1495, partidosJugados: 45, partidosGanados: 35, winRate: 78, cambioSemanal: +40 },
      { posicion: 2, nombre: 'Elena Rodríguez', rating: 1480, partidosJugados: 42, partidosGanados: 33, winRate: 79, cambioSemanal: +35 },
      { posicion: 3, nombre: 'Miguel Ángel', rating: 1465, partidosJugados: 40, partidosGanados: 31, winRate: 78, cambioSemanal: +30 },
    ],
    '4ta': [
      { posicion: 1, nombre: 'Alejandro Pro', rating: 1695, partidosJugados: 60, partidosGanados: 50, winRate: 83, cambioSemanal: +45 },
      { posicion: 2, nombre: 'Sofía Elite', rating: 1680, partidosJugados: 58, partidosGanados: 48, winRate: 83, cambioSemanal: +42 },
      { posicion: 3, nombre: 'Fernando Master', rating: 1665, partidosJugados: 55, partidosGanados: 45, winRate: 82, cambioSemanal: +38 },
    ],
    'Libre': [
      { posicion: 1, nombre: 'Martín Campeón', rating: 1895, partidosJugados: 80, partidosGanados: 70, winRate: 88, cambioSemanal: +50 },
      { posicion: 2, nombre: 'Lucía Estrella', rating: 1880, partidosJugados: 75, partidosGanados: 65, winRate: 87, cambioSemanal: +48 },
      { posicion: 3, nombre: 'Gabriel Maestro', rating: 1865, partidosJugados: 72, partidosGanados: 62, winRate: 86, cambioSemanal: +45 },
    ],
  };

  const categorias: { id: Categoria; nombre: string; rango: string; color: string; bgColor: string; textColor: string; icon: any }[] = [
    { 
      id: '8va', 
      nombre: '8va', 
      rango: 'Principiante', 
      color: 'from-amber-700/40 to-orange-800/40',
      bgColor: 'bg-amber-900/20',
      textColor: 'text-amber-700',
      icon: Medal 
    },
    { 
      id: '7ma', 
      nombre: '7ma', 
      rango: 'Intermedio Bajo', 
      color: 'from-slate-400/40 to-slate-600/40',
      bgColor: 'bg-slate-500/20',
      textColor: 'text-slate-400',
      icon: Medal 
    },
    { 
      id: '6ta', 
      nombre: '6ta', 
      rango: 'Intermedio', 
      color: 'from-yellow-600/40 to-amber-600/40',
      bgColor: 'bg-yellow-700/20',
      textColor: 'text-yellow-600',
      icon: Trophy 
    },
    { 
      id: '5ta', 
      nombre: '5ta', 
      rango: 'Intermedio Alto', 
      color: 'from-cyan-400/40 to-teal-500/40',
      bgColor: 'bg-cyan-500/20',
      textColor: 'text-cyan-400',
      icon: Award 
    },
    { 
      id: '4ta', 
      nombre: '4ta', 
      rango: 'Avanzado', 
      color: 'from-blue-400/40 to-indigo-500/40',
      bgColor: 'bg-blue-500/20',
      textColor: 'text-blue-400',
      icon: Trophy 
    },
    { 
      id: 'Libre', 
      nombre: 'Libre', 
      rango: 'Profesional', 
      color: 'from-purple-400/40 to-pink-500/40',
      bgColor: 'bg-purple-500/20',
      textColor: 'text-purple-400',
      icon: Trophy 
    },
  ];

  const jugadoresTodos = jugadoresPorCategoria[categoriaSeleccionada];
  const jugadores = mostrarTodos ? jugadoresTodos : jugadoresTodos.slice(0, LIMITE_INICIAL);
  const categoriaActual = categorias.find(c => c.id === categoriaSeleccionada)!;
  const hayMasJugadores = jugadoresTodos.length > LIMITE_INICIAL;

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 md:gap-4"
      >
        <div>
          <div className="flex items-center gap-2 md:gap-3 mb-1 md:mb-2">
            <div className="h-0.5 md:h-1 w-8 md:w-12 bg-gradient-to-r from-primary to-secondary rounded-full" />
            <h1 className="text-2xl md:text-5xl font-black text-textPrimary tracking-tight">
              Rankings por Categoría
            </h1>
          </div>
          <p className="text-textSecondary text-xs md:text-base ml-10 md:ml-15">
            Mejores jugadores de cada categoría
          </p>
        </div>
      </motion.div>

      {/* Filtro de Género */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex gap-2 md:gap-3"
      >
        {(['masculino', 'femenino', 'mixto'] as Genero[]).map((genero) => (
          <button
            key={genero}
            onClick={() => setGeneroSeleccionado(genero)}
            className={`px-4 md:px-6 py-2 md:py-3 rounded-lg md:rounded-xl text-sm md:text-base font-bold transition-all active:scale-95 ${
              generoSeleccionado === genero
                ? 'bg-primary text-white'
                : 'bg-cardBg text-textSecondary hover:bg-cardBorder'
            }`}
          >
            {genero.charAt(0).toUpperCase() + genero.slice(1)}
          </button>
        ))}
      </motion.div>

      {/* Tabs de Categorías */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-3 md:flex md:flex-wrap gap-2 md:gap-3"
      >
        {categorias.map((categoria, index) => {
          const Icon = categoria.icon;
          return (
            <button
              key={categoria.id}
              onClick={() => setCategoriaSeleccionada(categoria.id)}
              className={`flex flex-col md:flex-row items-center justify-center gap-1 md:gap-3 px-2 md:px-6 py-2 md:py-4 rounded-lg md:rounded-xl text-sm md:text-base font-bold transition-all active:scale-95 ${
                categoriaSeleccionada === categoria.id
                  ? `${categoria.bgColor} ${categoria.textColor} border-2 ${categoria.textColor.replace('text-', 'border-')}`
                  : 'bg-cardBg text-textSecondary hover:bg-cardBorder border-2 border-transparent'
              }`}
            >
              <Icon size={16} className="md:w-5 md:h-5 flex-shrink-0" />
              <div className="text-center md:text-left">
                <p className="text-xs md:text-sm font-bold">{categoria.nombre}</p>
                <p className="text-[9px] md:text-xs opacity-80 hidden md:block">{categoria.rango}</p>
              </div>
            </button>
          );
        })}
      </motion.div>

      {/* Estadísticas de la Categoría */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card className={categoriaActual.bgColor}>
          <div className="p-3 md:p-6">
            <div className="flex items-center gap-2 md:gap-4 mb-2 md:mb-4">
              <div className={`w-10 h-10 md:w-16 md:h-16 rounded-full ${categoriaActual.bgColor} border-2 ${categoriaActual.textColor.replace('text-', 'border-')} flex items-center justify-center flex-shrink-0`}>
                <categoriaActual.icon size={20} className={`${categoriaActual.textColor} md:w-8 md:h-8`} />
              </div>
              <div className="min-w-0">
                <h2 className="text-lg md:text-3xl font-black text-textPrimary">{categoriaActual.nombre}</h2>
                <p className="text-textSecondary text-[10px] md:text-base truncate">Rango: {categoriaActual.rango}</p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 md:gap-6 mt-2 md:mt-6">
              <div className="text-center">
                <p className="text-xl md:text-3xl font-black text-primary">{jugadoresTodos.length}</p>
                <p className="text-textSecondary text-[9px] md:text-sm">Jugadores</p>
              </div>
              <div className="text-center">
                <p className="text-xl md:text-3xl font-black text-secondary">{jugadoresTodos[0]?.rating || 0}</p>
                <p className="text-textSecondary text-[9px] md:text-sm">Rating Máx</p>
              </div>
              <div className="text-center">
                <p className="text-xl md:text-3xl font-black text-accent">{jugadoresTodos.length > 0 ? Math.round(jugadoresTodos.reduce((acc, j) => acc + j.winRate, 0) / jugadoresTodos.length) : 0}%</p>
                <p className="text-textSecondary text-[9px] md:text-sm">Win Rate</p>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Top 3 Destacado */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-6">
        {jugadores.slice(0, 3).map((jugador, index) => (
          <motion.div
            key={jugador.posicion}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 + index * 0.1 }}
          >
            <Card className={index === 0 ? `border-2 ${categoriaActual.textColor.replace('text-', 'border-')}` : ''}>
              <div className="p-3 md:p-6 text-center">
                <div className="relative inline-block mb-2 md:mb-4">
                  <div className={`w-14 h-14 md:w-20 md:h-20 rounded-full ${categoriaActual.bgColor} border-2 ${categoriaActual.textColor.replace('text-', 'border-')} flex items-center justify-center ${categoriaActual.textColor} text-xl md:text-3xl font-black`}>
                    {jugador.posicion}
                  </div>
                  {index === 0 && (
                    <div className={`absolute -top-1 -right-1 md:-top-2 md:-right-2 w-5 h-5 md:w-8 md:h-8 ${categoriaActual.bgColor} border-2 ${categoriaActual.textColor.replace('text-', 'border-')} rounded-full flex items-center justify-center`}>
                      <Trophy size={10} className={`${categoriaActual.textColor} md:w-4 md:h-4`} />
                    </div>
                  )}
                </div>

                <h3 className="text-sm md:text-xl font-bold text-textPrimary mb-1 md:mb-2 truncate px-1">{jugador.nombre}</h3>
                
                <div className="mb-2 md:mb-4">
                  <p className="text-2xl md:text-4xl font-black text-primary mb-0.5 md:mb-1">{jugador.rating}</p>
                  <div className="flex items-center justify-center gap-1">
                    <TrendingUp size={12} className="text-secondary md:w-4 md:h-4" />
                    <span className="text-secondary font-bold text-xs md:text-base">+{jugador.cambioSemanal}</span>
                  </div>
                </div>

                <div className="px-2">
                  <RatingProgressBar
                    currentRating={jugador.rating}
                    size="sm"
                    showLabel={false}
                  />
                </div>

                <div className="grid grid-cols-2 gap-2 md:gap-4 mt-2 md:mt-4 pt-2 md:pt-4 border-t border-cardBorder">
                  <div>
                    <p className="text-lg md:text-2xl font-bold text-textPrimary">{jugador.winRate}%</p>
                    <p className="text-[9px] md:text-xs text-textSecondary">Win Rate</p>
                  </div>
                  <div>
                    <p className="text-lg md:text-2xl font-bold text-textPrimary">{jugador.partidosJugados}</p>
                    <p className="text-[9px] md:text-xs text-textSecondary">Partidos</p>
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Resto del Ranking */}
      {jugadores.length > 3 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <Card>
            <div className="p-3 md:p-6">
              <h3 className="text-sm md:text-xl font-bold text-textPrimary mb-3 md:mb-6 flex items-center gap-2">
                <Users size={16} className="md:w-6 md:h-6" />
                Resto del Ranking
              </h3>

              <div className="space-y-2 md:space-y-3">
                {jugadores.slice(3).map((jugador, index) => (
                  <motion.div
                    key={jugador.posicion}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.9 + index * 0.02 }}
                    className="flex items-center justify-between p-2 md:p-4 bg-background rounded-lg md:rounded-xl border border-cardBorder hover:border-primary/50 transition-colors active:scale-[0.98]"
                  >
                    <div className="flex items-center gap-2 md:gap-4 flex-1 min-w-0">
                      <div className="w-8 h-8 md:w-12 md:h-12 rounded-full bg-cardBorder flex items-center justify-center text-textPrimary font-bold text-xs md:text-base flex-shrink-0">
                        {jugador.posicion}
                      </div>
                      <div className="min-w-0">
                        <p className="text-textPrimary font-semibold text-xs md:text-base truncate">{jugador.nombre}</p>
                        <p className="text-textSecondary text-[9px] md:text-sm">{jugador.partidosJugados} partidos</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 md:gap-6 flex-shrink-0">
                      <div className="text-right">
                        <p className="text-lg md:text-2xl font-bold text-primary">{jugador.rating}</p>
                        <p className="text-secondary text-[9px] md:text-sm font-bold">+{jugador.cambioSemanal}</p>
                      </div>
                      <div className="text-right hidden md:block">
                        <p className="text-lg font-bold text-textPrimary">{jugador.winRate}%</p>
                        <p className="text-textSecondary text-xs">Win Rate</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Botón Cargar Más */}
              {!mostrarTodos && hayMasJugadores && (
                <div className="mt-6 text-center">
                  <button
                    onClick={() => setMostrarTodos(true)}
                    className="w-full py-3 bg-cardBorder hover:bg-primary/20 text-textPrimary font-bold rounded-lg transition-colors"
                  >
                    Cargar más jugadores ({jugadoresTodos.length - LIMITE_INICIAL} restantes)
                  </button>
                </div>
              )}

              {mostrarTodos && hayMasJugadores && (
                <div className="mt-6 text-center">
                  <button
                    onClick={() => {
                      setMostrarTodos(false);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    className="w-full py-3 bg-cardBorder hover:bg-primary/20 text-textPrimary font-bold rounded-lg transition-colors"
                  >
                    Mostrar menos
                  </button>
                </div>
              )}
            </div>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
