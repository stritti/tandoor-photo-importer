// Service Worker für PWA-Funktionalität
const CACHE_NAME = 'recipe-analyzer-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/favicon.ico',
  '/offline.html'
];

// Installation des Service Workers
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Cache geöffnet');
        return cache.addAll(urlsToCache);
      })
  );
});

// Aktivierung des Service Workers
self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch-Event-Handler für Netzwerkanfragen
self.addEventListener('fetch', (event) => {
  // Ignoriere chrome-extension Anfragen
  if (event.request.url.startsWith('chrome-extension://')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        
        // Nur HTTP(S) URLs cachen
        if (!event.request.url.startsWith('http')) {
          return fetch(event.request);
        }
        
        return fetch(event.request)
          .then((response) => {
            // Prüfen, ob wir eine gültige Antwort erhalten haben
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // WICHTIG: Response klonen, da sie nur einmal verwendet werden kann
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then((cache) => {
                // Nur GET-Anfragen cachen
                if (event.request.method === 'GET') {
                  try {
                    cache.put(event.request, responseToCache);
                  } catch (error) {
                    console.error('Caching fehlgeschlagen:', error);
                  }
                }
              });

            return response;
          });
      })
      .catch(() => {
        // Wenn offline und keine Cache-Version vorhanden, zeige Offline-Seite
        if (event.request.mode === 'navigate') {
          return caches.match('/offline.html');
        }
      })
  );
});
