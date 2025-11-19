import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Trophy, TrendingUp, Target, Award, Medal } from 'lucide-react';
import Card from '../components/Card';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import { logger } from '../utils/logger';

// Categorías según la documentación
const CATEGORIAS = [
  { nombre: '8va', descripcion: 'Principiante / Princ. avanzado', ratingMin: 0, ratingMax: 899, color: 'from-gray-500 to-gray-600' },
  { nombre: '7ma', descripcion: 'Golpes más sólidos', ratingMin: 900, ratingMax: 1049, color: 'from-blue-500 to-blue-600' },
  { nombre: '6ta', descripcion: 'Mejor dominio y estrategia', ratingMin: 1050, ratingMax: 1199, color: 'from-green-500 to-green-600' },
  { nombre: '5ta', descripcion: 'Buenos jugadores, constancia', ratingMin: 1200, ratingMax: 1349, color: 'from-yellow-500 to-yellow-600' },
  { nombre: '4ta', descripcion: 'Muy buenos, técnica + estrategia', ratingMin: 1350, ratingMax: 1499, color: 'from-orange-500 to-orange-600' },
  { nombre: 'Libre', descripcion: 'Élite local (top provincia)', ratingMin: 1500, ratingMax: 9999, color: 'from-purple-500 to-pink-500' },
];

function getCategoriaInfo(rating: number) {
  return CATEGORIAS.find(cat => rating >= cat.ratingMin && rating <= cat.ratingMax) || CATEGORIAS[0];
}

