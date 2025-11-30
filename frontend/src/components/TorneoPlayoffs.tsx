import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Crown, Zap } from 'lucide-react';
import Card from './Card';
import Button from './Button';
import SkeletonLoader from './SkeletonLoader';

interface TorneoPlayoffsProps {
  torneoId: number;
  esOrganizador: boolean;
}

interface Partido {
  id: number;
  pareja1_id?: number;
  pareja2_id?: number;
  pareja1_nombre?: string;
  pareja2_nombre?: string;
  ganador_id?: number;
  resultado?: any;
  fase: string;
  estado: string;
}

export default function TorneoPlayoffs({ torneoId, esOrganizador }: TorneoPlayoffsProps) {
  const [partidos, setPartidos] = useState<Partido[]>([]);
  const [loading, setLoading] = useState(true);
  const [generando, setGenerando] = useState(false);

  useEffect(() => {
    cargarPlayoffs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [torneoId]);

  const cargarPlayoffs = async () => {
    try {
      setLoading(true);
      // TODO: Cuando esté el endpoint, descomentar esto
      // const data = await torneoService.listarPartidosPlayoffs(torneoId);
      // setPartidos(data);
      
      // Mock data para diseño
      setPartidos(generarMockPlayoffs());
    } catch (error) {
      console.error('Error al cargar playoffs:', error);
    } finally {
      setLoading(false);
    }
  };

  const generarPlayoffs = async () => {
    try {
      setGenerando(true);
      // TODO: Implementar cuando esté el endpoint
      // await torneoService.generarPlayoffs(torneoId);
      await cargarPlayoffs();
    } catch (error: any) {
      console.error('Error al generar playoffs:', error);
      alert(error.response?.data?.detail || 'Error al generar playoffs');
    } finally {
      setGenerando(false);
    }
  };

  // Mock data para diseño
  const generarMockPlayoffs = (): Partido[] => {
    const partidos: Partido[] = [];
    let id = 1;

    // 16avos - 8 partidos
    for (let i = 0; i < 8; i++) {
      partidos.push({
        id: id++,
        pareja1_nombre: `Pareja ${i * 2 + 1}`,
        pareja2_nombre: `Pareja ${i * 2 + 2}`,
        ganador_id: i % 2 === 0 ? 1 : 2,
        fase: '16avos',
        estado: 'confirmado',
        resultado: { sets: [{ gamesEquipoA: 6, gamesEquipoB: 4 }, { gamesEquipoA: 6, gamesEquipoB: 2 }] }
      });
    }

    // 8vos - 4 partidos
    for (let i = 0; i < 4; i++) {
      partidos.push({
        id: id++,
        pareja1_nombre: `Ganador ${i * 2 + 1}`,
        pareja2_nombre: `Ganador ${i * 2 + 2}`,
        ganador_id: i % 2 === 0 ? 1 : undefined,
        fase: '8vos',
        estado: i < 2 ? 'confirmado' : 'pendiente'
      });
    }

    // 4tos - 2 partidos
    for (let i = 0; i < 2; i++) {
      partidos.push({
        id: id++,
        pareja1_nombre: i === 0 ? 'Ganador 1' : undefined,
        pareja2_nombre: i === 0 ? 'Ganador 2' : undefined,
        fase: '4tos',
        estado: 'pendiente'
      });
    }

    // Semifinal - 2 partidos
    partidos.push({
      id: id++,
      fase: 'semifinal',
      estado: 'pendiente'
    });
    partidos.push({
      id: id++,
      fase: 'semifinal',
      estado: 'pendiente'
    });

    // Final
    partidos.push({
      id: id++,
      fase: 'final',
      estado: 'pendiente'
    });

    return partidos;
  };

  const agruparPorFase = () => {
    const fases = {
      '16avos': partidos.filter(p => p.fase === '16avos'),
      '8vos': partidos.filter(p => p.fase === '8vos'),
      '4tos': partidos.filter(p => p.fase === '4tos'),
      'semifinal': partidos.filter(p => p.fase === 'semifinal'),
      'final': partidos.filter(p => p.fase === 'final')
    };
    return fases;
  };

  const PartidoCard = ({ partido, index }: { partido: Partido; index: number }) => {
    const ganadorA = partido.ganador_id === partido.pareja1_id;
    const ganadorB = partido.ganador_id === partido.pareja2_id;
    const esFinal = partido.fase === 'final';

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: index * 0.05 }}
        className={`relative ${esFinal ? 'w-full' : ''}`}
      >
        <Card className={`hover:shadow-lg transition-all ${esFinal ? 'border-2 border-accent' : ''}`}>
          <div className="p-2 md:p-3">
            {/* Indicador de fase */}
            {esFinal && (
              <div className="absolute -top-2 md:-top-3 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-accent to-primary px-2 md:px-4 py-0.5 md:py-1 rounded-full">
                <div className="flex items-center gap-1 md:gap-2">
                  <Crown size={10} className="text-white md:w-[14px] md:h-[14px]" />
                  <span className="text-[10px] md:text-xs font-bold text-white">FINAL</span>
                </div>
              </div>
            )}

            {/* Parejas */}
            <div className="space-y-1.5 md:space-y-2">
              {/* Pareja 1 */}
              <div className={`flex items-center justify-between p-1.5 md:p-2 rounded-lg transition-all ${
                ganadorA 
                  ? 'bg-gradient-to-r from-green-500/20 to-green-500/5 border border-green-500/30' 
                  : partido.pareja1_nombre 
                  ? 'bg-background' 
                  : 'bg-background/50 border border-dashed border-cardBorder'
              }`}>
                <div className="flex items-center gap-1 md:gap-2 flex-1 min-w-0">
                  {ganadorA && <Trophy size={10} className="text-green-500 flex-shrink-0 md:w-3 md:h-3" />}
                  <span className={`text-[10px] md:text-xs font-bold truncate ${
                    ganadorA ? 'text-green-500' : 
                    partido.pareja1_nombre ? 'text-textPrimary' : 'text-textSecondary'
                  }`}>
                    {partido.pareja1_nombre || 'TBD'}
                  </span>
                </div>
                {partido.resultado && (
                  <span className={`text-xs md:text-sm font-bold ml-1 md:ml-2 ${ganadorA ? 'text-green-500' : 'text-textSecondary'}`}>
                    {partido.resultado.sets.filter((s: any) => s.ganador === 'equipoA').length}
                  </span>
                )}
              </div>

              {/* VS Divider */}
              <div className="flex items-center justify-center">
                <div className="h-px flex-1 bg-cardBorder" />
                <span className="px-1 md:px-2 text-[8px] md:text-xs font-bold text-textSecondary">VS</span>
                <div className="h-px flex-1 bg-cardBorder" />
              </div>

              {/* Pareja 2 */}
              <div className={`flex items-center justify-between p-1.5 md:p-2 rounded-lg transition-all ${
                ganadorB 
                  ? 'bg-gradient-to-r from-green-500/20 to-green-500/5 border border-green-500/30' 
                  : partido.pareja2_nombre 
                  ? 'bg-background' 
                  : 'bg-background/50 border border-dashed border-cardBorder'
              }`}>
                <div className="flex items-center gap-1 md:gap-2 flex-1 min-w-0">
                  {ganadorB && <Trophy size={10} className="text-green-500 flex-shrink-0 md:w-3 md:h-3" />}
                  <span className={`text-[10px] md:text-xs font-bold truncate ${
                    ganadorB ? 'text-green-500' : 
                    partido.pareja2_nombre ? 'text-textPrimary' : 'text-textSecondary'
                  }`}>
                    {partido.pareja2_nombre || 'TBD'}
                  </span>
                </div>
                {partido.resultado && (
                  <span className={`text-xs md:text-sm font-bold ml-1 md:ml-2 ${ganadorB ? 'text-green-500' : 'text-textSecondary'}`}>
                    {partido.resultado.sets.filter((s: any) => s.ganador === 'equipoB').length}
                  </span>
                )}
              </div>
            </div>

            {/* Estado */}
            <div className="mt-1.5 md:mt-2 text-center">
              <span className={`text-[9px] md:text-xs font-bold ${
                partido.estado === 'confirmado' ? 'text-green-500' :
                partido.estado === 'pendiente' ? 'text-yellow-500' : 'text-textSecondary'
              }`}>
                {partido.estado === 'confirmado' ? '✓ Finalizado' : '⏱ Pendiente'}
              </span>
            </div>
          </div>
        </Card>
      </motion.div>
    );
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <SkeletonLoader height="400px" />
      </div>
    );
  }

  if (partidos.length === 0) {
    return (
      <Card>
        <div className="p-8 text-center">
          <div className="bg-gradient-to-br from-accent/20 to-primary/20 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Trophy size={40} className="text-accent" />
          </div>
          <h3 className="text-2xl font-bold text-textPrimary mb-2">
            Fase de Playoffs
          </h3>
          <p className="text-textSecondary mb-6 max-w-md mx-auto">
            Los playoffs se generan automáticamente cuando finaliza la fase de grupos. 
            Los 2 primeros de cada zona clasifican a la eliminación directa.
          </p>
          {esOrganizador && (
            <Button
              onClick={generarPlayoffs}
              disabled={generando}
              variant="accent"
              className="gap-2"
            >
              <Zap size={18} />
              {generando ? 'Generando...' : 'Generar Playoffs'}
            </Button>
          )}
        </div>
      </Card>
    );
  }

  const fases = agruparPorFase();

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="inline-flex items-center gap-2 md:gap-3 bg-gradient-to-r from-accent/10 to-primary/10 px-4 md:px-6 py-2 md:py-3 rounded-full mb-2">
          <Trophy className="text-accent" size={18} />
          <h2 className="text-lg md:text-2xl font-bold text-textPrimary">Fase de Playoffs</h2>
          <Trophy className="text-primary" size={18} />
        </div>
        <p className="text-xs md:text-base text-textSecondary">Eliminación directa - El camino al campeonato</p>
      </motion.div>

      {/* Bracket de playoffs */}
      <div className="overflow-x-auto pb-4 -mx-4 px-4 md:mx-0 md:px-0">
        <div className="min-w-[900px] md:min-w-[1200px] flex gap-3 md:gap-6 justify-center">
          {/* 16avos */}
          {fases['16avos'].length > 0 && (
            <div className="flex-shrink-0 w-36 md:w-48">
              <div className="text-center mb-3 md:mb-4">
                <div className="inline-block bg-primary/10 px-2 md:px-4 py-1 md:py-2 rounded-lg">
                  <h3 className="text-[10px] md:text-sm font-bold text-primary">16avos</h3>
                </div>
              </div>
              <div className="space-y-6 md:space-y-8">
                {fases['16avos'].map((partido, idx) => (
                  <PartidoCard key={partido.id} partido={partido} index={idx} />
                ))}
              </div>
            </div>
          )}

          {/* 8vos */}
          {fases['8vos'].length > 0 && (
            <div className="flex-shrink-0 w-36 md:w-48">
              <div className="text-center mb-3 md:mb-4">
                <div className="inline-block bg-primary/10 px-2 md:px-4 py-1 md:py-2 rounded-lg">
                  <h3 className="text-[10px] md:text-sm font-bold text-primary">8vos</h3>
                </div>
              </div>
              <div className="space-y-6 md:space-y-8 mt-12 md:mt-20">
                {fases['8vos'].map((partido, idx) => (
                  <div key={partido.id} className="mb-24 md:mb-32">
                    <PartidoCard partido={partido} index={idx} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 4tos */}
          {fases['4tos'].length > 0 && (
            <div className="flex-shrink-0 w-36 md:w-48">
              <div className="text-center mb-3 md:mb-4">
                <div className="inline-block bg-primary/10 px-2 md:px-4 py-1 md:py-2 rounded-lg">
                  <h3 className="text-[10px] md:text-sm font-bold text-primary">Cuartos</h3>
                </div>
              </div>
              <div className="space-y-6 md:space-y-8 mt-32 md:mt-48">
                {fases['4tos'].map((partido, idx) => (
                  <div key={partido.id} className="mb-48 md:mb-64">
                    <PartidoCard partido={partido} index={idx} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Semifinales */}
          {fases['semifinal'].length > 0 && (
            <div className="flex-shrink-0 w-36 md:w-48">
              <div className="text-center mb-3 md:mb-4">
                <div className="inline-block bg-accent/10 px-2 md:px-4 py-1 md:py-2 rounded-lg">
                  <h3 className="text-[10px] md:text-sm font-bold text-accent">Semis</h3>
                </div>
              </div>
              <div className="space-y-6 md:space-y-8 mt-64 md:mt-96">
                {fases['semifinal'].map((partido, idx) => (
                  <div key={partido.id} className={idx === 0 ? 'mb-64 md:mb-96' : ''}>
                    <PartidoCard partido={partido} index={idx} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Final */}
          {fases['final'].length > 0 && (
            <div className="flex-shrink-0 w-44 md:w-64">
              <div className="text-center mb-3 md:mb-4">
                <div className="inline-block bg-gradient-to-r from-accent to-primary px-3 md:px-6 py-1 md:py-2 rounded-lg">
                  <div className="flex items-center gap-1 md:gap-2">
                    <Crown size={12} className="text-white md:w-4 md:h-4" />
                    <h3 className="text-[10px] md:text-sm font-bold text-white">FINAL</h3>
                    <Crown size={12} className="text-white md:w-4 md:h-4" />
                  </div>
                </div>
              </div>
              <div className="mt-[400px] md:mt-[600px]">
                {fases['final'].map((partido, idx) => (
                  <PartidoCard key={partido.id} partido={partido} index={idx} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Leyenda */}
      <Card>
        <div className="p-3 md:p-4">
          <div className="flex flex-wrap gap-3 md:gap-4 justify-center items-center text-xs md:text-sm">
            <div className="flex items-center gap-1.5 md:gap-2">
              <div className="w-2 h-2 md:w-3 md:h-3 rounded-full bg-green-500" />
              <span className="text-textSecondary">Ganador</span>
            </div>
            <div className="flex items-center gap-1.5 md:gap-2">
              <div className="w-2 h-2 md:w-3 md:h-3 rounded-full bg-yellow-500" />
              <span className="text-textSecondary">Pendiente</span>
            </div>
            <div className="flex items-center gap-1.5 md:gap-2">
              <div className="w-2 h-2 md:w-3 md:h-3 rounded border-2 border-dashed border-cardBorder" />
              <span className="text-textSecondary">Por definir</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
