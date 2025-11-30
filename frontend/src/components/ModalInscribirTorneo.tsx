import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Users, AlertCircle, Search } from 'lucide-react';
import Button from './Button';
import { useTorneos } from '../context/TorneosContext';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ModalInscribirTorneoProps {
  isOpen: boolean;
  onClose: () => void;
  torneoId: number;
  torneoNombre: string;
}

export default function ModalInscribirTorneo({
  isOpen,
  onClose,
  torneoId,
  torneoNombre,
}: ModalInscribirTorneoProps) {
  const { inscribirPareja, loading } = useTorneos();
  const { usuario } = useAuth();
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [selectedCompanero, setSelectedCompanero] = useState<any>(null);
  
  const [formData, setFormData] = useState({
    jugador2_id: '',
    nombre_pareja: '',
  });

  // Buscar usuarios cuando cambia el query
  useEffect(() => {
    const buscarUsuarios = async () => {
      if (searchQuery.length < 2) {
        setSearchResults([]);
        return;
      }

      try {
        setSearching(true);
        const response = await axios.get(`${API_URL}/usuarios/buscar`, {
          params: { q: searchQuery, limit: 5 }
        });
        
        // Filtrar para no mostrar al usuario actual
        const resultados = response.data.filter((u: any) => u.id_usuario !== usuario?.id_usuario);
        setSearchResults(resultados);
      } catch (err) {
        console.error('Error buscando usuarios:', err);
        setSearchResults([]);
      } finally {
        setSearching(false);
      }
    };

    const timeoutId = setTimeout(buscarUsuarios, 300);
    return () => clearTimeout(timeoutId);
  }, [searchQuery, usuario]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!usuario) {
      setError('Debes iniciar sesión para inscribirte');
      return;
    }

    if (!formData.jugador2_id) {
      setError('Debes ingresar el ID de tu compañero');
      return;
    }

    if (!formData.nombre_pareja || formData.nombre_pareja.trim().length < 3) {
      setError('El nombre de la pareja debe tener al menos 3 caracteres');
      return;
    }

    try {
      await inscribirPareja(torneoId, {
        jugador1_id: usuario.id_usuario,
        jugador2_id: parseInt(formData.jugador2_id),
        nombre_pareja: formData.nombre_pareja.trim(),
      });

      setSuccess(true);
      setTimeout(() => {
        onClose();
        setSuccess(false);
        setFormData({ jugador2_id: '', nombre_pareja: '' });
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Error al inscribir pareja');
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
      setError('');
      setSuccess(false);
      setFormData({ jugador2_id: '', nombre_pareja: '' });
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-cardBg rounded-xl border border-cardBorder w-full max-w-md max-h-[90vh] overflow-y-auto"
            >
              {success ? (
                <div className="p-6 text-center">
                  <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Users size={32} className="text-green-500" />
                  </div>
                  <h3 className="text-xl font-bold text-textPrimary mb-2">
                    ¡Inscripción Exitosa!
                  </h3>
                  <p className="text-textSecondary">
                    Tu pareja ha sido inscrita en el torneo
                  </p>
                </div>
              ) : (
                <>
                  {/* Header */}
                  <div className="flex items-center justify-between p-6 border-b border-cardBorder">
                    <div>
                      <h2 className="text-xl font-bold text-textPrimary">
                        Inscribirse al Torneo
                      </h2>
                      <p className="text-sm text-textSecondary mt-1">
                        {torneoNombre}
                      </p>
                    </div>
                    <button
                      onClick={handleClose}
                      disabled={loading}
                      className="text-textSecondary hover:text-textPrimary transition-colors disabled:opacity-50"
                    >
                      <X size={24} />
                    </button>
                  </div>

                  {/* Form */}
                  <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {/* Info del usuario actual */}
                    <div className="bg-primary/10 rounded-lg p-4">
                      <p className="text-xs text-textSecondary mb-1">Jugador 1 (Tú)</p>
                      <p className="font-bold text-textPrimary">
                        {usuario?.nombre} {usuario?.apellido}
                      </p>
                      <p className="text-xs text-textSecondary">
                        Rating: {usuario?.rating || 1200}
                      </p>
                    </div>

                    {/* Buscar compañero */}
                    <div>
                      <label className="block text-sm font-bold text-textSecondary mb-2">
                        Buscar Compañero *
                      </label>
                      
                      {selectedCompanero ? (
                        <div className="bg-primary/10 rounded-lg p-4 flex items-center justify-between">
                          <div>
                            <p className="font-bold text-textPrimary">
                              {selectedCompanero.nombre} {selectedCompanero.apellido}
                            </p>
                            <p className="text-xs text-textSecondary">
                              Rating: {selectedCompanero.rating || 1200}
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => {
                              setSelectedCompanero(null);
                              setFormData({ ...formData, jugador2_id: '' });
                            }}
                            className="text-textSecondary hover:text-red-500 transition-colors"
                          >
                            <X size={20} />
                          </button>
                        </div>
                      ) : (
                        <div className="relative">
                          <div className="relative">
                            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" />
                            <input
                              type="text"
                              value={searchQuery}
                              onChange={(e) => setSearchQuery(e.target.value)}
                              placeholder="Busca por nombre o apellido..."
                              disabled={loading}
                              className="w-full pl-10 pr-4 py-3 bg-background border border-cardBorder rounded-lg text-textPrimary placeholder-textSecondary focus:outline-none focus:border-primary transition-colors disabled:opacity-50"
                            />
                          </div>
                          
                          {/* Resultados de búsqueda */}
                          {searchQuery.length >= 2 && (
                            <div className="absolute z-10 w-full mt-2 bg-card border border-cardBorder rounded-lg shadow-lg max-h-60 overflow-y-auto">
                              {searching ? (
                                <div className="p-4 text-center text-textSecondary">
                                  Buscando...
                                </div>
                              ) : searchResults.length > 0 ? (
                                searchResults.map((user) => (
                                  <button
                                    key={user.id_usuario}
                                    type="button"
                                    onClick={() => {
                                      setSelectedCompanero(user);
                                      setFormData({ ...formData, jugador2_id: user.id_usuario.toString() });
                                      setSearchQuery('');
                                      setSearchResults([]);
                                    }}
                                    className="w-full p-3 text-left hover:bg-background transition-colors border-b border-cardBorder last:border-b-0"
                                  >
                                    <p className="font-bold text-textPrimary">
                                      {user.nombre} {user.apellido}
                                    </p>
                                    <p className="text-xs text-textSecondary">
                                      Rating: {user.rating || 1200} • ID: {user.id_usuario}
                                    </p>
                                  </button>
                                ))
                              ) : (
                                <div className="p-4 text-center text-textSecondary">
                                  No se encontraron usuarios
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                      
                      <p className="text-xs text-textSecondary mt-1">
                        {selectedCompanero 
                          ? 'Compañero seleccionado' 
                          : 'Escribe al menos 2 caracteres para buscar'}
                      </p>
                    </div>

                    {/* Nombre de la pareja */}
                    <div>
                      <label className="block text-sm font-bold text-textSecondary mb-2">
                        Nombre de la Pareja *
                      </label>
                      <input
                        type="text"
                        value={formData.nombre_pareja}
                        onChange={(e) =>
                          setFormData({ ...formData, nombre_pareja: e.target.value })
                        }
                        placeholder="Ej: Los Cracks"
                        required
                        disabled={loading}
                        maxLength={50}
                        className="w-full px-4 py-3 bg-background border border-cardBorder rounded-lg text-textPrimary placeholder-textSecondary focus:outline-none focus:border-primary transition-colors disabled:opacity-50"
                      />
                    </div>

                    {/* Error */}
                    {error && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg"
                      >
                        <AlertCircle size={18} className="text-red-500 flex-shrink-0 mt-0.5" />
                        <p className="text-sm text-red-500">{error}</p>
                      </motion.div>
                    )}

                    {/* Botones */}
                    <div className="flex gap-3 pt-4">
                      <Button
                        type="button"
                        variant="ghost"
                        onClick={handleClose}
                        disabled={loading}
                        className="flex-1"
                      >
                        Cancelar
                      </Button>
                      <Button
                        type="submit"
                        variant="accent"
                        disabled={loading}
                        className="flex-1"
                      >
                        {loading ? 'Inscribiendo...' : 'Inscribirse'}
                      </Button>
                    </div>
                  </form>
                </>
              )}
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
