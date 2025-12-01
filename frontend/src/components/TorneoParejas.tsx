import { useState } from 'react';
import { motion } from 'framer-motion';
import { Users, Check, X, Trash2, AlertCircle } from 'lucide-react';
import { torneoService, Pareja } from '../services/torneo.service';
import Card from './Card';
import Button from './Button';

interface TorneoParejaProps {
  torneoId: number;
  parejas: Pareja[];
  esOrganizador: boolean;
  onUpdate: () => void;
}

export default function TorneoParejas({
  torneoId,
  parejas,
  esOrganizador,
  onUpdate,
}: TorneoParejaProps) {
  const [loading, setLoading] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const confirmarPareja = async (parejaId: number) => {
    try {
      setLoading(parejaId);
      setError(null);
      await torneoService.confirmarPareja(torneoId, parejaId);
      onUpdate();
    } catch (err: any) {
      console.error('Error al confirmar pareja:', err);
      setError(err.response?.data?.detail || 'Error al confirmar pareja');
    } finally {
      setLoading(null);
    }
  };

  const rechazarPareja = async (parejaId: number) => {
    if (!confirm('¿Estás seguro de eliminar esta pareja del torneo?')) return;

    try {
      setLoading(parejaId);
      setError(null);
      await torneoService.rechazarPareja(torneoId, parejaId);
      onUpdate();
    } catch (err: any) {
      console.error('Error al rechazar pareja:', err);
      setError(err.response?.data?.detail || 'Error al eliminar pareja');
    } finally {
      setLoading(null);
    }
  };

  const darBajaPareja = async (parejaId: number) => {
    if (!confirm('¿Estás seguro de dar de baja esta pareja?')) return;

    try {
      setLoading(parejaId);
      setError(null);
      await torneoService.darBajaPareja(torneoId, parejaId, 'Baja por organizador');
      onUpdate();
    } catch (err: any) {
      console.error('Error al dar de baja:', err);
      setError(err.response?.data?.detail || 'Error al dar de baja');
    } finally {
      setLoading(null);
    }
  };

  const parejasActivas = parejas.filter((p) => p.estado !== 'baja');
  const parejasBaja = parejas.filter((p) => p.estado === 'baja');

  if (parejas.length === 0) {
    return (
      <Card>
        <div className="p-6 text-center py-12">
          <Users size={48} className="mx-auto text-textSecondary mb-4" />
          <p className="text-textSecondary">Aún no hay parejas inscritas</p>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div className="p-4 md:p-6">
        {/* Error message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3"
          >
            <AlertCircle size={18} className="text-red-500 flex-shrink-0" />
            <p className="text-red-500 text-sm flex-1">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-red-500/70 hover:text-red-500"
            >
              <X size={16} />
            </button>
          </motion.div>
        )}

        {/* Header con contador */}
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-cardBorder">
          <h3 className="font-bold text-textPrimary flex items-center gap-2">
            <Users size={20} className="text-primary" />
            Parejas Inscritas
          </h3>
          <div className="flex gap-2">
            <span className="px-3 py-1 bg-green-500/10 text-green-500 rounded-full text-xs font-bold">
              {parejas.filter((p) => p.estado === 'confirmada').length} confirmadas
            </span>
            <span className="px-3 py-1 bg-yellow-500/10 text-yellow-500 rounded-full text-xs font-bold">
              {parejas.filter((p) => p.estado === 'inscripta').length} pendientes
            </span>
          </div>
        </div>

        {/* Lista de parejas activas */}
        <div className="space-y-2">
          {parejasActivas.map((pareja, index) => (
            <motion.div
              key={pareja.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.03 }}
              className="flex items-center justify-between p-3 md:p-4 bg-background rounded-lg hover:bg-background/80 transition-colors"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary text-sm font-bold flex-shrink-0">
                  {index + 1}
                </div>
                <div className="min-w-0">
                  <p className="font-bold text-textPrimary text-sm md:text-base truncate">
                    {pareja.nombre_pareja}
                  </p>
                  {pareja.jugador1_nombre && pareja.jugador2_nombre && (
                    <p className="text-xs text-textSecondary truncate">
                      {pareja.jugador1_nombre} & {pareja.jugador2_nombre}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2">
                {/* Estado badge */}
                <span
                  className={`px-2 md:px-3 py-1 rounded-full text-[10px] md:text-xs font-bold ${
                    pareja.estado === 'confirmada'
                      ? 'bg-green-500/10 text-green-500'
                      : 'bg-yellow-500/10 text-yellow-500'
                  }`}
                >
                  {pareja.estado === 'confirmada' ? 'Confirmada' : 'Pendiente'}
                </span>

                {/* Botones de acción para organizador */}
                {esOrganizador && (
                  <div className="flex gap-1">
                    {pareja.estado === 'inscripta' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => confirmarPareja(pareja.id)}
                        disabled={loading === pareja.id}
                        className="p-2 hover:bg-green-500/10 hover:text-green-500"
                        title="Confirmar pareja"
                      >
                        <Check size={16} />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() =>
                        pareja.estado === 'inscripta'
                          ? rechazarPareja(pareja.id)
                          : darBajaPareja(pareja.id)
                      }
                      disabled={loading === pareja.id}
                      className="p-2 hover:bg-red-500/10 hover:text-red-500"
                      title="Eliminar pareja"
                    >
                      <Trash2 size={16} />
                    </Button>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Parejas dadas de baja */}
        {parejasBaja.length > 0 && (
          <div className="mt-6 pt-4 border-t border-cardBorder">
            <h4 className="text-sm font-bold text-textSecondary mb-3">
              Parejas dadas de baja ({parejasBaja.length})
            </h4>
            <div className="space-y-2 opacity-60">
              {parejasBaja.map((pareja) => (
                <div
                  key={pareja.id}
                  className="flex items-center justify-between p-3 bg-background/50 rounded-lg"
                >
                  <p className="text-textSecondary text-sm line-through">
                    {pareja.nombre_pareja}
                  </p>
                  <span className="px-2 py-1 bg-red-500/10 text-red-500 rounded-full text-xs font-bold">
                    Baja
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Acciones masivas para organizador */}
        {esOrganizador && parejas.filter((p) => p.estado === 'inscripta').length > 0 && (
          <div className="mt-6 pt-4 border-t border-cardBorder">
            <Button
              variant="accent"
              onClick={async () => {
                const pendientes = parejas.filter((p) => p.estado === 'inscripta');
                for (const pareja of pendientes) {
                  await confirmarPareja(pareja.id);
                }
              }}
              className="w-full"
            >
              <Check size={18} className="mr-2" />
              Confirmar todas las parejas pendientes
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
}
