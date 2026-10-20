/* Duelo de Cartas Maker — permite instalarlo como app y abrirlo sin internet.
   Primero intenta descargar la versión más nueva; si no hay conexión, usa la guardada. */
const CACHE = 'duelo-cartas-v1';
const CORE = ['./', 'index.html', 'manifest.webmanifest', 'icono_192.png', 'icono_512.png', 'icono_maskable_512.png'];
self.addEventListener('install', e => { self.skipWaiting(); e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).catch(()=>{})); });
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;
  e.respondWith(
    fetch(e.request).then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return r; })
      .catch(() => caches.match(e.request).then(r => r || caches.match('index.html')))
  );
});
