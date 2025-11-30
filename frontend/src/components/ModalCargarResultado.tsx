import { useState } from 'react';
import { X, Plus, Minus } from 'lucide-react';
import { torneoService } from '../services/torneo.service';
import Button from './Button';

interface ModalCargarResultadoProps {
  isOpen: boolean;
  onClose: () => void;
  partido: any;
  torneoId: number;
  onResultadoCargado: () => void;
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
      onResultadoCargado();
    } catch (error: any) {
      console.error('Error al cargar resultado:', error);
      setError(error.response?.data?.detail || 'Error al cargar el resultado');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-textPrimary">Cargar Resultado</h2>
            <button
              onClick={onClose}
              className="text-textSecondary hover:text-textPrimary transition-colors"
            >
              <X size={24} />
            </button>
          </div>

          {/* Parejas */}
          <div className="mb-6 p-4 bg-background rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold text-textPrimary">
                {partido?.pareja1_nombre || `Pareja ${partido?.pareja1_id || '?'}`}
              </span>
              <span className="text-2xl font-bold text-primary">
                {sets.filter(s => s.completado && s.ganador === 'equipoA').length}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="font-bold text-textPrimary">
                {partido?.pareja2_nombre || `Pareja ${partido?.pareja2_id || '?'}`}
              </span>
              <span className="text-2xl font-bold text-primary">
                {sets.filter(s => s.completado && s.ganador === 'equipoB').length}
              </span>
            </div>
          </div>

          {/* Sets */}
          <div className="space-y-4 mb-6">
            {sets.map((set, index) => (
              <div key={index} className="p-4 bg-background rounded-lg">
                <h3 className="font-bold text-textPrimary mb-3">Set {index + 1}</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  {/* Equipo A */}
                  <div>
                    <label className="text-sm text-textSecondary mb-2 block">
                      {partido?.pareja1_nombre || `Pareja ${partido?.pareja1_id || '?'}`}
                    </label>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => actualizarGames(index, 'A', set.gamesEquipoA - 1)}
                      >
                        <Minus size={16} />
                      </Button>
                      <input
                        type="number"
                        min="0"
                        max="7"
                        value={set.gamesEquipoA}
                        onChange={(e) => actualizarGames(index, 'A', parseInt(e.target.value) || 0)}
                        className="w-16 text-center bg-card border border-cardBorder rounded-lg py-2 text-textPrimary font-bold text-xl"
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => actualizarGames(index, 'A', set.gamesEquipoA + 1)}
                      >
                        <Plus size={16} />
                      </Button>
                    </div>
                  </div>

                  {/* Equipo B */}
                  <div>
                    <label className="text-sm text-textSecondary mb-2 block">
                      {partido?.pareja2_nombre || `Pareja ${partido?.pareja2_id || '?'}`}
                    </label>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => actualizarGames(index, 'B', set.gamesEquipoB - 1)}
                      >
                        <Minus size={16} />
                      </Button>
                      <input
                        type="number"
                        min="0"
                        max="7"
                        value={set.gamesEquipoB}
                        onChange={(e) => actualizarGames(index, 'B', parseInt(e.target.value) || 0)}
                        className="w-16 text-center bg-card border border-cardBorder rounded-lg py-2 text-textPrimary font-bold text-xl"
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => actualizarGames(index, 'B', set.gamesEquipoB + 1)}
                      >
                        <Plus size={16} />
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Estado del set */}
                {set.completado && (
                  <div className="mt-3 p-2 bg-green-500/10 rounded text-center">
                    <span className="text-sm text-green-500 font-bold">
                      ✓ Set válido - Ganador: {set.ganador === 'equipoA' ? (partido?.pareja1_nombre || `Pareja ${partido?.pareja1_id}`) : (partido?.pareja2_nombre || `Pareja ${partido?.pareja2_id}`)}
                    </span>
                  </div>
                )}
                {!set.completado && (set.gamesEquipoA > 0 || set.gamesEquipoB > 0) && (
                  <div className="mt-3 p-2 bg-yellow-500/10 rounded text-center">
                    <span className="text-sm text-yellow-500">
                      Resultado inválido para pádel
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Botones para agregar/quitar sets */}
          <div className="flex gap-2 mb-6">
            {sets.length < 3 && (
              <Button variant="ghost" onClick={agregarSet} className="flex-1">
                <Plus size={16} className="mr-2" />
                Agregar 3er Set
              </Button>
            )}
            {sets.length > 2 && (
              <Button variant="ghost" onClick={quitarSet} className="flex-1">
                <Minus size={16} className="mr-2" />
                Quitar 3er Set
              </Button>
            )}
          </div>

          {/* Error */}
          {error && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
              <p className="text-red-500 text-sm">{error}</p>
            </div>
          )}

          {/* Acciones */}
          <div className="flex gap-3">
            <Button variant="ghost" onClick={onClose} className="flex-1">
              Cancelar
            </Button>
            <Button
              variant="accent"
              onClick={handleSubmit}
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Guardando...' : 'Guardar Resultado'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
