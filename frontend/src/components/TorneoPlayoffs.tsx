import { useEffect, useState } from 'react';
import { Trophy, Zap, Users, Info } from 'lucide-react';
import Card from './Card';
import Button from './Button';
import SkeletonLoader from './SkeletonLoader';
import TorneoBracket from './TorneoBracket';
import torneoService from '../services/torneo.service';
import { useTorneos } from '../context/TorneosContext';

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
  const [playoffsGenerados, setPlayoffsGenerados] = useState(false);
  const { parejas } = useTorneos();

  useEffect(() => {
    cargarPlayoffs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [torneoId]);

  const cargarPlayoffs = async () => {
    try {
      setLoading(true);
      const data = await torneoService.listarPartidosPlayoffs(torneoId);
      if (data && data.partidos && data.partidos.length > 0) {
        setPartidos(data.partidos);
        setPlayoffsGenerados(true);
      } else {
        setPartidos([]);
        setPlayoffsGenerados(false);
      }
    } catch (error: any) {
      // Si el endpoint no existe o no hay playoffs, mostrar estado vacío
      setPartidos([]);
      setPlayoffsGenerados(false);
    } finally {
      setLoading(false);
    }
  };

  const generarPlayoffs = async () => {
    try {
      setGenerando(true);
      await torneoService.generarPlayoffs(torneoId, 2);
      await cargarPlayoffs();
    } catch (error: any) {
      console.error('Error al generar playoffs:', error);
      alert(error.response?.data?.detail || 'Error al generar playoffs');
    } finally {
      setGenerando(false);
    }
  };

  // Calcular información del bracket basado en parejas
  const parejasConfirmadas = parejas.filter(p => p.estado === 'confirmada').length;
  const parejasInscritas = parejas.filter(p => p.estado !== 'baja').length;
  const parejasActivas = parejasConfirmadas > 0 ? parejasConfirmadas : parejasInscritas;
  
  // Determinar tamaño del bracket necesario
  const calcularTamañoBracket = (numParejas: number) => {
    if (numParejas <= 2) return { rondas: 1, nombre: 'Final directa' };
    if (numParejas <= 4) return { rondas: 2, nombre: 'Semifinales + Final' };
    if (numParejas <= 8) return { rondas: 3, nombre: 'Cuartos + Semis + Final' };
    if (numParejas <= 16) return { rondas: 4, nombre: '8vos + Cuartos + Semis + Final' };
    return { rondas: 5, nombre: '16avos + 8vos + Cuartos + Semis + Final' };
  };

  const bracketInfo = calcularTamañoBracket(parejasActivas);

  if (loading) {
    return (
      <div className="space-y-4">
        <SkeletonLoader height="200px" />
      </div>
    );
  }

  // Estado vacío - No hay playoffs generados
  if (!playoffsGenerados || partidos.length === 0) {
    return (
      <Card>
        <div className="p-6 md:p-8 text-center">
          <div className="bg-gradient-to-br from-accent/20 to-primary/20 w-16 h-16 md:w-20 md:h-20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Trophy size={32} className="text-accent md:w-10 md:h-10" />
          </div>
          
          <h3 className="text-xl md:text-2xl font-bold text-textPrimary mb-2">
            Fase de Playoffs
          </h3>
          
          {parejasInscritas === 0 ? (
            <>
              <p className="text-textSecondary mb-4 text-sm md:text-base">
                Aún no hay parejas inscritas en el torneo.
              </p>
              <div className="bg-background rounded-lg p-4 max-w-md mx-auto">
                <div className="flex items-center gap-2 text-textSecondary text-sm">
                  <Info size={16} />
                  <span>Inscribí parejas primero para poder generar los playoffs.</span>
                </div>
              </div>
            </>
          ) : (
            <>
              <p className="text-textSecondary mb-4 text-sm md:text-base max-w-md mx-auto">
                Los playoffs se generan cuando finaliza la fase de grupos. 
                Los mejores de cada zona clasifican a la eliminación directa.
              </p>
              
              {/* Info del bracket estimado */}
              <div className="bg-background rounded-lg p-4 max-w-md mx-auto mb-6">
                <div className="flex items-center justify-center gap-2 mb-3">
                  <Users size={18} className="text-primary" />
                  <span className="font-bold text-textPrimary">
                    {parejasActivas} parejas
                  </span>
                  <span className="text-textSecondary text-sm">
                    (inscritas)
                  </span>
                </div>
                <p className="text-sm text-textSecondary">
                  Formato estimado: <span className="text-primary font-bold">{bracketInfo.nombre}</span>
                </p>
              </div>

              {esOrganizador && (
                <Button
                  onClick={generarPlayoffs}
                  disabled={generando || parejasActivas < 2}
                  variant="accent"
                  className="gap-2"
                >
                  <Zap size={18} />
                  {generando ? 'Generando...' : 'Generar Playoffs'}
                </Button>
              )}

              {parejasActivas < 2 && (
                <p className="text-xs text-textSecondary mt-4">
                  Se necesitan al menos 2 parejas para generar playoffs.
                </p>
              )}
            </>
          )}
        </div>
      </Card>
    );
  }

  // Mostrar bracket de playoffs usando el nuevo componente
  return (
    <Card>
      <div className="p-4 md:p-6">
        <TorneoBracket 
          partidos={partidos} 
          torneoId={torneoId}
          esOrganizador={esOrganizador}
          onResultadoCargado={cargarPlayoffs}
        />
      </div>
    </Card>
  );
}
