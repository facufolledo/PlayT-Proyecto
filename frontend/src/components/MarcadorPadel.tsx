import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, Plus, Minus, Trophy, AlertCircle, CheckCircle, Flag } from 'lucide-react';
import Modal from './Modal';
import Button from './Button';
import { Sala } from '../utils/types';
import { useSalas } from '../context/SalasContext';
import { useAuth } from '../context/AuthContext';
import { 
  Set, 
  SuperTiebreak, 
  FormatoPartido, 
  ResultadoPartido 
} from '../utils/padelTypes';
import {
  validarSet,
  setCompleto,
  requiereTiebreak,
  validarSuperTiebreak,
  supertiebreakCompleto,
  ganadorSet,
  ganadorSuperTiebreak,
  contarSetsGanados,
  requiereSuperTiebreak,
  puedeIncrementarGame,
  puedeIncrementarPunto,
  obtenerMensajeError
} from '../utils/padelValidation';

interface MarcadorPadelProps {
  isOpen: boolean;
  onClose: () => void;
  sala: Sala | null;
}

export default function MarcadorPadel({ isOpen, onClose, sala }: MarcadorPadelProps) {
  const { updateSala } = useSalas();
  const { usuario } = useAuth();
  
  const [formato, setFormato] = useState<FormatoPartido>('best_of_3');
  const [sets, setSets] = useState<Set[]>([
    { gamesEquipoA: 0, gamesEquipoB: 0, completado: false },
    { gamesEquipoA: 0, gamesEquipoB: 0, completado: false },
    { gamesEquipoA: 0, gamesEquipoB: 0, completado: false }
  ]);
  const [supertiebreak, setSupertiebreak] = useState<SuperTiebreak>({
    puntosEquipoA: 0,
    puntosEquipoB: 0,
    completado: false
  });
  const [error, setError] = useState('');
  const [mostrarSupertiebreak, setMostrarSupertiebreak] = useState(false);

  useEffect(() => {
    if (sala?.resultado) {
      // Cargar resultado existente
      const resultado = sala.resultado as ResultadoPartido;
      setFormato(resultado.formato);
      setSets(resultado.sets);
      if (resultado.supertiebreak) {
        setSupertiebreak(resultado.supertiebreak);
        setMostrarSupertiebreak(true);
      }
    }
  }, [sala]);

  if (!sala) return null;

  const esCreador = usuario?.id_usuario?.toString() === sala.creador_id?.toString();
  const yaConfirmado = sala.estadoConfirmacion === 'confirmado';
  const pendienteConfirmacion = sala.estadoConfirmacion === 'pendiente_confirmacion';

  // Actualizar games de un set
  const handleUpdateGames = (setIndex: number, equipo: 'equipoA' | 'equipoB', delta: number) => {
    setError('');
    const newSets = [...sets];
    const currentSet = newSets[setIndex];

    const newGamesA = equipo === 'equipoA' 
      ? Math.max(0, currentSet.gamesEquipoA + delta)
      : currentSet.gamesEquipoA;
    const newGamesB = equipo === 'equipoB'
      ? Math.max(0, currentSet.gamesEquipoB + delta)
      : currentSet.gamesEquipoB;

    // Validar si se puede hacer el cambio
    if (delta > 0) {
      const puede = puedeIncrementarGame(currentSet.gamesEquipoA, currentSet.gamesEquipoB);
      if (equipo === 'equipoA' && !puede.equipoA) {
        setError('No se puede incrementar más este set');
        return;
      }
      if (equipo === 'equipoB' && !puede.equipoB) {
        setError('No se puede incrementar más este set');
        return;
      }
    }

    // Actualizar el set
    currentSet.gamesEquipoA = newGamesA;
    currentSet.gamesEquipoB = newGamesB;

    // Verificar si el set está completo
    if (setCompleto(newGamesA, newGamesB)) {
      currentSet.completado = true;
      currentSet.ganador = ganadorSet(newGamesA, newGamesB) || undefined;
      
      // Verificar si se debe jugar supertiebreak
      if (setIndex === 1 && requiereSuperTiebreak(newSets)) {
        setMostrarSupertiebreak(true);
      }
    } else {
      currentSet.completado = false;
      currentSet.ganador = undefined;
    }

    setSets(newSets);

    // Iniciar partido si estaba programado
    if (sala.estado === 'programada') {
      updateSala(sala.id, { estado: 'activa' });
    }
  };

  // Actualizar puntos del supertiebreak
  const handleUpdatePuntos = (equipo: 'equipoA' | 'equipoB', delta: number) => {
    setError('');
    const newPuntosA = equipo === 'equipoA'
      ? Math.max(0, supertiebreak.puntosEquipoA + delta)
      : supertiebreak.puntosEquipoA;
    const newPuntosB = equipo === 'equipoB'
      ? Math.max(0, supertiebreak.puntosEquipoB + delta)
      : supertiebreak.puntosEquipoB;

    // Validar si se puede hacer el cambio
    if (delta > 0) {
      const puede = puedeIncrementarPunto(supertiebreak.puntosEquipoA, supertiebreak.puntosEquipoB);
      if (equipo === 'equipoA' && !puede.equipoA) {
        setError('El supertiebreak ya está completo');
        return;
      }
      if (equipo === 'equipoB' && !puede.equipoB) {
        setError('El supertiebreak ya está completo');
        return;
      }
    }

    const newSupertiebreak = {
      puntosEquipoA: newPuntosA,
      puntosEquipoB: newPuntosB,
      completado: supertiebreakCompleto(newPuntosA, newPuntosB),
      ganador: ganadorSuperTiebreak(newPuntosA, newPuntosB) || undefined
    };

    setSupertiebreak(newSupertiebreak);
  };

  // Guardar resultado (solo creador)
  const handleGuardarResultado = () => {
    setError('');

    // Validar que todos los sets necesarios estén completos
    const setsGanados = contarSetsGanados(sets);
    const partidoCompleto = setsGanados.equipoA === 2 || setsGanados.equipoB === 2 ||
      (mostrarSupertiebreak && supertiebreak.completado);

    if (!partidoCompleto) {
      setError('Debes completar el partido antes de guardar el resultado');
      return;
    }

    // Determinar ganador
    let ganador: 'equipoA' | 'equipoB';
    if (mostrarSupertiebreak && supertiebreak.completado) {
      ganador = supertiebreak.ganador!;
    } else {
      ganador = setsGanados.equipoA > setsGanados.equipoB ? 'equipoA' : 'equipoB';
    }

    const resultado: ResultadoPartido = {
      formato,
      sets: sets.filter(s => s.completado),
      supertiebreak: mostrarSupertiebreak ? supertiebreak : undefined,
      ganador,
      completado: true,
      creadoPor: usuario?.id_usuario?.toString(),
      confirmadoPor: [usuario?.id_usuario?.toString() || '']
    };

    // Actualizar sala con resultado
    updateSala(sala.id, {
      resultado,
      estadoConfirmacion: 'pendiente_confirmacion',
      ganador
    });

    onClose();
  };

  // Confirmar resultado (rival)
  const handleConfirmarResultado = () => {
    if (!sala.resultado) return;

    const resultado = sala.resultado as ResultadoPartido;
    resultado.confirmadoPor = [
      ...(resultado.confirmadoPor || []),
      usuario?.id_usuario?.toString() || ''
    ];

    updateSala(sala.id, {
      resultado,
      estadoConfirmacion: 'confirmado'
    });

    // TODO: Enviar al backend para calcular Elo

    onClose();
  };

  // Reportar resultado (rival)
  const handleReportarResultado = () => {
    if (!sala.resultado) return;

    const resultado = sala.resultado as ResultadoPartido;
    resultado.reportadoPor = [
      ...(resultado.reportadoPor || []),
      usuario?.id_usuario?.toString() || ''
    ];

    updateSala(sala.id, {
      resultado,
      estadoConfirmacion: 'disputado'
    });

    onClose();
  };

  const setsGanados = contarSetsGanados(sets);

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="bg-cardBg rounded-2xl md:rounded-3xl p-4 md:p-6 w-full max-w-4xl border border-cardBorder shadow-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 md:mb-6">
          <div className="flex-1 min-w-0">
            <h2 className="text-lg md:text-2xl font-bold text-textPrimary mb-1 truncate">
              {sala.nombre}
            </h2>
            <p className="text-textSecondary text-[10px] md:text-sm leading-tight">
              <span className="hidden sm:inline">Formato: Best of 3 (6 games) • Set 3: SuperTieBreak a 10</span>
              <span className="sm:hidden">Best of 3 • ST a 10</span>
            </p>
          </div>
          <motion.button
            onClick={onClose}
            whileHover={{ scale: 1.1, rotate: 90 }}
            whileTap={{ scale: 0.9 }}
            className="text-textSecondary hover:text-textPrimary transition-colors bg-cardBorder rounded-full p-2 flex-shrink-0 ml-2"
          >
            <X size={20} className="md:w-6 md:h-6" />
          </motion.button>
        </div>

        {/* Mensaje de error */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 mb-4 flex items-center gap-2"
          >
            <AlertCircle size={18} className="text-red-500 flex-shrink-0" />
            <p className="text-red-500 text-sm">{error}</p>
          </motion.div>
        )}

        {/* Estado del partido */}
        {yaConfirmado && (
          <div className="bg-secondary/10 border border-secondary/50 rounded-lg p-3 mb-4 flex items-center gap-2">
            <CheckCircle size={18} className="text-secondary flex-shrink-0" />
            <p className="text-secondary text-sm font-bold">
              Partido confirmado por ambos jugadores
            </p>
          </div>
        )}

        {pendienteConfirmacion && !esCreador && (
          <div className="bg-accent/10 border border-accent/50 rounded-lg p-3 mb-4 flex items-center gap-2">
            <Flag size={18} className="text-accent flex-shrink-0" />
            <p className="text-accent text-sm font-bold">
              Resultado cargado por el creador. Por favor, confirma o reporta.
            </p>
          </div>
        )}

        {/* Nombres de jugadores */}
        <div className="grid grid-cols-2 gap-2 md:gap-4 mb-4 md:mb-6">
          <div className="bg-primary/10 rounded-lg p-2 md:p-3 border border-primary/30">
            <h3 className="text-primary font-black text-xs md:text-base mb-1 md:mb-2">EQUIPO A</h3>
            <p className="text-textPrimary font-semibold text-[10px] md:text-sm truncate leading-tight">
              {sala.equipoA.jugador1.nombre}
            </p>
            <p className="text-textPrimary font-semibold text-[10px] md:text-sm truncate leading-tight">
              {sala.equipoA.jugador2.nombre}
            </p>
          </div>
          <div className="bg-secondary/10 rounded-lg p-2 md:p-3 border border-secondary/30">
            <h3 className="text-secondary font-black text-xs md:text-base mb-1 md:mb-2">EQUIPO B</h3>
            <p className="text-textPrimary font-semibold text-[10px] md:text-sm truncate leading-tight">
              {sala.equipoB.jugador1.nombre}
            </p>
            <p className="text-textPrimary font-semibold text-[10px] md:text-sm truncate leading-tight">
              {sala.equipoB.jugador2.nombre}
            </p>
          </div>
        </div>

        {/* Marcador de sets */}
        <div className="space-y-2 md:space-y-4 mb-4 md:mb-6">
          {sets.slice(0, mostrarSupertiebreak ? 2 : 3).map((set, index) => (
            <SetDisplay
              key={index}
              setNumber={index + 1}
              set={set}
              onUpdateGames={(equipo, delta) => handleUpdateGames(index, equipo, delta)}
              disabled={yaConfirmado || (pendienteConfirmacion && !esCreador)}
              esCreador={esCreador}
            />
          ))}

          {/* SuperTiebreak */}
          {mostrarSupertiebreak && (
            <SuperTiebreakDisplay
              supertiebreak={supertiebreak}
              onUpdatePuntos={handleUpdatePuntos}
              disabled={yaConfirmado || (pendienteConfirmacion && !esCreador)}
              esCreador={esCreador}
            />
          )}
        </div>

        {/* Resumen */}
        <div className="bg-background rounded-lg p-3 md:p-4 mb-3 md:mb-4">
          <div className="flex items-center justify-between">
            <div className="text-center flex-1">
              <p className="text-textSecondary text-[10px] md:text-xs mb-1">Sets Ganados</p>
              <p className="text-primary text-xl md:text-3xl font-black">{setsGanados.equipoA}</p>
            </div>
            <div className="text-textSecondary font-bold text-sm md:text-base">-</div>
            <div className="text-center flex-1">
              <p className="text-textSecondary text-[10px] md:text-xs mb-1">Sets Ganados</p>
              <p className="text-secondary text-xl md:text-3xl font-black">{setsGanados.equipoB}</p>
            </div>
          </div>
        </div>

        {/* Botones de acción */}
        {!yaConfirmado && (
          <div className="flex flex-col md:flex-row gap-2 md:gap-3">
            {esCreador && !pendienteConfirmacion && (
              <Button
                variant="primary"
                onClick={handleGuardarResultado}
                className="flex-1 flex items-center justify-center gap-2 text-sm md:text-base py-2.5 md:py-3"
              >
                <Trophy size={16} className="md:w-[18px] md:h-[18px]" />
                Guardar Resultado
              </Button>
            )}

            {!esCreador && pendienteConfirmacion && (
              <>
                <Button
                  variant="primary"
                  onClick={handleConfirmarResultado}
                  className="flex-1 flex items-center justify-center gap-2 text-sm md:text-base py-2.5 md:py-3"
                >
                  <CheckCircle size={16} className="md:w-[18px] md:h-[18px]" />
                  Confirmar Resultado
                </Button>
                <Button
                  variant="ghost"
                  onClick={handleReportarResultado}
                  className="flex-1 flex items-center justify-center gap-2 text-sm md:text-base py-2.5 md:py-3 bg-red-500/20 hover:bg-red-500/30 border-red-500/50"
                >
                  <Flag size={16} className="md:w-[18px] md:h-[18px]" />
                  Reportar
                </Button>
              </>
            )}
          </div>
        )}
      </div>
    </Modal>
  );
}

