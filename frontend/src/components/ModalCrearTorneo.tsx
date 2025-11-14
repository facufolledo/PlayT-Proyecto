import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Trophy, Calendar, Users, FileText, Lock } from 'lucide-react';
import Button from './Button';
import Input from './Input';
import { useTorneos } from '../context/TorneosContext';
import { useAuth } from '../context/AuthContext';

interface ModalCrearTorneoProps {
  isOpen: boolean;
  onClose: () => void;
}

const FORMATOS = [
  { value: 'eliminacion-simple', label: 'Eliminación Simple', descripcion: 'Un solo partido, pierdes y quedas fuera', requiereAutorizacion: false },
  { value: 'eliminacion-doble', label: 'Eliminación Doble', descripcion: 'Dos oportunidades, bracket de ganadores y perdedores', requiereAutorizacion: false },
  { value: 'round-robin', label: 'Round Robin', descripcion: 'Todos contra todos', requiereAutorizacion: false },
  { value: 'grupos', label: 'Por Grupos', descripcion: 'Fase de grupos + eliminación directa', requiereAutorizacion: false },
  { value: 'por-puntos', label: 'Por Puntos', descripcion: 'Sistema de puntuación acumulativa (Solo admin)', requiereAutorizacion: true },
] as const;

const CATEGORIAS = ['8va', '7ma', '6ta', '5ta', '4ta', 'Libre'];

const GENEROS = [
  { value: 'masculino', label: 'Masculino', icon: '♂' },
  { value: 'femenino', label: 'Femenino', icon: '♀' },
  { value: 'mixto', label: 'Mixto', icon: '⚥' },
] as const;

export default function ModalCrearTorneo({ isOpen, onClose }: ModalCrearTorneoProps) {
  const { addTorneo } = useTorneos();
  const { usuario } = useAuth();
  const esAdmin = usuario?.rol === 'admin';
  
  const [formData, setFormData] = useState<{
    nombre: string;
    fechaInicio: string;
    fechaFin: string;
    categoria: string;
    formato: 'eliminacion-simple' | 'eliminacion-doble' | 'round-robin' | 'grupos' | 'por-puntos';
    genero: 'masculino' | 'femenino' | 'mixto';
    descripcion: string;
    participantes: number;
  }>({
    nombre: '',
    fechaInicio: '',
    fechaFin: '',
    categoria: '8va',
    formato: 'eliminacion-simple',
    genero: 'masculino',
    descripcion: '',
    participantes: 8,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    addTorneo({
      ...formData,
      estado: 'programado',
      salasIds: [],
    });

    onClose();
    setFormData({
      nombre: '',
      fechaInicio: '',
      fechaFin: '',
      categoria: '8va',
      formato: 'eliminacion-simple',
      genero: 'masculino',
      descripcion: '',
      participantes: 8,
    });
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
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
                  onClick={onClose}
                  className="text-textSecondary hover:text-textPrimary transition-colors"
                >
                  <X size={20} />
                </motion.button>
              </div>

              <form onSubmit={handleSubmit} className="p-3 sm:p-5 space-y-4 sm:space-y-5">
                {/* Nombre del torneo */}
                <div>
                  <label className="block text-textSecondary text-xs sm:text-sm font-bold mb-1.5">
                    <div className="flex items-center gap-2">
                      <Trophy size={14} />
                      Nombre del Torneo
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
                        <span className="hidden sm:inline">Fecha de Inicio</span>
                        <span className="sm:hidden">Inicio</span>
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
                        <span className="hidden sm:inline">Fecha de Fin</span>
                        <span className="sm:hidden">Fin</span>
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
                    Categoría
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
                    Género
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {GENEROS.map((gen) => (
                      <motion.button
                        key={gen.value}
                        type="button"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setFormData({ ...formData, genero: gen.value })}
                        className={`py-2 sm:py-2.5 px-3 rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 ${
                          formData.genero === gen.value
                            ? 'bg-gradient-to-r from-primary to-blue-600 text-white shadow-lg shadow-primary/30'
                            : 'bg-cardBorder text-textSecondary hover:text-textPrimary'
                        }`}
                      >
                        <span className="text-lg">{gen.icon}</span>
                        <span>{gen.label}</span>
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Formato */}
                <div>
                  <label className="block text-textSecondary text-xs sm:text-sm font-bold mb-1.5">
                    Formato del Torneo
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {FORMATOS.map((formato) => {
                      const estaDeshabilitado = formato.requiereAutorizacion && !esAdmin;
                      
                      return (
                        <motion.button
                          key={formato.value}
                          type="button"
                          whileHover={!estaDeshabilitado ? { scale: 1.02 } : {}}
                          whileTap={!estaDeshabilitado ? { scale: 0.98 } : {}}
                          onClick={() => !estaDeshabilitado && setFormData({ ...formData, formato: formato.value })}
                          disabled={estaDeshabilitado}
                          className={`p-2.5 sm:p-3 rounded-lg text-left transition-all border-2 relative ${
                            formData.formato === formato.value
                              ? 'border-primary bg-primary/10'
                              : estaDeshabilitado
                              ? 'border-cardBorder bg-cardBorder/50 opacity-50 cursor-not-allowed'
                              : 'border-cardBorder bg-cardBorder hover:border-primary/50'
                          }`}
                        >
                          {estaDeshabilitado && (
                            <div className="absolute top-2 right-2">
                              <Lock size={14} className="text-textSecondary" />
                            </div>
                          )}
                          <p className="font-bold text-textPrimary text-sm mb-0.5">{formato.label}</p>
                          <p className="text-[10px] sm:text-xs text-textSecondary leading-tight">{formato.descripcion}</p>
                        </motion.button>
                      );
                    })}
                  </div>
                </div>

                {/* Participantes */}
                <div>
                  <label className="block text-textSecondary text-xs sm:text-sm font-bold mb-1.5">
                    <div className="flex items-center gap-1.5">
                      <Users size={14} />
                      Participantes
                    </div>
                  </label>
                  <div className="flex items-center gap-2 sm:gap-3">
                    <Input
                      type="number"
                      min="4"
                      max="64"
                      step="4"
                      value={formData.participantes}
                      onChange={(e) => setFormData({ ...formData, participantes: parseInt(e.target.value) })}
                      required
                      className="w-20 sm:w-24"
                    />
                    <span className="text-textSecondary text-xs sm:text-sm">
                      {formData.participantes} jugadores ({formData.participantes / 2} parejas)
                    </span>
                  </div>
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
                    onClick={onClose}
                    className="flex-1 text-sm"
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    variant="accent"
                    className="flex-1 text-sm"
                  >
                    Crear Torneo
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
