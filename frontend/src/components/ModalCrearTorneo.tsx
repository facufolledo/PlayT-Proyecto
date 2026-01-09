import { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Trophy, Calendar, MapPin, FileText, Check, Loader2 } from 'lucide-react';
import Button from './Button';
import Input from './Input';
import { useTorneos } from '../context/TorneosContext';
import { torneoService } from '../services/torneo.service';

interface ModalCrearTorneoProps {
  isOpen: boolean;
  onClose: () => void;
}

interface CategoriaSistema {
  id: number;
  nombre: string;
  sexo: string;
}

export default function ModalCrearTorneo({ isOpen, onClose }: ModalCrearTorneoProps) {
  const { crearTorneo, loading, error, limpiarError } = useTorneos();
  
  const [formData, setFormData] = useState({
    nombre: '',
    fechaInicio: '',
    fechaFin: '',
    descripcion: '',
    lugar: '',
    canchasDisponibles: 2,
  });

  // Categorías del sistema
  const [categoriasSistema, setCategoriasSistema] = useState<CategoriaSistema[]>([]);
  const [loadingCategorias, setLoadingCategorias] = useState(false);

  // Géneros habilitados
  const [generoMasculino, setGeneroMasculino] = useState(true);
  const [generoFemenino, setGeneroFemenino] = useState(false);
  
  // Categorías seleccionadas por género
  const [categoriasMasc, setCategoriasMasc] = useState<string[]>([]);
  const [categoriasFem, setCategoriasFem] = useState<string[]>([]);
  
  // Max parejas por defecto (se eliminó del UI pero se mantiene internamente)
  const maxParejas = 32; // Valor por defecto alto para no limitar
  
  const [creandoCategorias, setCreandoCategorias] = useState(false);

  // Cargar categorías del sistema al abrir
  useEffect(() => {
    if (isOpen && categoriasSistema.length === 0) {
      cargarCategoriasSistema();
    }
  }, [isOpen]);

  const cargarCategoriasSistema = async () => {
    try {
      setLoadingCategorias(true);
      const cats = await torneoService.obtenerCategoriasDelSistema();
      setCategoriasSistema(cats);
      // Seleccionar primera categoría masculina por defecto
      const primeraMasc = cats.find(c => c.sexo === 'masculino');
      if (primeraMasc) {
        setCategoriasMasc([primeraMasc.nombre]);
      }
    } catch (err) {
      console.error('Error cargando categorías:', err);
    } finally {
      setLoadingCategorias(false);
    }
  };

  // Filtrar categorías por género
  const categoriasMasculinas = categoriasSistema.filter(c => c.sexo === 'masculino');
  const categoriasFemeninas = categoriasSistema.filter(c => c.sexo === 'femenino');

  // Toggle categoría
  const toggleCategoria = (cat: string, genero: 'masc' | 'fem') => {
    if (genero === 'masc') {
      setCategoriasMasc(prev => 
        prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat]
      );
    } else {
      setCategoriasFem(prev => 
        prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat]
      );
    }
  };

  // Construir lista de categorías para enviar
  const categoriasFinales = useMemo(() => {
    const result: { nombre: string; genero: string; max_parejas: number }[] = [];
    
    if (generoMasculino) {
      categoriasMasc.forEach(cat => {
        result.push({ nombre: cat, genero: 'masculino', max_parejas: maxParejas });
      });
    }
    
    if (generoFemenino) {
      categoriasFem.forEach(cat => {
        result.push({ nombre: cat, genero: 'femenino', max_parejas: maxParejas });
      });
    }
    
    return result;
  }, [generoMasculino, generoFemenino, categoriasMasc, categoriasFem, maxParejas]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.nombre.trim()) return;
    if (!formData.fechaInicio || !formData.fechaFin) return;
    if (new Date(formData.fechaInicio) >= new Date(formData.fechaFin)) return;
    if (categoriasFinales.length === 0) return;
    
    try {
      limpiarError();
      
      // 1. Probar autenticación primero
      console.log('🔍 Probando autenticación...');
      await torneoService.testAuth();
      
      const torneoData = {
        nombre: formData.nombre.trim(),
        descripcion: formData.descripcion?.trim() || undefined,
        categoria: categoriasFinales[0].nombre,
        genero: categoriasFinales[0].genero,
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
      
      // 2. Probar envío de datos
      console.log('🔍 Probando envío de datos...');
      await torneoService.testCreate(torneoData);
      
      // 3. Crear torneo real
      console.log('🔍 Creando torneo...');
      const nuevoTorneo = await crearTorneo(torneoData);
      
      if (nuevoTorneo && categoriasFinales.length > 0) {
        setCreandoCategorias(true);
        const torneoId = parseInt(nuevoTorneo.id);
        for (let i = 0; i < categoriasFinales.length; i++) {
          const cat = categoriasFinales[i];
          try {
            await torneoService.crearCategoria(torneoId, {
              nombre: cat.nombre,
              genero: cat.genero,
              max_parejas: cat.max_parejas,
              orden: i
            });
          } catch (err) {
            console.error('Error creando categoría:', err);
          }
        }
        setCreandoCategorias(false);
      }
      
      // Reset
      setFormData({ nombre: '', fechaInicio: '', fechaFin: '', descripcion: '', lugar: '', canchasDisponibles: 2 });
      setGeneroMasculino(true);
      setGeneroFemenino(false);
      setCategoriasMasc(['5ta']);
      setCategoriasFem([]);
      onClose();
    } catch (err: any) {
      console.error('Error al crear torneo:', err);
      setCreandoCategorias(false);
    }
  };

  const handleClose = () => {
    limpiarError();
    onClose();
  };

  // Cuando se desactiva un género, limpiar sus categorías
  const toggleGenero = (genero: 'masc' | 'fem') => {
    if (genero === 'masc') {
      if (generoMasculino && !generoFemenino) return; // No permitir desactivar ambos
      setGeneroMasculino(!generoMasculino);
      if (generoMasculino) setCategoriasMasc([]);
    } else {
      if (generoFemenino && !generoMasculino) return;
      setGeneroFemenino(!generoFemenino);
      if (generoFemenino) setCategoriasFem([]);
    }
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
              className="bg-cardBg rounded-xl border border-cardBorder shadow-2xl w-full max-w-lg max-h-[95vh] overflow-y-auto"
            >
              {/* Header */}
              <div className="sticky top-0 bg-cardBg border-b border-cardBorder p-3 flex items-center justify-between z-10">
                <div className="flex items-center gap-2">
                  <div className="bg-accent/10 p-1.5 rounded-lg">
                    <Trophy className="text-accent w-4 h-4" />
                  </div>
                  <h2 className="text-base font-bold text-textPrimary">Crear Torneo</h2>
                </div>
                <button onClick={handleClose} className="text-textSecondary hover:text-textPrimary">
                  <X size={18} />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="p-3 space-y-4">
                {error && (
                  <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-2 text-red-500 text-xs">
                    {error}
                  </div>
                )}

                {/* Nombre */}
                <div>
                  <label className="block text-textSecondary text-xs font-bold mb-1">
                    <Trophy size={12} className="inline mr-1" />
                    Nombre del Torneo *
                  </label>
                  <Input
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    placeholder="Ej: Torneo de Verano 2025"
                    required
                  />
                </div>

                {/* Fechas */}
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-textSecondary text-xs font-bold mb-1">
                      <Calendar size={12} className="inline mr-1" />Inicio *
                    </label>
                    <Input
                      type="date"
                      value={formData.fechaInicio}
                      onChange={(e) => setFormData({ ...formData, fechaInicio: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-textSecondary text-xs font-bold mb-1">
                      <Calendar size={12} className="inline mr-1" />Fin *
                    </label>
                    <Input
                      type="date"
                      value={formData.fechaFin}
                      onChange={(e) => setFormData({ ...formData, fechaFin: e.target.value })}
                      required
                    />
                  </div>
                </div>

                {/* Géneros del torneo */}
                <div>
                  <label className="block text-textSecondary text-xs font-bold mb-2">
                    Géneros del Torneo *
                  </label>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => toggleGenero('masc')}
                      className={`flex-1 py-2 rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 ${
                        generoMasculino
                          ? 'bg-blue-500 text-white'
                          : 'bg-cardBorder text-textSecondary hover:bg-blue-500/20'
                      }`}
                    >
                      {generoMasculino && <Check size={14} />}
                      ♂ Masculino
                    </button>
                    <button
                      type="button"
                      onClick={() => toggleGenero('fem')}
                      className={`flex-1 py-2 rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2 ${
                        generoFemenino
                          ? 'bg-pink-500 text-white'
                          : 'bg-cardBorder text-textSecondary hover:bg-pink-500/20'
                      }`}
                    >
                      {generoFemenino && <Check size={14} />}
                      ♀ Femenino
                    </button>
                  </div>
                </div>

                {/* Categorías Masculino */}
                {generoMasculino && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-3"
                  >
                    <label className="block text-blue-400 text-xs font-bold mb-2">
                      ♂ Categorías Masculino
                    </label>
                    {loadingCategorias ? (
                      <div className="flex items-center gap-2 text-textSecondary text-xs">
                        <Loader2 size={14} className="animate-spin" />
                        Cargando...
                      </div>
                    ) : categoriasMasculinas.length > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {categoriasMasculinas.map((cat) => (
                          <button
                            key={cat.id}
                            type="button"
                            onClick={() => toggleCategoria(cat.nombre, 'masc')}
                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                              categoriasMasc.includes(cat.nombre)
                                ? 'bg-blue-500 text-white'
                                : 'bg-cardBorder text-textSecondary hover:bg-blue-500/20'
                            }`}
                          >
                            {cat.nombre}
                          </button>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[10px] text-textSecondary">No hay categorías masculinas</p>
                    )}
                    {categoriasMasc.length === 0 && categoriasMasculinas.length > 0 && (
                      <p className="text-[10px] text-blue-400/70 mt-2">Seleccioná al menos una categoría</p>
                    )}
                  </motion.div>
                )}

                {/* Categorías Femenino */}
                {generoFemenino && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="bg-pink-500/5 border border-pink-500/20 rounded-lg p-3"
                  >
                    <label className="block text-pink-400 text-xs font-bold mb-2">
                      ♀ Categorías Femenino
                    </label>
                    {loadingCategorias ? (
                      <div className="flex items-center gap-2 text-textSecondary text-xs">
                        <Loader2 size={14} className="animate-spin" />
                        Cargando...
                      </div>
                    ) : categoriasFemeninas.length > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {categoriasFemeninas.map((cat) => (
                          <button
                            key={cat.id}
                            type="button"
                            onClick={() => toggleCategoria(cat.nombre, 'fem')}
                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                              categoriasFem.includes(cat.nombre)
                                ? 'bg-pink-500 text-white'
                                : 'bg-cardBorder text-textSecondary hover:bg-pink-500/20'
                            }`}
                          >
                            {cat.nombre}
                          </button>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[10px] text-textSecondary">No hay categorías femeninas</p>
                    )}
                    {categoriasFem.length === 0 && categoriasFemeninas.length > 0 && (
                      <p className="text-[10px] text-pink-400/70 mt-2">Seleccioná al menos una categoría</p>
                    )}
                  </motion.div>
                )}

                {/* Resumen de categorías */}
                {categoriasFinales.length > 0 && (
                  <div className="bg-accent/5 border border-accent/20 rounded-lg p-2">
                    <p className="text-[10px] text-textSecondary mb-1">Categorías a crear:</p>
                    <div className="flex flex-wrap gap-1">
                      {categoriasFinales.map((cat, i) => (
                        <span
                          key={i}
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            cat.genero === 'masculino' 
                              ? 'bg-blue-500/20 text-blue-400' 
                              : 'bg-pink-500/20 text-pink-400'
                          }`}
                        >
                          {cat.nombre} {cat.genero === 'masculino' ? '♂' : '♀'}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Canchas disponibles */}
                <div>
                  <label className="block text-textSecondary text-xs font-bold mb-1">
                    <MapPin size={12} className="inline mr-1" />Canchas disponibles
                  </label>
                  <Input
                    type="number"
                    min="1"
                    max="10"
                    value={formData.canchasDisponibles}
                    onChange={(e) => setFormData({ ...formData, canchasDisponibles: parseInt(e.target.value) || 1 })}
                  />
                </div>

                {/* Lugar */}
                <div>
                  <label className="block text-textSecondary text-xs font-bold mb-1">
                    <MapPin size={12} className="inline mr-1" />Lugar (Opcional)
                  </label>
                  <Input
                    value={formData.lugar}
                    onChange={(e) => setFormData({ ...formData, lugar: e.target.value })}
                    placeholder="Ej: Club Central"
                  />
                </div>

                {/* Descripción */}
                <div>
                  <label className="block text-textSecondary text-xs font-bold mb-1">
                    <FileText size={12} className="inline mr-1" />Descripción (Opcional)
                  </label>
                  <textarea
                    value={formData.descripcion}
                    onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                    placeholder="Premios, reglas especiales..."
                    className="w-full bg-background border border-cardBorder rounded-lg px-2 py-1.5 text-xs text-textPrimary placeholder-textSecondary focus:outline-none focus:border-primary resize-none"
                    rows={2}
                  />
                </div>

                {/* Botones */}
                <div className="flex gap-2 pt-2">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={handleClose}
                    className="flex-1 text-xs py-2"
                    disabled={loading || creandoCategorias}
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    variant="accent"
                    className="flex-1 text-xs py-2"
                    disabled={loading || creandoCategorias || categoriasFinales.length === 0}
                  >
                    {loading ? 'Creando...' : creandoCategorias ? 'Creando categorías...' : 'Crear Torneo'}
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
