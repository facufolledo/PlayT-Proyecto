import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Card from '../components/Card';
import Button from '../components/Button';
import ModalCrearSala from '../components/ModalCrearSala';
import ModalUnirseSala from '../components/ModalUnirseSala';
import SalaEspera from '../components/SalaEspera';
import MarcadorPadel from '../components/MarcadorPadel';
import ModalConfirmarResultado from '../components/ModalConfirmarResultado';
import SalaCard from '../components/SalaCard';
import { Plus, Filter, AlertCircle } from 'lucide-react';
import { useSalas } from '../context/SalasContext';
import { useAuth } from '../context/AuthContext';
import { Sala } from '../utils/types';

export default function Salas() {
  const { salas, getSalasPendientesConfirmacion, cargarSalas } = useSalas();
  const { usuario } = useAuth();
  const [codigoUrl, setCodigoUrl] = useState<string | null>(null);

  // Cargar salas cuando se monta la página y hay usuario
  useEffect(() => {
    if (usuario) {
      cargarSalas();
    }
    
    // Verificar si hay un código en la URL
    const params = new URLSearchParams(window.location.search);
    const codigo = params.get('codigo');
    if (codigo) {
      // Guardar código y abrir modal
      setCodigoUrl(codigo);
      setModalUnirseOpen(true);
      // Limpiar la URL
      window.history.replaceState({}, '', '/salas');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [usuario]);
  const [modalCrearOpen, setModalCrearOpen] = useState(false);
  const [modalUnirseOpen, setModalUnirseOpen] = useState(false);
  const [modalEsperaOpen, setModalEsperaOpen] = useState(false);
  const [modalMarcadorOpen, setModalMarcadorOpen] = useState(false);
  const [modalConfirmarOpen, setModalConfirmarOpen] = useState(false);
  const [salaSeleccionada, setSalaSeleccionada] = useState<Sala | null>(null);
  const [filtro, setFiltro] = useState<'todas' | 'activa' | 'programada' | 'finalizada'>('todas');
  const [mostrarTodas, setMostrarTodas] = useState(false);
  const ITEMS_POR_PAGINA = 20;

  const salasPendientes = usuario ? getSalasPendientesConfirmacion(usuario.id_usuario?.toString() || '') : [];

  const salasActivas = salas.filter(s => s.estado === 'activa' || s.estado === 'en_juego');
  const salasProgramadas = salas.filter(s => s.estado === 'programada');
  const salasFinalizadas = salas.filter(s => s.estado === 'finalizada');

  const salasFiltradas = filtro === 'todas'
    ? salas
    : filtro === 'activa' 
      ? salas.filter(s => s.estado === 'activa' || s.estado === 'en_juego')
      : salas.filter(s => s.estado === filtro);

  const salasMostradas = mostrarTodas ? salasFiltradas : salasFiltradas.slice(0, ITEMS_POR_PAGINA);

  const handleOpenMarcador = (sala: Sala) => {
    setSalaSeleccionada(sala);
    
    // Si la sala está en espera, abrir sala de espera
    if (sala.estado === 'esperando') {
      setModalEsperaOpen(true);
    } else if (sala.estado === 'en_juego' || sala.estado === 'activa') {
      // Si está en juego o activa, abrir marcador
      setModalMarcadorOpen(true);
    } else {
      // Para otros estados (programada, etc), abrir sala de espera
      setModalEsperaOpen(true);
    }
  };

  const handleIniciarPartido = () => {
    // Cerrar sala de espera y abrir marcador
    setModalEsperaOpen(false);
    setModalMarcadorOpen(true);
  };

  return (
    <div className="space-y-8">
      {/* Header mejorado */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 md:gap-4"
      >
        <div className="relative">
          <div className="flex items-center gap-2 md:gap-3 mb-1 md:mb-2">
            <div className="h-0.5 md:h-1 w-8 md:w-12 bg-gradient-to-r from-primary to-secondary rounded-full" />
            <h1 className="text-2xl md:text-5xl font-black text-textPrimary tracking-tight">
              Salas
            </h1>
          </div>
          <p className="text-textSecondary text-xs md:text-base ml-10 md:ml-15">Gestiona tus partidos de pádel</p>
        </div>
        <div className="flex gap-2">
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button variant="secondary" onClick={() => setModalUnirseOpen(true)} className="text-xs md:text-sm px-3 md:px-4 py-2 md:py-2.5">
              <div className="flex items-center gap-1 md:gap-2">
                <span className="text-lg">🔗</span>
                <span className="hidden sm:inline">Unirse</span>
              </div>
            </Button>
          </motion.div>
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button variant="primary" onClick={() => setModalCrearOpen(true)} className="text-xs md:text-sm px-3 md:px-4 py-2 md:py-2.5">
              <div className="flex items-center gap-1 md:gap-2">
                <Plus size={16} className="md:w-[18px] md:h-[18px]" />
                <span className="hidden sm:inline">Nueva Sala</span>
                <span className="sm:hidden">Nueva</span>
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
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-4">
        {[
          { label: 'Total', value: salas.length, color: 'from-cyan-500 to-blue-500', icon: '📊', borderColor: 'cyan-500' },
          { label: 'En Juego', value: salasActivas.length, color: 'from-secondary to-pink-500', icon: '🎾', borderColor: 'secondary' },
          { label: 'Programadas', value: salasProgramadas.length, color: 'from-primary to-blue-500', icon: '📅', borderColor: 'primary' },
          { label: 'Finalizadas', value: salasFinalizadas.length, color: 'from-accent to-yellow-400', icon: '🏆', borderColor: 'accent' }
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            whileHover={{ y: -4, scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="group cursor-pointer relative"
          >
            <div className="bg-cardBg rounded-lg md:rounded-xl p-2 md:p-4 border border-cardBorder group-hover:border-transparent transition-all duration-200 relative overflow-hidden">
              {/* Glow effect - solo desktop */}
              <div className={`hidden md:block absolute -inset-[1px] bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-xl -z-10 blur-sm`} />

              <div className="flex items-center justify-between mb-1 md:mb-2">
                <span className="text-lg md:text-2xl">{stat.icon}</span>
                <p className="text-2xl md:text-4xl font-black text-textPrimary tracking-tight">
                  {stat.value}
                </p>
              </div>
              <p className="text-textSecondary text-[10px] md:text-xs font-bold uppercase tracking-wider">{stat.label}</p>
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
        {(['todas', 'activa', 'programada', 'finalizada'] as const).map((f) => (
          <Button
            key={f}
            variant={filtro === f ? 'primary' : 'secondary'}
            onClick={() => setFiltro(f)}
            className="text-sm"
          >
            {f === 'todas' ? 'Todas' : f === 'activa' ? 'En Juego' : f === 'programada' ? 'Programadas' : 'Finalizadas'}
          </Button>
        ))}
      </div>

      {/* Lista de salas */}
      {salasFiltradas.length === 0 ? (
        <Card>
          <div className="text-center py-8 md:py-12 text-textSecondary px-4">
            <p className="text-base md:text-lg mb-2 md:mb-4">
              {filtro === 'todas'
                ? 'No hay salas creadas'
                : `No hay salas ${filtro === 'activa' ? 'en juego' : filtro === 'programada' ? 'programadas' : 'finalizadas'}`}
            </p>
            <p className="text-xs md:text-sm">
              {filtro === 'todas' && 'Crea tu primera sala para comenzar a gestionar partidos'}
            </p>
          </div>
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 md:gap-6">
            <AnimatePresence mode="popLayout">
              {salasMostradas.map((sala) => (
                <SalaCard
                  key={sala.id}
                  sala={sala}
                  onOpenMarcador={handleOpenMarcador}
                />
              ))}
            </AnimatePresence>
          </div>

          {/* Botón Cargar Más */}
          {!mostrarTodas && salasFiltradas.length > ITEMS_POR_PAGINA && (
            <div className="mt-4 md:mt-6 text-center">
              <Button
                variant="primary"
                onClick={() => setMostrarTodas(true)}
                className="w-full md:w-auto"
              >
                Cargar más ({salasFiltradas.length - ITEMS_POR_PAGINA} restantes)
              </Button>
            </div>
          )}

          {mostrarTodas && salasFiltradas.length > ITEMS_POR_PAGINA && (
            <div className="mt-4 md:mt-6 text-center">
              <Button
                variant="ghost"
                onClick={() => {
                  setMostrarTodas(false);
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
                className="w-full md:w-auto"
              >
                Mostrar menos
              </Button>
            </div>
          )}
        </>
      )}

      {/* Modales */}
      <ModalCrearSala isOpen={modalCrearOpen} onClose={() => setModalCrearOpen(false)} />
      <ModalUnirseSala 
        isOpen={modalUnirseOpen} 
        onClose={() => {
          setModalUnirseOpen(false);
          setCodigoUrl(null);
        }} 
        codigoInicial={codigoUrl || undefined}
      />
      <SalaEspera
        isOpen={modalEsperaOpen}
        onClose={() => {
          setModalEsperaOpen(false);
          setSalaSeleccionada(null);
        }}
        sala={salaSeleccionada}
        onIniciarPartido={handleIniciarPartido}
      />
      <MarcadorPadel
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
