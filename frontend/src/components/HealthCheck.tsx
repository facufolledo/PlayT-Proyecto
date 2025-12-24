import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Database, Zap, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';
import Button from './Button';
import Card from './Card';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'loading';
  message?: string;
  details?: any;
}

interface SystemHealth {
  api: HealthStatus;
  database: HealthStatus;
  cache: HealthStatus;
}

export default function HealthCheck() {
  const [health, setHealth] = useState<SystemHealth>({
    api: { status: 'loading' },
    database: { status: 'loading' },
    cache: { status: 'loading' }
  });
  const [loading, setLoading] = useState(false);
  const [clearingCache, setClearingCache] = useState(false);

  useEffect(() => {
    checkHealth();
    // Auto-refresh cada 30 segundos
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token') || localStorage.getItem('firebase_token');
    return {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };
  };

  const checkHealth = async () => {
    setLoading(true);
    
    // Check API Health
    try {
      const apiResponse = await axios.get(`${API_URL}/health/`);
      setHealth(prev => ({
        ...prev,
        api: {
          status: 'healthy',
          message: apiResponse.data.message || 'API funcionando correctamente',
          details: apiResponse.data
        }
      }));
    } catch (err: any) {
      setHealth(prev => ({
        ...prev,
        api: {
          status: 'unhealthy',
          message: err.response?.data?.detail || 'API no disponible',
          details: err.response?.data
        }
      }));
    }

    // Check Database Health
    try {
      const dbResponse = await axios.get(`${API_URL}/health/db`, getAuthHeaders());
      setHealth(prev => ({
        ...prev,
        database: {
          status: 'healthy',
          message: 'Base de datos conectada',
          details: dbResponse.data
        }
      }));
    } catch (err: any) {
      setHealth(prev => ({
        ...prev,
        database: {
          status: 'unhealthy',
          message: err.response?.data?.detail || 'Error de conexión a BD',
          details: err.response?.data
        }
      }));
    }

    // Check Cache Health
    try {
      const cacheResponse = await axios.get(`${API_URL}/health/cache`, getAuthHeaders());
      setHealth(prev => ({
        ...prev,
        cache: {
          status: 'healthy',
          message: 'Sistema de caché operativo',
          details: cacheResponse.data
        }
      }));
    } catch (err: any) {
      setHealth(prev => ({
        ...prev,
        cache: {
          status: 'unhealthy',
          message: err.response?.data?.detail || 'Error en sistema de caché',
          details: err.response?.data
        }
      }));
    }

    setLoading(false);
  };

  const clearCache = async () => {
    try {
      setClearingCache(true);
      await axios.post(`${API_URL}/health/cache/clear`, {}, getAuthHeaders());
      // Recheck health after clearing cache
      await checkHealth();
    } catch (err: any) {
      console.error('Error clearing cache:', err);
      alert(err.response?.data?.detail || 'Error al limpiar caché');
    } finally {
      setClearingCache(false);
    }
  };

  const getStatusIcon = (status: HealthStatus['status']) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'unhealthy':
        return <AlertTriangle className="text-red-500" size={20} />;
      case 'loading':
        return <RefreshCw className="text-yellow-500 animate-spin" size={20} />;
    }
  };

  const getStatusColor = (status: HealthStatus['status']) => {
    switch (status) {
      case 'healthy':
        return 'border-green-500/30 bg-green-500/5';
      case 'unhealthy':
        return 'border-red-500/30 bg-red-500/5';
      case 'loading':
        return 'border-yellow-500/30 bg-yellow-500/5';
    }
  };

  const overallStatus = Object.values(health).every(h => h.status === 'healthy') 
    ? 'healthy' 
    : Object.values(health).some(h => h.status === 'unhealthy') 
    ? 'unhealthy' 
    : 'loading';

  return (
    <Card>
      <div className="p-4 md:p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${
              overallStatus === 'healthy' ? 'bg-green-500/10' :
              overallStatus === 'unhealthy' ? 'bg-red-500/10' : 'bg-yellow-500/10'
            }`}>
              <Activity className={`${
                overallStatus === 'healthy' ? 'text-green-500' :
                overallStatus === 'unhealthy' ? 'text-red-500' : 'text-yellow-500'
              }`} size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold text-textPrimary">Estado del Sistema</h2>
              <p className="text-textSecondary text-sm">
                Monitoreo en tiempo real de los servicios
              </p>
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button
              variant="ghost"
              onClick={checkHealth}
              disabled={loading}
              className="flex items-center gap-2"
            >
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
              Actualizar
            </Button>
            <Button
              variant="secondary"
              onClick={clearCache}
              disabled={clearingCache}
              className="flex items-center gap-2"
            >
              <Zap size={16} />
              {clearingCache ? 'Limpiando...' : 'Limpiar Caché'}
            </Button>
          </div>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* API Status */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-4 rounded-lg border ${getStatusColor(health.api.status)}`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Activity size={18} className="text-textSecondary" />
                <span className="font-bold text-textPrimary">API</span>
              </div>
              {getStatusIcon(health.api.status)}
            </div>
            <p className="text-sm text-textSecondary mb-2">
              {health.api.message || 'Verificando...'}
            </p>
            {health.api.details && (
              <div className="text-xs text-textSecondary">
                <p>Uptime: {health.api.details.uptime || 'N/A'}</p>
                <p>Versión: {health.api.details.version || 'N/A'}</p>
              </div>
            )}
          </motion.div>

          {/* Database Status */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className={`p-4 rounded-lg border ${getStatusColor(health.database.status)}`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Database size={18} className="text-textSecondary" />
                <span className="font-bold text-textPrimary">Base de Datos</span>
              </div>
              {getStatusIcon(health.database.status)}
            </div>
            <p className="text-sm text-textSecondary mb-2">
              {health.database.message || 'Verificando...'}
            </p>
            {health.database.details && (
              <div className="text-xs text-textSecondary">
                <p>Pool: {health.database.details.pool_size || 'N/A'}/{health.database.details.max_overflow || 'N/A'}</p>
                <p>Conexiones: {health.database.details.checked_in || 'N/A'} activas</p>
              </div>
            )}
          </motion.div>

          {/* Cache Status */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className={`p-4 rounded-lg border ${getStatusColor(health.cache.status)}`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Zap size={18} className="text-textSecondary" />
                <span className="font-bold text-textPrimary">Caché</span>
              </div>
              {getStatusIcon(health.cache.status)}
            </div>
            <p className="text-sm text-textSecondary mb-2">
              {health.cache.message || 'Verificando...'}
            </p>
            {health.cache.details && (
              <div className="text-xs text-textSecondary">
                <p>Entradas: {health.cache.details.cache_size || 'N/A'}</p>
                <p>Hit Rate: {health.cache.details.hit_rate || 'N/A'}%</p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Overall Status */}
        <div className="mt-6 pt-4 border-t border-cardBorder">
          <div className="flex items-center justify-center gap-3">
            {getStatusIcon(overallStatus)}
            <span className={`font-bold ${
              overallStatus === 'healthy' ? 'text-green-500' :
              overallStatus === 'unhealthy' ? 'text-red-500' : 'text-yellow-500'
            }`}>
              {overallStatus === 'healthy' && 'Todos los sistemas operativos'}
              {overallStatus === 'unhealthy' && 'Algunos sistemas presentan problemas'}
              {overallStatus === 'loading' && 'Verificando estado de los sistemas...'}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}