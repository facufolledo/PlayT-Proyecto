import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, User, Trophy, MapPin, ArrowRight, Users } from 'lucide-react';
import Input from '../components/Input';
import Button from '../components/Button';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { useDebounce } from '../hooks/useDebounce';
import { perfilService, PerfilPublico } from '../services/perfil.service';
import { clientLogger } from '../utils/clientLogger';

export default function BuscarJugadores() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [jugadores, setJugadores] = useState<PerfilPublico[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasSearched, setHasSearched] = useState(false);

  // Debounce para la búsqueda
  const debouncedSearchQuery = useDebounce(searchQuery, 300);

  useEffect(() => {
    if (debouncedSearchQuery.length >= 2) {
      buscarJugadores(debouncedSearchQuery);
    } else {
      setJugadores([]);
      setHasSearched(false);
    }
  }, [debouncedSearchQuery]);

  const buscarJugadores = async (query: string) => {
    try {
      setLoading(true);
      setError('');
      setHasSearched(true);
      
      clientLogger.userAction('Search players', { query });
      
      const resultados = await perfilService.buscarJugadores(query, 20);
      setJugadores(resultados);
      
    } catch (err: any) {
      setError(err.message || 'Error en la búsqueda');
      setJugadores([]);
    } finally {
      setLoading(false);
    }
  };

  const getCategoriaByRating = (rating: number): { nombre: string; color: string } => {
    if (rating >= 1800) return { nombre: 'Libre', color: 'from-purple-500 to-pink-500' };
    if (rating >= 1600) return { nombre: '4ta', color: 'from-orange-500 to-orange-600' };
    if (rating >= 1400) return { nombre: '5ta', color: 'from-yellow-500 to-yellow-600' };
    if (rating >= 1200) return { nombre: '6ta', color: 'from-green-500 to-green-600' };
    if (rating >= 1000) return { nombre: '7ma', color: 'from-blue-500 to-blue-600' };
    return { nombre: '8va', color: 'from-gray-500 to-gray-600' };
  };

  return (
    <div className="min-h-screen p-4 md:p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="h-1 w-12 bg-gradient-to-r from-primary to-secondary rounded-full" />
            <h1 className="text-3xl md:text-5xl font-black text-textPrimary">
              Buscar Jugadores
            </h1>
            <div className="h-1 w-12 bg-gradient-to-r from-secondary to-primary rounded-full" />
          </div>
          <p className="text-textSecondary text-sm md:text-base">
            Encuentra y explora los perfiles de otros jugadores de pádel
          </p>
        </motion.div>

        {/* Barra de búsqueda */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="relative mb-8"
        >
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-textSecondary" size={20} />
            <Input
              type="text"
              placeholder="Buscar por nombre, apellido o usuario..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-12 pr-4 py-4 text-lg bg-cardBg border-2 border-cardBorder focus:border-primary rounded-xl"
            />
          </div>
          {searchQuery.length > 0 && searchQuery.length < 2 && (
            <p className="text-textSecondary text-sm mt-2">
              Escribe al menos 2 caracteres para buscar
            </p>
          )}
        </motion.div>

        {/* Resultados */}
        <AnimatePresence mode="wait">
          {loading && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Array.from({ length: 6 }).map((_, i) => (
                  <LoadingSkeleton key={i} variant="card" />
                ))}
              </div>
            </motion.div>
          )}

          {error && (
            <motion.div
              key="error"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="text-center py-12"
            >
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-8">
                <User size={48} className="mx-auto mb-4 text-red-500 opacity-50" />
                <h3 className="text-lg font-bold text-red-500 mb-2">Error en la búsqueda</h3>
                <p className="text-textSecondary">{error}</p>
              </div>
            </motion.div>
          )}

          {hasSearched && !loading && !error && jugadores.length === 0 && (
            <motion.div
              key="no-results"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="text-center py-12"
            >
              <div className="bg-cardBorder/30 rounded-xl p-8">
                <Users size={48} className="mx-auto mb-4 text-textSecondary opacity-50" />
                <h3 className="text-lg font-bold text-textPrimary mb-2">No se encontraron jugadores</h3>
                <p className="text-textSecondary">
                  Intenta con otros términos de búsqueda
                </p>
              </div>
            </motion.div>
          )}

          {jugadores.length > 0 && (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="mb-4">
                <p className="text-textSecondary text-sm">
                  {jugadores.length} jugador{jugadores.length !== 1 ? 'es' : ''} encontrado{jugadores.length !== 1 ? 's' : ''}
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {jugadores.map((jugador, index) => {
                  const categoria = getCategoriaByRating(jugador.rating);
                  
                  return (
                    <motion.div
                      key={jugador.id_usuario}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      whileHover={{ scale: 1.02 }}
                      className="bg-cardBg rounded-xl p-4 border border-cardBorder hover:border-primary/50 transition-all cursor-pointer group"
                      onClick={() => navigate(`/jugador/${jugador.nombre_usuario}`)}
                    >
                      <div className="flex items-center gap-4">
                        {/* Avatar */}
                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xl font-black overflow-hidden flex-shrink-0">
                          {jugador.foto_perfil ? (
                            <img
                              src={jugador.foto_perfil}
                              alt={`${jugador.nombre} ${jugador.apellido}`}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <span>{jugador.nombre?.charAt(0)}{jugador.apellido?.charAt(0)}</span>
                          )}
                        </div>

                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="text-lg font-bold text-textPrimary truncate">
                              {jugador.nombre} {jugador.apellido}
                            </h3>
                            <ArrowRight 
                              size={16} 
                              className="text-textSecondary group-hover:text-primary transition-colors flex-shrink-0" 
                            />
                          </div>
                          
                          <p className="text-textSecondary text-sm mb-2 truncate">
                            @{jugador.nombre_usuario}
                          </p>

                          <div className="flex items-center gap-3 flex-wrap">
                            {/* Rating */}
                            <div className="flex items-center gap-1">
                              <Trophy size={14} className="text-primary" />
                              <span className="font-bold text-primary">{jugador.rating}</span>
                            </div>

                            {/* Categoría */}
                            <span className={`px-2 py-1 rounded-full text-white text-xs font-bold bg-gradient-to-r ${categoria.color}`}>
                              {categoria.nombre}
                            </span>

                            {/* Ubicación */}
                            {jugador.ciudad && (
                              <div className="flex items-center gap-1 text-textSecondary">
                                <MapPin size={12} />
                                <span className="text-xs truncate">{jugador.ciudad}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>

              {/* Mensaje si hay muchos resultados */}
              {jugadores.length >= 20 && (
                <div className="mt-6 text-center">
                  <p className="text-textSecondary text-sm">
                    Mostrando los primeros 20 resultados. Refina tu búsqueda para encontrar jugadores específicos.
                  </p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Sugerencias cuando no hay búsqueda */}
        {!hasSearched && searchQuery.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-center py-12"
          >
            <div className="bg-gradient-to-br from-primary/10 to-secondary/10 rounded-xl p-8 border border-primary/20">
              <Search size={48} className="mx-auto mb-4 text-primary opacity-50" />
              <h3 className="text-lg font-bold text-textPrimary mb-2">¿Buscas a alguien?</h3>
              <p className="text-textSecondary mb-4">
                Encuentra jugadores por nombre, apellido o nombre de usuario
              </p>
              <div className="flex flex-wrap justify-center gap-2 text-sm">
                <span className="px-3 py-1 bg-cardBorder/50 rounded-full text-textSecondary">
                  Ejemplo: "Juan"
                </span>
                <span className="px-3 py-1 bg-cardBorder/50 rounded-full text-textSecondary">
                  Ejemplo: "García"
                </span>
                <span className="px-3 py-1 bg-cardBorder/50 rounded-full text-textSecondary">
                  Ejemplo: "@juanp"
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
