#!/usr/bin/env python3
"""영상이 앱 안에서 재생되는지 먼저 확인한다 — 콘텐츠를 고르기 전의 관문.

지역 차단도 아니고 자막도 멀쩡한데, 저작권자가 「유튜브 밖 재생」만 막아 둔 영상이 있다.
yt-dlp 메타데이터로는 안 잡힌다(playable_in_embed 이 True 로 나온다). 실제로 임베드해 봐야 안다.
밀키☆서브웨이가 그랬고, 그 앱의 예문 343건이 소리를 들을 수 없게 됐다.

방법: videoId 하나만 넣은 미니 페이지를 간이 서버 뒤에서 헤드리스 크롬으로 열고,
      onReady / onError 를 <title> 에 심어 읽는다. 후보 하나에 몇 초면 끝난다.

⚠ 판정은 「어느 도메인에서 여는가」에 따라 달라진다. 127.0.0.1 로 열면 멀쩡한 영상도
   ERROR 150 이 나온다(실제로 firstlove·reasons 가 그랬다 — 둘 다 배포 도메인에서는 정상).
   그래서 이 도구는 배포 도메인 이름으로 테스트 페이지를 연다(--host-resolver-rules 로
   그 이름을 127.0.0.1 로 돌린다). 다른 곳에 올릴 거면 --origin 으로 도메인을 바꾼다.

사용:
  python3 tools/embed_check.py kzZ6KXDM1RI                 # ID 나 유튜브 주소 여러 개
  python3 tools/embed_check.py --apps                      # 이미 만든 앱들의 영상을 전수 점검
판정: OK=재생됨 / BLOCKED=앱 안 재생 차단(101·150) / 그 밖은 오류 코드와 함께 표시.
막힌 영상이 하나라도 있으면 종료 코드 1 — 만들기 전에 걸러 내기 위한 것이다.
"""
import glob
import http.server
import os
import re
import subprocess
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGIN = 'vinni-tokyo.github.io'          # 실제로 앱이 올라가는 도메인. 판정이 여기에 달려 있다
PAGE = """<!doctype html><title>WAIT</title><div id="p"></div>
<script src="https://www.youtube.com/iframe_api"></script>
<script>
function onYouTubeIframeAPIReady(){
  new YT.Player('p', {videoId: '__VID__', height: '200', width: '320',
    events: {onReady: () => { document.title = 'READY'; },
             onError: e => { document.title = 'ERROR ' + e.data; }}});
}
setTimeout(() => { if (document.title === 'WAIT') document.title = 'TIMEOUT'; }, 9000);
</script>"""
# 101·150 = 저작권자가 외부 사이트 재생을 막음. 100=없는 영상, 2=잘못된 ID, 5=플레이어 오류
BLOCK = {'101', '150'}
WHY = {'101': '앱 안 재생 차단', '150': '앱 안 재생 차단', '100': '영상 없음', '2': '잘못된 ID', '5': '플레이어 오류'}


def chrome():
    for pat in ('~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome',
                '/usr/bin/chromium', '/usr/bin/google-chrome'):
        hit = sorted(glob.glob(os.path.expanduser(pat)))
        if hit:
            return hit[-1]
    sys.exit('크롬을 찾지 못했습니다 (playwright 캐시나 chromium 을 설치하세요)')


def vid_of(s):
    m = re.search(r'(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})', s)
    return m.group(1) if m else s.strip()


def serve(dirname):
    class Q(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=dirname, **k)

        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Q)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def check(vids, origin=ORIGIN):
    tmp = tempfile.mkdtemp(prefix='embedcheck-')
    srv = serve(tmp)
    port = srv.server_address[1]
    exe = chrome()
    out = []
    try:
        for v in vids:
            open(os.path.join(tmp, v + '.html'), 'w', encoding='utf-8').write(PAGE.replace('__VID__', v))
            r = subprocess.run([exe, '--headless=new', '--no-sandbox', '--disable-gpu',
                                '--window-size=800,600', '--virtual-time-budget=11000',
                                f'--host-resolver-rules=MAP {origin} 127.0.0.1', '--dump-dom',
                                f'http://{origin}:{port}/{v}.html'],      # 배포 도메인으로 열어야 판정이 맞다
                               capture_output=True, text=True, timeout=90)
            m = re.search(r'<title>([^<]*)</title>', r.stdout)
            out.append((v, (m.group(1) if m else 'NO-TITLE').strip()))
    finally:
        srv.shutdown()
    return out


def app_vids():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, '*-cards', '*.html'))):
        if os.path.basename(f) == 'index.html':
            continue
        m = re.search(r"VID = '([^']+)'", open(f, encoding='utf-8').read())
        if m:
            rows.append((os.path.basename(os.path.dirname(f)), os.path.basename(f), m.group(1)))
    seen, uniq = set(), []
    for app, page, v in rows:
        if v not in seen:
            seen.add(v)
            uniq.append((app, page, v))
    return uniq


def main():
    argv = sys.argv[1:]
    origin = ORIGIN
    for i, a in enumerate(argv):
        if a == '--origin' and i + 1 < len(argv): origin = argv[i + 1]
    args = [a for a in argv if a != '--apps' and a != '--origin' and a != origin]
    if '--apps' in sys.argv:
        rows = app_vids()
        print(f'이미 만든 앱의 영상 {len(rows)}개를 점검합니다\n')
        res = dict(check([v for _, _, v in rows], origin))
        bad = 0
        for app, page, v in rows:
            st = res.get(v, '?')
            code = st.split()[-1] if st.startswith('ERROR') else ''
            mark = 'OK     ' if st == 'READY' else ('BLOCKED' if code in BLOCK else 'NG     ')
            if st != 'READY':
                bad += 1
            print(f'  {mark} {app:<20} {v}  {"" if st == "READY" else st + (" · " + WHY.get(code, "") if WHY.get(code) else "")}')
        print(f'\n재생 가능 {len(rows) - bad} · 문제 {bad}')
        return 1 if bad else 0

    if not args:
        print(__doc__)
        return 2
    vids = [vid_of(a) for a in args]
    bad = 0
    print(f'기준 도메인: {origin}\n')
    for v, st in check(vids, origin):
        code = st.split()[-1] if st.startswith('ERROR') else ''
        if st == 'READY':
            print(f'  OK      {v}  앱 안에서 재생됩니다 — 써도 됩니다')
        elif code in BLOCK:
            bad += 1
            print(f'  BLOCKED {v}  앱 안 재생을 저작권자가 막았습니다 ({st}) — 다른 영상을 고르세요')
        else:
            bad += 1
            print(f'  NG      {v}  {st}{" · " + WHY[code] if code in WHY else ""}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
