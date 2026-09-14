#!/usr/bin/env python3
"""노래방: 아래 고정 조작부가 현재 가사 줄을 덮던 것을 고친다.

버그: 비워 둘 아래 여백을 150px 로 못박았는데 실제 조작부(마디 패널+이동 줄)는 180~193px 이다.
게다가 화면이 짧으면 위쪽 영상에 밀려 가사 줄 자체가 고정 조작부 뒤로 들어갔다.
실측: 360x740 에서 116px, 360x780 에서 76px 가려짐. 844 이상에서는 안 보이던 결함.

고침: ① 여백을 조작부 실제 높이에서 재서 맞춘다(창 크기가 바뀌어도 다시 잰다).
      ② 줄이 바뀔 때 현재 줄이 조작부에 가리면 그만큼만 굴려 보이게 한다.

사용: python3 patch_karafit.py <앱폴더>/src/tpl.html [...]
"""
import io
import sys

JS = '''
/* 노래방: 아래 고정 조작부가 현재 가사 줄을 덮지 않게 한다.
   비워 둘 높이를 150px 로 못박았더니 실제 조작부(180~193px)보다 작았고,
   화면이 짧으면 가사 줄이 그 뒤로 들어갔다. 실측해서 맞추고, 줄이 바뀌면 보이게 굴린다. */
function karaFixEl(){ const k = document.querySelector('#karaView .kfix'); return (k && getComputedStyle(k).position === 'fixed') ? k : null; }
function karaFit(){
  const p = document.querySelector('#karaView .kara'); if(!p) return;
  const k = karaFixEl();
  p.style.paddingBottom = k ? (Math.ceil(k.getBoundingClientRect().height) + 16) + 'px' : '';
}
function karaReveal(){
  const k = karaFixEl(), n = document.querySelector('#karaView .kara-now');
  if(!k || !n || view !== 'kara') return;
  const lid = k.getBoundingClientRect().top, r = n.getBoundingClientRect(), gap = 12;
  const soft = matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
  if(r.bottom > lid - gap) window.scrollBy({ top: r.bottom - (lid - gap), behavior: soft });
  else if(r.top < 8) window.scrollBy({ top: r.top - 8, behavior: soft });
}
addEventListener('resize', karaFit);
addEventListener('orientationchange', () => setTimeout(karaFit, 250));
'''


def patch(path):
    h = io.open(path, encoding='utf-8').read()
    if 'function karaFit(' in h:
        print(f'skip (이미 적용) {path}')
        return

    # ① 동작 — karaPaint 바로 앞에 둔다
    anchor = 'function karaPaint(t){'
    assert h.count(anchor) == 1, f'{path}: karaPaint {h.count(anchor)}개'
    h = h.replace(anchor, JS + anchor)

    # ② 줄이 바뀐 직후 보이게 굴린다 — karaPaint 안쪽의 첫 번째 것만
    line = ('    if(cur && stopAt === null){ const k = deck.findIndex(x => x.id === cur.id); '
            'if(k >= 0 && k !== index){ index = k; showCard(); } }')
    at = h.index(line, h.index('function karaPaint(t){'))
    h = h[:at + len(line)] + '\n    requestAnimationFrame(karaReveal);' + h[at + len(line):]

    # ③ 노래방으로 들어올 때 여백을 잰다 — switchView 는 앱마다 두 가지 꼴이 있다
    forms = [("if(v === 'kara'){ karaLast = -2; karaPaint(",
              "if(v === 'kara'){ karaLast = -2; requestAnimationFrame(karaFit); karaPaint("),
             ("if(v === 'kara') karaPaint(",
              "if(v === 'kara'){ requestAnimationFrame(karaFit); } if(v === 'kara') karaPaint(")]
    for old, new in forms:
        if h.count(old) == 1:
            h = h.replace(old, new)
            break
    else:
        raise AssertionError(f'{path}: switchView 앵커를 못 찾음')

    io.open(path, 'w', encoding='utf-8').write(h)
    print(f'ok   {path}')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        patch(p)
