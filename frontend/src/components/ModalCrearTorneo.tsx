import { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Trophy, Calendar, MapPin, FileText, Check, Loader2, DollarSign, Clock } from 'lucide-react';
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

// Generar opciones de horario cada 30 minutos
const generarOpcionesHorario = () => {
  return Array.from({ length: 48 }, (_, i) => {
    const h = Math.floor(i / 2);
    const m = i % 2 === 0 ? '00' : '30';
    return `${h.toString().padStart(2, '0')}:${m}`;
  });
};

const OPCIONES_HORARIO = generarOpcionesHorario();

export default function ModalCrearTorneo({ isOpen, onClose }: ModalCrearTorneoProps) {
  const { crearTorneo, loading, error, limpiarError } = useTorneos();
  
  const [formData, setFormData] = useState({
    nombre: '',
    fechaInicio: '',
    fechaFin: '',
    descripcion: '',
    lugar: '',
    canchasDisponibles: 2,
    requierePago: false,
    monto: 0,
    alias: '',
    titular: '',
    banco: '',
  });

  const [horariosDisponibles, setHorariosDisponibles] = useState<{
    semana: {desde: string, hasta: string}[],
    finDeSemana: {desde: string, hasta: string}[]
  }>({
    semana: [],
    finDeSemana: []
  });

  const [categoriasSistema, setCategoriasSistema] = useState<CategoriaSistema[]>([]);
  const [loadingCategorias, setLoadingCategorias] = useState(false);
  const [generoMasculino, setGeneroMasculino] = useState(true);
  const [generoFemenino, setGeneroFemenino] = useState(false);
  const [categoriasMasc, setCategoriasMasc] = useState<string[]>([]);
  const [categoriasFem, setCategoriasFem] = useState<string[]>([]);
  const [creandoCategorias, setCreandoCategorias] = useState(false);

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
      const primeraMasc = cats.find(c => c.sexo === 'masculino');
      if (primeraMasc) setCategoriasMasc([primeraMasc.nombre]);
    } catch (err) {
      console.error('Error cargando categorías:', err);
    } finally {
      setLoadingCategorias(false);
    }
  };

  const categoriasMasculinas = categoriasSistema.filter(c => c.sexo === 'masculino');
  const categoriasFemeninas = categoriasSistema.filter(c => c.sexo === 'femenino');

  const toggleCategoria = (cat: string, genero: 'masc' | 'fem') => {
    if (genero === 'masc') {
      setCategoriasMasc(prev => prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat]);
    } else {
      setCategoriasFem(prev => prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat]);
    }
  };

  const categoriasFinales = useMemo(() => {
    const result: { nombre: string; genero: string; max_parejas: number }[] = [];
    if (generoMasculino) {
      categoriasMasc.forEach(cat => result.push({ nombre: cat, genero: 'masculino', max_parejas: 999 }));
    }
    if (generoFemenino) {
      categoriasFem.forEach(cat => result.push({ nombre: cat, genero: 'femenino', max_parejas: 999 }));
    }
    return result;
  }, [generoMasculino, generoFemenino, categoriasMasc, categoriasFem]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.nombre.trim() || !formData.fechaInicio || !formData.fechaFin) return;
    if (new Date(formData.fechaInicio) >= new Date(formData.fechaFin)) return;
    if (categoriasFinales.length === 0) return;
    
    try {
      limpiarError();
      
      const torneoData = {
        nombre: formData.nombre.trim(),
        descripcion: formData.descripcion?.trim() || undefined,
        categoria: categoriasFinales[0].nombre,
        genero: categoriasFinales[0].genero,
        fecha_inicio: formData.fechaInicio,
        fecha_fin: formData.fechaFin,
        lugar: formData.lugar?.trim() || undefined,
        requiere_pago: formData.requierePago,
        monto_inscripcion: formData.requierePago ? formData.monto : undefined,
        alias_cbu_cvu: formData.requierePago ? formData.alias.trim() : undefined,
        titular_cuenta: formData.requierePago ? formData.titular.trim() : undefined,
        banco: formData.requierePago ? formData.banco.trim() : undefined,
        horarios_disponibles: {
          semana: horariosDisponibles.semana.filter(h => h.desde && h.hasta),
          finDeSemana: horariosDisponibles.finDeSemana.filter(h => h.desde && h.hasta)
        },
        reglas_json: {
          puntos_victoria: 3,
          puntos_derrota: 0,
          sets_para_ganar: 2,
          canchas_disponibles: formData.canchasDisponibles
        }
      };
      
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
      setFormData({ 
        nombre: '', fechaInicio: '', fechaFin: '', descripcion: '', lugar: '', 
        canchasDisponibles: 2, requierePago: false, monto: 0, alias: '', titular: '', banco: ''
      });
      setHorariosDisponibles({ semana: [], finDeSemana: [] });
      setGeneroMasculino(true);
      setGeneroFemenino(false);
      setCategoriasMasc([]);
      setCategoriasFem([]);
      onClose();
    } catch (err: any) {
      console.error('Error al crear torneo:', err);
      setCreandoCategorias(false);
    }
  };

  const toggleGenero = (genero: 'masc' | 'fem') => {
    if (genero === 'masc') {
      if (generoMasculino && !generoFemenino) return;
      setGeneroMasculino(!generoMasculino);
      if (generoMasculino) setCategoriasMasc([]);
    } else {
      if (generoFemenino && !generoMasculino) return;
      setGeneroFemenino(!generoFemenino);
      if (generoFemenino) setCategoriasFem([]);
    }
  };

  const agregarHorario = (tipo: 'semana' | 'finDeSemana') => {
    setHorariosDisponibles(prev => ({
      ...prev,
      [tipo]: [...prev[tipo], { desde: '', hasta: '' }]
    }));
  };

  const eliminarHorario = (tipo: 'semana' | 'finDeSemana', index: number) => {
    setHorariosDisponibles(prev => ({
      ...prev,
      [tipo]: prev[tipo].filter((_, i) => i !== index)
    }));
  };

  const actualizarHorario = (tipo: 'semana' | 'finDeSemana', index: number, campo: 'desde' | 'hasta', valor: string) => {
    setHorariosDisponibles(prev => ({
      ...prev,
      [tipo]: prev[tipo].map((h, i) => i === index ? { ...h, [campo]: valor } : h)
    }));
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => { limpiarError(); onClose(); }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />
          
          <div className="fixed inset-0 flex items-start sm:items-center justify-center z-50 p-0 sm:p-4 overflow-y-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-cardBg rounded-none sm:rounded-xl border-0 sm:border border-cardBorder shadow-2xl w-full max-w-5xl min-h-screen sm:min-h-0 sm:my-4"
            >
              {/* Header Sticky */}
              <div className="sticky top-0 bg-cardBg/95 backdrop-blur-sm border-b border-cardBorder p-3 sm:p-4 flex items-center justify-between z-10">
                <div className="flex items-center gap-2">
                  <div className="bg-accent/10 p-1.5 rounded-lg">
                    <Trophy className="text-accent w-4 h-4 sm:w-5 sm:h-5" />
                  </div>
                  <h2 className="text-base sm:text-lg font-bold text-textPrimary">Crear Torneo</h2>
                </div>
                <button onClick={() => { limpiarError(); onClose(); }} className="text-textSecondary hover:text-textPrimary">
                  <X size={20} />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="p-3 sm:p-4 space-y-3 sm:space-y-4">
                {error && (
                  <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-2 text-red-500 text-xs">
                    {error}
                  </div>
                )}

                {/* Grid Responsive: 1 col móvil, 2 cols desktop */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4">
                  {/* Columna Izquierda: Datos Básicos */}
                  <div className="space-y-2 sm:space-y-3">
                    <div>
                      <label className="block text-textSecondary text-xs font-bold mb-1">
                        <Trophy size={11} className="inline mr-1" />Nombre *
                      </label>
                      <Input
                        value={formData.nombre}
                        onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                        placeholder="Ej: Torneo de Verano 2025"
                        required
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-textSecondary text-xs font-bold mb-1">
                          <Calendar size={11} className="inline mr-1" />Inicio *
                        </label>
                        <Input type="date" value={formData.fechaInicio} onChange={(e) => setFormData({ ...formData, fechaInicio: e.target.value })} required />
                      </div>
                      <div>
                        <label className="block text-textSecondary text-xs font-bold mb-1">
                          <Calendar size={11} className="inline mr-1" />Fin *
                        </label>
                        <Input type="date" value={formData.fechaFin} onChange={(e) => setFormData({ ...formData, fechaFin: e.target.value })} required />
                      </div>
                    </div>

                    <div>
                      <label className="block text-textSecondary text-xs font-bold mb-1">
                        <MapPin size={11} className="inline mr-1" />Lugar
                      </label>
                      <Input value={formData.lugar} onChange={(e) => setFormData({ ...formData, lugar: e.target.value })} placeholder="Ej: Club Central" />
                    </div>

                    <div>
                      <label className="block text-textSecondary text-xs font-bold mb-1">
                        Canchas disponibles
                      </label>
                      <Input type="number" min="1" max="10" value={formData.canchasDisponibles} onChange={(e) => setFormData({ ...formData, canchasDisponibles: parseInt(e.target.value) || 1 })} />
                    </div>

                    <div>
                      <label className="block text-textSecondary text-xs font-bold mb-1">
                        <FileText size={11} className="inline mr-1" />Descripción
                      </label>
                      <textarea
                        value={formData.descripcion}
                        onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                        placeholder="Premios, reglas especiales..."
                        className="w-full bg-background border border-cardBorder rounded-lg px-2 py-1.5 text-xs text-textPrimary placeholder-textSecondary focus:outline-none focus:border-primary resize-none"
                        rows={3}
                      />
                    </div>
                  </div>

                  {/* Columna Derecha: Géneros y Categorías */}
                  <div className="space-y-2 sm:space-y-3">
                    <div>
                      <label className="block text-textSecondary text-xs font-bold mb-2">Géneros *</label>
                      <div className="grid grid-cols-2 gap-2">
                        <button type="button" onClick={() => toggleGenero('masc')} className={`py-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${generoMasculino ? 'bg-blue-500 text-white' : 'bg-cardBorder text-textSecondary hover:bg-blue-500/20'}`}>
                          {generoMasculino && <Check size={12} />}♂ Masculino
                        </button>
                        <button type="button" onClick={() => toggleGenero('fem')} className={`py-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${generoFemenino ? 'bg-pink-500 text-white' : 'bg-cardBorder text-textSecondary hover:bg-pink-500/20'}`}>
                          {generoFemenino && <Check size={12} />}♀ Femenino
                        </button>
                      </div>
                    </div>

                    {generoMasculino && (
                      <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-2.5">
                        <label className="block text-blue-400 text-xs font-bold mb-2">♂ Categorías Masculino</label>
                        {loadingCategorias ? (
                          <div className="flex items-center gap-2 text-textSecondary text-xs"><Loader2 size={12} className="animate-spin" />Cargando...</div>
                        ) : (
                          <div className="flex flex-wrap gap-1.5">
                            {categoriasMasculinas.map((cat) => (
                              <button key={cat.id} type="button" onClick={() => toggleCategoria(cat.nombre, 'masc')} className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${categoriasMasc.includes(cat.nombre) ? 'bg-blue-500 text-white' : 'bg-cardBorder text-textSecondary hover:bg-blue-500/20'}`}>
                                {cat.nombre}
                              </button>
                            ))}
                          </div>
                        )}
                      </motion.div>
                    )}

                    {generoFemenino && (
                      <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="bg-pink-500/5 border border-pink-500/20 rounded-lg p-2.5">
                        <label className="block text-pink-400 text-xs font-bold mb-2">♀ Categorías Femenino</label>
                        {loadingCategorias ? (
                          <div className="flex items-center gap-2 text-textSecondary text-xs"><Loader2 size={12} className="animate-spin" />Cargando...</div>
                        ) : (
                          <div className="flex flex-wrap gap-1.5">
                            {categoriasFemeninas.map((cat) => (
                              <button key={cat.id} type="button" onClick={() => toggleCategoria(cat.nombre, 'fem')} className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${categoriasFem.includes(cat.nombre) ? 'bg-pink-500 text-white' : 'bg-cardBorder text-textSecondary hover:bg-pink-500/20'}`}>
                                {cat.nombre}
                              </button>
                            ))}
                          </div>
                        )}
                      </motion.div>
                    )}

                    {categoriasFinales.length > 0 && (
                      <div className="bg-accent/5 border border-accent/20 rounded-lg p-2">
                        <p className="text-[10px] text-textSecondary mb-1">Categorías a crear:</p>
                        <div className="flex flex-wrap gap-1">
                          {categoriasFinales.map((cat, i) => (
                            <span key={i} className={`px-2 py-0.5 rounded text-[10px] font-bold ${cat.genero === 'masculino' ? 'bg-blue-500/20 text-blue-400' : 'bg-pink-500/20 text-pink-400'}`}>
                              {cat.nombre} {cat.genero === 'masculino' ? '♂' : '♀'}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Pago - Ancho Completo */}
                <div className="bg-cardHover rounded-lg p-2 sm:p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-textSecondary text-xs font-bold flex items-center gap-1.5">
                      <DollarSign size={12} />¿Requiere pago de inscripción?
                    </label>
                    <button type="button" onClick={() => setFormData({ ...formData, requierePago: !formData.requierePago })} className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${formData.requierePago ? 'bg-accent' : 'bg-cardBorder'}`}>
                      <span className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${formData.requierePago ? 'translate-x-5' : 'translate-x-1'}`} />
                    </button>
                  </div>

                  {formData.requierePago && (
                    <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-cardBorder">
                      <div>
                        <label className="block text-textSecondary text-xs font-bold mb-1">Monto *</label>
                        <Input type="number" min="0" value={formData.monto} onChange={(e) => setFormData({ ...formData, monto: parseInt(e.target.value) || 0 })} placeholder="Ej: 5000" required={formData.requierePago} />
                      </div>
                      <div>
                        <label className="block text-textSecondary text-xs font-bold mb-1">Alias/CBU/CVU *</label>
                        <Input value={formData.alias} onChange={(e) => setFormData({ ...formData, alias: e.target.value })} placeholder="Ej: torneo.padel" required={formData.requierePago} />
                      </div>
                      <div>
                        <label className="block text-textSecondary text-xs font-bold mb-1">Titular *</label>
                        <Input value={formData.titular} onChange={(e) => setFormData({ ...formData, titular: e.target.value })} placeholder="Ej: Juan Pérez" required={formData.requierePago} />
                      </div>
                      <div>
                        <label className="block text-textSecondary text-xs font-bold mb-1">Banco *</label>
                        <Input value={formData.banco} onChange={(e) => setFormData({ ...formData, banco: e.target.value })} placeholder="Ej: Banco Galicia" required={formData.requierePago} />
                      </div>
                    </motion.div>
                  )}
                </div>

                {/* Horarios - Ancho Completo - Colapsable en móvil */}
                <details className="bg-cardHover rounded-lg">
                  <summary className="p-2 sm:p-3 cursor-pointer text-textSecondary text-xs font-bold flex items-center gap-1.5">
                    <Clock size={12} />Horarios disponibles (opcional)
                  </summary>
                  <div className="p-2 sm:p-3 pt-0">
                    <p className="text-[10px] text-textSecondary mb-2">Define los horarios en los que se pueden programar partidos</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 sm:gap-3">
                      {/* Semana */}
                      <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-2">
                        <label className="block text-blue-400 text-[10px] font-bold mb-2">Lunes a Viernes</label>
                        {horariosDisponibles.semana.map((horario, index) => (
                          <div key={index} className="flex gap-1.5 items-end mb-2">
                            <div className="flex-1">
                              <label className="block text-[9px] text-textSecondary mb-0.5">Desde</label>
                              <select value={horario.desde} onChange={(e) => actualizarHorario('semana', index, 'desde', e.target.value)} className="w-full bg-background border border-cardBorder rounded px-1.5 py-1 text-[11px] text-textPrimary focus:outline-none focus:border-primary">
                                <option value="">--</option>
                                {OPCIONES_HORARIO.map(h => <option key={h} value={h}>{h}</option>)}
                              </select>
                            </div>
                            <div className="flex-1">
                              <label className="block text-[9px] text-textSecondary mb-0.5">Hasta</label>
                              <select value={horario.hasta} onChange={(e) => actualizarHorario('semana', index, 'hasta', e.target.value)} disabled={!horario.desde} className="w-full bg-background border border-cardBorder rounded px-1.5 py-1 text-[11px] text-textPrimary focus:outline-none focus:border-primary disabled:opacity-50">
                                <option value="">--</option>
                                {OPCIONES_HORARIO.filter(h => h > horario.desde).map(h => <option key={h} value={h}>{h}</option>)}
                              </select>
                            </div>
                            <button type="button" onClick={() => eliminarHorario('semana', index)} className="px-1.5 py-1 text-red-500 hover:bg-red-50 rounded text-xs">✕</button>
                          </div>
                        ))}
                        <button type="button" onClick={() => agregarHorario('semana')} className="w-full py-1.5 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded text-[10px] font-medium transition-colors">+ Agregar</button>
                      </div>

                      {/* Fin de Semana */}
                      <div className="bg-green-500/5 border border-green-500/20 rounded-lg p-2">
                        <label className="block text-green-400 text-[10px] font-bold mb-2">Sábado y Domingo</label>
                        {horariosDisponibles.finDeSemana.map((horario, index) => (
                          <div key={index} className="flex gap-1.5 items-end mb-2">
                            <div className="flex-1">
                              <label className="block text-[9px] text-textSecondary mb-0.5">Desde</label>
                              <select value={horario.desde} onChange={(e) => actualizarHorario('finDeSemana', index, 'desde', e.target.value)} className="w-full bg-background border border-cardBorder rounded px-1.5 py-1 text-[11px] text-textPrimary focus:outline-none focus:border-primary">
                                <option value="">--</option>
                                {OPCIONES_HORARIO.map(h => <option key={h} value={h}>{h}</option>)}
                              </select>
                            </div>
                            <div className="flex-1">
                              <label className="block text-[9px] text-textSecondary mb-0.5">Hasta</label>
                              <select value={horario.hasta} onChange={(e) => actualizarHorario('finDeSemana', index, 'hasta', e.target.value)} disabled={!horario.desde} className="w-full bg-background border border-cardBorder rounded px-1.5 py-1 text-[11px] text-textPrimary focus:outline-none focus:border-primary disabled:opacity-50">
                                <option value="">--</option>
                                {OPCIONES_HORARIO.filter(h => h > horario.desde).map(h => <option key={h} value={h}>{h}</option>)}
                              </select>
                            </div>
                            <button type="button" onClick={() => eliminarHorario('finDeSemana', index)} className="px-1.5 py-1 text-red-500 hover:bg-red-50 rounded text-xs">✕</button>
                          </div>
                        ))}
                        <button type="button" onClick={() => agregarHorario('finDeSemana')} className="w-full py-1.5 bg-green-500/10 hover:bg-green-500/20 text-green-400 rounded text-[10px] font-medium transition-colors">+ Agregar</button>
                      </div>
                    </div>
                  </div>
                </details>

                {/* Botones */}
                <div className="flex gap-2 pt-2 border-t border-cardBorder sticky bottom-0 bg-cardBg pb-2">
                  <Button type="button" variant="ghost" onClick={() => { limpiarError(); onClose(); }} className="flex-1 text-xs sm:text-sm py-2.5 sm:py-3" disabled={loading || creandoCategorias}>
                    Cancelar
                  </Button>
                  <Button type="submit" variant="accent" className="flex-1 text-xs sm:text-sm py-2.5 sm:py-3" disabled={loading || creandoCategorias || categoriasFinales.length === 0}>
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
