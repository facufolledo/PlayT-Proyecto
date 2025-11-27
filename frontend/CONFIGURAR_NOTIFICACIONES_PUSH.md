# Configuración de Notificaciones Push con Firebase Cloud Messaging

## 1. Instalar dependencias

```bash
npm install firebase
```

## 2. Configurar Firebase en el proyecto

Crear archivo `src/services/firebase.ts`:

```typescript
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage } from 'firebase/messaging';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

export { messaging, getToken, onMessage };
```

## 3. Crear Service Worker

Crear archivo `public/firebase-messaging-sw.js`:

```javascript
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "TU_API_KEY",
  authDomain: "TU_AUTH_DOMAIN",
  projectId: "TU_PROJECT_ID",
  storageBucket: "TU_STORAGE_BUCKET",
  messagingSenderId: "TU_MESSAGING_SENDER_ID",
  appId: "TU_APP_ID"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log('Mensaje recibido en background:', payload);
  
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/icon-192x192.png',
    badge: '/icon-192x192.png',
    data: payload.data
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
```

## 4. Solicitar permiso y obtener token

Crear archivo `src/services/notification.service.ts`:

```typescript
import { messaging, getToken, onMessage } from './firebase';
import { authService } from './auth.service';

const VAPID_KEY = import.meta.env.VITE_FIREBASE_VAPID_KEY;

export const notificationService = {
  async requestPermission(): Promise<string | null> {
    try {
      const permission = await Notification.requestPermission();
      
      if (permission === 'granted') {
        const token = await getToken(messaging, { vapidKey: VAPID_KEY });
        
        if (token) {
          // Enviar token al backend
          await this.registerToken(token);
          return token;
        }
      }
      
      return null;
    } catch (error) {
      console.error('Error al solicitar permiso de notificaciones:', error);
      return null;
    }
  },

  async registerToken(token: string): Promise<void> {
    try {
      const headers = await authService.getHeaders();
      
      await fetch(`${import.meta.env.VITE_API_URL}/usuarios/fcm-token`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ fcm_token: token }),
      });
    } catch (error) {
      console.error('Error al registrar token FCM:', error);
    }
  },

  setupMessageListener(): void {
    onMessage(messaging, (payload) => {
      console.log('Mensaje recibido:', payload);
      
      // Mostrar notificación personalizada
      if (payload.notification) {
        new Notification(payload.notification.title || 'Notificación', {
          body: payload.notification.body,
          icon: '/icon-192x192.png',
          data: payload.data
        });
      }
    });
  }
};
```

## 5. Inicializar en App.tsx

```typescript
import { useEffect } from 'react';
import { notificationService } from './services/notification.service';

function App() {
  useEffect(() => {
    // Solicitar permiso de notificaciones
    notificationService.requestPermission();
    
    // Configurar listener de mensajes
    notificationService.setupMessageListener();
  }, []);

  // ... resto del componente
}
```

## 6. Variables de entorno

Agregar en `.env`:

```
VITE_FIREBASE_API_KEY=tu_api_key
VITE_FIREBASE_AUTH_DOMAIN=tu_auth_domain
VITE_FIREBASE_PROJECT_ID=tu_project_id
VITE_FIREBASE_STORAGE_BUCKET=tu_storage_bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=tu_messaging_sender_id
VITE_FIREBASE_APP_ID=tu_app_id
VITE_FIREBASE_VAPID_KEY=tu_vapid_key
```

## 7. Obtener VAPID Key

1. Ve a Firebase Console
2. Project Settings > Cloud Messaging
3. En "Web Push certificates", genera un nuevo par de claves
4. Copia la clave pública (VAPID key)

## 8. Backend - Ejecutar migración

```bash
cd backend
python agregar_fcm_token.py
```

## Notas

- Las notificaciones solo funcionan en HTTPS (excepto localhost)
- El usuario debe dar permiso explícito
- Las notificaciones en background requieren el service worker
- Las notificaciones en foreground se manejan con `onMessage`
