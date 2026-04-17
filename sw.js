const CACHE_NAME = 'vertextrack-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/analyse.html',
  '/index.html',
  'https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.2.0/dist/tf.min.js',
  'https://cdn.jsdelivr.net/npm/@tensorflow-models/pose-detection@2.1.0/dist/pose-detection.min.js'
];

// Installation — mise en cache
self.addEventListener('install', function(event) {
  console.log('[SW] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      console.log('[SW] Caching assets');
      return cache.addAll(ASSETS_TO_CACHE).catch(function(err) {
        console.warn('[SW] Cache partial fail:', err);
      });
    })
  );
  self.skipWaiting();
});

// Activation — nettoyage ancien cache
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(k) { return k !== CACHE_NAME; })
            .map(function(k) { return caches.delete(k); })
      );
    })
  );
  self.clients.claim();
});

// Fetch — cache first pour TF.js, network first pour reste
self.addEventListener('fetch', function(event) {
  var url = event.request.url;
  
  // Cache first pour les modèles TF.js (gros fichiers)
  if (url.includes('tensorflow') || url.includes('pose-detection') 
      || url.includes('tfjs') || url.includes('model.json')
      || url.includes('group1-shard')) {
    event.respondWith(
      caches.match(event.request).then(function(cached) {
        if (cached) {
          console.log('[SW] Serving from cache:', url.slice(-40));
          return cached;
        }
        return fetch(event.request).then(function(response) {
          if (response.ok) {
            var clone = response.clone();
            caches.open(CACHE_NAME).then(function(cache) {
              cache.put(event.request, clone);
            });
          }
          return response;
        });
      })
    );
    return;
  }
  
  // Network first pour le reste
  event.respondWith(
    fetch(event.request).catch(function() {
      return caches.match(event.request);
    })
  );
});
