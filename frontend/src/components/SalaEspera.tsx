import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X, Copy, Users, Play, Crown } from 'lucide-react';
import Modal from './Modal';
import Button from './Button';
import AsignarEquipos from './AsignarEquipos';
import ModalAntiTrampa from './ModalAntiTrampa';
import { Sala } from '../utils/types';
import { useAuth } from '../context/AuthContext';
import { salaService } from '../services/sala.service';
import { useSalas } from '../context/SalasContext';

interface SalaEsperaProps {
  isOpen: boolean;
  onClose: () => void;
  sala: Sala | null;
  onIniciarPartido: () => void;
}

export default function SalaEspera({ isOpen, onClose, sala, onIniciarPartido }: SalaEsperaProps) {
  const { usuario } = useAuth();
  const { cargarSalas } = useSalas();
  const [copiado, setCopiado] = useState(false);
  const [asignando, setAsignando] = useState(false);
  const [mostrarAsignacion, setMostrarAsignacion] = useState(false);
  const [errorAntiTrampa, setErrorAntiTrampa] = useState<{
    mensaje: string;
    jugadores: string[];
    partidos: number;
    limite: number;
  } | null>(null);

  // Recargar salas cada vez que se abre el modal y cada 30 segundos
  useEffect(() => {
    if (isOpen) {
      cargarSalas();
      
      // Polling cada 30 segundos para actualizar jugadores (reducido de 15s)
      const interval = setInterval(() => {
        cargarSalas();
      }, 30000);
      
      return () => clearInterval(interval);
    }
  }, [isOpen, cargarSalas]);

  if (!sala) return null;

  const esCreador = usuario?.id_usuario === sala.creador_id;
  const jugadores = sala.jugadores || [];
  const hayEquiposAsignados = sala.equiposAsignados;
  const puedeIniciar = jugadores.length === 4 && hayEquiposAsignados;
  
  // Verificar si el usuario es participante de la sala
  const esParticipante = jugadores.some(j => j.id === usuario?.id_usuario?.toString());

  const copiarCodigo = () => {
    if (sala.codigoInvitacion) {
      navigator.clipboard.writeText(sala.codigoInvitacion);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    }
  };

  const [mensajeExito, setMensajeExito] = useState<string | null>(null);

  const handleAsignarEquipos = async (equipos: { [key: string]: number }) => {
    if (!esCreador) return;

    try {
      setAsignando(true);
      await salaService.asignarEquipos(parseInt(sala.id), equipos);
      setMostrarAsignacion(false);
      
      // Mostrar mensaje de éxito
      setMensajeExito('¡Equipos asignados correctamente!');
      
      // Recargar salas para actualizar la vista
      await cargarSalas();
      
      // Ocultar mensaje después de 2 segundos
      setTimeout(() => {
        setMensajeExito(null);
      }, 2000);
    } catch (error: any) {
      console.error('Error al asignar equipos:', error);
      alert(error.message || 'Error al asignar equipos');
    } finally {
      setAsignando(false);
    }
  };

  const iniciarPartido = async () => {
    if (!esCreador || !puedeIniciar) return;

    try {
      setMensajeExito('Iniciando partido...');
      const resultado = await salaService.iniciarPartido(parseInt(sala.id));
      
      // Mostrar éxito y abrir marcador inmediatamente
      setMensajeExito('¡Partido iniciado!');
      
      // Abrir marcador sin esperar a que se recarguen las salas
      onIniciarPartido();
      
      // Recargar salas en segundo plano
      cargarSalas().catch(err => console.error('Error al recargar:', err));
    } catch (error: any) {
      console.error('Error completo al iniciar partido:', error);
      
      // Mostrar modal para error de anti-trampa
      if (error.message && error.message.includes('ya jugó')) {
        // Extraer información del mensaje
        const partes = error.message.split('Límite:');
        const mensaje = partes[0].trim();
        
        // Intentar extraer nombres de jugadores del mensaje
        const matchJugadores = mensaje.match(/\((.*?)\)/);
        const jugadores = matchJugadores 
          ? matchJugadores[1].split(',').map((j: string) => j.trim())
          : [];
        
        // Extraer números de partidos
        const matchPartidos = mensaje.match(/(\d+)\s+partidos/);
        const partidos = matchPartidos ? parseInt(matchPartidos[1]) : 2;
        
        setErrorAntiTrampa({
          mensaje: mensaje,
          jugadores: jugadores,
          partidos: partidos,
          limite: 2
        });
      } else {
        alert(error.message || 'Error al iniciar partido');
      }
    }
  };

  return (
    <>
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="bg-cardBg rounded-2xl md:rounded-3xl p-4 md:p-6 w-full max-w-2xl border border-cardBorder shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 md:mb-6">
          <div className="flex-1 min-w-0">
            <h2 className="text-lg md:text-2xl font-bold text-textPrimary mb-1 truncate">
              {sala.nombre}
            </h2>
            <p className="text-textSecondary text-xs md:text-sm">
              Sala de Espera • {jugadores.length}/4 jugadores
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

        {/* Mensaje de éxito */}
        {mensajeExito && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-green-500/10 border border-green-500/30 rounded-xl p-3 mb-4 text-center"
          >
            <p className="text-green-500 font-bold text-sm">✓ {mensajeExito}</p>
          </motion.div>
        )}

        {/* Código de invitación - Solo visible para participantes */}
        {esParticipante ? (
          <div className="bg-background rounded-xl p-4 mb-4 md:mb-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-textSecondary text-xs md:text-sm mb-1">Código de Invitación</p>
                <p className="text-primary text-2xl md:text-3xl font-black tracking-widest">
                  {sala.codigoInvitacion || 'N/A'}
                </p>
              </div>
              <Button
                variant="ghost"
                onClick={copiarCodigo}
                className="flex flex-col items-center gap-1 px-3 md:px-4"
              >
                <Copy size={20} />
                <span className="text-xs">{copiado ? '✓ Copiado' : 'Copiar'}</span>
              </Button>
            </div>
          </div>
        ) : (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 mb-4 md:mb-6 text-center">
            <p className="text-red-500 font-bold text-sm mb-1">🔒 Acceso Restringido</p>
            <p className="text-textSecondary text-xs">
              Debes ser invitado para ver esta sala
            </p>
          </div>
        )}

        {/* Lista de jugadores */}
        <div className="mb-4 md:mb-6">
          <div className="flex items-center gap-2 mb-3">
            <Users size={18} className="text-primary" />
            <h3 className="text-textPrimary font-bold text-sm md:text-base">
              Jugadores ({jugadores.length}/4)
            </h3>
          </div>

          <div className="space-y-2">
            {jugadores.map((jugador) => {
              const esCreador = jugador.id === sala.creador_id?.toString();
              return (
                <motion.div
                  key={jugador.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="bg-background rounded-lg p-3 flex items-center gap-3"
                >
                  <div className={`w-10 h-10 rounded-full ${esCreador ? 'bg-accent/20' : 'bg-gradient-to-br from-primary to-secondary'} flex items-center justify-center text-white font-bold flex-shrink-0 relative`}>
                    <span className={esCreador ? 'text-accent' : ''}>
                      {jugador.nombre.charAt(0).toUpperCase()}
                    </span>
                    {esCreador && (
                      <Crown size={14} className="absolute -top-1 -right-1 text-accent" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-textPrimary font-semibold text-sm md:text-base truncate">
                        {jugador.nombre}
                      </p>
                      {esCreador && (
                        <span className="text-accent text-xs font-bold">Anfitrión</span>
                      )}
                    </div>
                    <p className="text-textSecondary text-xs">
                      Rating: {jugador.rating || 1500}
                    </p>
                  </div>
                </motion.div>
              );
            })}

            {/* Espacios vacíos */}
            {Array.from({ length: 4 - jugadores.length }).map((_, i) => (
              <div
                key={`empty-${i}`}
                className="bg-background/50 rounded-lg p-3 border-2 border-dashed border-cardBorder flex items-center gap-3"
              >
                <div className="w-10 h-10 rounded-full bg-cardBorder flex items-center justify-center flex-shrink-0">
                  <Users size={18} className="text-textSecondary" />
                </div>
                <p className="text-textSecondary text-sm">Esperando jugador...</p>
              </div>
            ))}
          </div>
        </div>

        {/* Equipos asignados */}
        {hayEquiposAsignados && (
          <div className="mb-4 md:mb-6 bg-accent/10 border border-accent/30 rounded-xl p-4">
            <p className="text-accent font-bold text-sm mb-3">✓ Equipos Asignados</p>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-primary/10 rounded-lg p-3">
                <p className="text-primary font-bold text-xs mb-2">EQUIPO A</p>
                <p className="text-textPrimary text-xs">{sala.equipoA.jugador1.nombre}</p>
                <p className="text-textPrimary text-xs">{sala.equipoA.jugador2.nombre}</p>
              </div>
              <div className="bg-secondary/10 rounded-lg p-3">
                <p className="text-secondary font-bold text-xs mb-2">EQUIPO B</p>
                <p className="text-textPrimary text-xs">{sala.equipoB.jugador1.nombre}</p>
                <p className="text-textPrimary text-xs">{sala.equipoB.jugador2.nombre}</p>
              </div>
            </div>
          </div>
        )}

        {/* Asignación de equipos */}
        {esCreador && jugadores.length === 4 && !hayEquiposAsignados && mostrarAsignacion && (
          <div className="mb-4 bg-background rounded-xl p-4">
            <AsignarEquipos
              jugadores={jugadores}
              onAsignar={handleAsignarEquipos}
              onCancelar={() => setMostrarAsignacion(false)}
              loading={asignando}
              creadorId={typeof sala.creador_id === 'number' ? sala.creador_id : parseInt(sala.creador_id?.toString() || '0')}
            />
          </div>
        )}

        {/* Botones de acción */}
        {esCreador && (
          <div className="space-y-2">
            {jugadores.length === 4 && !hayEquiposAsignados && !mostrarAsignacion && (
              <Button
                variant="secondary"
                onClick={() => setMostrarAsignacion(true)}
                disabled={asignando}
                className="w-full flex items-center justify-center gap-2"
              >
                <Users size={18} />
                Asignar Equipos
              </Button>
            )}

            {puedeIniciar && (
              <Button
                variant="primary"
                onClick={iniciarPartido}
                className="w-full flex items-center justify-center gap-2"
              >
                <Play size={18} />
                Iniciar Partido
              </Button>
            )}

            {jugadores.length < 4 && (
              <div className="bg-primary/10 border border-primary/30 rounded-xl p-3 text-center">
                <p className="text-textSecondary text-xs">
                  Esperando {4 - jugadores.length} jugador{4 - jugadores.length > 1 ? 'es' : ''} más...
                </p>
              </div>
            )}
          </div>
        )}

        {!esCreador && esParticipante && (
          <div className="bg-background rounded-xl p-4 text-center">
            <p className="text-textSecondary text-sm">
              Esperando que el creador inicie el partido...
            </p>
          </div>
        )}
      </div>
    </Modal>

    {/* Modal de error anti-trampa */}
    {errorAntiTrampa && (
      <ModalAntiTrampa
        isOpen={true}
        onClose={() => setErrorAntiTrampa(null)}
        mensaje={errorAntiTrampa.mensaje}
        jugadoresBloqueados={errorAntiTrampa.jugadores}
        partidosJugados={errorAntiTrampa.partidos}
        limite={errorAntiTrampa.limite}
      />
    )}
  </>
  );
}
