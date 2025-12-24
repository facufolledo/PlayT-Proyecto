import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface UsuarioBusqueda {
  id_usuario: number;
  nombre_usuario: string;
  nombre: string;
  apellido: string;
  nombre_completo: string;
  rating: number;
  partidos_jugados: number;
  categoria: string | null;
  ciudad: string | null;
  foto_perfil: string | null;
}

interface BuscadorUsuariosProps {
  placeholder?: string;
  className?: string;
  onSelect?: (usuario: UsuarioBusqueda) => void;
  autoFocus?: boolean;
}

export default function BuscadorUsuarios({
  placeholder = 'Buscar jugadores...',
  className = '',
  onSelect,
  autoFocus = false
}: BuscadorUsuariosProps) {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [resultados, setResultados] = useState<UsuarioBusqueda[]>([]);
  const [loading, setLoading] = useState(false);
  const [mostrarResultados, setMostrarResultados] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Debounce de búsqueda
  useEffect(() => {
    if (query.length < 2) {
      setResultados([]);
      return;
    }

    const timer = setTimeout(() => {
      buscarUsuarios();
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  // Cerrar al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setMostrarResultados(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const buscarUsuarios = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/usuarios/buscar`, {
        params: { q: query, limit: 8 }
      });
      setResultados(response.data);
    } catch (error) {
      console.error('Error buscando usuarios:', error);
      setResultados([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (usuario: UsuarioBusqueda) => {
    if (onSelect) {
      onSelect(usuario);
    } else {
      navigate(`/${usuario.nombre_usuario}`);
    }
    setQuery('');
    setMostrarResultados(false);
  };

  const limpiar = () => {
    setQuery('');
    setResultados([]);
    inputRef.current?.focus();
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {/* Input de búsqueda */}
      <div className="relative">
        <Search 
          size={18} 
          className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" 
        />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setMostrarResultados(true)}
          placeholder={placeholder}
          autoFocus={autoFocus}
          className="w-full pl-10 pr-10 py-2.5 bg-cardBg border border-cardBorder rounded-lg
                     text-textPrimary placeholder-textSecondary
                     focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary
                     transition-colors"
        />
        {query && (
          <button
            onClick={limpiar}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-textSecondary hover:text-textPrimary"
          >
            <X size={18} />
          </button>
        )}
      </div>

      {/* Resultados */}
      <AnimatePresence>
        {mostrarResultados && (query.length >= 2 || resultados.length > 0) && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-full left-0 right-0 mt-2 bg-cardBg border border-cardBorder 
                       rounded-lg shadow-xl z-50 max-h-80 overflow-y-auto"
          >
            {loading ? (
              <div className="p-4 text-center">
                <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto" />
                <p className="text-textSecondary text-sm mt-2">Buscando...</p>
              </div>
            ) : resultados.length === 0 ? (
              <div className="p-4 text-center">
                <User size={32} className="mx-auto mb-2 text-textSecondary opacity-50" />
                <p className="text-textSecondary text-sm">
                  {query.length < 2 ? 'Escribe al menos 2 caracteres' : 'No se encontraron jugadores'}
                </p>
              </div>
            ) : (
              <div className="py-2">
                {resultados.map((usuario) => (
                  <button
                    key={usuario.id_usuario}
                    onClick={() => handleSelect(usuario)}
                    className="w-full px-4 py-3 flex items-center gap-3 hover:bg-primary/10 transition-colors text-left"
                  >
                    {/* Avatar */}
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-secondary 
                                    flex items-center justify-center text-white font-bold text-sm
                                    overflow-hidden flex-shrink-0">
                      {usuario.foto_perfil ? (
                        <img 
                          src={usuario.foto_perfil} 
                          alt={usuario.nombre_completo}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <span>{usuario.nombre?.charAt(0)}{usuario.apellido?.charAt(0)}</span>
                      )}
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-textPrimary truncate">
                        {usuario.nombre_completo}
                      </p>
                      <p className="text-xs text-textSecondary truncate">
                        @{usuario.nombre_usuario}
                        {usuario.ciudad && ` · ${usuario.ciudad}`}
                      </p>
                    </div>

                    {/* Rating */}
                    <div className="text-right flex-shrink-0">
                      <p className="font-bold text-primary">{usuario.rating}</p>
                      {usuario.categoria && (
                        <p className="text-xs text-textSecondary">{usuario.categoria}</p>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
