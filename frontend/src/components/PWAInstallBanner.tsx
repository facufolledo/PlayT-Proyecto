/**
 * Banner de instalación PWA
 * Se muestra después de 5 visitas si la app no está instalada
 */

import { usePWAInstall } from '../hooks/usePWAInstall';
import { X, Download, Smartphone } from 'lucide-react';

export function PWAInstallBanner() {
  const { showBanner, canInstall, install, dismissBanner } = usePWAInstall();

  if (!showBanner || !canInstall) return null;

  const handleInstall = async () => {
    const success = await install();
    if (success) {
      console.log('✅ PWA instalada exitosamente');
    }
  };

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 animate-slide-up">
      <div className="bg-gradient-to-r from-[#7C3AED] to-[#5B21B6] rounded-xl shadow-2xl p-4 border border-purple-400/20">
        <button
          onClick={dismissBanner}
          className="absolute top-2 right-2 text-white/70 hover:text-white transition-colors"
          aria-label="Cerrar"
        >
          <X size={20} />
        </button>
        
        <div className="flex items-start gap-3">
          <div className="bg-white/20 rounded-lg p-2 flex-shrink-0">
            <Smartphone className="text-white" size={24} />
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="text-white font-semibold text-sm mb-1">
              Instala Drive+ en tu dispositivo
            </h3>
            <p className="text-white/80 text-xs mb-3">
              Accede más rápido y recibe notificaciones de tus torneos
            </p>
            
            <div className="flex gap-2">
              <button
                onClick={handleInstall}
                className="flex items-center gap-1.5 bg-white text-purple-700 px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-purple-50 transition-colors"
              >
                <Download size={16} />
                Instalar
              </button>
              <button
                onClick={dismissBanner}
                className="text-white/70 hover:text-white px-3 py-1.5 text-sm transition-colors"
              >
                Ahora no
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PWAInstallBanner;
