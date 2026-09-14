#!/usr/bin/env python3
"""화면 잠금 — 공부 중 오터치 방지.

탭 줄 오른쪽 끝의 자물쇠 버튼을 누르면 전체 화면을 덮는 막이 내려온다.
막을 2초간 꾹 누르고 있으면 풀린다(손을 떼면 처음부터). PC 는 Esc 로도 풀린다.
영상·음원은 그대로 재생되고, 잠긴 동안 키보드 단축키도 먹지 않는다.

사용: python3 patch_lock.py <앱폴더>/src/tpl.html [...]
이미 적용된 파일은 건너뛴다(여러 번 돌려도 안전).
"""
import sys


def rep(h, old, new, cnt=1):
    n = h.count(old)
    assert n == cnt, f'앵커 {n}개 (기대 {cnt}): {old[:70]!r}'
    return h.replace(old, new)


CSS = '''.tab.lock{flex:0 0 auto;padding:6px 10px;border-left:1px solid var(--line-2);border-radius:0 7px 7px 0;margin-left:2px;color:var(--ink-3)}
.tab.lock:hover{color:var(--brand)}
.tab.lock>.ic{display:block}
.lockveil{position:fixed;inset:0;z-index:9999;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;
 background:rgba(9,11,17,.985);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px);color:#fff;touch-action:none;-webkit-user-select:none;user-select:none;cursor:pointer}
.lockveil .lk-ic{width:44px;height:44px;fill:none;stroke:#fff;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round;opacity:.92}
.lockveil .lk-t{font-size:17px;font-weight:700;letter-spacing:-.01em}
.lockveil .lk-s{font-size:13px;line-height:1.75;color:#9aa3b8;text-align:center}
.lockveil .lk-s .sub{display:block;font-size:12px;color:#6f778c}
.lockveil .lk-bar{width:212px;height:6px;border-radius:99px;background:rgba(255,255,255,.16);overflow:hidden}
.lockveil .lk-bar span{display:block;height:100%;width:0;border-radius:99px;background:#fff}
.lockveil.holding .lk-bar span{width:100%;transition:width 2s linear}
@media(prefers-reduced-motion:reduce){.lockveil.holding .lk-bar span{transition:none;width:100%}}
'''

ICON = '<symbol id="i-lock" viewBox="0 0 24 24"><rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/></symbol>\n'

BTN = ('    <button class="tab lock" id="tabLock" title="화면 잠금 · 2초 길게 눌러 해제 / 画面ロック" '
       'aria-label="화면 잠금"><svg class="ic"><use href="#i-lock"/></svg></button>\n')

VEIL = '''<div class="lockveil" id="lockVeil" hidden>
 <svg class="lk-ic"><use href="#i-lock"/></svg>
 <div class="lk-t">화면이 잠겼습니다</div>
 <div class="lk-s">2초간 꾹 누르면 풀립니다<span class="sub" lang="ja">2秒長押しで解除</span></div>
 <div class="lk-bar"><span></span></div>
</div>
'''

JS = '''
/* 화면 잠금 — 공부 중 오터치 방지. 막을 2초간 꾹 누르면 풀린다(떼면 처음부터). */
const LOCK_MS = 2000;
let locked = false, lkTimer = null;
function lkCancel(){ if(lkTimer){ clearTimeout(lkTimer); lkTimer = null; } const v = $('lockVeil'); if(v) v.classList.remove('holding'); }
function lockOn(){ if(locked) return; locked = true; lkCancel(); $('lockVeil').hidden = false; document.body.style.overflow = 'hidden'; }
function lockOff(){ if(!locked) return; locked = false; lkCancel(); $('lockVeil').hidden = true; document.body.style.overflow = ''; }
(() => {
  const v = $('lockVeil'); if(!v) return;
  v.addEventListener('pointerdown', e => { if(!locked) return; e.preventDefault(); lkCancel(); v.classList.add('holding'); lkTimer = setTimeout(lockOff, LOCK_MS); });
  ['pointerup', 'pointercancel', 'pointerleave'].forEach(t => v.addEventListener(t, () => { if(locked) lkCancel(); }));
  v.addEventListener('contextmenu', e => e.preventDefault());
  $('tabLock').onclick = lockOn;
  /* 잠긴 동안에는 단축키를 먹지 않는다. Esc 는 PC 용 비상구. */
  document.addEventListener('keydown', e => {
    if(!locked) return;
    if(e.key === 'Escape'){ lockOff(); return; }
    e.preventDefault(); e.stopPropagation();
  }, true);
})();
'''


def patch(path):
    h = open(path, encoding='utf-8').read()
    if 'id="lockVeil"' in h:
        print(f'skip (이미 적용) {path}')
        return
    h = rep(h, '.tab.home:hover{color:var(--brand)}\n', '.tab.home:hover{color:var(--brand)}\n' + CSS)
    h = rep(h, '<symbol id="i-home"', ICON + '<symbol id="i-home"')

    # 탭 줄 끝(노래방 탭 뒤)에 자물쇠 버튼
    end = h.index('</div>', h.index('<div class="tabs">'))
    h = h[:end] + BTN + '   ' + h[end:]

    # 막은 마지막 <script> 바로 앞에 — 스크립트가 돌 때 이미 DOM 에 있어야 핸들러가 붙는다
    i = h.rindex('<script>')
    h = h[:i] + VEIL + h[i:]

    # 스크립트 맨 끝에 동작
    i = h.rindex('</script>')
    h = h[:i] + JS + h[i:]

    open(path, 'w', encoding='utf-8').write(h)
    print(f'ok   {path}')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        patch(p)
