#!/usr/bin/env python3
"""아이폰에서 음량 버튼이 먹지 않던 것을 고친다.

문제: 아이폰(iOS Safari)은 오디오 요소의 volume 값을 무시한다. 소리 크기는 기기의
      하드웨어 버튼으로만 바뀐다. 그래서 a.volume = 0.3 을 넣어도 아무 일도 없었다.
      PC 에서는 그대로 동작했기 때문에 버튼이 고장 난 것처럼 보이지 않았다.

고침: Web Audio 의 이득(gain) 노드를 거쳐 소리를 낸다. 이건 아이폰에서도 먹는다.
      다만 소리 통로를 바꾸는 일이라 잘못되면 아예 무음이 될 수 있다. 그래서
      · AudioContext 가 실제로 running 일 때만 연결한다(아니면 예전처럼 그냥 튼다)
      · 연결에 실패하면 원래 방식으로 되돌린다
      · 첫 터치에서 미리 AudioContext 를 깨워 둔다(첫 재생부터 먹도록)
      최악의 경우라도 「음량 조절이 안 먹는다」로 끝나고, 무음이 되지는 않는다.

브라우저 음성(speechSynthesis)은 아이폰에서 음량을 여전히 못 바꾼다 — 그쪽은
방법이 없다. 음원이 심긴 앱은 거의 항상 음원 쪽으로 난다.

사용: python3 patch_volgain.py <앱폴더>/src/tpl.html [...]
"""
import io
import sys

HELPERS = '''/* 아이폰은 오디오의 volume 을 무시한다(하드웨어 버튼으로만 바뀐다).
   그래서 Web Audio 의 이득 노드를 거쳐 크기를 바꾼다. 연결이 안 되면 그냥 튼다 — 무음보다 낫다. */
let aCtx = null, aGain = null;
function aCtxGet(){
  if(aCtx) return aCtx;
  const C = window.AudioContext || window.webkitAudioContext;
  if(!C) return null;
  try{ aCtx = new C(); }catch(e){ aCtx = null; }
  return aCtx;
}
function aCtxWake(){ const c = aCtxGet(); if(c && c.state === 'suspended') c.resume().catch(() => {}); }
addEventListener('pointerdown', aCtxWake, { passive: true });
addEventListener('keydown', aCtxWake);
function aWire(el){
  const c = aCtxGet();
  if(!c) return false;
  if(c.state === 'suspended') c.resume().catch(() => {});
  if(c.state !== 'running') return false;      /* 아직 안 깨어났으면 건드리지 않는다 */
  try{
    const s = c.createMediaElementSource(el), g = c.createGain();
    g.gain.value = aVol(); s.connect(g); g.connect(c.destination); aGain = g;
    return true;
  }catch(e){ return false; }
}
'''

OLD_CYCLE = ("function aVolCycle(){ const v = A_VOLS[(A_VOLS.indexOf(aVol()) + 1) % A_VOLS.length]; "
             "store.set('avol', v); if(aCur){ try{ aCur.volume = v; }catch(e){} } aVolPaint(); }")
NEW_CYCLE = ("function aVolCycle(){ const v = A_VOLS[(A_VOLS.indexOf(aVol()) + 1) % A_VOLS.length]; "
             "store.set('avol', v); "
             "if(aGain){ try{ aGain.gain.value = v; }catch(e){} }   /* 이득 노드를 거치는 경우 */ "
             "if(aCur){ try{ aCur.volume = aGain ? 1 : v; }catch(e){} } aVolPaint(); }")

OLD_PLAY = ("if(src){ const a = new Audio(src); aCur = a; a.playbackRate = rate || 1; a.volume = aVol(); "
            "a.onended = after; a.onerror = after; a.play().catch(after); }")
NEW_PLAY = ("if(src){ const a = new Audio(src); aCur = a; a.playbackRate = rate || 1; "
            "a.volume = aWire(a) ? 1 : aVol();   /* 이득 노드를 타면 크기는 거기서 준다 */ "
            "a.onended = after; a.onerror = after; a.play().catch(after); }")

ANCHOR = 'function aPlay(text, times, gap, cb, which, rate){'


def patch(path):
    h = io.open(path, encoding='utf-8').read()
    if 'function aWire(' in h:
        print('  건너뜀(이미 적용):', path)
        return
    for old in (OLD_CYCLE, OLD_PLAY, ANCHOR):
        assert h.count(old) == 1, f'{path}: 못 찾았다 — {old[:46]}'
    h = h.replace(OLD_CYCLE, NEW_CYCLE, 1).replace(OLD_PLAY, NEW_PLAY, 1)
    h = h.replace(ANCHOR, HELPERS + ANCHOR, 1)
    io.open(path, 'w', encoding='utf-8').write(h)
    print('  고침:', path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for p in sys.argv[1:]:
        patch(p)
