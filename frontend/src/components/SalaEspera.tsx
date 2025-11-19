import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Copy, Share2, MessageCircle, Users, Calendar, Clock, 
  Crown, LogOut, Play, UserPlus, AlertCircle 
} from 'lucide-react';
import Button from './Button';
import { Sala } from '../utils/types';
import { useAuth } from '../context/AuthContext';

interface SalaEsperaProps {
  sala: Sala;
  onAsignarEquipos: () => void;
  onIniciarPartido: () => void;
  onSalir: () => void;
}

export default function SalaEspera({ sala, onAsignarEquipos, onIniciarPartido, onSalir }: SalaEsperaProps) {
  const { usuario } = useAuth();
  const [copiado, setCopiado] = useState(false);
  
  const esCreador = sala.jugadores?.some(j => j.id === usuario?.id && j.esCreador);
  const jugadoresActuales = sala.jugadores?.length || 0;
  const salaLlena = jugadoresActuales === 4;
  const puedeAsignarEquipos = esCreador && salaLlena && !sala.equiposAsignados;
  const puedeIniciar = esCreador && sala.equiposAsignados;

  const copiarCodigo = () => {
    if (sala.codigoInvitacion) {
      navigator.clipboard.writeText(sala.codigoInvitacion);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    }
  };

  const compartirWhatsApp = () => {
    if (sala.codigoInvitacion) {
      const mensaje = `¡Únete a mi partido de pádel!\n\n📍 ${sala.nombre}\n📅 ${new Date(sala.fecha).toLocaleDateString()}\n⏰ ${new Date(sala.fecha).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}\n\n🔑 Código: ${sala.codigoInvitacion}\n\nEntra a PlayR y usa este código para unirte.`;
      window.open(`https://wa.me/?text=${encodeURIComponent(mensaje)}`, '_blank');
    }
  };

  const compartirLink = () => {
    if (sala.codigoInvitacion) {
      const link = `${window.location.origin}/salas/unirse/${sala.codigoInvitacion}`;
      navigator.clipboard.writeText(link);
      alert('¡Link copiado!');
    }
  };

  // Simular actualización en tiempo real (en producción usar WebSockets)
  useEffect(() => {
    const interval = setInterval(() => {
      // Aquí iría la lógica de polling o WebSocket
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header con código */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-primary/20 to-secondary/20 rounded-2xl p-6 border border-primary/30"
      >
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-center md:text-left">
            <h1 className="text-3xl font-black text-textPrimary mb-2">{sala.nombre}</h1>
            <div className="flex flex-wrap items-center gap-4 text-textSecondary text-sm">
              <span className="flex items-center gap-1">
                <Calendar size={16} />
                {new Date(sala.fecha).toLocaleDateString('es-ES', { 
                  weekday: 'long', 
                  day: 'numeric', 
                  month: 'long' 
                })}
              </span>
              <span className="flex items-center gap-1">
                <Clock size={16} />
                {new Date(sala.fecha).toLocaleTimeString('es-ES', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </span>
            </div>
          </div>

          <div className="text-center">
            <p className="text-textSecondary text-xs mb-2">Código de Invitación</p>
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="text-4xl font-black text-primary tracking-widest cursor-pointer"
              onClick={copiarCodigo}
            >
              {sala.codigoInvitacion}
            </motion.div>
            {copiado && (
              <motion.p
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="text-secondary text-xs mt-1"
              >
                ✓ Copiado
              </motion.p>
            )}
          </div>
        </div>

        {/* Botones de compartir */}
        <div className="flex flex-wrap gap-2 mt-4">
          <Button
            variant="ghost"
            onClick={copiarCodigo}
            className="flex-1 min-w-[140px] flex items-center justify-center gap-2"
          >
            <Copy size={16} />
            Copiar Código
          </Button>
          <Button
            variant="ghost"
            onClick={compartirWhatsApp}
            className="flex-1 min-w-[140px] flex items-center justify-center gap-2 bg-[#25D366]/20 hover:bg-[#25D366]/30 text-[#25D366]"
          >
            <MessageCircle size={16} />
            WhatsApp
          </Button>
          <Button
            variant="ghost"
            onClick={compartirLink}
            className="flex-1 min-w-[140px] flex items-center justify-center gap-2"
          >
            <Share2 size={16} />
            Copiar Link
          </Button>
        </div>
      </motion.div>

      {/* Lista de jugadores */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-cardBg rounded-2xl p-6 border border-cardBorder"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-textPrimary flex items-center gap-2">
            <Users size={24} />
            Jugadores
          </h2>
          <div className="bg-primary/20 px-4 py-2 rounded-full">
            <span className="text-primary font-bold">{jugadoresActuales}/4</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <AnimatePresence>
            {sala.jugadores?.map((jugador, index) => (
              <motion.div
                key={jugador.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: index * 0.1 }}
                className="bg-background rounded-xl p-4 border border-cardBorder flex items-center gap-3"
              >
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-bold text-lg">
                  {jugador.nombre.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1">
                  <p className="text-textPrimary font-semibold flex items-center gap-2">
                    {jugador.nombre}
                    {jugador.esCreador && (
                      <Crown size={16} className="text-accent" />
                    )}
                  </p>
                  <p className="text-textSecondary text-sm">
                    Rating: {jugador.rating || 1000}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Slots vacíos */}
          {Array.from({ length: 4 - jugadoresActuales }).map((_, index) => (
            <motion.div
              key={`empty-${index}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: (jugadoresActuales + index) * 0.1 }}
              className="bg-background/50 rounded-xl p-4 border border-dashed border-cardBorder flex items-center gap-3"
            >
              <div className="w-12 h-12 rounded-full bg-cardBorder flex items-center justify-center">
                <UserPlus size={24} className="text-textSecondary" />
              </div>
              <div>
                <p className="text-textSecondary font-semibold">Esperando...</p>
                <p className="text-textSecondary text-sm">Slot disponible</p>
              </div>
            </motion.div>
          ))}
        </div>

        {!salaLlena && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 bg-primary/10 border border-primary/30 rounded-xl p-4 flex items-start gap-3"
          >
            <AlertCircle size={20} className="text-primary flex-shrink-0 mt-0.5" />
            <p className="text-textSecondary text-sm">
              Esperando {4 - jugadoresActuales} jugador{4 - jugadoresActuales !== 1 ? 'es' : ''} más. 
              Comparte el código para que se unan.
            </p>
          </motion.div>
        )}
      </motion.div>

      {/* Acciones */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="flex flex-col sm:flex-row gap-3"
      >
        <Button
          variant="ghost"
          onClick={onSalir}
          className="flex items-center justify-center gap-2"
        >
          <LogOut size={18} />
          Salir de la Sala
        </Button>

        {esCreador && (
          <>
            {puedeAsignarEquipos && (
              <Button
                variant="secondary"
                onClick={onAsignarEquipos}
                className="flex-1 flex items-center justify-center gap-2"
              >
                <Users size={18} />
                Asignar Equipos
              </Button>
            )}

            {puedeIniciar && (
              <Button
                variant="primary"
                onClick={onIniciarPartido}
                className="flex-1 flex items-center justify-center gap-2"
              >
                <Play size={18} />
                Iniciar Partido
              </Button>
            )}

            {!salaLlena && (
              <div className="flex-1 bg-cardBorder/50 rounded-xl p-4 text-center">
                <p className="text-textSecondary text-sm">
                  Esperando jugadores para continuar...
                </p>
              </div>
            )}
          </>
        )}
      </motion.div>

      {/* Indicador de actualización en tiempo real */}
      <motion.div
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="text-center text-textSecondary text-xs flex items-center justify-center gap-2"
      >
        <div className="w-2 h-2 bg-secondary rounded-full" />
        Actualizando en tiempo real
      </motion.div>
    </div>
  );
}
