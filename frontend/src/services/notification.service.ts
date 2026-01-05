/**
 * Servicio de Notificaciones Push con Firebase Cloud Messaging
 */
import { getMessaging, getToken, onMessage, Messaging } from 'firebase/messaging';
import app from '../config/firebase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const VAPID_KEY = import.meta.env.VITE_FIREBASE_VAPID_KEY;

let messaging: Messaging | null = null;

// Inicializar messaging solo si está soportado
const initMessaging = () => {
  if (messaging) return messaging;
  
  try {
    if ('Notification' in window && 'serviceWorker' in navigator) {
      messaging = getMessaging(app);
    }
  } catch (error) {
    console.warn('Firebase Messaging no disponible:', error);
  }
  
  return messaging;
};

export const notificationService = {
  /**
   * Verifica si las notificaciones están soportadas
   */
  isSupported(): boolean {
    return 'Notification' in window && 'serviceWorker' in navigator;
  },

  /**
   * Obtiene el estado actual del permiso
   */
  getPermissionStatus(): NotificationPermission | 'unsupported' {
    if (!this.isSupported()) return 'unsupported';
    return Notification.permission;
  },

  /**
   * Solicita permiso y registra el token FCM
   */
  async requestPermission(): Promise<string | null> {
    if (!this.isSupported()) {
      console.warn('Notificaciones no soportadas en este navegador');
      return null;
    }

    try {
      const permission = await Notification.requestPermission();
      
      if (permission !== 'granted') {
        console.log('Permiso de notificaciones denegado');
        return null;
      }

      // Registrar service worker
      await this.registerServiceWorker();
      
      const msg = initMessaging();
      if (!msg) return null;

      if (!VAPID_KEY) {
        console.warn('VAPID_KEY no configurada');
        return null;
      }

      const token = await getToken(msg, { vapidKey: VAPID_KEY });
      
      if (token) {
        console.log('Token FCM obtenido');
        await this.registerTokenInBackend(token);
        return token;
      }
      
      return null;
    } catch (error) {
      console.error('Error solicitando permiso:', error);
      return null;
    }
  },

  /**
   * Registra el service worker de Firebase
   */
  async registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
    try {
      const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
      console.log('Service Worker registrado');
      return registration;
    } catch (error) {
      console.error('Error registrando Service Worker:', error);
      return null;
    }
  },

  /**
   * Envía el token FCM al backend
   */
  async registerTokenInBackend(token: string): Promise<boolean> {
    try {
      const authToken = localStorage.getItem('firebase_token');
      if (!authToken) return false;

      const response = await fetch(`${API_URL}/usuarios/fcm-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ fcm_token: token })
      });

      return response.ok;
    } catch (error) {
      console.error('Error registrando token en backend:', error);
      return false;
    }
  },

  /**
   * Configura el listener para mensajes en foreground
   */
  setupForegroundListener(callback?: (payload: any) => void): void {
    const msg = initMessaging();
    if (!msg) return;

    onMessage(msg, (payload) => {
      console.log('Notificación recibida:', payload);
      
      // Mostrar notificación nativa si la app está en foreground
      if (payload.notification && Notification.permission === 'granted') {
        new Notification(payload.notification.title || 'PlayT', {
          body: payload.notification.body,
          icon: '/logo-playr.png',
          data: payload.data
        });
      }

      // Callback personalizado
      if (callback) callback(payload);
    });
  }
};
