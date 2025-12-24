import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Plus, Minus, Trophy } from 'lucide-react';
import { torneoService } from '../services/torneo.service';
import Button from './Button';

interface ModalCargarResultadoProps {
  isOpen: boolean;
  onClose: () => void;
  partido: any;
  torneoId: number;
  onResultadoCargado: (partidoActualizado?: any) => void;
}

interface Set {
  gamesEquipoA: number;
  gamesEquipoB: number;
  ganador: 'equipoA' | 'equipoB' | null;
  completado: boolean;
}

export default function ModalCargarResultado({
  isOpen,
  onClose,
  partido,
  torneoId,
  onResultadoCargado
}: ModalCargarResultadoProps) {
  const [sets, setSets] = useState<Set[]>([
    { gamesEquipoA: 0, gamesEquipoB: 0, ganador: null, completado: false },
    { gamesEquipoA: 0, gamesEquipoB: 0, ganador: null, completado: false }
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const agregarSet = () => {
    if (sets.length < 3) {
      setSets([...sets, { gamesEquipoA: 0, gamesEquipoB: 0, ganador: null, completado: false }]);
    }
  };

  const quitarSet = () => {
    if (sets.length > 2) {
      setSets(sets.slice(0, -1));
    }
  };

  const actualizarGames = (setIndex: number, equipo: 'A' | 'B', valor: number) => {
    const nuevosSets = [...sets];
    
    // Limitar valores entre 0 y 7
    const valorLimitado = Math.max(0, Math.min(7, valor));
    
    if (equipo === 'A') {
      nuevosSets[setIndex].gamesEquipoA = valorLimitado;
    } else {
      nuevosSets[setIndex].gamesEquipoB = valorLimitado;
    }
    
    // Determinar ganador del set
    const gamesA = nuevosSets[setIndex].gamesEquipoA;
    const gamesB = nuevosSets[setIndex].gamesEquipoB;
    
    // Validar y marcar como completado si es válido
    const esValido = validarSet(gamesA, gamesB);
    if (esValido) {
      nuevosSets[setIndex].ganador = gamesA > gamesB ? 'equipoA' : 'equipoB';
      nuevosSets[setIndex].completado = true;
    } else {
      nuevosSets[setIndex].ganador = null;
      nuevosSets[setIndex].completado = false;
    }
    
    setSets(nuevosSets);
  };

  const validarSet = (gamesA: number, gamesB: number): boolean => {
    const mayor = Math.max(gamesA, gamesB);
    const menor = Math.min(gamesA, gamesB);
    
    // 6-0, 6-1, 6-2, 6-3, 6-4
    if (mayor === 6 && menor <= 4) return true;
    // 7-5
    if (mayor === 7 && menor === 5) return true;
    // 7-6 (tiebreak)
    if (mayor === 7 && menor === 6) return true;
    
    return false;
  };

  const validarResultado = (): string | null => {
    // Verificar que todos los sets estén completados
    const setsCompletados = sets.filter(s => s.completado);
    if (setsCompletados.length < 2) {
      return 'Debe completar al menos 2 sets';
    }

    // Contar sets ganados
    const setsEquipoA = setsCompletados.filter(s => s.ganador === 'equipoA').length;
    const setsEquipoB = setsCompletados.filter(s => s.ganador === 'equipoB').length;

    // Verificar que haya un ganador
    if (setsEquipoA < 2 && setsEquipoB < 2) {
      return 'Debe haber un ganador con al menos 2 sets';
    }

    // Si hay 3 sets, verificar que sea 2-1
    if (setsCompletados.length === 3) {
      if (!((setsEquipoA === 2 && setsEquipoB === 1) || (setsEquipoA === 1 && setsEquipoB === 2))) {
        return 'Con 3 sets, el resultado debe ser 2-1';
      }
    }

    return null;
  };

  const handleSubmit = async () => {
    const errorValidacion = validarResultado();
    if (errorValidacion) {
      setError(errorValidacion);
      return;
    }

    try {
      setLoading(true);
      setError('');

      const resultado = {
        sets: sets.filter(s => s.completado)
      };

      await torneoService.cargarResultado(torneoId, partido.id_partido, resultado);
      
      // Crear partido actualizado con el resultado
      const partidoActualizado = {
        ...partido,
        estado: 'confirmado',
        resultado_padel: resultado
      };
      
      onResultadoCargado(partidoActualizado);
    } catch (error: any) {
      console.error('Error al cargar resultado:', error);
      setError(error.response?.data?.detail || 'Error al cargar el resultado');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-2 md:p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-card rounded-xl max-w-2xl w-full max-h-[95vh] md:max-h-[90vh] overflow-y-auto shadow-2xl border border-cardBorder"
      >
        <div className="p-4 md:p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4 md:mb-6 pb-3 md:pb-4 border-b border-cardBorder">
            <div className="flex items-center gap-2 md:gap-3">
              <div className="bg-gradient-to-br from-accent to-primary p-1.5 md:p-2 rounded-lg">
                <Trophy size={16} className="text-white md:w-5 md:h-5" />
              </div>
              <h2 className="text-lg md:text-2xl font-bold text-textPrimary">Cargar Resultado</h2>
            </div>
            <button
              onClick={onClose}
              className="text-textSecondary hover:text-red-500 transition-colors p-1.5 md:p-2 hover:bg-red-500/10 rounded-lg"
            >
              <X size={20} className="md:w-6 md:h-6" />
            </button>
          </div>

          {/* Parejas - Marcador */}
          <div className="mb-4 md:mb-6 p-3 md:p-5 bg-gradient-to-br from-background to-background/50 rounded-xl border border-cardBorder">
            <div className="flex items-center justify-between mb-2 md:mb-3 p-2 md:p-3 bg-card rounded-lg">
              <span className="font-bold text-textPrimary text-sm md:text-lg truncate flex-1 mr-2">
                {partido?.pareja1_nombre || `Pareja ${partido?.pareja1_id || '?'}`}
              </span>
              <div className="bg-primary/10 px-3 md:px-4 py-1 md:py-2 rounded-lg">
                <span className="text-2xl md:text-3xl font-bold text-primary">
                  {sets.filter(s => s.completado && s.ganador === 'equipoA').length}
                </span>
              </div>
            </div>
            <div className="flex items-center justify-center my-1.5 md:my-2">
              <div className="h-px flex-1 bg-cardBorder" />
              <span className="px-2 md:px-3 text-[10px] md:text-xs font-bold text-textSecondary">VS</span>
              <div className="h-px flex-1 bg-cardBorder" />
            </div>
            <div className="flex items-center justify-between p-2 md:p-3 bg-card rounded-lg">
              <span className="font-bold text-textPrimary text-sm md:text-lg truncate flex-1 mr-2">
                {partido?.pareja2_nombre || `Pareja ${partido?.pareja2_id || '?'}`}
              </span>
              <div className="bg-primary/10 px-3 md:px-4 py-1 md:py-2 rounded-lg">
                <span className="text-2xl md:text-3xl font-bold text-primary">
                  {sets.filter(s => s.completado && s.ganador === 'equipoB').length}
                </span>
              </div>
            </div>
          </div>

          {/* Sets */}
          <div className="space-y-3 md:space-y-4 mb-4 md:mb-6">
            {sets.map((set, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-3 md:p-4 bg-background rounded-xl border border-cardBorder"
              >
                <div className="flex items-center justify-between mb-2 md:mb-3">
                  <h3 className="font-bold text-textPrimary text-sm md:text-base">Set {index + 1}</h3>
                  {set.completado && (
                    <div className="flex items-center gap-1 text-green-500 text-[10px] md:text-xs font-bold">
                      <Trophy size={10} className="md:w-3 md:h-3" />
                      <span>Válido</span>
                    </div>
                  )}
                </div>
                
                <div className="grid grid-cols-2 gap-2 md:gap-4">
                  {/* Equipo A */}
                  <div>
                    <label className="text-[10px] md:text-sm text-textSecondary mb-1 md:mb-2 block truncate">
                      {partido?.pareja1_nombre || `Pareja ${partido?.pareja1_id || '?'}`}
                    </label>
                    <div className="flex items-center gap-1 md:gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => actualizarGames(index, 'A', set.gamesEquipoA - 1)}
                        className="p-1 md:p-2"
                      >
                        <Minus size={14} className="md:w-4 md:h-4" />
                      </Button>
                      <input
                        type="number"
                        min="0"
                        max="7"
                        value={set.gamesEquipoA}
                        onChange={(e) => actualizarGames(index, 'A', parseInt(e.target.value) || 0)}
                        className="w-12 md:w-16 text-center bg-card border border-cardBorder rounded-lg py-1.5 md:py-2 text-textPrimary font-bold text-lg md:text-xl"
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => actualizarGames(index, 'A', set.gamesEquipoA + 1)}
                        className="p-1 md:p-2"
                      >
                        <Plus size={14} className="md:w-4 md:h-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Equipo B */}
                  <div>
                    <label className="text-[10px] md:text-sm text-textSecondary mb-1 md:mb-2 block truncate">
                      {partido?.pareja2_nombre || `Pareja ${partido?.pareja2_id || '?'}`}
                    </label>
                    <div className="flex items-center gap-1 md:gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => actualizarGames(index, 'B', set.gamesEquipoB - 1)}
                        className="p-1 md:p-2"
                      >
                        <Minus size={14} className="md:w-4 md:h-4" />
                      </Button>
                      <input
                        type="number"
                        min="0"
                        max="7"
                        value={set.gamesEquipoB}
                        onChange={(e) => actualizarGames(index, 'B', parseInt(e.target.value) || 0)}
                        className="w-12 md:w-16 text-center bg-card border border-cardBorder rounded-lg py-1.5 md:py-2 text-textPrimary font-bold text-lg md:text-xl"
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => actualizarGames(index, 'B', set.gamesEquipoB + 1)}
                        className="p-1 md:p-2"
                      >
                        <Plus size={14} className="md:w-4 md:h-4" />
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Estado del set */}
                {set.completado && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 md:mt-3 p-2 md:p-3 bg-gradient-to-r from-green-500/10 to-green-500/5 rounded-lg border border-green-500/20"
                  >
                    <div className="flex items-center justify-center gap-1.5 md:gap-2">
                      <Trophy size={12} className="text-green-500 flex-shrink-0 md:w-[14px] md:h-[14px]" />
                      <span className="text-xs md:text-sm text-green-500 font-bold text-center">
                        Ganador: {set.ganador === 'equipoA' ? (partido?.pareja1_nombre || `Pareja ${partido?.pareja1_id}`) : (partido?.pareja2_nombre || `Pareja ${partido?.pareja2_id}`)}
                      </span>
                    </div>
                  </motion.div>
                )}
                {!set.completado && (set.gamesEquipoA > 0 || set.gamesEquipoB > 0) && (
                  <div className="mt-2 md:mt-3 p-2 md:p-3 bg-yellow-500/10 rounded-lg border border-yellow-500/20 text-center">
                    <span className="text-xs md:text-sm text-yellow-500 font-medium">
                      ⚠ Resultado inválido para pádel
                    </span>
                  </div>
                )}
              </motion.div>
            ))}
          </div>

          {/* Botones para agregar/quitar sets */}
          <div className="flex gap-2 mb-4 md:mb-6">
            {sets.length < 3 && (
              <Button variant="ghost" onClick={agregarSet} className="flex-1 text-xs md:text-sm py-2">
                <Plus size={14} className="mr-1 md:mr-2 md:w-4 md:h-4" />
                Agregar 3er Set
              </Button>
            )}
            {sets.length > 2 && (
              <Button variant="ghost" onClick={quitarSet} className="flex-1 text-xs md:text-sm py-2">
                <Minus size={14} className="mr-1 md:mr-2 md:w-4 md:h-4" />
                Quitar 3er Set
              </Button>
            )}
          </div>

          {/* Error */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-3 md:mb-4 p-3 md:p-4 bg-red-500/10 border border-red-500/20 rounded-lg"
            >
              <p className="text-red-500 text-xs md:text-sm font-medium flex items-center gap-2">
                <span className="text-base md:text-lg flex-shrink-0">⚠</span>
                <span className="flex-1">{error}</span>
              </p>
            </motion.div>
          )}

          {/* Acciones */}
          <div className="flex gap-2 md:gap-3 pt-3 md:pt-4 border-t border-cardBorder">
            <Button 
              variant="ghost" 
              onClick={onClose} 
              className="flex-1 hover:bg-red-500/10 hover:text-red-500 text-xs md:text-base py-2 md:py-3"
            >
              Cancelar
            </Button>
            <Button
              variant="accent"
              onClick={handleSubmit}
              disabled={loading || validarResultado() !== null}
              className="flex-1 gap-1.5 md:gap-2 text-xs md:text-base py-2 md:py-3"
            >
              {loading ? (
                <>
                  <div className="w-3 h-3 md:w-4 md:h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Guardando...</span>
                </>
              ) : (
                <>
                  <Trophy size={14} className="md:w-4 md:h-4" />
                  <span>Guardar</span>
                </>
              )}
            </Button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
