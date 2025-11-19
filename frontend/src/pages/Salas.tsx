import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Card from '../components/Card';
import Button from '../components/Button';
import ModalCrearSala from '../components/ModalCrearSala';
import ModalUnirseSala from '../components/ModalUnirseSala';
import MarcadorInteractivo from '../components/MarcadorInteractivo';
import ModalConfirmarResultado from '../components/ModalConfirmarResultado';
import SalaCard from '../components/SalaCard';
import { Plus, Filter, AlertCircle, LogIn } from 'lucide-react';
import { useSalas } from '../context/SalasContext';
import { useAuth } from '../context/AuthContext';
import { Sala } from '../utils/types';

export default function Salas() {
  const { salas, loading, error, getSalasPendientesConfirmacion } = useSalas();
  const { usuario } = useAuth();
  const [modalCrearOpen, setModalCrearOpen] = useState(false);
  const [modalUnirseOpen, setModalUnirseOpen] = useState(false);
  const [modalMarcadorOpen, setModalMarcadorOpen] = useState(false);
  const [modalConfirmarOpen, setModalConfirmarOpen] = useState(false);
  const [salaSeleccionada, setSalaSeleccionada] = useState<Sala | null>(null);
  const [filtro, setFiltro] = useState<'todas' | 'esperando' | 'activa' | 'programada' | 'finalizada'>('todas');

  const salasPendientes = usuario ? getSalasPendientesConfirmacion(usuario.id) : [];

  const salasEsperando = salas.filter(s => s.estado === 'esperando');
  const salasActivas = salas.filter(s => s.estado === 'activa');
  const salasProgramadas = salas.filter(s => s.estado === 'programada');
  const salasFinalizadas = salas.filter(s => s.estado === 'finalizada');

  const salasFiltradas = filtro === 'todas' 
    ? salas 
    : salas.filter(s => s.estado === filtro);

  const handleOpenMarcador = (sala: Sala) => {
    setSalaSeleccionada(sala);
    setModalMarcadorOpen(true);
  };

  const handleSalaCreada = (salaId: string, codigo: string) => {
    // Opcional: navegar a la sala de espera
    console.log('Sala creada:', salaId, codigo);
  };

  const handleUnido = (salaId: string) => {
    // Opcional: navegar a la sala de espera
    console.log('Unido a sala:', salaId);
  };

  return (
    <div className="space-y-8">
      {/* Header mejorado */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
      >
        <div className="relative">
          <div className="flex items-center gap-3 mb-2">
            <div className="h-1 w-12 bg-gradient-to-r from-primary to-secondary rounded-full" />
            <h1 className="text-5xl font-black text-textPrimary tracking-tight">
              Salas
            </h1>
          </div>
          <p className="text-textSecondary text-base ml-15">Gestiona tus partidos de pádel</p>
        </div>
        <div className="flex gap-3">
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button variant="secondary" onClick={() => setModalUnirseOpen(true)}>
              <div className="flex items-center gap-2">
                <LogIn size={20} />
                Unirse a Sala
              </div>
            </Button>
          </motion.div>
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button variant="primary" onClick={() => setModalCrearOpen(true)}>
              <div className="flex items-center gap-2">
                <Plus size={20} />
                Nueva Sala
              </div>
            </Button>
          </motion.div>
        </div>
      </motion.div>

      {/* Alerta de confirmaciones pendientes */}
      {salasPendientes.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-accent/10 border border-accent/30 rounded-xl p-4"
        >
          <div className="flex items-center gap-3">
            <AlertCircle size={24} className="text-accent" />
            <div className="flex-1">
              <p className="text-accent font-bold">
                Tienes {salasPendientes.length} {salasPendientes.length === 1 ? 'partido pendiente' : 'partidos pendientes'} de confirmación
              </p>
              <p className="text-textSecondary text-sm">
                Confirma los resultados para que sean oficiales
              </p>
            </div>
            <Button
              variant="accent"
              onClick={() => {
                setSalaSeleccionada(salasPendientes[0]);
                setModalConfirmarOpen(true);
              }}
              className="text-sm"
            >
              Confirmar Ahora
            </Button>
          </div>
        </motion.div>
      )}

      {/* Estadísticas estilo gaming */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: 'Total', value: salas.length, color: 'from-cyan-500 to-blue-500', icon: '📊', borderColor: 'cyan-500' },
          { label: 'Esperando', value: salasEsperando.length, color: 'from-purple-500 to-pink-500', icon: '⏳', borderColor: 'purple-500' },
          { label: 'En Juego', value: salasActivas.length, color: 'from-secondary to-pink-500', icon: '🎾', borderColor: 'secondary' },
          { label: 'Programadas', value: salasProgramadas.length, color: 'from-primary to-blue-500', icon: '📅', borderColor: 'primary' },
          { label: 'Finalizadas', value: salasFinalizadas.length, color: 'from-accent to-yellow-400', icon: '🏆', borderColor: 'accent' }
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -6, scale: 1.03 }}
            className="group cursor-pointer relative"
          >
            <div className="bg-cardBg rounded-xl p-4 border border-cardBorder group-hover:border-transparent transition-all duration-300 relative overflow-hidden">
              {/* Glow effect */}
              <div className={`absolute -inset-[1px] bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl -z-10 blur-sm`} />
              
              <div className="flex items-center justify-between mb-2">
                <span className="text-2xl">{stat.icon}</span>
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
        ))}
      </div>

      {/* Filtros */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-2 text-textSecondary">
          <Filter size={18} />
          <span className="text-sm">Filtrar:</span>
        </div>
        {(['todas', 'esperando', 'activa', 'programada', 'finalizada'] as const).map((f) => (
          <Button
            key={f}
            variant={filtro === f ? 'primary' : 'secondary'}
            onClick={() => setFiltro(f)}
            className="text-sm"
          >
            {f === 'todas' ? 'Todas' : 
             f === 'esperando' ? 'Esperando' :
             f === 'activa' ? 'En Juego' : 
             f === 'programada' ? 'Programadas' : 
             'Finalizadas'}
          </Button>
        ))}
      </div>

      {/* Error */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/10 border border-red-500/30 rounded-xl p-4"
        >
          <div className="flex items-center gap-3">
            <AlertCircle size={24} className="text-red-500" />
            <div className="flex-1">
              <p className="text-red-500 font-bold">Error al cargar salas</p>
              <p className="text-textSecondary text-sm">{error}</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Loading */}
      {loading && (
        <Card>
          <div className="text-center py-12">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"
            />
            <p className="text-textSecondary">Cargando salas...</p>
          </div>
        </Card>
      )}

      {/* Lista de salas */}
      {!loading && salasFiltradas.length === 0 ? (
        <Card>
          <div className="text-center py-12 text-textSecondary">
            <p className="text-lg mb-4">
              {filtro === 'todas' 
                ? 'No hay salas creadas' 
                : `No hay salas ${
                    filtro === 'esperando' ? 'esperando jugadores' :
                    filtro === 'activa' ? 'en juego' : 
                    filtro === 'programada' ? 'programadas' : 
                    'finalizadas'
                  }`}
            </p>
            <p className="text-sm">
              {filtro === 'todas' && 'Crea tu primera sala para comenzar a gestionar partidos'}
            </p>
          </div>
        </Card>
      ) : !loading && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AnimatePresence mode="popLayout">
            {salasFiltradas.map((sala) => (
              <SalaCard
                key={sala.id}
                sala={sala}
                onOpenMarcador={handleOpenMarcador}
              />
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Modales */}
      <ModalCrearSala 
        isOpen={modalCrearOpen} 
        onClose={() => setModalCrearOpen(false)}
        onSalaCreada={handleSalaCreada}
      />
      <ModalUnirseSala
        isOpen={modalUnirseOpen}
        onClose={() => setModalUnirseOpen(false)}
        onUnido={handleUnido}
      />
      <MarcadorInteractivo
        isOpen={modalMarcadorOpen}
        onClose={() => {
          setModalMarcadorOpen(false);
          setSalaSeleccionada(null);
        }}
        sala={salaSeleccionada}
      />
      <ModalConfirmarResultado
        isOpen={modalConfirmarOpen}
        onClose={() => {
          setModalConfirmarOpen(false);
          setSalaSeleccionada(null);
        }}
        sala={salaSeleccionada}
      />
    </div>
  );
}
