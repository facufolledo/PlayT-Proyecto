import { setupRetryInterceptor } from './apiInterceptor';
import { applyAccessibilityStyles } from './accessibility';
import { clientLogger } from './clientLogger';
import { cacheManager } from './cacheManager';

// Inicializar todas las mejoras de la aplicación
export function initializeApp() {
  try {
    // 1. Configurar interceptores de API con retry
    setupRetryInterceptor();
    clientLogger.info('API interceptors configured');

    // 2. Aplicar estilos de accesibilidad
    applyAccessibilityStyles();
    clientLogger.info('Accessibility styles applied');

    // 3. Configurar limpieza automática de caché
    // Ya se configura automáticamente en cacheManager

    // 4. Detectar capacidades del navegador
    const capabilities = detectBrowserCapabilities();
    clientLogger.info('Browser capabilities detected', capabilities);

    // 5. Configurar performance monitoring
    setupPerformanceMonitoring();

    // 6. Configurar error boundaries globales
    setupGlobalErrorHandling();

    clientLogger.info('App initialization completed successfully');
    
    return true;
  } catch (error) {
    clientLogger.error('App initialization failed', error);
    return false;
  }
}

// Detectar capacidades del navegador
function detectBrowserCapabilities() {
  const capabilities = {
    // APIs modernas
    intersectionObserver: 'IntersectionObserver' in window,
    serviceWorker: 'serviceWorker' in navigator,
    webGL: !!document.createElement('canvas').getContext('webgl'),
    
    // Almacenamiento
    localStorage: (() => {
      try {
        localStorage.setItem('test', 'test');
        localStorage.removeItem('test');
        return true;
      } catch {
        return false;
      }
    })(),
    
    // Red
    connection: 'connection' in navigator,
    onLine: navigator.onLine,
    
    // Dispositivo
    touchScreen: 'ontouchstart' in window,
    deviceMemory: (navigator as any).deviceMemory || 'unknown',
    hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
    
    // Preferencias
    prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    prefersDarkMode: window.matchMedia('(prefers-color-scheme: dark)').matches,
    
    // Viewport
    viewportWidth: window.innerWidth,
    viewportHeight: window.innerHeight,
    devicePixelRatio: window.devicePixelRatio || 1
  };

  // Guardar en localStorage para análisis
  try {
    localStorage.setItem('browserCapabilities', JSON.stringify(capabilities));
  } catch (error) {
    clientLogger.warn('Could not save browser capabilities', error);
  }

  return capabilities;
}

// Configurar monitoreo de performance
function setupPerformanceMonitoring() {
  // Web Vitals básicos
  if ('PerformanceObserver' in window) {
    try {
      // Largest Contentful Paint (LCP)
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        clientLogger.performance('LCP', lastEntry.startTime);
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

      // First Input Delay (FID)
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          clientLogger.performance('FID', entry.processingStart - entry.startTime);
        });
      });
      fidObserver.observe({ entryTypes: ['first-input'] });

      // Cumulative Layout Shift (CLS)
      let clsValue = 0;
      const clsObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
          }
        });
        clientLogger.performance('CLS', clsValue);
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });

    } catch (error) {
      clientLogger.warn('Performance monitoring setup failed', error);
    }
  }

  // Monitorear memoria (si está disponible)
  if ('memory' in performance) {
    setInterval(() => {
      const memory = (performance as any).memory;
      clientLogger.performance('Memory usage', {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        limit: memory.jsHeapSizeLimit
      });
    }, 60000); // Cada minuto
  }
}

// Configurar manejo global de errores
function setupGlobalErrorHandling() {
  // Ya se configura en clientLogger, pero podemos agregar más lógica aquí
  
  // Manejar promesas rechazadas
  window.addEventListener('unhandledrejection', (event) => {
    // Prevenir que aparezca en consola si ya lo manejamos
    if (event.reason?.handled) {
      event.preventDefault();
    }
  });

  // Manejar errores de recursos (imágenes, scripts, etc.)
  window.addEventListener('error', (event) => {
    if (event.target !== window) {
      clientLogger.error('Resource loading error', {
        source: (event.target as any)?.src || (event.target as any)?.href,
        type: (event.target as any)?.tagName,
        message: event.message
      });
    }
  }, true);
}

// Función para obtener información del dispositivo
export function getDeviceInfo() {
  return {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    languages: navigator.languages,
    cookieEnabled: navigator.cookieEnabled,
    onLine: navigator.onLine,
    
    // Pantalla
    screenWidth: screen.width,
    screenHeight: screen.height,
    colorDepth: screen.colorDepth,
    
    // Viewport
    viewportWidth: window.innerWidth,
    viewportHeight: window.innerHeight,
    
    // Zona horaria
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    
    // Timestamp
    timestamp: new Date().toISOString()
  };
}

// Función para limpiar recursos al cerrar la app
export function cleanupApp() {
  try {
    // Enviar logs pendientes
    clientLogger.sendLogsToServer();
    
    // Limpiar caché expirado
    cacheManager.cleanup();
    
    clientLogger.info('App cleanup completed');
  } catch (error) {
    console.error('App cleanup failed:', error);
  }
}

// Configurar cleanup automático
window.addEventListener('beforeunload', cleanupApp);
window.addEventListener('pagehide', cleanupApp);
