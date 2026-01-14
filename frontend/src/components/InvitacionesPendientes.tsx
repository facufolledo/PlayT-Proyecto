import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, Check, X, Clock, Trophy, CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Button from './Button';
import torneoService from '../services/torneo.service';

interface Invitacion {
  pareja_id: number;
  torneo_id: number;
  torneo_nombre: string;
  companero_id: number;
  companero_nombre: string;
  fecha_expiracion: string;
  codigo: string;
}

interface ConfirmacionExitosa {
  torneo_id: number;
  torneo_nombre: string;
}

export default function InvitacionesPendientes() {
  const navigate = useNavigate();
  const [invitaciones, setInvitaciones] = useState<Invitacion[]>([]);
  const [loading, setLoading] = useState(true);
  const [procesando, setProcesando] = useState<number | null>(null);
  const [codigoManual, setCodigoManual] = useState('');
  const [errorCodigo, setErrorCodigo] = useState('');
  const [confirmacionExitosa, setConfirmacionExitosa] = useState<ConfirmacionExitosa | null>(null);

  useEffect(() => {
    cargarInvitaciones();
  }, []);

  const cargarInvitaciones = async () => {
    try {
      setLoading(true);
      const data = await torneoService.obtenerMisInvitaciones();
      setInvitaciones(data.invitaciones || []);
    } catch (err) {
      console.error('Error cargando invitaciones:', err);
      setInvitaciones([]);
    } finally {
      setLoading(false);
    }
  };

  const confirmarInvitacion = async (codigo: string, torneoNombre: string, torneoId: number) => {
    try {
      setProcesando(invitaciones.find(i => i.codigo === codigo)?.pareja_id || null);
      await torneoService.confirmarParejaPorCodigo(codigo);
      setConfirmacionExitosa({ torneo_id: torneoId, torneo_nombre: torneoNombre });
      await cargarInvitaciones();
    } catch (err: any) {
      console.error('Error confirmando:', err);
      console.error('Error detail:', err.response?.data);
      setErrorCodigo(err.response?.data?.detail || 'Error al confirmar');
    } finally {
      setProcesando(null);
    }
  };

  const rechazarInvitacion = async (parejaId: number) => {
    try {
      setProcesando(parejaId);
      await torneoService.rechazarInvitacion(parejaId);
      await cargarInvitaciones();
    } catch (err) {
      console.error('Error rechazando:', err);
    } finally {
      setProcesando(null);
    }
  };

  const confirmarPorCodigoManual = async () => {
    if (codigoManual.length < 6) {
      setErrorCodigo('El código debe tener 6 caracteres');
      return;
    }
    
    try {
      setErrorCodigo('');
      const resultado = await torneoService.confirmarParejaPorCodigo(codigoManual.toUpperCase());
      // Obtener info del torneo para mostrar en el modal
      const torneo = await torneoService.obtenerTorneo(resultado.torneo_id);
      setConfirmacionExitosa({ torneo_id: resultado.torneo_id, torneo_nombre: torneo.nombre || 'Torneo' });
      setCodigoManual('');
      await cargarInvitaciones();
    } catch (err: any) {
      setErrorCodigo(err.response?.data?.detail || 'Código inválido');
    }
  };

  const calcularTiempoRestante = (fechaExpiracion: string) => {
    const ahora = new Date();
    const expira = new Date(fechaExpiracion);
    const diff = expira.getTime() - ahora.getTime();
    
    if (diff <= 0) return 'Expirado';
    
    const horas = Math.floor(diff / (1000 * 60 * 60));
    const minutos = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (horas > 24) {
      return `${Math.floor(horas / 24)}d ${horas % 24}h`;
    }
    return `${horas}h ${minutos}m`;
  };

  if (loading) {
    return (
      <div className="bg-card rounded-xl p-4 border border-cardBorder animate-pulse">
        <div className="h-6 bg-cardBorder rounded w-1/3 mb-4"></div>
        <div className="h-20 bg-cardBorder rounded"></div>
      </div>
    );
  }

  return (
    <div className="bg-card rounded-xl border border-cardBorder overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-cardBorder flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Users size={20} className="text-accent" />
          <h3 className="font-bold text-textPrimary">Invitaciones a Torneos</h3>
          {invitaciones.length > 0 && (
            <span className="bg-accent text-white text-xs font-bold px-2 py-0.5 rounded-full">
              {invitaciones.length}
            </span>
          )}
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Input para código manual */}
        <div className="flex gap-2">
          <input
            type="text"
            value={codigoManual}
            onChange={(e) => setCodigoManual(e.target.value.toUpperCase())}
            placeholder="Ingresa código de invitación"
            maxLength={6}
            className="flex-1 px-3 py-2 bg-background border border-cardBorder rounded-lg text-sm text-textPrimary placeholder-textSecondary focus:outline-none focus:border-primary uppercase tracking-widest font-mono"
          />
          <Button
            variant="accent"
            onClick={confirmarPorCodigoManual}
            disabled={codigoManual.length < 6}
            className="text-sm px-4"
          >
            Confirmar
          </Button>
        </div>
        
        {errorCodigo && (
          <p className="text-xs text-red-500">{errorCodigo}</p>
        )}

        {/* Lista de invitaciones */}
        {invitaciones.length === 0 ? (
          <div className="text-center py-6 text-textSecondary">
            <Trophy size={32} className="mx-auto mb-2 opacity-50" />
            <p className="text-sm">No tienes invitaciones pendientes</p>
          </div>
        ) : (
          <AnimatePresence>
            {invitaciones.map((inv) => (
              <motion.div
                key={inv.pareja_id}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -100 }}
                className="bg-background rounded-lg p-3 border border-cardBorder"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-textPrimary text-sm truncate">
                      {inv.torneo_nombre}
                    </p>
                    <p className="text-xs text-textSecondary">
                      Compañero: <span className="text-primary">{inv.companero_nombre}</span>
                    </p>
                    <div className="flex items-center gap-1 mt-1 text-xs text-yellow-500">
                      <Clock size={12} />
                      <span>Expira en {calcularTiempoRestante(inv.fecha_expiracion)}</span>
                    </div>
                  </div>
                  
                  <div className="flex gap-2 flex-shrink-0">
                    <button
                      onClick={() => rechazarInvitacion(inv.pareja_id)}
                      disabled={procesando === inv.pareja_id}
                      className="p-2 rounded-lg bg-red-500/10 text-red-500 hover:bg-red-500/20 transition-colors disabled:opacity-50"
                      title="Rechazar"
                    >
                      <X size={16} />
                    </button>
                    <button
                      onClick={() => confirmarInvitacion(inv.codigo, inv.torneo_nombre, inv.torneo_id)}
                      disabled={procesando === inv.pareja_id}
                      className="p-2 rounded-lg bg-green-500/10 text-green-500 hover:bg-green-500/20 transition-colors disabled:opacity-50"
                      title="Aceptar"
                    >
                      <Check size={16} />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>

      {/* Modal de confirmación exitosa */}
      <AnimatePresence>
        {confirmacionExitosa && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setConfirmacionExitosa(null)}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            />
            <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="bg-cardBg rounded-xl border border-cardBorder p-6 max-w-sm w-full text-center"
              >
                <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle size={32} className="text-green-500" />
                </div>
                <h3 className="text-xl font-bold text-textPrimary mb-2">
                  ¡Inscripción Confirmada!
                </h3>
                <p className="text-textSecondary text-sm mb-4">
                  Ya estás inscripto en <span className="text-primary font-bold">{confirmacionExitosa.torneo_nombre}</span>
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    onClick={() => setConfirmacionExitosa(null)}
                    className="flex-1"
                  >
                    Cerrar
                  </Button>
                  <Button
                    variant="accent"
                    onClick={() => {
                      setConfirmacionExitosa(null);
                      navigate(`/torneos/${confirmacionExitosa.torneo_id}`);
                    }}
                    className="flex-1"
                  >
                    Ver Torneo
                  </Button>
                </div>
              </motion.div>
            </div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
