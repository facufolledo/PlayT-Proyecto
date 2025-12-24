import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Monitor, 
  Database, 
  Wifi, 
  Clock, 
  BarChart3, 
  Bug, 
  Settings,
  X,
  RefreshCw,
  Trash2
} from 'lucide-react';
import { clientLogger } from '../utils/clientLogger';
import { cacheManager } from '../utils/cacheManager';
import { getDeviceInfo } from '../utils/appInitializer';

interface DevDashboardProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function DevDashboard({ isOpen, onClose }: DevDashboardProps) {
  const [activeTab, setActiveTab] = useState<'logs' | 'cache' | 'performance' | 'device'>('logs');
  const [logs, setLogs] = useState<any[]>([]);
  const [cacheStats, setCacheStats] = useState<any>({});
  const [deviceInfo, setDeviceInfo] = useState<any>({});

  useEffect(() => {
    if (isOpen) {
      // Cargar datos iniciales
      setLogs(clientLogger.getLogs());
      setCacheStats(cacheManager.getStats());
      setDeviceInfo(getDeviceInfo());

      // Actualizar cada segundo
      const interval = setInterval(() => {
        setLogs(clientLogger.getLogs());
        setCacheStats(cacheManager.getStats());
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [isOpen]);

  const clearLogs = () => {
    clientLogger.clearLogs();
    setLogs([]);
  };

  const clearCache = () => {
    // Limpiar caché manualmente
    cacheManager.cleanup();
    setCacheStats(cacheManager.getStats());
  };

  const tabs = [
    { id: 'logs', label: 'Logs', icon: Bug },
    { id: 'cache', label: 'Caché', icon: Database },
    { id: 'performance', label: 'Performance', icon: BarChart3 },
    { id: 'device', label: 'Dispositivo', icon: Monitor }
  ];

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="fixed inset-4 bg-cardBg rounded-xl border border-cardBorder shadow-2xl overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-cardBorder">
            <div className="flex items-center gap-2">
              <Settings className="text-primary" size={20} />
              <h2 className="text-lg font-bold text-textPrimary">Dashboard de Desarrollo</h2>
            </div>
            <button
              onClick={onClose}
              className="text-textSecondary hover:text-textPrimary transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          <div className="flex h-full">
            {/* Sidebar */}
            <div className="w-48 border-r border-cardBorder p-4">
              <nav className="space-y-2">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`
                        w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left transition-colors
                        ${activeTab === tab.id 
                          ? 'bg-primary text-white' 
                          : 'text-textSecondary hover:text-textPrimary hover:bg-cardBorder'
                        }
                      `}
                    >
                      <Icon size={16} />
                      {tab.label}
                    </button>
                  );
                })}
              </nav>
            </div>

            {/* Content */}
            <div className="flex-1 p-4 overflow-auto">
              {activeTab === 'logs' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-textPrimary">
                      Logs del Cliente ({logs.length})
                    </h3>
                    <button
                      onClick={clearLogs}
                      className="flex items-center gap-1 px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                    >
                      <Trash2 size={14} />
                      Limpiar
                    </button>
                  </div>
                  
                  <div className="space-y-2 max-h-96 overflow-auto">
                    {logs.slice(-50).reverse().map((log, index) => (
                      <div
                        key={index}
                        className={`
                          p-3 rounded border text-sm font-mono
                          ${log.level === 'ERROR' ? 'border-red-200 bg-red-50' :
                            log.level === 'WARN' ? 'border-yellow-200 bg-yellow-50' :
                            log.level === 'INFO' ? 'border-blue-200 bg-blue-50' :
                            'border-gray-200 bg-gray-50'
                          }
                        `}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className={`
                            px-2 py-0.5 rounded text-xs font-bold
                            ${log.level === 'ERROR' ? 'bg-red-500 text-white' :
                              log.level === 'WARN' ? 'bg-yellow-500 text-white' :
                              log.level === 'INFO' ? 'bg-blue-500 text-white' :
                              'bg-gray-500 text-white'
                            }
                          `}>
                            {log.level}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="text-gray-800">{log.message}</div>
                        {log.data && (
                          <pre className="mt-2 text-xs text-gray-600 overflow-auto">
                            {JSON.stringify(log.data, null, 2)}
                          </pre>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'cache' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-textPrimary">Estado del Caché</h3>
                    <button
                      onClick={clearCache}
                      className="flex items-center gap-1 px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                    >
                      <RefreshCw size={14} />
                      Limpiar
                    </button>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 border border-cardBorder rounded-lg">
                      <h4 className="font-semibold text-textPrimary mb-2">Memoria</h4>
                      <div className="text-2xl font-bold text-primary">{cacheStats.memorySize}</div>
                      <div className="text-sm text-textSecondary">items en memoria</div>
                    </div>

                    <div className="p-4 border border-cardBorder rounded-lg">
                      <h4 className="font-semibold text-textPrimary mb-2">LocalStorage</h4>
                      <div className="text-2xl font-bold text-secondary">{cacheStats.localStorageSize}</div>
                      <div className="text-sm text-textSecondary">items persistentes</div>
                    </div>

                    <div className="p-4 border border-cardBorder rounded-lg">
                      <h4 className="font-semibold text-textPrimary mb-2">Límite</h4>
                      <div className="text-2xl font-bold text-accent">{cacheStats.maxSize}</div>
                      <div className="text-sm text-textSecondary">máximo en memoria</div>
                    </div>

                    <div className="p-4 border border-cardBorder rounded-lg">
                      <h4 className="font-semibold text-textPrimary mb-2">TTL Default</h4>
                      <div className="text-2xl font-bold text-textPrimary">
                        {Math.round((cacheStats.defaultTTL || 0) / 1000 / 60)}m
                      </div>
                      <div className="text-sm text-textSecondary">tiempo de vida</div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'performance' && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-textPrimary">Métricas de Performance</h3>
                  
                  <div className="grid grid-cols-2 gap-4">
                    {/* Navigation Timing */}
                    {performance.timing && (
                      <>
                        <div className="p-4 border border-cardBorder rounded-lg">
                          <h4 className="font-semibold text-textPrimary mb-2">Carga de Página</h4>
                          <div className="text-2xl font-bold text-primary">
                            {performance.timing.loadEventEnd - performance.timing.navigationStart}ms
                          </div>
                          <div className="text-sm text-textSecondary">tiempo total</div>
                        </div>

                        <div className="p-4 border border-cardBorder rounded-lg">
                          <h4 className="font-semibold text-textPrimary mb-2">DOM Ready</h4>
                          <div className="text-2xl font-bold text-secondary">
                            {performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart}ms
                          </div>
                          <div className="text-sm text-textSecondary">DOM listo</div>
                        </div>
                      </>
                    )}

                    {/* Memory (si está disponible) */}
                    {(performance as any).memory && (
                      <>
                        <div className="p-4 border border-cardBorder rounded-lg">
                          <h4 className="font-semibold text-textPrimary mb-2">Memoria Usada</h4>
                          <div className="text-2xl font-bold text-accent">
                            {Math.round((performance as any).memory.usedJSHeapSize / 1024 / 1024)}MB
                          </div>
                          <div className="text-sm text-textSecondary">heap JavaScript</div>
                        </div>

                        <div className="p-4 border border-cardBorder rounded-lg">
                          <h4 className="font-semibold text-textPrimary mb-2">Memoria Total</h4>
                          <div className="text-2xl font-bold text-textPrimary">
                            {Math.round((performance as any).memory.totalJSHeapSize / 1024 / 1024)}MB
                          </div>
                          <div className="text-sm text-textSecondary">heap total</div>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'device' && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-textPrimary">Información del Dispositivo</h3>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 border border-cardBorder rounded-lg">
                      <h4 className="font-semibold text-textPrimary mb-2">Conexión</h4>
                      <div className="flex items-center gap-2">
                        <Wifi className={navigator.onLine ? 'text-green-500' : 'text-red-500'} size={16} />
                        <span>{navigator.onLine ? 'Online' : 'Offline'}</span>
                      </div>
                    </div>

                    <div className="p-4 border border-cardBorder rounded-lg">
                      <h4 className="font-semibold text-textPrimary mb-2">Viewport</h4>
                      <div className="text-sm">
                        {deviceInfo.viewportWidth} × {deviceInfo.viewportHeight}
                      </div>
                    </div>

                    <div className="p-4 border border-cardBorder rounded-lg">
                      <h4 className="font-semibold text-textPrimary mb-2">Plataforma</h4>
                      <div className="text-sm">{deviceInfo.platform}</div>
                    </div>

                    <div className="p-4 border border-cardBorder rounded-lg">
                      <h4 className="font-semibold text-textPrimary mb-2">Idioma</h4>
                      <div className="text-sm">{deviceInfo.language}</div>
                    </div>
                  </div>

                  <div className="p-4 border border-cardBorder rounded-lg">
                    <h4 className="font-semibold text-textPrimary mb-2">User Agent</h4>
                    <div className="text-xs font-mono text-textSecondary break-all">
                      {deviceInfo.userAgent}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

// Hook para abrir el dashboard con combinación de teclas
export function useDevDashboard() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl + Shift + D para abrir dashboard (solo en desarrollo)
      if (event.ctrlKey && event.shiftKey && event.key === 'D' && import.meta.env.DEV) {
        event.preventDefault();
        setIsOpen(prev => !prev);
        clientLogger.userAction('Dev dashboard toggled', { isOpen: !isOpen });
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  return {
    isOpen,
    setIsOpen,
    toggle: () => setIsOpen(prev => !prev)
  };
}