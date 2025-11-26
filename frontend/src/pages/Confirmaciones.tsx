import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, CheckCircle, Clock, Users, Bell } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import ModalConfirmarResultado from '../components/ModalConfirmarResultado';
import { useSalas } from '../context/SalasContext';
import { useAuth } from '../context/AuthContext';
import { Sala } from '../utils/types';

export default function Confirmaciones() {
  const { salas, getSalasPendientesConfirmacion } = useSalas();
  const { usuario } = useAuth();
  const [modalOpen, setModalOpen] = useState(false);
  const [salaSeleccionada, setSalaSeleccionada] = useState<Sala | null>(null);

  const salasPendientes = usuario ? getSalasPendientesConfirmacion(usuario.id) : [];
  const salasConfirmadas = salas.filter(s => s.estado === 'finalizada' && s.resultadoFinal);
  const salasDisputadas = salas.filter(s => s.estadoConfirmacion === 'disputado');

  const handleConfirmar = (sala: Sala) => {
    setSalaSeleccionada(sala);
    setModalOpen(true);
  };

  const getEquipoUsuario = (sala: Sala) => {
    if (!usuario) return null;
    const estaEnA = sala.equipoA.jugador1.id === usuario.id || sala.equipoA.jugador2.id === usuario.id;
    return estaEnA ? 'equipoA' : 'equipoB';
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="h-1 w-12 bg-gradient-to-r from-accent to-yellow-500 rounded-full" />
          <h1 className="text-5xl font-black text-textPrimary tracking-tight">
            Confirmaciones
          </h1>
        </div>
        <p className="text-textSecondary text-base ml-15">Confirma los resultados de tus partidos</p>
      </motion.div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label: 'Pendientes', value: salasPendientes.length, color: 'from-accent to-yellow-500', icon: Clock },
          { label: 'Confirmadas', value: salasConfirmadas.length, color: 'from-secondary to-pink-500', icon: CheckCircle },
          { label: 'Disputadas', value: salasDisputadas.length, color: 'from-red-500 to-red-600', icon: AlertCircle }
        ].map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ y: -6, scale: 1.03 }}
              className="group cursor-pointer relative"
            >
              <div className="bg-cardBg rounded-xl p-4 border border-cardBorder group-hover:border-transparent transition-all duration-300 relative overflow-hidden">
                <div className={`absolute -inset-[1px] bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl -z-10 blur-sm`} />
                
                <div className="flex items-center justify-between mb-2">
                  <div className={`bg-gradient-to-br ${stat.color} p-2 rounded-lg`}>
                    <Icon size={20} className="text-white" />
                  </div>
                  <motion.p 
                    className="text-4xl font-black text-textPrimary tracking-tight"
                    key={stat.value}
                    initial={{ scale: 1.3, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    {stat.value}
                  </motion.p>
                </div>
                <p className="text-textSecondary text-xs font-bold uppercase tracking-wider">{stat.label}</p>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Partidos Pendientes */}
      <div>
        <h2 className="text-2xl font-bold text-textPrimary mb-4 flex items-center gap-2">
          <Clock className="text-accent" size={28} />
          Pendientes de Confirmación
        </h2>

        {salasPendientes.length === 0 ? (
          <Card>
            <div className="text-center py-12 text-textSecondary">
              <div className="bg-accent/10 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
                <Bell size={40} className="text-accent" />
              </div>
              <p className="text-lg mb-4">No tienes confirmaciones pendientes</p>
              <p className="text-sm">Cuando finalices un partido, aparecerá aquí para confirmar</p>
            </div>
          </Card>
        ) : (
          <div className="space-y-4">
            <AnimatePresence mode="popLayout">
              {salasPendientes.map((sala, index) => {
                const equipoUsuario = getEquipoUsuario(sala);
                const otroEquipo = equipoUsuario === 'equipoA' ? 'equipoB' : 'equipoA';
                const otroEquipoConfirmo = sala[otroEquipo].confirmado;

                return (
                  <motion.div
                    key={sala.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ scale: 1.02, x: 5 }}
                  >
                    <Card hoverable>
                      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-3">
                            <h3 className="text-xl font-bold text-textPrimary">{sala.nombre}</h3>
                            {otroEquipoConfirmo && (
                              <span className="px-2 py-1 rounded-full bg-secondary/10 text-secondary text-xs font-bold flex items-center gap-1">
                                <CheckCircle size={12} />
                                Rival confirmó
                              </span>
                            )}
                          </div>
                          
                          <div className="flex items-center gap-6 text-sm mb-3">
                            <div className={`flex items-center gap-2 ${sala.ganador === 'equipoA' ? 'text-primary font-bold' : 'text-textSecondary'}`}>
                              <Users size={16} />
                              <span>{sala.equipoA.jugador1.nombre} / {sala.equipoA.jugador2.nombre}</span>
                              <span className="text-2xl font-black">{sala.equipoA.puntos}</span>
                            </div>
                            <span className="text-textSecondary font-bold">VS</span>
                            <div className={`flex items-center gap-2 ${sala.ganador === 'equipoB' ? 'text-secondary font-bold' : 'text-textSecondary'}`}>
                              <span className="text-2xl font-black">{sala.equipoB.puntos}</span>
                              <span>{sala.equipoB.jugador1.nombre} / {sala.equipoB.jugador2.nombre}</span>
                            </div>
                          </div>

                          <p className="text-textSecondary text-xs">
                            {new Date(sala.fecha).toLocaleDateString('es-ES', { 
                              day: 'numeric', 
                              month: 'long', 
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        </div>

                        <Button
                          variant="accent"
                          onClick={() => handleConfirmar(sala)}
                        >
                          Confirmar Resultado
                        </Button>
                      </div>
                    </Card>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Partidos Confirmados Recientes */}
      {salasConfirmadas.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-textPrimary mb-4 flex items-center gap-2">
            <CheckCircle className="text-secondary" size={28} />
            Confirmados Recientemente
          </h2>

          <div className="space-y-3">
            {salasConfirmadas.slice(0, 5).map((sala, index) => (
              <motion.div
                key={sala.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card>
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="text-textPrimary font-bold mb-2">{sala.nombre}</p>
                      <div className="flex items-center gap-4 text-sm">
                        <span className={`${sala.ganador === 'equipoA' ? 'text-primary font-bold' : 'text-textSecondary'}`}>
                          {sala.equipoA.jugador1.nombre} / {sala.equipoA.jugador2.nombre} - {sala.equipoA.puntos}
                        </span>
                        <span className="text-textSecondary">VS</span>
                        <span className={`${sala.ganador === 'equipoB' ? 'text-secondary font-bold' : 'text-textSecondary'}`}>
                          {sala.equipoB.puntos} - {sala.equipoB.jugador1.nombre} / {sala.equipoB.jugador2.nombre}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-secondary text-sm font-bold">
                      <CheckCircle size={16} />
                      Confirmado
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      <ModalConfirmarResultado
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSalaSeleccionada(null);
        }}
        sala={salaSeleccionada}
      />
    </div>
  );
}
