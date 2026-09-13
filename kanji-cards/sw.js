/* 설치형 앱(PWA)용 서비스 워커 v2.
   페이지(HTML)는 항상 네트워크에서 새로 받는다(cache: no-store) → GitHub Pages 의 10분 캐시와 앱 캐시를 건너뛰어 배포 즉시 반영.
   오프라인일 때만 브라우저 캐시에 있는 것을 쓴다. 그 외 요청은 건드리지 않는다 */
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil((async () => { const ks = await caches.keys(); await Promise.all(ks.map(k => caches.delete(k))); await self.clients.claim(); })()));
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (u.origin !== location.origin) return;
  if (e.request.mode === 'navigate' || u.pathname.endsWith('.html') || u.pathname.endsWith('.webmanifest')) {
    e.respondWith(fetch(e.request, {cache: 'no-store'}).catch(() => caches.match(e.request).then(r => r || fetch(e.request))));
  }
});
