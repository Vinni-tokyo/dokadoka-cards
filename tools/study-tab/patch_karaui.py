#!/usr/bin/env python3
"""노래방 화면을 가사 중심으로 정리한다.

문제: 가사 위에 「카드로 · 처음부터 · 이 줄부터 · 일시정지」가 놓여 있는데 넷 다 아래 바와 겹친다.
      마디·미세 조정 패널도 늘 펼쳐져 있어 화면 아래쪽을 크게 차지했다.

고침: ① 가사 위 조작 줄에서 버튼 넷을 걷어낸다(읽기·뜻 체크와 위치 표시만 남긴다).
      ② 「처음부터·이 줄부터·일시정지」는 서랍으로 옮겨 기능은 그대로 둔다. 「카드로」는 아래 바에 이미 있다.
      ③ 마디·미세 조정은 기본이 닫힌 서랍이 되고, 아래 바의 버튼으로 연다.
      ④ 그래서 늘 고정되는 것은 이동 바 한 줄뿐이다.

라벨 순서가 앱 계열마다 달라(한국어 학습용 / 일본어 학습용) 글자가 아니라 id 로 찾는다.
사용: python3 patch_karaui.py <앱폴더>/src/tpl.html [...]
"""
import io
import sys

JS = '''/* 마디·미세 조정은 서랍으로 — 기본은 닫혀 있고 아래 바의 버튼으로 연다.
   가사 위에 있던 「카드로·처음부터·이 줄부터·일시정지」는 아래 바와 겹쳐 걷어내고,
   뒤 셋은 이 서랍으로 옮겼다. 고정되는 것은 이동 바 한 줄뿐이다. */
var barsOpen = false;
function barsPaint(){
  var can = !(BARS.length < 2 || OFFLINE), b = $('knBars');
  if(!can) barsOpen = false;
  if(b){ b.hidden = !can; b.setAttribute('aria-pressed', String(barsOpen)); }
  $('barBox').hidden = !barsOpen;
  requestAnimationFrame(() => {                    /* 서랍을 여닫으면 고정 바 높이가 바뀐다 */
    if(typeof karaFit === 'function') karaFit();
    if(typeof karaReveal === 'function') karaReveal();   /* 열면서 가사가 가리면 다시 올려 준다 */
  });
}
'''

BTN = ('\n       <button class="btn knback" id="knBars" aria-pressed="false" hidden '
       'title="마디 · 미세 조정 / 小節・微調整"><svg class="ic"><use href="#i-bars"/></svg></button>')


def patch(path):
    h = io.open(path, encoding='utf-8').read()
    if 'id="knBars"' in h:
        print(f'skip (이미 적용) {path}')
        return

    # ① 아래 바에 칸 하나를 더 낸다
    a = '.kara .knav{grid-template-columns:auto 1fr 1.2fr .9fr 1fr;gap:6px}'
    assert h.count(a) == 1, f'{path}: knav CSS 앵커 {h.count(a)}개'
    h = h.replace(a, '.kara .knav{grid-template-columns:auto 1fr 1.15fr .85fr 1fr auto;gap:5px}')

    # ② 가사 위 조작 줄에서 버튼 넷을 들어낸다
    i = h.index('<div class="kara-top">')
    j = h.index('</div>', i)
    kept, moved = [], []
    for ln in h[i:j].split('\n'):
        if 'id="karaBack"' in ln:
            continue                                   # 카드로 — 아래 바에 이미 있다
        if any(k in ln for k in ('id="karaStart"', 'id="karaHere"', 'id="karaPause"')):
            moved.append(ln.strip())                   # 서랍으로 옮긴다
            continue
        kept.append(ln)
    assert len(moved) == 3, f'{path}: 옮길 버튼 {len(moved)}개 (기대 3)'
    h = h[:i] + '\n'.join(kept) + h[j:]

    # ③ 서랍 맨 위에 옮긴 버튼 셋
    a = '<div class="bars" id="barBox" hidden>'
    assert h.count(a) == 1, f'{path}: barBox 앵커 {h.count(a)}개'
    h = h.replace(a, a + '\n        <div class="bars-row">'
                  + ''.join('\n         ' + m for m in moved) + '\n        </div>')

    # ④ 아래 바에 서랍 여닫는 버튼
    k = h.index('id="knNext"')
    e = h.index('</button>', k) + len('</button>')
    h = h[:e] + BTN + h[e:]

    # ⑤ 동작 — rebuildBars 보다 먼저 선언되게 둔다(호출 시점 TDZ 방지)
    a = 'function rebuildBars(){'
    assert h.count(a) == 1, f'{path}: rebuildBars 앵커 {h.count(a)}개'
    h = h.replace(a, JS + a)
    a = "  $('barBox').hidden = BARS.length < 2 || OFFLINE;"
    assert h.count(a) == 1, f'{path}: barBox 표시 앵커 {h.count(a)}개'
    h = h.replace(a, '  barsPaint();')

    # ⑥ 걷어낸 버튼의 연결을 지우고, 서랍 버튼을 잇는다
    a = "$('karaBack').onclick = karaBack;\n"
    assert h.count(a) == 1, f'{path}: karaBack 연결 {h.count(a)}개'
    h = h.replace(a, '')
    a = "$('knBack').onclick = karaBack;"
    assert h.count(a) == 1
    h = h.replace(a, a + "\n$('knBars').onclick = () => { barsOpen = !barsOpen; barsPaint(); };")

    # ⑦ 카드의 「마디 반복」으로 들어오면 서랍을 열어 준다
    a = "if(BARS.length >= 2 && player && ready) $('barLine').click(); };"
    if h.count(a) == 1:
        h = h.replace(a, "if(BARS.length >= 2 && player && ready){ barsOpen = true; barsPaint(); $('barLine').click(); } };")

    io.open(path, 'w', encoding='utf-8').write(h)
    print(f'ok   {path}')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        patch(p)
