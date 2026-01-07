import { useEffect, useState } from 'react';
import { clientLogger } from './clientLogger';

// Hook para detectar preferencias de accesibilidad
export function useAccessibilityPreferences() {
  const [preferences, setPreferences] = useState({
    prefersReducedMotion: false,
    prefersHighContrast: false,
    prefersDarkMode: false,
    fontSize: 'normal' as 'small' | 'normal' | 'large'
  });

  useEffect(() => {
    // Detectar preferencias del sistema
    const updatePreferences = () => {
      const newPreferences = {
        prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
        prefersHighContrast: window.matchMedia('(prefers-contrast: high)').matches,
        prefersDarkMode: window.matchMedia('(prefers-color-scheme: dark)').matches,
        fontSize: (localStorage.getItem('fontSize') as any) || 'normal'
      };

      setPreferences(newPreferences);
      
      clientLogger.info('Accessibility preferences updated', newPreferences);
    };

    // Listeners para cambios en preferencias
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const contrastQuery = window.matchMedia('(prefers-contrast: high)');
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

    motionQuery.addEventListener('change', updatePreferences);
    contrastQuery.addEventListener('change', updatePreferences);
    darkModeQuery.addEventListener('change', updatePreferences);

    updatePreferences();

    return () => {
      motionQuery.removeEventListener('change', updatePreferences);
      contrastQuery.removeEventListener('change', updatePreferences);
      darkModeQuery.removeEventListener('change', updatePreferences);
    };
  }, []);

  const setFontSize = (size: 'small' | 'normal' | 'large') => {
    localStorage.setItem('fontSize', size);
    setPreferences(prev => ({ ...prev, fontSize: size }));
    
    // Aplicar clase CSS al body
    document.body.className = document.body.className.replace(/font-size-\w+/g, '');
    document.body.classList.add(`font-size-${size}`);
    
    clientLogger.userAction('Font size changed', { size });
  };

  return {
    ...preferences,
    setFontSize
  };
}

// Hook para navegación por teclado
export function useKeyboardNavigation() {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Escape para cerrar modales
      if (event.key === 'Escape') {
        const openModal = document.querySelector('[role="dialog"]');
        if (openModal) {
          const closeButton = openModal.querySelector('[aria-label*="cerrar"], [aria-label*="close"]');
          if (closeButton instanceof HTMLElement) {
            closeButton.click();
            clientLogger.userAction('Modal closed via keyboard', { key: 'Escape' });
          }
        }
      }

      // Tab trap en modales
      if (event.key === 'Tab') {
        const modal = document.querySelector('[role="dialog"]');
        if (modal) {
          const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          );
          
          if (focusableElements.length > 0) {
            const firstElement = focusableElements[0] as HTMLElement;
            const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

            if (event.shiftKey && document.activeElement === firstElement) {
              event.preventDefault();
              lastElement.focus();
            } else if (!event.shiftKey && document.activeElement === lastElement) {
              event.preventDefault();
              firstElement.focus();
            }
          }
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);
}

// Hook para anuncios de screen reader
export function useScreenReader() {
  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', priority);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;

    document.body.appendChild(announcement);

    // Remover después de que se haya anunciado
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);

    clientLogger.userAction('Screen reader announcement', { message, priority });
  };

  return { announce };
}

// Utilidades para ARIA
export const ariaUtils = {
  // Generar ID único para aria-describedby
  generateId: (prefix: string = 'aria') => `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,

  // Configurar relaciones ARIA
  setAriaRelation: (element: HTMLElement, relation: string, targetId: string) => {
    element.setAttribute(relation, targetId);
  },

  // Anunciar cambios de estado
  announceStateChange: (element: HTMLElement, state: string) => {
    element.setAttribute('aria-label', state);
    
    // Trigger screen reader update
    const event = new CustomEvent('ariaUpdate', { detail: { element, state } });
    element.dispatchEvent(event);
  }
};

// Componente para skip links
export function SkipLinks() {
  return (
    <div className="sr-only focus-within:not-sr-only">
      <a
        href="#main-content"
        className="absolute top-0 left-0 z-50 p-2 bg-primary text-white focus:relative focus:z-auto"
      >
        Saltar al contenido principal
      </a>
      <a
        href="#navigation"
        className="absolute top-0 left-0 z-50 p-2 bg-primary text-white focus:relative focus:z-auto"
      >
        Saltar a la navegación
      </a>
    </div>
  );
}

// Hook para focus management
export function useFocusManagement() {
  const [focusHistory, setFocusHistory] = useState<HTMLElement[]>([]);

  const saveFocus = () => {
    const activeElement = document.activeElement as HTMLElement;
    if (activeElement && activeElement !== document.body) {
      setFocusHistory(prev => [...prev, activeElement]);
    }
  };

  const restoreFocus = () => {
    const lastFocused = focusHistory[focusHistory.length - 1];
    if (lastFocused && document.contains(lastFocused)) {
      lastFocused.focus();
      setFocusHistory(prev => prev.slice(0, -1));
    }
  };

  const focusFirst = (container: HTMLElement) => {
    const focusable = container.querySelector(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) as HTMLElement;
    
    if (focusable) {
      focusable.focus();
    }
  };

  return {
    saveFocus,
    restoreFocus,
    focusFirst
  };
}

// Aplicar estilos de accesibilidad
export function applyAccessibilityStyles() {
  const style = document.createElement('style');
  style.textContent = `
    /* Screen reader only */
    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }

    /* Focus visible */
    .focus-visible:focus {
      outline: 2px solid #3b82f6;
      outline-offset: 2px;
    }

    /* High contrast mode */
    @media (prefers-contrast: high) {
      * {
        border-color: currentColor !important;
      }
    }

    /* Reduced motion */
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
    }

    /* Font size classes */
    .font-size-small {
      font-size: 0.875rem;
    }

    .font-size-normal {
      font-size: 1rem;
    }

    .font-size-large {
      font-size: 1.125rem;
    }
  `;

  document.head.appendChild(style);
}
