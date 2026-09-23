#!/usr/bin/env python3
"""음량 버튼의 3단계를 눈에 보이게 한다.

문제: 🔈 🔉 🔊 세 이모지는 12.5px 에서 거의 같아 보인다. 눌러도 바뀐 줄 모른다.
      (기능은 멀쩡했다 — 30% → 60% → 100% 로 돌고 있었다. 보이지 않았을 뿐이다.)

고침: 이모지를 버리고 스피커 그림을 버튼 안에 직접 그린다. 음파 두 가닥을 따로 두고
      단계에 따라 0가닥 · 1가닥 · 2가닥을 켠다. 굵은 선이라 작아도 구별된다.
      <use> 로 불러온 그림은 바깥 CSS 가 속을 못 건드려서(그림자 트리) 직접 그린다.
      버튼 너비는 그대로다 — 글자가 아니라 그림이라 한 줄에 그대로 들어간다.

사용: python3 patch_volicon.py <앱폴더>/src/tpl.html [...]
"""
import io
import sys

OLD_BTN = '<button class="btn btn-sm" id="ttsVol" title="읽어주기 음량">🔉</button>'
NEW_BTN = ('<button class="btn btn-sm" id="ttsVol" data-lv="2" title="읽어주기 음량">'
           '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">'
           '<path d="M11 5L6.5 9H3v6h3.5L11 19z"/>'
           '<path class="w1" d="M14.8 9.6a4 4 0 010 4.8"/>'
           '<path class="w2" d="M17.8 6.8a8 8 0 010 10.4"/>'
           '</svg></button>')

OLD_JS = ("function aVolPaint(){ const b = document.getElementById('ttsVol'); if(!b) return; "
          "const v = aVol(); b.textContent = v <= 0.3 ? '🔈' : v <= 0.6 ? '🔉' : '🔊'; "
          "b.title = '읽어주기 음량 ' + Math.round(v * 100) + '% (누르면 바뀜)'; }")
NEW_JS = ("function aVolPaint(){ const b = document.getElementById('ttsVol'); if(!b) return; "
          "const v = aVol(), pct = Math.round(v * 100); "
          "b.dataset.lv = v <= 0.3 ? '1' : v <= 0.6 ? '2' : '3';   /* 음파 가닥 수로 보여 준다 */ "
          "b.title = '읽어주기 음량 ' + pct + '% (누르면 바뀜)'; "
          "b.setAttribute('aria-label', '읽어주기 음량 ' + pct + '%'); }")

CSS = ('\n#ttsVol .w1,#ttsVol .w2{transition:opacity .15s}'
       '\n#ttsVol[data-lv="1"] .w1,#ttsVol[data-lv="1"] .w2,#ttsVol[data-lv="2"] .w2{opacity:.16}'
       '   /* 음량 3단계: 음파 0가닥 · 1가닥 · 2가닥 */')


def patch(path):
    h = io.open(path, encoding='utf-8').read()
    if 'id="ttsVol" data-lv' in h:
        print('  건너뜀(이미 적용):', path)
        return
    for old in (OLD_BTN, OLD_JS):
        assert h.count(old) == 1, f'{path}: 못 찾았다 — {old[:40]}'
    h = h.replace(OLD_BTN, NEW_BTN, 1).replace(OLD_JS, NEW_JS, 1)

    anchor = '.ttsrow .btn[aria-pressed=true]{'
    j = h.index('\n', h.index(anchor))
    h = h[:j] + CSS + h[j:]

    io.open(path, 'w', encoding='utf-8').write(h)
    print('  고침:', path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for p in sys.argv[1:]:
        patch(p)
