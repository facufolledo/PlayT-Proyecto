import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Users, TrendingUp } from 'lucide-react';
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {zonas.map((zona, index) => (
          <motion.div
            key={zona.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card>
              <div className="p-6 flex flex-col h-full min-h-[280px]">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-textPrimary">
                    {zona.nombre}
                  </h3>
                  <div className="bg-primary/10 px-3 py-1 rounded-full">
                    <span className="text-primary font-bold text-sm">
                      {zona.parejas?.length || 0} parejas
                    </span>
                  </div>
                </div>

                {/* Parejas de la zona - altura fija */}
                <div className="space-y-2 mb-4 flex-1">
                  {zona.parejas?.map((pareja: any) => (
                    <div
                      key={pareja.id}
                      className="flex items-center gap-2 p-3 bg-background rounded-lg"
                    >
                      <Users size={16} className="text-textSecondary" />
                      <span className="text-sm text-textPrimary">
                        {pareja.pareja_nombre || `Pareja ${pareja.jugador1_id}/${pareja.jugador2_id}`}
                      </span>
                    </div>
                  ))}
                </div>

                <Button
                  variant="ghost"
                  onClick={() => verTablaPosiciones(zona.id)}
                  className="w-full flex items-center justify-center gap-2 mt-auto"
                >
                  <TrendingUp size={16} />
                  Ver Tabla de Posiciones
                </Button>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Tabla de Posiciones Modal */}
      {tablaPosiciones && zonaSeleccionada && (
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-textPrimary">
                Tabla de Posiciones - {tablaPosiciones.zona_nombre}
              </h3>
              <Button
                variant="ghost"
                onClick={() => {
                  setTablaPosiciones(null);
                  setZonaSeleccionada(null);
                }}
              >
                Cerrar
              </Button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-cardBorder">
                    <th className="text-left py-3 px-2 text-textSecondary text-sm">Pos</th>
                    <th className="text-left py-3 px-2 text-textSecondary text-sm">Pareja</th>
                    <th className="text-center py-3 px-2 text-textSecondary text-sm">PJ</th>
                    <th className="text-center py-3 px-2 text-textSecondary text-sm">PG</th>
                    <th className="text-center py-3 px-2 text-textSecondary text-sm">PP</th>
                    <th className="text-center py-3 px-2 text-textSecondary text-sm">SG</th>
                    <th className="text-center py-3 px-2 text-textSecondary text-sm">SP</th>
                    <th className="text-center py-3 px-2 text-textSecondary text-sm">GG</th>
                    <th className="text-center py-3 px-2 text-textSecondary text-sm">GP</th>
                    <th className="text-center py-3 px-2 text-textSecondary text-sm">Pts</th>
                  </tr>
                </thead>
                <tbody>
                  {tablaPosiciones.tabla?.map((item: any, index: number) => (
                    <tr
                      key={item.pareja_id}
                      className={`border-b border-cardBorder ${
                        index < 2 ? 'bg-green-500/5' : ''
                      }`}
                    >
                      <td className="py-3 px-2">
                        <div className="flex items-center gap-2">
                          {index < 2 && <Trophy size={14} className="text-green-500" />}
                          <span className="font-bold text-textPrimary">{item.posicion}</span>
                        </div>
                      </td>
                      <td className="py-3 px-2 text-textPrimary">
                        {item.pareja_nombre || `${item.jugador1_id}/${item.jugador2_id}`}
                      </td>
                      <td className="py-3 px-2 text-center text-textSecondary">
                        {item.partidos_jugados}
                      </td>
                      <td className="py-3 px-2 text-center text-green-500 font-bold">
                        {item.partidos_ganados}
                      </td>
                      <td className="py-3 px-2 text-center text-red-500">
                        {item.partidos_perdidos}
                      </td>
                      <td className="py-3 px-2 text-center text-textSecondary">
                        {item.sets_ganados}
                      </td>
                      <td className="py-3 px-2 text-center text-textSecondary">
                        {item.sets_perdidos}
                      </td>
                      <td className="py-3 px-2 text-center text-green-500">
                        {item.games_ganados}
                      </td>
                      <td className="py-3 px-2 text-center text-red-500">
                        {item.games_perdidos}
                      </td>
                      <td className="py-3 px-2 text-center">
                        <span className="font-bold text-primary">{item.puntos}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-4 space-y-3">
              <div className="p-4 bg-green-500/10 rounded-lg">
                <p className="text-sm text-green-500 flex items-center gap-2">
                  <Trophy size={16} />
                  Los primeros 2 clasifican a la siguiente fase
                </p>
              </div>
              
              <Button
                variant="ghost"
                onClick={() => {
                  // Cerrar el modal y cambiar a la tab de Fixture
                  setTablaPosiciones(null);
                  setZonaSeleccionada(null);
                  // Disparar evento para cambiar tab (el componente padre debe escucharlo)
                  window.dispatchEvent(new CustomEvent('cambiarTab', { detail: 'partidos' }));
                }}
                className="w-full"
              >
                Ver Resultados de los Partidos
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
