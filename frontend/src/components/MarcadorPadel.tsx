import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, Plus, Minus, Trophy, CheckCircle, Flag, Crown } from 'lucide-react';
import Button from './Button';
import ModalExito from './ModalExito';
import ModalConfirmacionExitosa from './ModalConfirmacionExitosa';
import { PlayerLink } from './UserLink';
import { Sala } from '../utils/types';
import { useSalas } from '../context/SalasContext';
import { useAuth } from '../context/AuthContext';
import { salaService } from '../services/sala.service';

interface MarcadorPadelProps {
  isOpen: boolean;
  onClose: () => void;
  sala: Sala | null;
}

interface Set {
  gamesEquipoA: number;
  gamesEquipoB: number;
  ganador: 'equipoA' | 'equipoB' | null;
  completado: boolean;
  esSuperTiebreak?: boolean;
}

export default function MarcadorPadel({ isOpen, onClose, sala }: MarcadorPadelProps) {
  const { cargarSalas } = useSalas();
  const { usuario, reloadUser } = useAuth();
  
  const [sets, setSets] = useState<Set[]>([
    { gamesEquipoA: 0, gamesEquipoB: 0, ganador: null, completado: false },
    { gamesEquipoA: 0, gamesEquipoB: 0, ganador: null, completado: false }
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mostrarModalExito, setMostrarModalExito] = useState(false);
  const [mostrarModalConfirmacion, setMostrarModalConfirmacion] = useState(false);
  const [datosConfirmacion, setDatosConfirmacion] = useState<any>(null);

  const esCreador = usuario?.id_usuario?.toString() === sala?.creador_id?.toString();
  const yaConfirmado = sala?.estadoConfirmacion === 'confirmado';
  const pendienteConfirmacion = sala?.estadoConfirmacion === 'pendiente_confirmacion';
  const puedeEditar = esCreador && !yaConfirmado;

  useEffect(() => {
    if (isOpen && sala?.resultado?.sets) {
      const setsExistentes = sala.resultado.sets.map((s: any) => ({
        gamesEquipoA: s.gamesEquipoA || 0,
        gamesEquipoB: s.gamesEquipoB || 0,
        ganador: s.ganador || null,
        completado: s.completado || false,
        esSuperTiebreak: s.esSuperTiebreak || false
      }));
      setSets(setsExistentes.length >= 2 ? setsExistentes : [
        { gamesEquipoA: 0, gamesEquipoB: 0, ganador: null, completado: false },
        { gamesEquipoA: 0, gamesEquipoB: 0, ganador: null, completado: false }
      ]);
    } else if (isOpen) {
      setSets([
        { gamesEquipoA: 0, gamesEquipoB: 0, ganador: null, completado: false },
        { gamesEquipoA: 0, gamesEquipoB: 0, ganador: null, completado: false }
      ]);
    }
  }, [isOpen, sala?.resultado]);

  if (!isOpen || !sala) return null;

  // Validar set normal (6 games)
  const validarSetNormal = (gamesA: number, gamesB: number): boolean => {
    const mayor = Math.max(gamesA, gamesB);
    const menor = Math.min(gamesA, gamesB);
    if (mayor === 6 && menor <= 4) return true;
    if (mayor === 7 && menor === 5) return true;
    if (mayor === 7 && menor === 6) return true;
    return false;
  };

  // Validar supertiebreak (10 puntos, diferencia de 2)
  const validarSuperTiebreak = (puntosA: number, puntosB: number): boolean => {
    const mayor = Math.max(puntosA, puntosB);
    const menor = Math.min(puntosA, puntosB);
    // Gana con 10+ y diferencia de 2
    if (mayor >= 10 && (mayor - menor) >= 2) return true;
    return false;
  };

  const actualizarGames = (setIndex: number, equipo: 'A' | 'B', delta: number) => {
    if (!puedeEditar) return;
    const nuevosSets = [...sets];
    const set = nuevosSets[setIndex];
    const esSuperTiebreak = set.esSuperTiebreak;
    const maxValor = esSuperTiebreak ? 99 : 7; // Supertiebreak puede ir más alto
    
    if (equipo === 'A') {
      set.gamesEquipoA = Math.max(0, Math.min(maxValor, set.gamesEquipoA + delta));
    } else {
      set.gamesEquipoB = Math.max(0, Math.min(maxValor, set.gamesEquipoB + delta));
    }
    
    // Validar según tipo
    const esValido = esSuperTiebreak 
      ? validarSuperTiebreak(set.gamesEquipoA, set.gamesEquipoB)
      : validarSetNormal(set.gamesEquipoA, set.gamesEquipoB);
    
    if (esValido) {
      set.ganador = set.gamesEquipoA > set.gamesEquipoB ? 'equipoA' : 'equipoB';
      set.completado = true;
    } else {
      set.ganador = null;
      set.completado = false;
    }
    setSets(nuevosSets);
  };

  const agregarTercerSet = (esSuperTiebreak: boolean) => {
    if (sets.length < 3) {
      setSets([...sets, { gamesEquipoA: 0, gamesEquipoB: 0, ganador: null, completado: false, esSuperTiebreak }]);
    }
  };

  const quitarTercerSet = () => {
    if (sets.length > 2) {
      setSets(sets.slice(0, 2));
    }
  };

  const validarResultado = (): string | null => {
    const setsCompletados = sets.filter(s => s.completado);
    if (setsCompletados.length < 2) return 'Completa al menos 2 sets';
    const setsA = setsCompletados.filter(s => s.ganador === 'equipoA').length;
    const setsB = setsCompletados.filter(s => s.ganador === 'equipoB').length;
    if (setsA < 2 && setsB < 2) return 'Debe haber un ganador (2 sets)';
    return null;
  };

  const setsGanadosA = sets.filter(s => s.completado && s.ganador === 'equipoA').length;
  const setsGanadosB = sets.filter(s => s.completado && s.ganador === 'equipoB').length;
  
  // Construir nombres de equipos con los jugadores disponibles
  const getNombreEquipo = (equipo: any, fallback: string) => {
    const j1 = equipo?.jugador1?.nombre;
    const j2 = equipo?.jugador2?.nombre;
    if (j1 && j2) return `${j1} / ${j2}`;
    if (j1) return j1;
    if (j2) return j2;
    return fallback;
  };
  
  // Renderizar nombres de equipo como links clickeables
  const renderEquipoLinks = (equipo: any, fallback: string) => {
    const j1 = equipo?.jugador1;
    const j2 = equipo?.jugador2;
    if (j1?.nombre && j2?.nombre) {
      return (
        <span className="flex items-center gap-1 flex-wrap justify-center">
          <PlayerLink id={j1.id} nombre={j1.nombre} nombreUsuario={j1.nombreUsuario} size="sm" />
          <span>/</span>
          <PlayerLink id={j2.id} nombre={j2.nombre} nombreUsuario={j2.nombreUsuario} size="sm" />
        </span>
      );
    }
    if (j1?.nombre) return <PlayerLink id={j1.id} nombre={j1.nombre} nombreUsuario={j1.nombreUsuario} size="sm" />;
    if (j2?.nombre) return <PlayerLink id={j2.id} nombre={j2.nombre} nombreUsuario={j2.nombreUsuario} size="sm" />;
    return <span>{fallback}</span>;
  };
  
  const equipoANombre = getNombreEquipo(sala.equipoA, 'Equipo A');
  const equipoBNombre = getNombreEquipo(sala.equipoB, 'Equipo B');

  const handleGuardarResultado = async () => {
    const err = validarResultado();
    if (err) { setError(err); return; }
    try {
      setLoading(true); setError('');
      const ganador = setsGanadosA > setsGanadosB ? 'equipoA' : 'equipoB';
      await salaService.cargarResultado(parseInt(sala.id), {
        formato: 'best_of_3', sets: sets.filter(s => s.completado), ganador, completado: true
      });
      setMostrarModalExito(true);
      cargarSalas();
    } catch (e: any) { setError(e.message || 'Error al guardar'); }
    finally { setLoading(false); }
  };

  const handleConfirmarResultado = async () => {
    try {
      setLoading(true); setError('');
      const response = await salaService.confirmarResultado(parseInt(sala.id));
      if (response.elo_aplicado) await reloadUser();
      setDatosConfirmacion(response);
      setMostrarModalConfirmacion(true);
      cargarSalas();
    } catch (e: any) { setError(e.message || 'Error al confirmar'); }
    finally { setLoading(false); }
  };

  return (
    <>
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-2 md:p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-cardBg rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-2xl border border-cardBorder"
        >
          {/* Header */}
          <div className="sticky top-0 bg-cardBg/95 backdrop-blur-sm px-4 py-3 border-b border-cardBorder flex items-center justify-between z-10">
            <div>
              <h2 className="text-lg font-bold text-textPrimary">{sala.nombre}</h2>
              <p className="text-textSecondary text-xs">Best of 3 (6 games) • Set 3: SuperTiebreak a 10</p>
            </div>
            <button onClick={onClose} className="text-textSecondary hover:text-red-500 p-2 rounded-full hover:bg-red-500/10 transition-all">
              <X size={20} />
            </button>
          </div>

          <div className="p-4 space-y-4">
            {/* Estado */}
            {yaConfirmado && (
              <div className="bg-green-500/10 border border-green-500/30 rounded-xl px-4 py-2 flex items-center gap-2">
                <CheckCircle size={18} className="text-green-500" />
                <span className="text-green-500 text-sm font-bold">Partido confirmado</span>
              </div>
            )}
            {pendienteConfirmacion && !esCreador && (
              <div className="bg-accent/10 border border-accent/30 rounded-xl px-4 py-3">
                <p className="text-accent text-sm font-bold">⚠️ Resultado pendiente de confirmación</p>
                <p className="text-textSecondary text-xs">Revisa y confirma si es correcto</p>
              </div>
            )}
            {pendienteConfirmacion && esCreador && (
              <div className="bg-primary/10 border border-primary/30 rounded-xl px-4 py-2">
                <p className="text-primary text-sm font-bold">✓ Resultado guardado</p>
                <p className="text-textSecondary text-xs">Esperando confirmación de rivales</p>
              </div>
            )}

            {/* Marcador Principal */}
            <div className="bg-background/50 rounded-xl border border-cardBorder overflow-hidden">
              {/* Equipo A */}
              <div className="flex items-center justify-between p-3 border-b border-cardBorder/50">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <div className="text-textPrimary font-bold text-sm truncate">{renderEquipoLinks(sala.equipoA, 'Equipo A')}</div>
                  {esCreador && <Crown size={14} className="text-accent flex-shrink-0" />}
                </div>
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-2xl font-black ${setsGanadosA > setsGanadosB ? 'bg-primary text-white' : 'bg-cardBorder text-textPrimary'}`}>
                  {setsGanadosA}
                </div>
              </div>
              
              {/* VS */}
              <div className="flex items-center justify-center py-1 bg-cardBorder/20">
                <span className="text-textSecondary text-xs font-bold">VS</span>
              </div>
              
              {/* Equipo B */}
              <div className="flex items-center justify-between p-3">
                <div className="text-textPrimary font-bold text-sm truncate flex-1">{renderEquipoLinks(sala.equipoB, 'Equipo B')}</div>
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-2xl font-black ${setsGanadosB > setsGanadosA ? 'bg-secondary text-white' : 'bg-cardBorder text-textPrimary'}`}>
                  {setsGanadosB}
                </div>
              </div>
            </div>

            {/* Sets */}
            {sets.map((set, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`rounded-xl border p-4 ${set.completado ? 'bg-green-500/5 border-green-500/30' : 'bg-background/30 border-cardBorder'}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-bold text-textPrimary text-sm">
                    {set.esSuperTiebreak ? 'Super Tiebreak' : `Set ${index + 1}`}
                  </h3>
                  {set.completado && (
                    <span className="text-green-500 text-xs font-bold flex items-center gap-1">
                      <Trophy size={12} /> Válido
                    </span>
                  )}
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  {/* Equipo A */}
                  <div>
                    <label className="text-xs text-textSecondary mb-2 block truncate">{equipoANombre}</label>
                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="sm" onClick={() => actualizarGames(index, 'A', -1)} 
                        disabled={!puedeEditar} className="p-2 bg-cardBorder/50 hover:bg-primary/20">
                        <Minus size={14} />
                      </Button>
                      <div className={`flex-1 text-center py-2 rounded-lg font-black text-xl ${set.ganador === 'equipoA' ? 'bg-primary/20 text-primary' : 'bg-cardBorder/30 text-textPrimary'}`}>
                        {set.gamesEquipoA}
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => actualizarGames(index, 'A', 1)}
                        disabled={!puedeEditar} className="p-2 bg-cardBorder/50 hover:bg-primary/20">
                        <Plus size={14} />
                      </Button>
                    </div>
                  </div>
                  
                  {/* Equipo B */}
                  <div>
                    <label className="text-xs text-textSecondary mb-2 block truncate">{equipoBNombre}</label>
                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="sm" onClick={() => actualizarGames(index, 'B', -1)}
                        disabled={!puedeEditar} className="p-2 bg-cardBorder/50 hover:bg-secondary/20">
                        <Minus size={14} />
                      </Button>
                      <div className={`flex-1 text-center py-2 rounded-lg font-black text-xl ${set.ganador === 'equipoB' ? 'bg-secondary/20 text-secondary' : 'bg-cardBorder/30 text-textPrimary'}`}>
                        {set.gamesEquipoB}
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => actualizarGames(index, 'B', 1)}
                        disabled={!puedeEditar} className="p-2 bg-cardBorder/50 hover:bg-secondary/20">
                        <Plus size={14} />
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Ganador del set */}
                {set.completado && (
                  <div className={`mt-3 py-2 rounded-lg text-center text-xs font-bold ${set.ganador === 'equipoA' ? 'bg-primary/20 text-primary' : 'bg-secondary/20 text-secondary'}`}>
                    Ganador: {set.ganador === 'equipoA' ? equipoANombre : equipoBNombre}
                  </div>
                )}
              </motion.div>
            ))}

            {/* Agregar/Quitar 3er set */}
            {puedeEditar && sets.length < 3 && (
              <div className="flex gap-2">
                <Button variant="ghost" onClick={() => agregarTercerSet(false)} className="flex-1 text-xs py-2">
                  <Plus size={14} className="mr-1" /> 3er Set Normal
                </Button>
                <Button variant="ghost" onClick={() => agregarTercerSet(true)} className="flex-1 text-xs py-2 bg-accent/10 hover:bg-accent/20 text-accent">
                  <Plus size={14} className="mr-1" /> Super Tiebreak (10)
                </Button>
              </div>
            )}
            {puedeEditar && sets.length > 2 && (
              <Button variant="ghost" onClick={quitarTercerSet} className="w-full text-xs py-2 text-red-400 hover:bg-red-500/10">
                <Minus size={14} className="mr-1" /> Quitar 3er Set
              </Button>
            )}

            {/* Error */}
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 text-center">
                <span className="text-red-400 text-sm">⚠ {error}</span>
              </div>
            )}

            {/* Acciones */}
            {!yaConfirmado && (
              <div className="flex gap-2 pt-2 border-t border-cardBorder">
                {esCreador && (
                  <Button 
                    variant="primary" 
                    onClick={handleGuardarResultado} 
                    disabled={loading || validarResultado() !== null}
                    className="flex-1 py-3"
                  >
                    {loading ? 'Guardando...' : <><Trophy size={16} className="mr-2" /> {pendienteConfirmacion ? 'Actualizar Resultado' : 'Guardar Resultado'}</>}
                  </Button>
                )}
                
                {!esCreador && pendienteConfirmacion && (
                  <>
                    <Button variant="primary" onClick={handleConfirmarResultado} disabled={loading} className="flex-1 py-3">
                      {loading ? 'Confirmando...' : <><CheckCircle size={16} className="mr-2" /> Confirmar Resultado</>}
                    </Button>
                    <Button variant="ghost" className="py-3 px-4 bg-red-500/10 hover:bg-red-500/20 text-red-400">
                      <Flag size={16} />
                    </Button>
                  </>
                )}
              </div>
            )}
          </div>
        </motion.div>
      </div>

      <ModalExito
        isOpen={mostrarModalExito}
        onClose={() => { setMostrarModalExito(false); onClose(); }}
        titulo="¡Resultado Guardado!"
        mensaje="Los rivales deben confirmar el resultado para que el Elo se aplique."
        icono={<Trophy size={48} className="text-white" />}
      />

      {datosConfirmacion && (
        <ModalConfirmacionExitosa
          isOpen={mostrarModalConfirmacion}
          onClose={() => { setMostrarModalConfirmacion(false); onClose(); }}
          confirmacionesTotales={datosConfirmacion.confirmaciones_totales || 0}
          faltanConfirmar={3 - (datosConfirmacion.confirmaciones_totales || 0)}
          eloAplicado={datosConfirmacion.elo_aplicado || false}
          cambioEloEstimado={datosConfirmacion.cambio_elo_usuario || 0}
          jugadoresFaltantes={datosConfirmacion.jugadores_faltantes || []}
        />
      )}
    </>
  );
}
