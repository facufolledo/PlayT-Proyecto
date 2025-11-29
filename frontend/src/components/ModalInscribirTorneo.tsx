import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Users, AlertCircle } from 'lucide-react';
import Button from './Button';
import { useTorneos } from '../context/TorneosContext';
import { useAuth } from '../context/AuthContext';

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
  
  const [formData, setFormData] = useState({
    jugador2_id: '',
    nombre_pareja: '',
  });

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

                    {/* ID del compañero */}
                    <div>
                      <label className="block text-sm font-bold text-textSecondary mb-2">
                        ID de tu Compañero *
                      </label>
                      <input
                        type="number"
                        value={formData.jugador2_id}
                        onChange={(e) =>
                          setFormData({ ...formData, jugador2_id: e.target.value })
                        }
                        placeholder="Ej: 123"
                        required
                        disabled={loading}
                        className="w-full px-4 py-3 bg-background border border-cardBorder rounded-lg text-textPrimary placeholder-textSecondary focus:outline-none focus:border-primary transition-colors disabled:opacity-50"
                      />
                      <p className="text-xs text-textSecondary mt-1">
                        Pídele a tu compañero su ID de usuario
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
