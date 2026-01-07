// Service Worker para Drive+ PWA
const CACHE_NAME = 'drive-plus-v1.0.1'; // Incrementado para forzar actualización
const RUNTIME_CACHE = 'drive-plus-runtime-v1.0.1';
const API_CACHE = 'drive-plus-api-v1.0.1';
const BASE_PATH = '/DriveP';

// Assets críticos para cachear en instalación
const PRECACHE_ASSETS = [
  `${BASE_PATH}/`,
  `${BASE_PATH}/index.html`,
  `${BASE_PATH}/manifest.json`,
  `${BASE_PATH}/logo-drive.png`
];

// Instalación del Service Worker
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker: Instalando...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('📦 Service Worker: Cacheando assets críticos');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activación del Service Worker
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker: Activando...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE && cacheName !== API_CACHE) {
            console.log('🗑️ Service Worker: Eliminando cache antiguo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Estrategia de fetch
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignorar chrome extensions y otros protocolos
  if (!url.protocol.startsWith('http')) return;

  // API Requests - Network First, fallback to cache
  if (url.pathname.startsWith('/api') || url.origin.includes('drive-plus-production.up.railway.app') || url.origin.includes('localhost:8000')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Solo cachear respuestas exitosas de GET
          if (response.status === 200 && request.method === 'GET') {
            const responseClone = response.clone();
            caches.open(API_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Si falla y es GET, intentar desde cache
          if (request.method === 'GET') {
            return caches.match(request).then((cachedResponse) => {
              if (cachedResponse) {
                return cachedResponse;
              }
              // Respuesta offline genérica
              return new Response(
                JSON.stringify({ error: 'Sin conexión', offline: true }),
                { headers: { 'Content-Type': 'application/json' } }
              );
            });
          }
          // Para métodos no-GET, re-lanzar el error
          throw error;
        })
    );
    return;
  }

  // Assets estáticos - Solo para requests GET
  if (request.method !== 'GET') return;

  // Assets estáticos - Cache First, fallback to network
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      return fetch(request).then((response) => {
        // No cachear respuestas no exitosas
        if (!response || response.status !== 200 || response.type === 'error') {
          return response;
        }

        const responseClone = response.clone();
        caches.open(RUNTIME_CACHE).then((cache) => {
          cache.put(request, responseClone);
        });

        return response;
      }).catch((error) => {
        console.log('❌ Error fetching:', request.url, error);
        // Si es un 404, no hacer nada especial
        return new Response('Not found', { status: 404 });
      });
    })
  );
});

// Sincronización en background
self.addEventListener('sync', (event) => {
  console.log('🔄 Service Worker: Sincronizando en background');
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

// Notificaciones push
self.addEventListener('push', (event) => {
  console.log('🔔 Service Worker: Push recibido');
  const data = event.data ? event.data.json() : {};
  
  const options = {
    body: data.body || 'Nueva notificación de Drive+',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    data: data.data || {},
    actions: [
      { action: 'open', title: 'Abrir' },
      { action: 'close', title: 'Cerrar' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'Drive+', options)
  );
});

// Click en notificación
self.addEventListener('notificationclick', (event) => {
  console.log('👆 Service Worker: Click en notificación');
  event.notification.close();

  if (event.action === 'open') {
    event.waitUntil(
      clients.openWindow(event.notification.data.url || '/')
    );
  }
});

// Función auxiliar para sincronización
async function syncData() {
  try {
    // Aquí puedes implementar lógica de sincronización
    console.log('📡 Sincronizando datos...');
    return Promise.resolve();
  } catch (error) {
    console.error('❌ Error en sincronización:', error);
    return Promise.reject(error);
  }
}
