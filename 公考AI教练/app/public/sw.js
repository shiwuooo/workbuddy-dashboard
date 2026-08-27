// 公考 AI 教练 · Service Worker（离线缓存静态资源）
const CACHE = 'gkcoach-v1';
const ASSETS = ['/', '/static/styles.css', '/static/app.js', '/manifest.webmanifest', '/icon.svg'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // 不缓存 API 请求（数据动态）
  if (url.pathname.startsWith('/api/')) return;
  // 页面导航：离线时回退到缓存首页
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).catch(() => caches.match('/')));
    return;
  }
  e.respondWith(
    caches.match(req).then(cached => cached || fetch(req).then(resp => {
      if (url.origin === self.location.origin &&
          (url.pathname.startsWith('/static/') ||
           ['.css', '.js', '.svg', '.webmanifest'].some(x => url.pathname.endsWith(x)))) {
        const copy = resp.clone();
        caches.open(CACHE).then(c => c.put(req, copy));
      }
      return resp;
    }).catch(() => caches.match(req)))
  );
});
