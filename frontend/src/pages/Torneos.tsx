import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Card from '../components/Card';
import Button from '../components/Button';
import ModalCrearTorneo from '../components/ModalCrearTorneo';
import TorneoCard from '../components/TorneoCard';
import { Plus, Filter, Trophy } from 'lucide-react';
import { useTorneos } from '../context/TorneosContext';

export default function Torneos() {
  const { torneos } = useTorneos();
  const [modalCrearOpen, setModalCrearOpen] = useState(false);
  const [filtro, setFiltro] = useState<'todos' | 'activo' | 'programado' | 'finalizado'>('todos');
  const [filtroGenero, setFiltroGenero] = useState<'todos' | 'masculino' | 'femenino' | 'mixto'>('todos');

  const torneosActivos = torneos.filter(t => t.estado === 'activo');
  const torneosProgramados = torneos.filter(t => t.estado === 'programado');
  const torneosFinalizados = torneos.filter(t => t.estado === 'finalizado');

  // Filtrar por estado
  let torneosFiltrados = filtro === 'todos' 
    ? torneos 
    : torneos.filter(t => t.estado === filtro);

  // Filtrar por género
  if (filtroGenero !== 'todos') {
    torneosFiltrados = torneosFiltrados.filter(t => t.genero === filtroGenero);
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
      >
        <div className="relative">
          <div className="flex items-center gap-3 mb-2">
            <div className="h-1 w-12 bg-gradient-to-r from-accent to-yellow-500 rounded-full" />
            <h1 className="text-5xl font-black text-textPrimary tracking-tight">
              Torneos
            </h1>
          </div>
          <p className="text-textSecondary text-base ml-15">Organiza y gestiona competencias</p>
        </div>
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Button variant="accent" onClick={() => setModalCrearOpen(true)}>
            <div className="flex items-center gap-2">
              <Plus size={20} />
              Nuevo Torneo
            </div>
          </Button>
        </motion.div>
      </motion.div>

      {/* Estadísticas */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total', value: torneos.length, color: 'from-cyan-500 to-blue-500', icon: '🏆' },
          { label: 'En Curso', value: torneosActivos.length, color: 'from-secondary to-pink-500', icon: '⚡' },
          { label: 'Programados', value: torneosProgramados.length, color: 'from-primary to-blue-500', icon: '📅' },
          { label: 'Finalizados', value: torneosFinalizados.length, color: 'from-accent to-yellow-400', icon: '✅' }
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
      <div className="space-y-4">
        {/* Filtro por Estado */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2 text-textSecondary">
            <Filter size={18} />
            <span className="text-sm font-bold">Estado:</span>
          </div>
          {(['todos', 'activo', 'programado', 'finalizado'] as const).map((f) => (
            <Button
              key={f}
              variant={filtro === f ? 'accent' : 'secondary'}
              onClick={() => setFiltro(f)}
              className="text-sm"
            >
              {f === 'todos' ? 'Todos' : f === 'activo' ? 'En Curso' : f === 'programado' ? 'Programados' : 'Finalizados'}
            </Button>
          ))}
        </div>

        {/* Filtro por Género */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2 text-textSecondary">
            <Filter size={18} />
            <span className="text-sm font-bold">Género:</span>
          </div>
          {[
            { value: 'todos', label: 'Todos', icon: '🏆' },
            { value: 'masculino', label: 'Masculino', icon: '♂' },
            { value: 'femenino', label: 'Femenino', icon: '♀' },
            { value: 'mixto', label: 'Mixto', icon: '⚥' }
          ].map((g) => (
            <Button
              key={g.value}
              variant={filtroGenero === g.value ? 'accent' : 'secondary'}
              onClick={() => setFiltroGenero(g.value as any)}
              className="text-sm flex items-center gap-1.5"
            >
              <span>{g.icon}</span>
              <span>{g.label}</span>
            </Button>
          ))}
        </div>
      </div>

      {/* Lista de torneos */}
      {torneosFiltrados.length === 0 ? (
        <Card>
          <div className="text-center py-12 text-textSecondary">
            <div className="bg-accent/10 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
              <Trophy size={40} className="text-accent" />
            </div>
            <p className="text-lg mb-4">
              {filtro === 'todos' 
                ? 'No hay torneos creados' 
                : `No hay torneos ${filtro === 'activo' ? 'en curso' : filtro === 'programado' ? 'programados' : 'finalizados'}`}
            </p>
            <p className="text-sm mb-4">
              {filtro === 'todos' && 'Crea tu primer torneo para comenzar a organizar competencias'}
            </p>
            {filtro === 'todos' && (
              <Button variant="accent" onClick={() => setModalCrearOpen(true)}>
                <div className="flex items-center gap-2">
                  <Plus size={20} />
                  Crear Primer Torneo
                </div>
              </Button>
            )}
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AnimatePresence mode="popLayout">
            {torneosFiltrados.map((torneo) => (
              <TorneoCard
                key={torneo.id}
                torneo={torneo}
              />
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Modal */}
      <ModalCrearTorneo isOpen={modalCrearOpen} onClose={() => setModalCrearOpen(false)} />
    </div>
  );
}
