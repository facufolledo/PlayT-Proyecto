import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, X, Wifi, WifiOff } from 'lucide-react';
import { showInstallPrompt, canInstall, isOnline, setupConnectivityListeners } from '../utils/pwa';
import Button from './Button';

export default function PWAInstallPrompt() {
  const [showInstall, setShowInstall] = useState(false);
  const [online, setOnline] = useState(isOnline());
  const [showOfflineBanner, setShowOfflineBanner] = useState(false);

  useEffect(() => {
    // Verificar si puede instalarse
    const checkInstallable = () => {
      setShowInstall(canInstall());
    };

    // Escuchar evento personalizado
    window.addEventListener('pwa-installable', checkInstallable as any);
    checkInstallable();

    // Configurar listeners de conectividad
    setupConnectivityListeners(
      () => {
        setOnline(true);
        setShowOfflineBanner(false);
      },
      () => {
        setOnline(false);
        setShowOfflineBanner(true);
      }
    );

    return () => {
      window.removeEventListener('pwa-installable', checkInstallable as any);
    };
  }, []);

  const handleInstall = async () => {
    const accepted = await showInstallPrompt();
    if (accepted) {
      setShowInstall(false);
    }
  };

  return (
    <>
      {/* Banner de instalación */}
      <AnimatePresence>
        {showInstall && (
          <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 100, opacity: 0 }}
            className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50"
          >
            <div className="bg-gradient-to-r from-primary to-blue-600 rounded-2xl p-4 shadow-2xl border border-blue-400/20">
              <button
                onClick={() => setShowInstall(false)}
                className="absolute top-2 right-2 text-white/80 hover:text-white transition-colors"
              >
                <X size={20} />
              </button>

              <div className="flex items-start gap-4">
                <div className="bg-white/20 p-3 rounded-xl">
                  <Download size={24} className="text-white" />
                </div>
                
                <div className="flex-1">
                  <h3 className="text-white font-bold text-lg mb-1">
                    Instalar PlayR
                  </h3>
                  <p className="text-white/90 text-sm mb-3">
                    Instala la app para acceso rápido y funcionalidad offline
                  </p>
                  
                  <Button
                    variant="ghost"
                    onClick={handleInstall}
                    className="bg-white text-primary hover:bg-white/90 w-full"
                  >
                    Instalar Ahora
                  </Button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Banner offline */}
      <AnimatePresence>
        {showOfflineBanner && (
          <motion.div
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -100, opacity: 0 }}
            className="fixed top-0 left-0 right-0 z-50"
          >
            <div className="bg-gradient-to-r from-red-500 to-red-600 px-4 py-3 shadow-lg">
              <div className="flex items-center justify-center gap-2 text-white">
                <WifiOff size={20} />
                <span className="font-semibold">Sin conexión</span>
                <span className="text-white/90 text-sm">
                  - Trabajando en modo offline
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Indicador de conexión (pequeño) */}
      {!showOfflineBanner && (
        <div className="fixed top-4 right-4 z-40">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className={`p-2 rounded-full ${
              online 
                ? 'bg-green-500/20 text-green-500' 
                : 'bg-red-500/20 text-red-500'
            }`}
          >
            {online ? <Wifi size={16} /> : <WifiOff size={16} />}
          </motion.div>
        </div>
      )}
    </>
  );
}