// Componente para mostrar un set
interface SetDisplayProps {
  setNumber: number;
  set: Set;
  onUpdateGames: (equipo: 'equipoA' | 'equipoB', delta: number) => void;
  disabled: boolean;
  esCreador: boolean;
}

function SetDisplay({ setNumber, set, onUpdateGames, disabled, esCreador }: SetDisplayProps) {
  const puedeModificar = esCreador && !disabled;

  return (
    <div className={`bg-background rounded-lg p-2 md:p-4 border ${set.completado ? 'border-accent/50' : 'border-cardBorder'}`}>
      <div className="flex items-center justify-between mb-2 md:mb-3">
        <h4 className="text-textPrimary font-bold text-xs md:text-base">SET {setNumber}</h4>
        {set.completado && (
          <span className="text-accent text-[10px] md:text-xs font-bold flex items-center gap-1">
            <CheckCircle size={12} className="md:w-[14px] md:h-[14px]" />
            <span className="hidden sm:inline">Completado</span>
            <span className="sm:hidden">✓</span>
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2 md:gap-4">
        {/* Equipo A */}
        <div className="text-center">
          <div className={`text-2xl md:text-4xl font-black mb-1.5 md:mb-2 ${set.ganador === 'equipoA' ? 'text-primary' : 'text-textPrimary'}`}>
            {set.gamesEquipoA}
          </div>
          {puedeModificar && !set.completado && (
            <div className="flex gap-1">
              <button
                onClick={() => onUpdateGames('equipoA', -1)}
                disabled={set.gamesEquipoA === 0}
                className="flex-1 bg-red-500/20 hover:bg-red-500/30 disabled:opacity-30 rounded p-1 md:p-1.5 transition-colors"
              >
                <Minus size={12} className="mx-auto md:w-[14px] md:h-[14px]" />
              </button>
              <button
                onClick={() => onUpdateGames('equipoA', 1)}
                className="flex-1 bg-primary/20 hover:bg-primary/30 rounded p-1 md:p-1.5 transition-colors"
              >
                <Plus size={12} className="mx-auto md:w-[14px] md:h-[14px]" />
              </button>
            </div>
          )}
        </div>

        {/* Equipo B */}
        <div className="text-center">
          <div className={`text-2xl md:text-4xl font-black mb-1.5 md:mb-2 ${set.ganador === 'equipoB' ? 'text-secondary' : 'text-textPrimary'}`}>
            {set.gamesEquipoB}
          </div>
          {puedeModificar && !set.completado && (
            <div className="flex gap-1">
              <button
                onClick={() => onUpdateGames('equipoB', -1)}
                disabled={set.gamesEquipoB === 0}
                className="flex-1 bg-red-500/20 hover:bg-red-500/30 disabled:opacity-30 rounded p-1 md:p-1.5 transition-colors"
              >
                <Minus size={12} className="mx-auto md:w-[14px] md:h-[14px]" />
              </button>
              <button
                onClick={() => onUpdateGames('equipoB', 1)}
                className="flex-1 bg-secondary/20 hover:bg-secondary/30 rounded p-1 md:p-1.5 transition-colors"
              >
                <Plus size={12} className="mx-auto md:w-[14px] md:h-[14px]" />
              </button>
            </div>
          )}
        </div>
      </div>

      {requiereTiebreak(set.gamesEquipoA, set.gamesEquipoB) && !set.completado && (
        <p className="text-accent text-[10px] md:text-xs text-center mt-1.5 md:mt-2">
          6-6: Debe jugarse tiebreak (resultado 7-6)
        </p>
      )}
    </div>
  );
}

// Componente para mostrar el supertiebreak
interface SuperTiebreakDisplayProps {
  supertiebreak: SuperTiebreak;
  onUpdatePuntos: (equipo: 'equipoA' | 'equipoB', delta: number) => void;
  disabled: boolean;
  esCreador: boolean;
}

function SuperTiebreakDisplay({ supertiebreak, onUpdatePuntos, disabled, esCreador }: SuperTiebreakDisplayProps) {
  const puedeModificar = esCreador && !disabled;

  return (
    <div className={`bg-gradient-to-br from-accent/10 to-yellow-500/10 rounded-lg p-2 md:p-4 border ${supertiebreak.completado ? 'border-accent' : 'border-accent/50'}`}>
      <div className="flex items-center justify-between mb-2 md:mb-3">
        <h4 className="text-accent font-black text-xs md:text-base">
          <span className="hidden sm:inline">SUPERTIEBREAK (a 10 puntos)</span>
          <span className="sm:hidden">SUPERTIEBREAK</span>
        </h4>
        {supertiebreak.completado && (
          <span className="text-accent text-[10px] md:text-xs font-bold flex items-center gap-1">
            <Trophy size={12} className="md:w-[14px] md:h-[14px]" />
            <span className="hidden sm:inline">Completado</span>
            <span className="sm:hidden">✓</span>
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2 md:gap-4">
        {/* Equipo A */}
        <div className="text-center">
          <div className={`text-3xl md:text-5xl font-black mb-1.5 md:mb-2 ${supertiebreak.ganador === 'equipoA' ? 'text-primary' : 'text-textPrimary'}`}>
            {supertiebreak.puntosEquipoA}
          </div>
          {puedeModificar && !supertiebreak.completado && (
            <div className="flex gap-1">
              <button
                onClick={() => onUpdatePuntos('equipoA', -1)}
                disabled={supertiebreak.puntosEquipoA === 0}
                className="flex-1 bg-red-500/20 hover:bg-red-500/30 disabled:opacity-30 rounded p-1 md:p-1.5 transition-colors"
              >
                <Minus size={12} className="mx-auto md:w-[14px] md:h-[14px]" />
              </button>
              <button
                onClick={() => onUpdatePuntos('equipoA', 1)}
                className="flex-1 bg-primary/20 hover:bg-primary/30 rounded p-1 md:p-1.5 transition-colors"
              >
                <Plus size={12} className="mx-auto md:w-[14px] md:h-[14px]" />
              </button>
            </div>
          )}
        </div>

        {/* Equipo B */}
        <div className="text-center">
          <div className={`text-3xl md:text-5xl font-black mb-1.5 md:mb-2 ${supertiebreak.ganador === 'equipoB' ? 'text-secondary' : 'text-textPrimary'}`}>
            {supertiebreak.puntosEquipoB}
          </div>
          {puedeModificar && !supertiebreak.completado && (
            <div className="flex gap-1">
              <button
                onClick={() => onUpdatePuntos('equipoB', -1)}
                disabled={supertiebreak.puntosEquipoB === 0}
                className="flex-1 bg-red-500/20 hover:bg-red-500/30 disabled:opacity-30 rounded p-1 md:p-1.5 transition-colors"
              >
                <Minus size={12} className="mx-auto md:w-[14px] md:h-[14px]" />
              </button>
              <button
                onClick={() => onUpdatePuntos('equipoB', 1)}
                className="flex-1 bg-secondary/20 hover:bg-secondary/30 rounded p-1 md:p-1.5 transition-colors"
              >
                <Plus size={12} className="mx-auto md:w-[14px] md:h-[14px]" />
              </button>
            </div>
          )}
        </div>
      </div>

      <p className="text-textSecondary text-[10px] md:text-xs text-center mt-1.5 md:mt-2">
        Mínimo 10 puntos • Ventaja de 2 puntos
      </p>
    </div>
  );
}
