/* 설치형 앱(PWA)용 최소 서비스 워커. 캐시하지 않고 그대로 네트워크에 넘긴다(항상 최신 버전, 오프라인 지원 없음) */
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', () => {});
