import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Users, TrendingUp, Award, Target } from 'lucide-react';
import { torneoService } from '../services/torneo.service';
import Card from './Card';
import Button from './Button';
import SkeletonLoader from './SkeletonLoader';

interface TorneoZonasProps {
  torneoId: number;
  esOrganizador: boolean;
}

export default function TorneoZonas({ torneoId, esOrganizador }: TorneoZonasProps) {
  const [zonas, setZonas] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generando, setGenerando] = useState(false);
  const [zonaSeleccionada, setZonaSeleccionada] = useState<number | null>(null);
  const [tablaPosiciones, setTablaPosiciones] = useState<any>(null);

  useEffect(() => {
    cargarZonas();
  }, [torneoId]);

  const cargarZonas = async () => {
    try {
      setLoading(true);
      const data = await torneoService.listarZonas(torneoId);
      setZonas(data);
    } catch (error) {
      console.error('Error al cargar zonas:', error);
    } finally {
      setLoading(false);
    }
  };

  const generarZonas = async () => {
    try {
      setGenerando(true);
      // Obtener parejas confirmadas
      const parejas = await torneoService.listarParejas(torneoId, 'confirmada');
      const parejasIds = parejas.map(p => p.id);
      
      await torneoService.generarZonas(torneoId, parejasIds);
      await cargarZonas();
    } catch (error: any) {
      console.error('Error al generar zonas:', error);
      alert(error.response?.data?.detail || 'Error al generar zonas');
    } finally {
      setGenerando(false);
    }
  };

  const verTablaPosiciones = async (zonaId: number) => {
    try {
      const tabla = await torneoService.obtenerTablaPosiciones(torneoId, zonaId);
      setTablaPosiciones(tabla);
      setZonaSeleccionada(zonaId);
    } catch (error) {
      console.error('Error al cargar tabla:', error);
      alert('Error al cargar la tabla de posiciones');
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SkeletonLoader height="280px" />
        <SkeletonLoader height="280px" />
      </div>
    );
  }

  if (zonas.length === 0) {
    return (
      <Card>
        <div className="p-6 text-center">
          <Users size={48} className="mx-auto text-textSecondary mb-4" />
          <h3 className="text-xl font-bold text-textPrimary mb-2">
            Aún no se generaron las zonas
          </h3>
          <p className="text-textSecondary mb-6">
            Las zonas se generan automáticamente cuando hay suficientes parejas confirmadas
          </p>
          {esOrganizador && (
            <Button
              onClick={generarZonas}
              disabled={generando}
              variant="accent"
            >
              {generando ? 'Generando...' : 'Generar Zonas'}
            </Button>
          )}
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Lista de Zonas */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4">
        {zonas.map((zona, index) => (
          <motion.div
            key={zona.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
          >
            <Card className="hover:shadow-lg transition-shadow">
              <div className="p-4 md:p-5 flex flex-col h-full min-h-[240px] md:min-h-[280px]">
                {/* Header de la zona */}
                <div className="flex items-center justify-between mb-3 pb-2 md:pb-3 border-b border-cardBorder">
                  <div className="flex items-center gap-2">
                    <div className="bg-gradient-to-br from-primary to-accent p-1.5 md:p-2 rounded-lg">
                      <Target size={16} className="text-white md:w-[18px] md:h-[18px]" />
                    </div>
                    <h3 className="text-base md:text-lg font-bold text-textPrimary">
                      {zona.nombre}
                    </h3>
                  </div>
                  <div className="bg-primary/10 px-2 md:px-3 py-1 rounded-full">
                    <span className="text-primary font-bold text-xs">
                      {zona.parejas?.length || 0}
                    </span>
                  </div>
                </div>

                {/* Parejas de la zona */}
                <div className="space-y-1.5 md:space-y-2 mb-3 md:mb-4 flex-1">
                  {zona.parejas?.map((pareja: any, idx: number) => (
                    <motion.div
                      key={pareja.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 + idx * 0.03 }}
                      className="flex items-center gap-2 md:gap-3 p-2 md:p-3 bg-background rounded-lg hover:bg-background/80 transition-colors group"
                    >
                      <div className="flex items-center justify-center w-5 h-5 md:w-6 md:h-6 rounded-full bg-primary/10 text-primary text-xs font-bold flex-shrink-0">
                        {idx + 1}
                      </div>
                      <Users size={12} className="text-textSecondary group-hover:text-primary transition-colors flex-shrink-0 md:w-[14px] md:h-[14px]" />
                      <span className="text-xs md:text-sm text-textPrimary font-medium flex-1 truncate">
                        {pareja.pareja_nombre || `Pareja ${pareja.jugador1_id}/${pareja.jugador2_id}`}
                      </span>
                    </motion.div>
                  ))}
                </div>

                {/* Botón de tabla */}
                <Button
                  variant="ghost"
                  onClick={() => verTablaPosiciones(zona.id)}
                  className="w-full flex items-center justify-center gap-2 mt-auto hover:bg-primary/10 hover:text-primary transition-all text-sm md:text-base py-2"
                >
                  <TrendingUp size={14} className="md:w-4 md:h-4" />
                  <span className="font-bold">Ver Tabla</span>
                </Button>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Tabla de Posiciones Modal */}
      {tablaPosiciones && zonaSeleccionada && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card className="border-2 border-primary/20">
            <div className="p-6">
              {/* Header mejorado */}
              <div className="flex items-center justify-between mb-4 md:mb-6 pb-3 md:pb-4 border-b border-cardBorder">
                <div className="flex items-center gap-2 md:gap-3">
                  <div className="bg-gradient-to-br from-primary to-accent p-2 md:p-3 rounded-lg">
                    <Award size={20} className="text-white md:w-6 md:h-6" />
                  </div>
                  <div>
                    <h3 className="text-lg md:text-2xl font-bold text-textPrimary">
                      {tablaPosiciones.zona_nombre}
                    </h3>
                    <p className="text-xs md:text-sm text-textSecondary">Tabla de Posiciones</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  onClick={() => {
                    setTablaPosiciones(null);
                    setZonaSeleccionada(null);
                  }}
                  className="hover:bg-red-500/10 hover:text-red-500 text-sm md:text-base px-2 md:px-4"
                >
                  Cerrar
                </Button>
              </div>

              {/* Tabla responsive */}
              <div className="overflow-x-auto -mx-6 px-6 md:mx-0 md:px-0">
                <table className="w-full min-w-[600px] md:min-w-0">
                  <thead>
                    <tr className="border-b-2 border-primary/20">
                      <th className="text-left py-2 md:py-3 px-2 md:px-3 text-textSecondary text-[10px] md:text-xs font-bold uppercase">Pos</th>
                      <th className="text-left py-2 md:py-3 px-2 md:px-3 text-textSecondary text-[10px] md:text-xs font-bold uppercase">Pareja</th>
                      <th className="text-center py-2 md:py-3 px-1 md:px-2 text-textSecondary text-[10px] md:text-xs font-bold uppercase">PJ</th>
                      <th className="text-center py-2 md:py-3 px-1 md:px-2 text-textSecondary text-[10px] md:text-xs font-bold uppercase">PG</th>
                      <th className="text-center py-2 md:py-3 px-1 md:px-2 text-textSecondary text-[10px] md:text-xs font-bold uppercase">PP</th>
                      <th className="text-center py-2 md:py-3 px-1 md:px-2 text-textSecondary text-[10px] md:text-xs font-bold uppercase">SG</th>
                      <th className="text-center py-2 md:py-3 px-1 md:px-2 text-textSecondary text-[10px] md:text-xs font-bold uppercase">SP</th>
                      <th className="text-center py-2 md:py-3 px-1 md:px-2 text-textSecondary text-[10px] md:text-xs font-bold uppercase hidden lg:table-cell">GG</th>
                      <th className="text-center py-2 md:py-3 px-1 md:px-2 text-textSecondary text-[10px] md:text-xs font-bold uppercase hidden lg:table-cell">GP</th>
                      <th className="text-center py-2 md:py-3 px-2 md:px-3 text-textSecondary text-[10px] md:text-xs font-bold uppercase">Pts</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tablaPosiciones.tabla?.map((item: any, index: number) => (
                      <motion.tr
                        key={item.pareja_id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className={`border-b border-cardBorder transition-colors hover:bg-background/50 ${
                          index < 2 ? 'bg-gradient-to-r from-green-500/10 to-transparent' : ''
                        }`}
                      >
                        <td className="py-2 md:py-4 px-2 md:px-3">
                          <div className="flex items-center gap-1 md:gap-2">
                            {index < 2 && (
                              <div className="bg-green-500/20 p-0.5 md:p-1 rounded">
                                <Trophy size={10} className="text-green-500 md:w-[14px] md:h-[14px]" />
                              </div>
                            )}
                            <span className={`font-bold text-xs md:text-base ${index < 2 ? 'text-green-500' : 'text-textPrimary'}`}>
                              {item.posicion}
                            </span>
                          </div>
                        </td>
                        <td className="py-2 md:py-4 px-2 md:px-3">
                          <span className="text-textPrimary font-medium text-xs md:text-base truncate block max-w-[120px] md:max-w-none">
                            {item.pareja_nombre || `${item.jugador1_id}/${item.jugador2_id}`}
                          </span>
                        </td>
                        <td className="py-2 md:py-4 px-1 md:px-2 text-center">
                          <span className="text-textSecondary font-medium text-xs md:text-base">{item.partidos_jugados}</span>
                        </td>
                        <td className="py-2 md:py-4 px-1 md:px-2 text-center">
                          <span className="text-green-500 font-bold text-xs md:text-base">{item.partidos_ganados}</span>
                        </td>
                        <td className="py-2 md:py-4 px-1 md:px-2 text-center">
                          <span className="text-red-500 font-bold text-xs md:text-base">{item.partidos_perdidos}</span>
                        </td>
                        <td className="py-2 md:py-4 px-1 md:px-2 text-center">
                          <span className="text-textSecondary text-xs md:text-base">{item.sets_ganados}</span>
                        </td>
                        <td className="py-2 md:py-4 px-1 md:px-2 text-center">
                          <span className="text-textSecondary text-xs md:text-base">{item.sets_perdidos}</span>
                        </td>
                        <td className="py-2 md:py-4 px-1 md:px-2 text-center hidden lg:table-cell">
                          <span className="text-green-500/70 text-xs md:text-base">{item.games_ganados}</span>
                        </td>
                        <td className="py-2 md:py-4 px-1 md:px-2 text-center hidden lg:table-cell">
                          <span className="text-red-500/70 text-xs md:text-base">{item.games_perdidos}</span>
                        </td>
                        <td className="py-2 md:py-4 px-2 md:px-3 text-center">
                          <div className="inline-flex items-center justify-center bg-primary/10 px-2 md:px-3 py-0.5 md:py-1 rounded-full">
                            <span className="font-bold text-primary text-sm md:text-lg">{item.puntos}</span>
                          </div>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Info y acciones */}
              <div className="mt-4 md:mt-6 space-y-2 md:space-y-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-3">
                  <div className="p-3 md:p-4 bg-gradient-to-r from-green-500/10 to-green-500/5 rounded-lg border border-green-500/20">
                    <div className="flex items-center gap-2 md:gap-3">
                      <Trophy size={16} className="text-green-500 flex-shrink-0 md:w-5 md:h-5" />
                      <div>
                        <p className="text-xs md:text-sm font-bold text-green-500">Clasifican a Playoffs</p>
                        <p className="text-[10px] md:text-xs text-textSecondary">Los primeros 2 de cada zona</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-3 md:p-4 bg-primary/5 rounded-lg border border-primary/20">
                    <div className="flex items-center gap-2 md:gap-3">
                      <Target size={16} className="text-primary flex-shrink-0 md:w-5 md:h-5" />
                      <div>
                        <p className="text-xs md:text-sm font-bold text-primary">Criterios de desempate</p>
                        <p className="text-[10px] md:text-xs text-textSecondary">Puntos → Sets → Games</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <Button
                  variant="accent"
                  onClick={() => {
                    setTablaPosiciones(null);
                    setZonaSeleccionada(null);
                    window.dispatchEvent(new CustomEvent('cambiarTab', { detail: 'partidos' }));
                  }}
                  className="w-full text-sm md:text-base py-2 md:py-3"
                >
                  Ver Resultados de los Partidos
                </Button>
              </div>
            </div>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
