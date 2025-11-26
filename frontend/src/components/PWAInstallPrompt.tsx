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
    // Verificar si es dispositivo móvil
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    // Verificar si puede instalarse
    const checkInstallable = () => {
      // Solo mostrar en móviles
      if (isMobile) {
        setShowInstall(canInstall());
      }
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
            className="fixed bottom-4 right-4 left-4 md:left-auto md:w-80 z-50"
          >
            <div className="bg-cardBg/95 backdrop-blur-xl rounded-lg border border-primary/30 shadow-2xl p-2.5">
              <button
                onClick={() => setShowInstall(false)}
                className="absolute top-1 right-1 text-textSecondary hover:text-textPrimary transition-colors"
              >
                <X size={16} />
              </button>

              <div className="flex items-center gap-2 pr-6">
                <div className="bg-primary/10 p-2 rounded-lg flex-shrink-0">
                  <Download size={18} className="text-primary" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className="text-textPrimary font-bold text-xs mb-0.5">
                    Instalar PlayR
                  </h3>
                  <p className="text-textSecondary text-[10px] mb-1.5">
                    Acceso rápido
                  </p>
                  
                  <button
                    onClick={handleInstall}
                    className="bg-primary hover:bg-primary/90 text-white w-full text-xs py-1.5 rounded-lg font-bold transition-colors"
                  >
                    Instalar
                  </button>
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

      {/* Indicador de conexión (solo icono) */}
      {!showOfflineBanner && (
        <div className="fixed bottom-4 right-4 z-40">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className={online ? 'text-green-500' : 'text-red-500'}
          >
            {online ? <Wifi size={20} /> : <WifiOff size={20} />}
          </motion.div>
        </div>
      )}
    </>
  );
}
