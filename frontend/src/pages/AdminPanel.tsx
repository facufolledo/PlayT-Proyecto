import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Users, Trophy, Database, Zap, Settings, AlertTriangle, FileText, Download } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import HealthCheck from '../components/HealthCheck';
import { adminService, EstadisticasAdmin, LogEntry, FiltrosLogs } from '../services/admin.service';

export default function AdminPanel() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<EstadisticasAdmin | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [error, setError] = useState('');
  const [vistaActual, setVistaActual] = useState<'estadisticas' | 'logs'>('estadisticas');
  const [filtrosLogs, setFiltrosLogs] = useState<FiltrosLogs>({ limit: 50 });

  useEffect(() => {
    // Verificar si el usuario es administrador
    if (!usuario?.es_administrador) {
      navigate('/dashboard');
      return;
    }
    
    cargarEstadisticas();
  }, [usuario, navigate]);

  const cargarEstadisticas = async () => {
    try {
      setLoading(true);
      const estadisticas = await adminService.getEstadisticas();
      setStats(estadisticas);
      setError('');
    } catch (error: any) {
      console.error('Error cargando estadísticas:', error);
      setError(error.message || 'Error al cargar estadísticas');
    } finally {
      setLoading(false);
    }
  };

  const cargarLogs = async () => {
    try {
      setLoadingLogs(true);
      const response = await adminService.getLogs(filtrosLogs);
      setLogs(response.logs);
    } catch (error: any) {
      console.error('Error cargando logs:', error);
      setError(error.message || 'Error al cargar logs');
    } finally {
      setLoadingLogs(false);
    }
  };

  const exportarLogs = async () => {
    try {
      const blob = await adminService.exportarLogs(filtrosLogs);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `logs_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error: any) {
      console.error('Error exportando logs:', error);
      setError(error.message || 'Error al exportar logs');
    }
  };

  const getNivelColor = (nivel: string) => {
    switch (nivel.toLowerCase()) {
      case 'error': return 'text-red-400 bg-red-400/20';
      case 'warning': return 'text-yellow-400 bg-yellow-400/20';
      case 'info': return 'text-blue-400 bg-blue-400/20';
      default: return 'text-gray-400 bg-gray-400/20';
    }
  };

  if (!usuario?.es_administrador) {
    return (
      <Card>
        <div className="p-6 text-center">
          <AlertTriangle size={48} className="mx-auto text-red-500 mb-4" />
          <h2 className="text-xl font-bold text-textPrimary mb-2">Acceso Denegado</h2>
          <p className="text-textSecondary mb-4">No tienes permisos de administrador</p>
          <Button onClick={() => navigate('/dashboard')}>
            Volver al Dashboard
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative"
      >
        <div className="flex items-center gap-2 md:gap-3 mb-1 md:mb-2">
          <div className="h-0.5 md:h-1 w-8 md:w-12 bg-gradient-to-r from-red-500 to-orange-500 rounded-full" />
          <h1 className="text-2xl md:text-5xl font-black text-textPrimary tracking-tight">
            Panel de Administración
          </h1>
        </div>
        <p className="text-textSecondary text-xs md:text-base ml-10 md:ml-15">
          Monitoreo y gestión del sistema Drive+
        </p>
      </motion.div>

      {/* Navegación de vistas */}
      <div className="flex gap-2">
        <Button
          variant={vistaActual === 'estadisticas' ? 'primary' : 'secondary'}
          onClick={() => setVistaActual('estadisticas')}
          className="flex items-center gap-2"
        >
          <Activity size={16} />
          Estadísticas
        </Button>
        <Button
          variant={vistaActual === 'logs' ? 'primary' : 'secondary'}
          onClick={() => {
            setVistaActual('logs');
            if (logs.length === 0) cargarLogs();
          }}
          className="flex items-center gap-2"
        >
          <FileText size={16} />
          Logs del Sistema
        </Button>
      </div>

      {vistaActual === 'estadisticas' ? (
        <>
          {/* Estadísticas Generales */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
            {[
              { 
                icon: Users, 
                label: 'Usuarios Totales', 
                value: stats?.usuarios_totales?.toString() || '0', 
                color: 'from-blue-500 to-blue-600',
                iconBg: 'bg-blue-500/10',
                iconColor: 'text-blue-500'
              },
              { 
                icon: Activity, 
                label: 'Activos (Mes)', 
                value: stats?.usuarios_activos_mes?.toString() || '0', 
                color: 'from-green-500 to-green-600',
                iconBg: 'bg-green-500/10',
                iconColor: 'text-green-500'
              },
              { 
                icon: Trophy, 
                label: 'Torneos Activos', 
                value: stats?.torneos_activos?.toString() || '0', 
                color: 'from-yellow-500 to-yellow-600',
                iconBg: 'bg-yellow-500/10',
                iconColor: 'text-yellow-500'
              },
              { 
                icon: Database, 
                label: 'Partidos Totales', 
                value: stats?.partidos_totales?.toString() || '0', 
                color: 'from-purple-500 to-purple-600',
                iconBg: 'bg-purple-500/10',
                iconColor: 'text-purple-500'
              },
            ].map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="group cursor-pointer"
                >
                  <div className="relative bg-cardBg rounded-lg p-3 md:p-4 border border-cardBorder group-hover:border-transparent transition-all duration-200 overflow-hidden">
                    <div className={`hidden md:block absolute -inset-[1px] bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-lg -z-10 blur-sm`} />
                    
                    <div className="relative z-10">
                      <div className="flex items-center justify-between mb-2">
                        <div className={`${stat.iconBg} p-1.5 md:p-2 rounded-lg`}>
                          <Icon size={16} className={`${stat.iconColor} md:w-5 md:h-5`} />
                        </div>
                        <motion.p 
                          className="text-xl md:text-2xl font-black text-textPrimary"
                          key={stat.value}
                          initial={{ scale: 0.8, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                        >
                          {loading ? '...' : stat.value}
                        </motion.p>
                      </div>
                      <p className="text-textSecondary text-[9px] md:text-xs font-bold uppercase tracking-wider">
                        {stat.label}
                      </p>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Top Jugadores */}
          {stats?.top_jugadores && stats.top_jugadores.length > 0 && (
            <Card>
              <div className="p-4">
                <h3 className="font-bold text-textPrimary mb-4 flex items-center gap-2">
                  <Trophy className="text-accent" size={20} />
                  Top Jugadores
                </h3>
                <div className="space-y-2">
                  {stats.top_jugadores.slice(0, 5).map((jugador, index) => (
                    <div key={jugador.id_usuario} className="flex items-center justify-between p-2 bg-cardBorder/20 rounded">
                      <div className="flex items-center gap-3">
                        <span className="text-accent font-bold">#{index + 1}</span>
                        <div>
                          <p className="font-semibold text-textPrimary text-sm">
                            {jugador.nombre} {jugador.apellido}
                          </p>
                          <p className="text-textSecondary text-xs">@{jugador.nombre_usuario}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-primary">{jugador.rating}</p>
                        <p className="text-textSecondary text-xs">{jugador.partidos_jugados} partidos</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          )}

          {/* Health Check del Sistema */}
          <HealthCheck />

          {/* Acciones Rápidas */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card>
              <div className="p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="bg-primary/10 p-2 rounded-lg">
                    <Users className="text-primary" size={20} />
                  </div>
                  <h3 className="font-bold text-textPrimary">Gestión de Usuarios</h3>
                </div>
                <p className="text-textSecondary text-sm mb-4">
                  Administrar usuarios, permisos y roles del sistema
                </p>
                <Button variant="primary" className="w-full text-sm" onClick={() => navigate('/buscar-jugadores')}>
                  Gestionar Usuarios
                </Button>
              </div>
            </Card>

            <Card>
              <div className="p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="bg-accent/10 p-2 rounded-lg">
                    <Trophy className="text-accent" size={20} />
                  </div>
                  <h3 className="font-bold text-textPrimary">Gestión de Torneos</h3>
                </div>
                <p className="text-textSecondary text-sm mb-4">
                  Supervisar torneos activos y resolver incidencias
                </p>
                <Button variant="accent" className="w-full text-sm" onClick={() => navigate('/torneos')}>
                  Ver Torneos
                </Button>
              </div>
            </Card>

            <Card>
              <div className="p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="bg-secondary/10 p-2 rounded-lg">
                    <Settings className="text-secondary" size={20} />
                  </div>
                  <h3 className="font-bold text-textPrimary">Configuración</h3>
                </div>
                <p className="text-textSecondary text-sm mb-4">
                  Ajustes del sistema, categorías y parámetros
                </p>
                <Button variant="secondary" className="w-full text-sm" disabled>
                  Próximamente
                </Button>
              </div>
            </Card>
          </div>
        </>
      ) : (
        /* Vista de Logs */
        <Card>
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-textPrimary flex items-center gap-2">
                <FileText className="text-primary" size={20} />
                Logs del Sistema
              </h3>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  onClick={cargarLogs}
                  disabled={loadingLogs}
                  className="text-sm"
                >
                  {loadingLogs ? 'Cargando...' : 'Actualizar'}
                </Button>
                <Button
                  variant="primary"
                  onClick={exportarLogs}
                  className="text-sm flex items-center gap-2"
                >
                  <Download size={14} />
                  Exportar
                </Button>
              </div>
            </div>

            {/* Filtros de logs */}
            <div className="mb-4 flex gap-2 flex-wrap">
              <select
                value={filtrosLogs.nivel || ''}
                onChange={(e) => setFiltrosLogs({ ...filtrosLogs, nivel: e.target.value || undefined })}
                className="bg-cardBg border border-cardBorder rounded px-3 py-1 text-sm text-textPrimary"
              >
                <option value="">Todos los niveles</option>
                <option value="error">Error</option>
                <option value="warning">Warning</option>
                <option value="info">Info</option>
              </select>
              
              <input
                type="date"
                value={filtrosLogs.fecha_desde || ''}
                onChange={(e) => setFiltrosLogs({ ...filtrosLogs, fecha_desde: e.target.value || undefined })}
                className="bg-cardBg border border-cardBorder rounded px-3 py-1 text-sm text-textPrimary"
                placeholder="Fecha desde"
              />
              
              <input
                type="date"
                value={filtrosLogs.fecha_hasta || ''}
                onChange={(e) => setFiltrosLogs({ ...filtrosLogs, fecha_hasta: e.target.value || undefined })}
                className="bg-cardBg border border-cardBorder rounded px-3 py-1 text-sm text-textPrimary"
                placeholder="Fecha hasta"
              />
            </div>

            {/* Lista de logs */}
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {loadingLogs ? (
                <div className="text-center py-8">
                  <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mx-auto mb-2"></div>
                  <p className="text-textSecondary text-sm">Cargando logs...</p>
                </div>
              ) : logs.length === 0 ? (
                <div className="text-center py-8 text-textSecondary">
                  <FileText size={32} className="mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No hay logs disponibles</p>
                </div>
              ) : (
                logs.map((log) => (
                  <div key={log.id} className="bg-cardBorder/20 rounded p-3 text-sm">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${getNivelColor(log.nivel)}`}>
                          {log.nivel.toUpperCase()}
                        </span>
                        <span className="text-textSecondary">
                          {new Date(log.timestamp).toLocaleString('es-AR')}
                        </span>
                      </div>
                      {log.usuario_nombre && (
                        <span className="text-textSecondary text-xs">
                          {log.usuario_nombre}
                        </span>
                      )}
                    </div>
                    <p className="text-textPrimary">{log.mensaje}</p>
                    {log.endpoint && (
                      <p className="text-textSecondary text-xs mt-1">
                        Endpoint: {log.endpoint}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-center gap-3"
        >
          <AlertTriangle className="text-red-500" size={20} />
          <p className="text-red-500 text-sm">{error}</p>
        </motion.div>
      )}
    </div>
  );
}