export default function MiRanking() {
  const { usuario } = useAuth();
  const [ranking, setRanking] = useState<any[]>([]);
  const [miPosicion, setMiPosicion] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const cargarRanking = async () => {
      if (!usuario) return;

      try {
        setIsLoading(true);
        const sexo = usuario.sexo === 'M' ? 'M' : 'F';
        const rankingData = await apiService.getRankingGeneral(sexo);
        setRanking(rankingData);

        // Encontrar mi posición
        const posicion = rankingData.findIndex(
          (j: any) => j.id_usuario === usuario.id_usuario
        );
        setMiPosicion(posicion !== -1 ? posicion + 1 : null);
      } catch (error) {
        logger.error('Error al cargar ranking:', error);
      } finally {
        setIsLoading(false);
      }
    };

    cargarRanking();
  }, [usuario]);

  if (!usuario) return null;

  const categoriaInfo = getCategoriaInfo(usuario.rating);
  const proximaCategoria = CATEGORIAS.find(cat => cat.ratingMin > usuario.rating);
  const puntosParaProxima = proximaCategoria ? proximaCategoria.ratingMin - usuario.rating : 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="h-1 w-12 bg-gradient-to-r from-primary to-secondary rounded-full" />
          <h1 className="text-5xl font-black text-textPrimary tracking-tight">
            Mi Ranking
          </h1>
        </div>
        <p className="text-textSecondary text-base ml-15">
          Tu posición y progreso en el ranking
        </p>
      </motion.div>

      {/* Estadísticas Principales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card gradient>
          <div className="text-center">
            <Trophy className="text-accent mx-auto mb-3" size={40} />
            <p className="text-4xl font-black text-textPrimary mb-1">
              {miPosicion ? `#${miPosicion}` : '-'}
            </p>
            <p className="text-textSecondary text-sm">Posición General</p>
          </div>
        </Card>

        <Card gradient>
          <div className="text-center">
            <Target className="text-primary mx-auto mb-3" size={40} />
            <p className="text-4xl font-black text-primary mb-1">{usuario.rating}</p>
            <p className="text-textSecondary text-sm">Rating Actual</p>
          </div>
        </Card>

        <Card gradient>
          <div className="text-center">
            <Award className="text-secondary mx-auto mb-3" size={40} />
            <p className="text-4xl font-black text-textPrimary mb-1">
              {usuario.partidos_jugados}
            </p>
            <p className="text-textSecondary text-sm">Partidos Jugados</p>
          </div>
        </Card>

        <Card gradient>
          <div className="text-center">
            <Medal className="text-purple-400 mx-auto mb-3" size={40} />
            <p className={`text-4xl font-black mb-1 bg-gradient-to-r ${categoriaInfo.color} bg-clip-text text-transparent`}>
              {categoriaInfo.nombre}
            </p>
            <p className="text-textSecondary text-sm">Categoría</p>
          </div>
        </Card>
      </div>

      {/* Información de Categoría */}
      <Card>
        <h2 className="text-2xl font-bold text-textPrimary mb-4">Tu Categoría</h2>
        <div className={`bg-gradient-to-r ${categoriaInfo.color} rounded-xl p-6 text-white mb-4`}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-3xl font-black mb-2">{categoriaInfo.nombre}</h3>
              <p className="text-white/90">{categoriaInfo.descripcion}</p>
              <p className="text-white/80 text-sm mt-2">
                Rango: {categoriaInfo.ratingMin} - {categoriaInfo.ratingMax === 9999 ? '∞' : categoriaInfo.ratingMax}
              </p>
            </div>
            <Trophy size={64} className="text-white/30" />
          </div>
        </div>

        {proximaCategoria && (
          <div className="bg-background rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <p className="text-textSecondary text-sm">Próxima categoría: <span className="text-textPrimary font-bold">{proximaCategoria.nombre}</span></p>
              <p className="text-primary font-bold">{puntosParaProxima} puntos</p>
            </div>
            <div className="w-full bg-cardBorder rounded-full h-3 overflow-hidden">
              <div
                className={`h-full bg-gradient-to-r ${proximaCategoria.color} transition-all duration-500`}
                style={{
                  width: `${Math.max(0, Math.min(100, ((categoriaInfo.ratingMax - categoriaInfo.ratingMin - puntosParaProxima) / (categoriaInfo.ratingMax - categoriaInfo.ratingMin)) * 100))}%`
                }}
              />
            </div>
          </div>
        )}
      </Card>

      {/* Jugadores Cercanos */}
      <Card>
        <h2 className="text-2xl font-bold text-textPrimary mb-6 flex items-center gap-2">
          <TrendingUp className="text-primary" size={28} />
          Jugadores Cercanos en el Ranking
        </h2>

        {isLoading ? (
          <p className="text-center text-textSecondary py-8">Cargando...</p>
        ) : (
          <div className="space-y-2">
            {ranking
              .slice(Math.max(0, (miPosicion || 1) - 3), (miPosicion || 1) + 2)
              .map((jugador, index) => {
                const posicion = Math.max(0, (miPosicion || 1) - 3) + index + 1;
                const esUsuarioActual = jugador.id_usuario === usuario.id_usuario;
                const nombreCompleto = `${jugador.nombre} ${jugador.apellido}`;

                return (
                  <motion.div
                    key={jugador.id_usuario}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`flex items-center justify-between p-4 rounded-xl ${
                      esUsuarioActual
                        ? 'bg-primary/10 border-2 border-primary'
                        : 'bg-background'
                    }`}
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center font-black ${
                        posicion === 1 ? 'bg-gradient-to-br from-yellow-400 to-yellow-600 text-white' :
                        posicion === 2 ? 'bg-gradient-to-br from-gray-300 to-gray-500 text-white' :
                        posicion === 3 ? 'bg-gradient-to-br from-orange-400 to-orange-600 text-white' :
                        'bg-cardBorder text-textSecondary'
                      }`}>
                        #{posicion}
                      </div>
                      <div>
                        <p className={`font-bold ${esUsuarioActual ? 'text-primary' : 'text-textPrimary'}`}>
                          {nombreCompleto} {esUsuarioActual && '(Tú)'}
                        </p>
                        <p className="text-textSecondary text-sm">@{jugador.nombre_usuario}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-black text-primary">{jugador.rating}</p>
                      <p className="text-textSecondary text-xs">{jugador.partidos_jugados} partidos</p>
                    </div>
                  </motion.div>
                );
              })}
          </div>
        )}
      </Card>
    </div>
  );
}
