import { useState } from 'react';
import { createPortal } from 'react-dom';
import { motion } from 'framer-motion';
import { Trophy, Edit3, Crown, Star, Sparkles } from 'lucide-react';
import ModalCargarResultado from './ModalCargarResultado';

interface Partido {
  id: number;
  id_partido?: number;
  pareja1_id?: number;
  pareja2_id?: number;
  pareja1_nombre?: string;
  pareja2_nombre?: string;
  ganador_id?: number;
  resultado?: any;
  fase: string;
  estado: string;
  numero_partido?: number;
}

interface TorneoBracketProps {
  partidos: Partido[];
  torneoId: number;
  esOrganizador: boolean;
  onResultadoCargado?: () => void;
}

export default function TorneoBracket({ partidos, torneoId, esOrganizador, onResultadoCargado }: TorneoBracketProps) {
  const [partidoSeleccionado, setPartidoSeleccionado] = useState<Partido | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  // Agrupar partidos por fase
  const fases = {
    '16avos': partidos.filter((p) => p.fase === '16avos'),
    '8vos': partidos.filter((p) => p.fase === '8vos'),
    '4tos': partidos.filter((p) => p.fase === '4tos' || p.fase === 'cuartos'),
    semis: partidos.filter((p) => p.fase === 'semifinal' || p.fase === 'semis'),
    final: partidos.filter((p) => p.fase === 'final'),
  };

  // Si hay semifinales pero no final, crear partido de final vacío
  if (fases.semis.length > 0 && fases.final.length === 0) {
    fases.final = [{
      id: -1,
      fase: 'final',
      estado: 'pendiente',
      pareja1_nombre: undefined,
      pareja2_nombre: undefined,
    }];
  }

  // Si hay cuartos pero no semis, crear semis vacías
  if (fases['4tos'].length > 0 && fases.semis.length === 0) {
    const numSemis = Math.ceil(fases['4tos'].length / 2);
    fases.semis = Array.from({ length: numSemis }, (_, i) => ({
      id: -100 - i,
      fase: 'semis',
      estado: 'pendiente',
      pareja1_nombre: undefined,
      pareja2_nombre: undefined,
    }));
    fases.final = [{
      id: -1,
      fase: 'final',
      estado: 'pendiente',
      pareja1_nombre: undefined,
      pareja2_nombre: undefined,
    }];
  }

  // Determinar qué fases mostrar
  const fasesActivas = Object.entries(fases).filter(([, p]) => p.length > 0);

  // Verificar si hay campeón (final con ganador)
  const partidoFinal = fases.final[0];
  const hayCampeon = partidoFinal?.ganador_id && partidoFinal?.estado === 'confirmado';
  const nombreCampeon = hayCampeon 
    ? (partidoFinal.ganador_id === partidoFinal.pareja1_id 
        ? partidoFinal.pareja1_nombre 
        : partidoFinal.pareja2_nombre)
    : null;

  const abrirModalResultado = (partido: Partido) => {
    setPartidoSeleccionado(partido);
    setModalOpen(true);
  };

  const handleResultadoCargado = () => {
    setModalOpen(false);
    setPartidoSeleccionado(null);
    onResultadoCargado?.();
  };

  // Componente para un partido individual
  const PartidoBox = ({
    partido,
    esFinal = false,
  }: {
    partido: Partido;
    esFinal?: boolean;
  }) => {
    const ganadorA = partido.ganador_id === partido.pareja1_id && partido.pareja1_id;
    const ganadorB = partido.ganador_id === partido.pareja2_id && partido.pareja2_id;
    const puedeCargarResultado = esOrganizador && partido.estado === 'pendiente' && partido.id > 0 && partido.pareja1_id && partido.pareja2_id;

    return (
      <div className={`relative ${esFinal ? 'scale-110' : ''}`}>
        <div
          className={`bg-card border-2 rounded-lg overflow-hidden min-w-[160px] ${
            esFinal ? 'border-accent shadow-lg shadow-accent/20' : 'border-primary/30'
          }`}
        >
          {/* Pareja 1 */}
          <div
            className={`flex items-center justify-between px-3 py-2 border-b border-cardBorder ${
              ganadorA ? 'bg-green-500/20' : 'bg-card'
            }`}
          >
            <div className="flex items-center gap-2 flex-1 min-w-0">
              {ganadorA && <Trophy size={12} className="text-green-500 flex-shrink-0" />}
              <span
                className={`text-xs font-bold truncate ${
                  ganadorA
                    ? 'text-green-500'
                    : partido.pareja1_nombre
                      ? 'text-textPrimary'
                      : 'text-textSecondary'
                }`}
              >
                {partido.pareja1_nombre || 'TBD'}
              </span>
            </div>
          </div>
          {/* Pareja 2 */}
          <div
            className={`flex items-center justify-between px-3 py-2 ${
              ganadorB ? 'bg-green-500/20' : 'bg-card'
            }`}
          >
            <div className="flex items-center gap-2 flex-1 min-w-0">
              {ganadorB && <Trophy size={12} className="text-green-500 flex-shrink-0" />}
              <span
                className={`text-xs font-bold truncate ${
                  ganadorB
                    ? 'text-green-500'
                    : partido.pareja2_nombre
                      ? 'text-textPrimary'
                      : 'text-textSecondary'
                }`}
              >
                {partido.pareja2_nombre || 'TBD'}
              </span>
            </div>
          </div>
          {/* Botón cargar resultado */}
          {puedeCargarResultado && (
            <button
              onClick={() => abrirModalResultado(partido)}
              className="w-full py-1.5 bg-accent/20 hover:bg-accent/30 transition-colors flex items-center justify-center gap-1 group"
            >
              <Edit3 size={10} className="text-accent group-hover:scale-110 transition-transform" />
              <span className="text-[10px] font-bold text-accent">Resultado</span>
            </button>
          )}
        </div>
      </div>
    );
  };

  // Componente para una columna de fase con conectores
  const FaseColumna = ({
    nombre,
    partidosFase,
    indice,
    totalFases,
  }: {
    nombre: string;
    partidosFase: Partido[];
    indice: number;
    totalFases: number;
  }) => {
    const esFinal = nombre === 'final';
    const esUltimaFase = indice === totalFases - 1;

    // Calcular espaciado vertical basado en la ronda
    const espaciado = Math.pow(2, indice) * 40;

    return (
      <div className="flex flex-col items-center">
        {/* Título de la fase */}
        <div
          className={`mb-4 px-4 py-1.5 rounded-lg ${
            esFinal
              ? 'bg-gradient-to-r from-accent to-primary'
              : 'bg-primary/10'
          }`}
        >
          <span
            className={`text-xs font-bold uppercase ${
              esFinal ? 'text-white' : 'text-primary'
            }`}
          >
            {nombre === 'semis'
              ? 'Semifinales'
              : nombre === '4tos'
                ? 'Cuartos'
                : nombre === '8vos'
                  ? 'Octavos'
                  : nombre === '16avos'
                    ? '16avos'
                    : 'Final'}
          </span>
        </div>

        {/* Partidos con conectores */}
        <div
          className="flex flex-col justify-around flex-1 relative"
          style={{ gap: `${espaciado}px` }}
        >
          {partidosFase.map((partido, idx) => (
            <motion.div
              key={partido.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: indice * 0.1 + idx * 0.05 }}
              className="relative"
            >
              <PartidoBox partido={partido} esFinal={esFinal} />

              {/* Línea horizontal hacia la derecha */}
              {!esUltimaFase && (
                <div
                  className="absolute top-1/2 -right-6 w-6 h-0.5 bg-primary/40"
                  style={{ transform: 'translateY(-50%)' }}
                />
              )}

              {/* Línea vertical conectora (para partidos pares) */}
              {!esUltimaFase && idx % 2 === 0 && partidosFase.length > 1 && (
                <div
                  className="absolute -right-6 bg-primary/40"
                  style={{
                    top: '50%',
                    height: `${espaciado + 52}px`,
                    width: '2px',
                  }}
                />
              )}
            </motion.div>
          ))}
        </div>
      </div>
    );
  };

  if (fasesActivas.length === 0) {
    return (
      <div className="text-center py-8">
        <Trophy size={48} className="mx-auto text-textSecondary mb-4" />
        <p className="text-textSecondary">No hay partidos de playoffs</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Sección Campeones */}
      {hayCampeon && nombreCampeon && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, type: 'spring' }}
          className="mb-8"
        >
          <div className="relative bg-gradient-to-br from-yellow-500/20 via-accent/20 to-yellow-500/20 rounded-2xl p-6 md:p-8 border-2 border-yellow-500/50 shadow-xl shadow-yellow-500/10 overflow-hidden">
            {/* Decoración de fondo */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-4 left-4 text-yellow-500">
                <Star size={40} fill="currentColor" />
              </div>
              <div className="absolute top-4 right-4 text-yellow-500">
                <Star size={40} fill="currentColor" />
              </div>
              <div className="absolute bottom-4 left-1/4 text-yellow-500">
                <Star size={24} fill="currentColor" />
              </div>
              <div className="absolute bottom-4 right-1/4 text-yellow-500">
                <Star size={24} fill="currentColor" />
              </div>
            </div>

            <div className="relative text-center">
              {/* Icono principal */}
              <motion.div
                initial={{ y: -20 }}
                animate={{ y: 0 }}
                transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                className="flex justify-center mb-4"
              >
                <div className="relative">
                  <div className="absolute -inset-4 bg-yellow-500/30 rounded-full blur-xl" />
                  <div className="relative bg-gradient-to-br from-yellow-400 to-yellow-600 p-4 rounded-full">
                    <Trophy size={48} className="text-white" />
                  </div>
                </div>
              </motion.div>

              {/* Título */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Crown size={24} className="text-yellow-500" />
                  <h2 className="text-2xl md:text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-yellow-500 to-yellow-600">
                    ¡CAMPEONES!
                  </h2>
                  <Crown size={24} className="text-yellow-500" />
                </div>
                <p className="text-textSecondary text-sm mb-4">Felicitaciones a los ganadores del torneo</p>
              </motion.div>

              {/* Nombre del campeón */}
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.5, type: 'spring' }}
                className="bg-gradient-to-r from-yellow-500/10 via-yellow-500/20 to-yellow-500/10 rounded-xl p-4 md:p-6 border border-yellow-500/30"
              >
                <div className="flex items-center justify-center gap-3">
                  <Sparkles size={24} className="text-yellow-500 animate-pulse" />
                  <span className="text-xl md:text-2xl font-bold text-yellow-500">
                    {nombreCampeon}
                  </span>
                  <Sparkles size={24} className="text-yellow-500 animate-pulse" />
                </div>
              </motion.div>

              {/* Badge de campeón */}
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.7 }}
                className="mt-4 inline-flex items-center gap-2 bg-yellow-500/20 px-4 py-2 rounded-full"
              >
                <Trophy size={16} className="text-yellow-500" />
                <span className="text-sm font-bold text-yellow-500">Campeón del Torneo</span>
                <Trophy size={16} className="text-yellow-500" />
              </motion.div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <div className="inline-flex items-center gap-3 bg-gradient-to-r from-accent/10 to-primary/10 px-6 py-3 rounded-full">
          <Trophy className="text-accent" size={24} />
          <h2 className="text-2xl font-bold text-textPrimary">
            {hayCampeon ? 'Resultados del Torneo' : 'Fase de Playoffs'}
          </h2>
          <Trophy className="text-primary" size={24} />
        </div>
        <p className="text-textSecondary mt-2">
          {hayCampeon ? 'Torneo finalizado' : 'Eliminación directa'}
        </p>
      </motion.div>

      {/* Bracket */}
      <div className="overflow-x-auto pb-4">
        <div className="flex items-center justify-center gap-12 min-w-max px-8">
          {fasesActivas.map(([nombre, partidosFase], idx) => (
            <FaseColumna
              key={nombre}
              nombre={nombre}
              partidosFase={partidosFase}
              indice={idx}
              totalFases={fasesActivas.length}
            />
          ))}
        </div>
      </div>

      {/* Leyenda */}
      <div className="mt-8 flex items-center justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-textSecondary">Ganador</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <span className="text-textSecondary">Pendiente</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded border border-dashed border-textSecondary" />
          <span className="text-textSecondary">Por definir</span>
        </div>
      </div>

      {/* Modal Cargar Resultado - usando portal para evitar problemas de overflow */}
      {partidoSeleccionado && createPortal(
        <ModalCargarResultado
          isOpen={modalOpen}
          onClose={() => {
            setModalOpen(false);
            setPartidoSeleccionado(null);
          }}
          partido={{
            ...partidoSeleccionado,
            id_partido: partidoSeleccionado.id_partido || partidoSeleccionado.id
          }}
          torneoId={torneoId}
          onResultadoCargado={handleResultadoCargado}
        />,
        document.body
      )}
    </div>
  );
}
