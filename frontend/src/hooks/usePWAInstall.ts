/**
 * Hook para manejar la instalación de PWA
 * Muestra el banner después de 5 visitas
 */

import { useState, useEffect, useCallback } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

interface PWAInstallState {
  canInstall: boolean;
  isInstalled: boolean;
  showBanner: boolean;
  visitCount: number;
}

const STORAGE_KEY = 'pwa-install-state';
const FIRST_SHOW_VISIT = 1; // Mostrar en la primera visita
const REVISIT_INTERVAL = 10; // Después de descartar, mostrar cada 10 visitas

// Detectar si es dispositivo móvil
const isMobileDevice = (): boolean => {
  const userAgent = navigator.userAgent || navigator.vendor || (window as any).opera;
  // Detectar móviles y tablets
  return /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent.toLowerCase()) ||
         (window.innerWidth <= 768 && 'ontouchstart' in window);
};

export function usePWAInstall() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [state, setState] = useState<PWAInstallState>({
    canInstall: false,
    isInstalled: false,
    showBanner: false,
    visitCount: 0
  });

  // Cargar estado guardado
  useEffect(() => {
    const savedState = localStorage.getItem(STORAGE_KEY);
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        setState(prev => ({ ...prev, ...parsed }));
      } catch (e) {
        console.error('Error parsing PWA state:', e);
      }
    }

    // Incrementar contador de visitas
    incrementVisitCount();

    // Verificar si ya está instalado
    checkIfInstalled();
  }, []);

  // Escuchar evento beforeinstallprompt
  useEffect(() => {
    const handleBeforeInstall = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      
      // Verificar si debemos mostrar el banner
      const savedState = localStorage.getItem(STORAGE_KEY);
      const parsed = savedState ? JSON.parse(savedState) : {};
      
      const shouldShow = shouldShowBanner(parsed);

      // Marcar como mostrado si se va a mostrar
      if (shouldShow && !parsed.hasBeenShown) {
        const savedState = localStorage.getItem(STORAGE_KEY);
        const current = savedState ? JSON.parse(savedState) : {};
        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({ ...current, hasBeenShown: true })
        );
      }

      setState(prev => ({
        ...prev,
        canInstall: true,
        showBanner: shouldShow
      }));
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    
    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
    };
  }, []);

  // Escuchar cuando se instala
  useEffect(() => {
    const handleAppInstalled = () => {
      setState(prev => ({
        ...prev,
        isInstalled: true,
        canInstall: false,
        showBanner: false
      }));
      setDeferredPrompt(null);
      saveState({ isInstalled: true, showBanner: false });
    };

    window.addEventListener('appinstalled', handleAppInstalled);
    
    return () => {
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const incrementVisitCount = () => {
    const savedState = localStorage.getItem(STORAGE_KEY);
    const parsed = savedState ? JSON.parse(savedState) : {};
    const newCount = (parsed.visitCount || 0) + 1;
    
    saveState({ visitCount: newCount });
    setState(prev => ({ ...prev, visitCount: newCount }));
  };

  const checkIfInstalled = () => {
    // Verificar si está en modo standalone (instalado)
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    // @ts-ignore - navigator.standalone es específico de iOS
    const isIOSStandalone = window.navigator.standalone === true;
    
    if (isStandalone || isIOSStandalone) {
      setState(prev => ({ ...prev, isInstalled: true, showBanner: false }));
    }
  };

  const shouldShowBanner = (savedState: any): boolean => {
    // Solo mostrar en dispositivos móviles
    if (!isMobileDevice()) return false;
    
    // No mostrar si ya está instalado
    if (savedState.isInstalled) return false;

    const visitCount = savedState.visitCount || 0;
    const hasBeenShown = savedState.hasBeenShown || false;
    const dismissCount = savedState.dismissCount || 0;
    const lastDismissVisit = savedState.lastDismissVisit || 0;

    // Primera vez: mostrar en la primera visita
    if (!hasBeenShown && visitCount >= FIRST_SHOW_VISIT) {
      return true;
    }

    // Si ya fue descartado, mostrar cada 10 visitas desde el último descarte
    if (dismissCount > 0) {
      const visitsSinceDismiss = visitCount - lastDismissVisit;
      if (visitsSinceDismiss >= REVISIT_INTERVAL) {
        return true;
      }
    }

    return false;
  };

  const saveState = (updates: Partial<any>) => {
    const savedState = localStorage.getItem(STORAGE_KEY);
    const current = savedState ? JSON.parse(savedState) : {};
    const newState = { ...current, ...updates };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newState));
  };

  const install = useCallback(async () => {
    if (!deferredPrompt) return false;

    try {
      await deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        setState(prev => ({
          ...prev,
          isInstalled: true,
          canInstall: false,
          showBanner: false
        }));
        saveState({ isInstalled: true });
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error installing PWA:', error);
      return false;
    }
  }, [deferredPrompt]);

  const dismissBanner = useCallback(() => {
    setState(prev => ({ ...prev, showBanner: false }));
    
    // Guardar que fue mostrado y descartado
    const savedState = localStorage.getItem(STORAGE_KEY);
    const parsed = savedState ? JSON.parse(savedState) : {};
    
    saveState({
      hasBeenShown: true,
      dismissCount: (parsed.dismissCount || 0) + 1,
      lastDismissVisit: parsed.visitCount || 0
    });
  }, []);

  const resetBanner = useCallback(() => {
    // Para testing: resetear el estado
    localStorage.removeItem(STORAGE_KEY);
    setState({
      canInstall: false,
      isInstalled: false,
      showBanner: false,
      visitCount: 0
    });
  }, []);

  return {
    ...state,
    install,
    dismissBanner,
    resetBanner
  };
}

export default usePWAInstall;
