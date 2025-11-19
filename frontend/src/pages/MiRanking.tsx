import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Trophy, Target, Calendar, Award } from 'lucide-react';
import Card from '../components/Card';
import RatingProgressBar from '../components/RatingProgressBar';
import { useAuth } from '../context/AuthContext';

export default function MiRanking() {
  const { usuario } = useAuth();

  // Datos de ejemplo - reemplazar con datos reales del backend
  const stats = {
    ratingActual: 1250,
    posicionGeneral: 42,
    posicionCategoria: 8,
    partidosJugados: 28,
    partidosGanados: 18,
    partidosPerdidos: 10,
    rachaActual: 3,
    mejorRacha: 7,
    cambioSemanal: +45,
    cambioMensual: +120
  };

  const historialReciente = [
    { fecha: '2025-11-18', rival: 'Juan Pérez', resultado: 'Victoria', cambio: +15, rating: 1250 },
    { fecha: '2025-11-17', rival: 'María García', resultado: 'Victoria', cambio: +18, rating: 1235 },
    { fecha: '2025-11-16', rival: 'Carlos López', resultado: 'Victoria', cambio: +12, rating: 1217 },
    { fecha: '2025-11-15', rival: 'Ana Martínez', resultado: 'Derrota', cambio: -20, rating: 1205 },
    { fecha: '2025-11-14', rival: 'Pedro Sánchez', resultado: 'Victoria', cambio: +16, rating: 1225 },
  ];

  const winRate = ((stats.partidosGanados / stats.partidosJugados) * 100).toFixed(1);

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
      >
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="h-1 w-12 bg-gradient-to-r from-primary to-secondary rounded-full" />
            <h1 className="text-5xl font-black text-textPrimary tracking-tight">
              Mi Ranking
            </h1>
          </div>
          <p className="text-textSecondary text-base ml-15">
            Tu progreso y estadísticas
          </p>
        </div>
      </motion.div>

      {/* Rating Principal */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="bg-gradient-to-br from-primary/10 to-secondary/10 border-primary/30">
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <p className="text-textSecondary text-sm mb-1">Rating Actual</p>
                <div className="flex items-baseline gap-3">
                  <h2 className="text-6xl font-black text-primary">{stats.ratingActual}</h2>
                  <div className="flex items-center gap-1">
                    {stats.cambioSemanal > 0 ? (
                      <TrendingUp size={20} className="text-secondary" />
                    ) : (
                      <TrendingDown size={20} className="text-red-500" />
                    )}
                    <span className={`text-lg font-bold ${stats.cambioSemanal > 0 ? 'text-secondary' : 'text-red-500'}`}>
                      {stats.cambioSemanal > 0 ? '+' : ''}{stats.cambioSemanal}
                    </span>
                    <span className="text-textSecondary text-sm">esta semana</span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <p className="text-textSecondary text-sm mb-1">Cambio Mensual</p>
                <p className={`text-2xl font-bold ${stats.cambioMensual > 0 ? 'text-secondary' : 'text-red-500'}`}>
                  {stats.cambioMensual > 0 ? '+' : ''}{stats.cambioMensual}
                </p>
              </div>
            </div>

            <RatingProgressBar
              currentRating={stats.ratingActual}
              size="lg"
            />
          </div>
        </Card>
      </motion.div>

      {/* Posiciones */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <div className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                  <Trophy size={24} className="text-primary" />
                </div>
                <div>
                  <p className="text-textSecondary text-sm">Posición General</p>
                  <p className="text-3xl font-black text-primary">#{stats.posicionGeneral}</p>
                </div>
              </div>
              <p className="text-textSecondary text-sm">
                De todos los jugadores registrados
              </p>
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <div className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center">
                  <Award size={24} className="text-secondary" />
                </div>
                <div>
                  <p className="text-textSecondary text-sm">Posición en Categoría</p>
                  <p className="text-3xl font-black text-secondary">#{stats.posicionCategoria}</p>
                </div>
              </div>
              <p className="text-textSecondary text-sm">
                En tu categoría (Oro)
              </p>
            </div>
          </Card>
        </motion.div>
      </div>

      {/* Estadísticas */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card>
          <div className="p-6">
            <h3 className="text-xl font-bold text-textPrimary mb-6">Estadísticas</h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <p className="text-4xl font-black text-primary mb-2">{stats.partidosJugados}</p>
                <p className="text-textSecondary text-sm">Partidos Jugados</p>
              </div>
              
              <div className="text-center">
                <p className="text-4xl font-black text-secondary mb-2">{winRate}%</p>
                <p className="text-textSecondary text-sm">Win Rate</p>
              </div>
              
              <div className="text-center">
                <p className="text-4xl font-black text-accent mb-2">{stats.rachaActual}</p>
                <p className="text-textSecondary text-sm">Racha Actual</p>
              </div>
              
              <div className="text-center">
                <p className="text-4xl font-black text-textPrimary mb-2">{stats.mejorRacha}</p>
                <p className="text-textSecondary text-sm">Mejor Racha</p>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-cardBorder">
              <div className="flex justify-around">
                <div className="text-center">
                  <p className="text-2xl font-bold text-secondary mb-1">{stats.partidosGanados}</p>
                  <p className="text-textSecondary text-xs">Victorias</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-500 mb-1">{stats.partidosPerdidos}</p>
                  <p className="text-textSecondary text-xs">Derrotas</p>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Historial Reciente */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card>
          <div className="p-6">
            <div className="flex items-center gap-2 mb-6">
              <Calendar size={24} className="text-primary" />
              <h3 className="text-xl font-bold text-textPrimary">Historial Reciente</h3>
            </div>

            <div className="space-y-3">
              {historialReciente.map((partido, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + index * 0.1 }}
                  className="flex items-center justify-between p-4 bg-background rounded-xl border border-cardBorder hover:border-primary/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-2 h-2 rounded-full ${
                      partido.resultado === 'Victoria' ? 'bg-secondary' : 'bg-red-500'
                    }`} />
                    <div>
                      <p className="text-textPrimary font-semibold">{partido.rival}</p>
                      <p className="text-textSecondary text-sm">
                        {new Date(partido.fecha).toLocaleDateString('es-ES', {
                          day: 'numeric',
                          month: 'short'
                        })}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                      partido.resultado === 'Victoria'
                        ? 'bg-secondary/20 text-secondary'
                        : 'bg-red-500/20 text-red-500'
                    }`}>
                      {partido.resultado}
                    </span>
                    
                    <div className="text-right">
                      <p className={`text-lg font-bold ${
                        partido.cambio > 0 ? 'text-secondary' : 'text-red-500'
                      }`}>
                        {partido.cambio > 0 ? '+' : ''}{partido.cambio}
                      </p>
                      <p className="text-textSecondary text-xs">{partido.rating}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Próximo Objetivo */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
      >
        <Card className="bg-gradient-to-br from-accent/10 to-accent/5 border-accent/30">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <Target size={28} className="text-accent" />
              <h3 className="text-xl font-bold text-textPrimary">Próximo Objetivo</h3>
            </div>
            
            <p className="text-textSecondary mb-4">
              Alcanza <span className="text-accent font-bold">1300 puntos</span> para subir a <span className="text-accent font-bold">Platino</span>
            </p>
            
            <RatingProgressBar
              currentRating={stats.ratingActual}
              minRating={1100}
              maxRating={1300}
              categoria="Oro → Platino"
              size="md"
            />
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
