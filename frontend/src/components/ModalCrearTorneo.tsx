import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Trophy, Calendar, MapPin, FileText } from 'lucide-react';
import Button from './Button';
import Input from './Input';
import { useTorneos } from '../context/TorneosContext';

interface ModalCrearTorneoProps {
  isOpen: boolean;
  onClose: () => void;
}

const CATEGORIAS = ['8va', '7ma', '6ta', '5ta', '4ta', 'Libre'];
const GENEROS = [
  { value: 'masculino', label: 'Masculino', icon: '♂' },
  { value: 'femenino', label: 'Femenino', icon: '♀' },
  { value: 'mixto', label: 'Mixto', icon: '⚥' },
];

export default function ModalCrearTorneo({ isOpen, onClose }: ModalCrearTorneoProps) {
  const { crearTorneo, loading, error, limpiarError } = useTorneos();
  
  const [formData, setFormData] = useState({
    nombre: '',
    fechaInicio: '',
    fechaFin: '',
    categoria: '5ta',
    genero: 'masculino',
    descripcion: '',
    lugar: '',
    canchasDisponibles: 2,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.nombre.trim()) {
      return;
    }
    
    if (!formData.fechaInicio || !formData.fechaFin) {
      return;
    }
    
    if (new Date(formData.fechaInicio) >= new Date(formData.fechaFin)) {
      return;
    }
    
    try {
      limpiarError();
      
      // Preparar datos para el backend
      const torneoData = {
        nombre: formData.nombre.trim(),
        descripcion: formData.descripcion?.trim() || undefined,
        categoria: formData.categoria,
        genero: formData.genero,
        fecha_inicio: formData.fechaInicio,
        fecha_fin: formData.fechaFin,
        lugar: formData.lugar?.trim() || undefined,
        reglas_json: {
          puntos_victoria: 3,
          puntos_derrota: 0,
          sets_para_ganar: 2,
          canchas_disponibles: formData.canchasDisponibles
        }
      };
      
      await crearTorneo(torneoData);
      
      // Reset form y cerrar
      setFormData({
        nombre: '',
        fechaInicio: '',
        fechaFin: '',
        categoria: '5ta',
        genero: 'masculino',
        descripcion: '',
        lugar: '',
        canchasDisponibles: 2,
      });
      onClose();
    } catch (err: any) {
      // El error ya se maneja en el context
      console.error('Error al crear torneo:', err);
    }
  };

  const handleClose = () => {
    limpiarError();
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />
          
          <div className="fixed inset-0 flex items-center justify-center z-50 p-2 sm:p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="bg-cardBg rounded-xl sm:rounded-2xl border border-cardBorder shadow-2xl w-full max-w-2xl max-h-[95vh] sm:max-h-[90vh] overflow-y-auto"
            >
              <div className="sticky top-0 bg-cardBg border-b border-cardBorder p-3 sm:p-4 flex items-center justify-between z-10">
                <div className="flex items-center gap-2 sm:gap-3">
                  <div className="bg-accent/10 p-2 rounded-lg">
                    <Trophy className="text-accent" size={20} />
                  </div>
                  <div>
                    <h2 className="text-lg sm:text-xl font-bold text-textPrimary">Crear Torneo</h2>
                    <p className="text-textSecondary text-xs hidden sm:block">Organiza una nueva competencia</p>
                  </div>
                </div>
                <motion.button
                  whileHover={{ scale: 1.1, rotate: 90 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={handleClose}
                  className="text-textSecondary hover:text-textPrimary transition-colors"
                >
                  <X size={20} />
                </motion.button>
              </div>

              <form onSubmit={handleSubmit} className="p-3 sm:p-5 space-y-4 sm:space-y-5">
                {/* Error message */}
                {error && (
                  <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-500 text-sm">
                    {error}
                  </div>
                )}

                {/* Nombre del torneo */}
                <div>
                  <label className="block text-textSecondary text-xs sm:text-sm font-bold mb-1.5">
                    <div className="flex items-center gap-2">
                      <Trophy size={14} />
                      Nombre del Torneo *
                    </div>
                  </label>
                  <Input
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    placeholder="Ej: Torneo de Verano 2025"
                    required
                  />
                </div>

                {/* Fechas */}
                <div className="grid grid-cols-2 gap-2 sm:gap-3">
                  <div>
                    <label className="block text-textSecondary text-xs sm:text-sm font-bold mb-1.5">
                      <div className="flex items-center gap-1.5">
                        <Calendar size={14} />
                        <span className="hidden sm:inline">Fecha de Inicio *</span>
                        <span className="sm:hidden">Inicio *</span>
                      </div>
                    </label>
                    <Input
                      type="date"
                      value={formData.fechaInicio}
                      onChange={(e) => setFormData({ ...formData, fechaInicio: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-textSecondary text-xs sm:text-sm font-bold mb-1.5">
                      <div className="flex items-center gap-1.5">
                        <Calendar size={14} />
                        <span className="hidden sm:inline">Fecha de Fin *</span>
                        <span className="sm:hidden">Fin *</span>
                      </div>
                    </label>
                    <Input
                      type="date"
                      value={formData.fechaFin}
                      onChange={(e) => setFormData({ ...formData, fechaFin: e.target.value })}
                      required
                    />
                  </div>
                </div>

                {/* Categoría */}
                <div>
                  <label className="block text-textSecondary text-xs sm:text-sm font-bold mb-1.5">
                    Categoría *
                  </label>
                  <div className="grid grid-cols-3 sm:grid-cols-6 gap-1.5 sm:gap-2">
                    {CATEGORIAS.map((cat) => (
                      <motion.button
                        key={cat}
                        type="button"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setFormData({ ...formData, categoria: cat })}
                        className={`py-1.5 sm:py-2 px-2 sm:px-3 rounded-lg text-sm font-bold transition-all ${
                          formData.categoria === cat
                            ? 'bg-gradient-to-r from-primary to-blue-600 text-white shadow-lg shadow-primary/30'
                            : 'bg-cardBorder text-textSecondary hover:text-textPrimary'
                        }`}
                      >
                        {cat}
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Género */}
                <div>
                  <label className="block text-textSecondary text-xs sm:text-sm font-bold mb-1.5">
                    Género *
                  </label>
                  <div className="grid grid-cols-3 gap-1.5 sm:gap-2">
                    {GENEROS.map((gen) => (
                      <motion.button
                        key={gen.value}
                        type="button"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setFormData({ ...formData, genero: gen.value })}
                        className={`py-1.5 sm:py-2 px-2 sm:px-3 rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-1.5 ${
                          formData.genero === gen.value
                            ? 'bg-gradient-to-r from-primary to-blue-600 text-white shadow-lg shadow-primary/30'
                            : 'bg-cardBorder text-textSecondary hover:text-textPrimary'
                        }`}
                      >
                        <span>{gen.icon}</span>
                        <span className="hidden sm:inline">{gen.label}</span>
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Lugar */}
                <div>
                  <label className="block text-textSecondary text-xs sm:text-sm font-bold mb-1.5">
                    <div className="flex items-center gap-1.5">
                      <MapPin size={14} />
                      Lugar (Opcional)
                    </div>
                  </label>
                  <Input
                    value={formData.lugar}
                    onChange={(e) => setFormData({ ...formData, lugar: e.target.value })}
                    placeholder="Ej: Club Central, Cancha 1"
                  />
                </div>

                {/* Canchas Disponibles */}
                <div>
                  <label className="block text-textSecondary text-xs sm:text-sm font-bold mb-1.5">
                    Canchas Disponibles *
                  </label>
                  <div className="flex items-center gap-3">
                    <Input
                      type="number"
                      min="1"
                      max="10"
                      value={formData.canchasDisponibles}
                      onChange={(e) => setFormData({ ...formData, canchasDisponibles: parseInt(e.target.value) || 1 })}
                      className="w-24"
                      required
                    />
                    <span className="text-textSecondary text-sm">
                      {formData.canchasDisponibles === 1 ? 'cancha' : 'canchas'} para jugar simultáneamente
                    </span>
                  </div>
                  <p className="text-xs text-textSecondary mt-1">
                    Esto ayuda a programar los partidos de forma eficiente
                  </p>
                </div>

                {/* Descripción */}
                <div>
                  <label className="block text-textSecondary text-xs sm:text-sm font-bold mb-1.5">
                    <div className="flex items-center gap-1.5">
                      <FileText size={14} />
                      Descripción (Opcional)
                    </div>
                  </label>
                  <textarea
                    value={formData.descripcion}
                    onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                    placeholder="Describe el torneo, premios, reglas especiales..."
                    className="w-full bg-background border border-cardBorder rounded-lg px-3 py-2 text-sm text-textPrimary placeholder-textSecondary focus:outline-none focus:border-primary transition-colors resize-none"
                    rows={3}
                  />
                </div>

                {/* Botones */}
                <div className="flex gap-2 sm:gap-3 pt-2">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={handleClose}
                    className="flex-1 text-sm"
                    disabled={loading}
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    variant="accent"
                    className="flex-1 text-sm"
                    disabled={loading}
                  >
                    {loading ? 'Creando...' : 'Crear Torneo'}
                  </Button>
                </div>
              </form>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
