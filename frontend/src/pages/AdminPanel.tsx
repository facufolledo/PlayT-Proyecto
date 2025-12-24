import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Users, Trophy, Database, Zap, Settings, AlertTriangle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import Card from '../components/Card';
import Button from '../components/Button';
import HealthCheck from '../components/HealthCheck';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface AdminStats {
  total_usuarios: number;
  usuarios_activos_mes: number;
  total_torneos: number;
  torneos_activos: number;
  total_partidos: number;
  partidos_hoy: number;
}

export default function AdminPanel() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Verificar si el usuario es administrador
    if (!usuario?.es_administrador) {
      navigate('/dashboard');
      return;
    }
    
    cargarEstadisticas();
  }, [usuario, navigate]);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token') || localStorage.getItem('firebase_token');
    return {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };
  };

  const cargarEstadisticas = async () => {
    try {
      setLoading(true);
      // Simular estadísticas por ahora - en el futuro se puede crear un endpoint específico
      await Promise.all([
        axios.get(`${API_URL}/usuarios/buscar`, { params: { limit: 1 } }),
        axios.get(`${API_URL}/torneos`, { params: { limit: 1 } })
      ]);

      // Por ahora usar datos simulados basados en las respuestas
      setStats({
        total_usuarios: 150, // Simulated
        usuarios_activos_mes: 45,
        total_torneos: 12,
        torneos_activos: 3,
        total_partidos: 89,
        partidos_hoy: 5
      });
    } catch (err: any) {
      console.error('Error cargando estadísticas:', err);
      setError('Error al cargar estadísticas del sistema');
    } finally {
      setLoading(false);
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
          Monitoreo y gestión del sistema PlayT
        </p>
      </motion.div>

      {/* Estadísticas Generales */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-3 md:gap-4">
        {[
          { 
            icon: Users, 
            label: 'Usuarios Totales', 
            value: stats?.total_usuarios?.toString() || '0', 
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
            label: 'Torneos Totales', 
            value: stats?.total_torneos?.toString() || '0', 
            color: 'from-yellow-500 to-yellow-600',
            iconBg: 'bg-yellow-500/10',
            iconColor: 'text-yellow-500'
          },
          { 
            icon: Trophy, 
            label: 'Torneos Activos', 
            value: stats?.torneos_activos?.toString() || '0', 
            color: 'from-orange-500 to-orange-600',
            iconBg: 'bg-orange-500/10',
            iconColor: 'text-orange-500'
          },
          { 
            icon: Database, 
            label: 'Partidos Totales', 
            value: stats?.total_partidos?.toString() || '0', 
            color: 'from-purple-500 to-purple-600',
            iconBg: 'bg-purple-500/10',
            iconColor: 'text-purple-500'
          },
          { 
            icon: Zap, 
            label: 'Partidos Hoy', 
            value: stats?.partidos_hoy?.toString() || '0', 
            color: 'from-pink-500 to-pink-600',
            iconBg: 'bg-pink-500/10',
            iconColor: 'text-pink-500'
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
            <Button variant="primary" className="w-full text-sm">
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
            <Button variant="accent" className="w-full text-sm">
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
            <Button variant="secondary" className="w-full text-sm">
              Configurar
            </Button>
          </div>
        </Card>
      </div>

      {/* Logs Recientes */}
      <Card>
        <div className="p-4">
          <h3 className="font-bold text-textPrimary mb-4 flex items-center gap-2">
            <Activity className="text-primary" size={20} />
            Actividad Reciente del Sistema
          </h3>
          <div className="space-y-2">
            {[
              { time: '14:32', action: 'Nuevo torneo creado', user: 'admin@playt.com', type: 'success' },
              { time: '14:15', action: 'Usuario registrado', user: 'nuevo.usuario@email.com', type: 'info' },
              { time: '13:45', action: 'Partido finalizado', user: 'Torneo Verano 2025', type: 'success' },
              { time: '13:20', action: 'Error de conexión BD', user: 'Sistema', type: 'error' },
              { time: '12:58', action: 'Caché limpiado', user: 'admin@playt.com', type: 'warning' },
            ].map((log, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-background rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <span className={`w-2 h-2 rounded-full ${
                    log.type === 'success' ? 'bg-green-500' :
                    log.type === 'error' ? 'bg-red-500' :
                    log.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                  }`} />
                  <div>
                    <p className="text-textPrimary text-sm font-medium">{log.action}</p>
                    <p className="text-textSecondary text-xs">{log.user}</p>
                  </div>
                </div>
                <span className="text-textSecondary text-xs">{log.time}</span>
              </div>
            ))}
          </div>
        </div>
      </Card>

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