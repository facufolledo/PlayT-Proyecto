// Service Worker para Firebase Cloud Messaging
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// Configuración de Firebase (se debe actualizar con tus credenciales)
// Nota: En producción, estas credenciales son públicas y seguras de exponer
firebase.initializeApp({
  apiKey: "AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  authDomain: "playt-xxxxx.firebaseapp.com",
  projectId: "playt-xxxxx",
  storageBucket: "playt-xxxxx.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:xxxxxxxxxxxxxxxx"
});

const messaging = firebase.messaging();

// Manejar mensajes en background
messaging.onBackgroundMessage((payload) => {
  console.log('[SW] Mensaje en background:', payload);

  const notificationTitle = payload.notification?.title || 'PlayT';
  const notificationOptions = {
    body: payload.notification?.body || '',
    icon: '/logo-drive-plus.png',
    badge: '/logo-drive-plus.png',
    tag: payload.data?.tipo || 'default',
    data: payload.data,
    actions: getActionsForType(payload.data?.tipo)
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// Acciones según el tipo de notificación
function getActionsForType(tipo) {
  switch (tipo) {
    case 'resultado_pendiente':
      return [
        { action: 'confirmar', title: 'Ver resultado' },
        { action: 'ignorar', title: 'Ignorar' }
      ];
    case 'invitacion_torneo':
      return [
        { action: 'ver', title: 'Ver invitación' },
        { action: 'ignorar', title: 'Ignorar' }
      ];
    default:
      return [];
  }
}

// Manejar click en notificación
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Click en notificación:', event);
  
  event.notification.close();

  const data = event.notification.data || {};
  let url = '/dashboard';

  // Determinar URL según el tipo
  switch (data.tipo) {
    case 'resultado_pendiente':
      url = '/salas/confirmaciones';
      break;
    case 'invitacion_torneo':
      url = '/torneos/mis-torneos';
      break;
    case 'elo_actualizado':
      url = '/perfil';
      break;
  }

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // Si ya hay una ventana abierta, enfocarla
      for (const client of clientList) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          client.navigate(url);
          return client.focus();
        }
      }
      // Si no hay ventana, abrir una nueva
      if (clients.openWindow) {
        return clients.openWindow(url);
      }
    })
  );
});
