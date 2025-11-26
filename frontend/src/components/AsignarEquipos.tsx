import { useState } from 'react';
import { Shuffle, Crown } from 'lucide-react';
import Button from './Button';
import { Jugador } from '../utils/types';

interface AsignarEquiposProps {
  jugadores: Jugador[];
  onAsignar: (equipos: { [key: string]: number }) => void;
  onCancelar: () => void;
  loading: boolean;
  creadorId?: number;
}

export default function AsignarEquipos({ jugadores, onAsignar, onCancelar, loading, creadorId }: AsignarEquiposProps) {
  const [equipoA, setEquipoA] = useState<Jugador[]>([]);
  const [equipoB, setEquipoB] = useState<Jugador[]>([]);
  const [sinAsignar, setSinAsignar] = useState<Jugador[]>(jugadores);

  const moverAEquipo = (jugador: Jugador, equipo: 'A' | 'B') => {
    if (equipo === 'A' && equipoA.length >= 2) return;
    if (equipo === 'B' && equipoB.length >= 2) return;

    setSinAsignar(prev => prev.filter(j => j.id !== jugador.id));
    
    if (equipo === 'A') {
      setEquipoA(prev => [...prev, jugador]);
    } else {
      setEquipoB(prev => [...prev, jugador]);
    }
  };

  const quitarDeEquipo = (jugador: Jugador, equipo: 'A' | 'B') => {
    if (equipo === 'A') {
      setEquipoA(prev => prev.filter(j => j.id !== jugador.id));
    } else {
      setEquipoB(prev => prev.filter(j => j.id !== jugador.id));
    }
    setSinAsignar(prev => [...prev, jugador]);
  };

  const asignarAutomatico = () => {
    const todosJugadores = [...sinAsignar, ...equipoA, ...equipoB];
    const ordenados = [...todosJugadores].sort((a, b) => (b.rating || 0) - (a.rating || 0));
    
    setEquipoA([ordenados[0], ordenados[3]]);
    setEquipoB([ordenados[1], ordenados[2]]);
    setSinAsignar([]);
  };

  const handleConfirmar = () => {
    if (equipoA.length !== 2 || equipoB.length !== 2) {
      alert('Debes asignar 2 jugadores a cada equipo');
      return;
    }

    const equipos: { [key: string]: number } = {};
    equipoA.forEach(j => equipos[j.id] = 1);
    equipoB.forEach(j => equipos[j.id] = 2);
    
    onAsignar(equipos);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-textPrimary font-bold text-lg">Asignar Equipos</h3>
        <Button
          variant="ghost"
          onClick={asignarAutomatico}
          className="text-xs flex items-center gap-1"
        >
          <Shuffle size={14} />
          Auto
        </Button>
      </div>

      {/* Jugadores sin asignar */}
      {sinAsignar.length > 0 && (
        <div className="bg-background rounded-lg p-3">
          <p className="text-textSecondary text-xs mb-2">Sin asignar:</p>
          <div className="space-y-2">
            {sinAsignar.map(jugador => (
              <div key={jugador.id} className="flex items-center gap-2 bg-cardBg rounded-md p-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xs font-bold">
                  {jugador.nombre.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-textPrimary text-sm font-semibold truncate">{jugador.nombre}</p>
                  <p className="text-textSecondary text-xs">Rating: {jugador.rating || 1500}</p>
                </div>
                <div className="flex gap-1">
                  <button
                    onClick={() => moverAEquipo(jugador, 'A')}
                    disabled={equipoA.length >= 2}
                    className="bg-primary/20 hover:bg-primary/30 disabled:opacity-30 text-primary px-2 py-1 rounded text-xs font-bold"
                  >
                    A
                  </button>
                  <button
                    onClick={() => moverAEquipo(jugador, 'B')}
                    disabled={equipoB.length >= 2}
                    className="bg-secondary/20 hover:bg-secondary/30 disabled:opacity-30 text-secondary px-2 py-1 rounded text-xs font-bold"
                  >
                    B
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Equipos */}
      <div className="grid grid-cols-2 gap-3">
        {/* Equipo A */}
        <div className="bg-primary/10 rounded-lg p-3 border border-primary/30">
          <p className="text-primary font-bold text-sm mb-2">EQUIPO A ({equipoA.length}/2)</p>
          <div className="space-y-2">
            {equipoA.map(jugador => {
              const esCreador = creadorId && jugador.id === creadorId.toString();
              return (
                <div key={jugador.id} className="bg-background rounded-md p-2">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1 flex-1 min-w-0">
                      <p className="text-textPrimary text-xs font-semibold truncate">{jugador.nombre}</p>
                      {esCreador && (
                        <Crown size={12} className="text-accent flex-shrink-0" />
                      )}
                    </div>
                    <button
                      onClick={() => quitarDeEquipo(jugador, 'A')}
                      className="text-red-500 text-xs flex-shrink-0"
                    >
                      ✕
                    </button>
                  </div>
                  <p className="text-textSecondary text-[10px]">Rating: {jugador.rating || 1500}</p>
                </div>
              );
            })}
            {equipoA.length < 2 && (
              <div className="bg-background/50 rounded-md p-2 border-2 border-dashed border-primary/30 text-center">
                <p className="text-textSecondary text-xs">Vacío</p>
              </div>
            )}
          </div>
        </div>

        {/* Equipo B */}
        <div className="bg-secondary/10 rounded-lg p-3 border border-secondary/30">
          <p className="text-secondary font-bold text-sm mb-2">EQUIPO B ({equipoB.length}/2)</p>
          <div className="space-y-2">
            {equipoB.map(jugador => {
              const esCreador = creadorId && jugador.id === creadorId.toString();
              return (
                <div key={jugador.id} className="bg-background rounded-md p-2">
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1 flex-1 min-w-0">
                      <p className="text-textPrimary text-xs font-semibold truncate">{jugador.nombre}</p>
                      {esCreador && (
                        <Crown size={12} className="text-accent flex-shrink-0" />
                      )}
                    </div>
                    <button
                      onClick={() => quitarDeEquipo(jugador, 'B')}
                      className="text-red-500 text-xs flex-shrink-0"
                    >
                      ✕
                    </button>
                  </div>
                  <p className="text-textSecondary text-[10px]">Rating: {jugador.rating || 1500}</p>
                </div>
              );
            })}
            {equipoB.length < 2 && (
              <div className="bg-background/50 rounded-md p-2 border-2 border-dashed border-secondary/30 text-center">
                <p className="text-textSecondary text-xs">Vacío</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Botones */}
      <div className="flex gap-2">
        <Button
          variant="ghost"
          onClick={onCancelar}
          disabled={loading}
          className="flex-1"
        >
          Cancelar
        </Button>
        <Button
          variant="primary"
          onClick={handleConfirmar}
          disabled={loading || equipoA.length !== 2 || equipoB.length !== 2}
          className="flex-1 relative"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="animate-spin">⚡</span>
              Asignando equipos...
            </span>
          ) : (
            'Confirmar Equipos'
          )}
        </Button>
      </div>
    </div>
  );
}
