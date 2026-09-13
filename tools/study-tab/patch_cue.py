"""재생·정지 키 + 디제이 큐(길게 누르면 누르는 동안만 재생, 떼면 구간 처음으로) — patch_foot.py 뒤에 적용.
사용: python3 patch_cue.py <tpl.html>"""
import sys
path = sys.argv[1]; h = open(path, encoding='utf-8').read(); N = 0
def rep(old, new):
    global h, N
    assert h.count(old) == 1, f'[{N}] {h.count(old)} matches: {old[:60]!r}'
    h = h.replace(old, new); N += 1
SONG = 'id="kfix"' in h

# 1. 카드 탭: 「이 장면 재생」 옆 정지, 모바일 하단 바에 정지
rep('''       <span class="lbl">이 장면 재생<span class="sub" lang="ja">この場面を再生</span></span></button>
      <button class="btn" id="loop">''', '''       <span class="lbl">이 장면 재생<span class="sub" lang="ja">この場面を再生</span></span></button>
      <button class="btn" id="stop" title="정지 / 停止 (S)"><svg class="ic fill"><use href="#i-stop"/></svg>
       <span class="lbl">정지<span class="sub" lang="ja">停止</span></span></button>
      <button class="btn" id="loop">''')
rep('''      <button class="btn btn-primary" id="cfPlay"><svg class="ic fill"><use href="#i-play"/></svg>재생</button>
      <button class="btn" id="cfNext">''', '''      <button class="btn btn-primary" id="cfPlay"><svg class="ic fill"><use href="#i-play"/></svg>재생</button>
      <button class="btn" id="cfStop"><svg class="ic fill"><use href="#i-stop"/></svg>정지</button>
      <button class="btn" id="cfNext">''')
rep('''<symbol id="i-home" viewBox="0 0 24 24">''', '''<symbol id="i-stop" viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="1.5"/></symbol>
<symbol id="i-home" viewBox="0 0 24 24">''')
rep(''' .cardfoot{display:grid;grid-template-columns:1fr 1.3fr 1fr;''', ''' .cardfoot{display:grid;grid-template-columns:1fr 1.3fr 1fr 1fr;''')
rep('''\n.cardfoot{display:none}\n''', '''\n.cardfoot{display:none}
.btn.holding{background:var(--accent);border-color:var(--accent);color:#fff}
.cue{touch-action:manipulation;user-select:none;-webkit-user-select:none;-webkit-touch-callout:none}''')

# 2. 재생 = 항상 구간 처음부터 / 길게 누르면 누르는 동안만 / 정지
rep('''$('play').onclick  = () => { const d = deck[index]; if(d) playSeg(d); };''', '''/* 디제이 큐 버튼: 탭 = 구간 처음부터 재생, 350ms 넘게 누르고 있으면 그동안만 재생하고 떼면 구간 처음으로 되돌려 멈춤 */
const HOLD_MS = 350;
function cueStop(seg){
  if(OFFLINE || !(player && ready)) return;
  stopAt = null; loopSeg = null; paintLoop();
  try{ player.pauseVideo(); player.seekTo(headOf(seg), true); }catch(e){}
  $('playStatus').innerHTML = bi('구간 처음(' + fmt(headOf(seg)) + ')에서 대기', '区間の頭(' + fmt(headOf(seg)) + ')で待機');
}
function stopAll(){
  if(OFFLINE || !(player && ready)) return;
  stopAt = null; loopSeg = null; paintLoop();
  if(typeof barAt !== 'undefined' && barAt != null){ barAt = null; if(typeof paintBars === 'function'){ paintBars(); paintBarLyrics(); } }
  try{ player.pauseVideo(); }catch(e){}
  $('playStatus').innerHTML = bi('정지', '停止');
}
function bindCue(btn, segFn){
  let timer = null, held = false, cur = null;
  btn.classList.add('cue');
  const down = e => {
    if(e.button != null && e.button !== 0) return;
    const r = segFn(); if(!r) return;
    cur = r; held = false;
    try{ btn.setPointerCapture(e.pointerId); }catch(x){}
    playSeg(r.seg, r.opts || {});
    timer = setTimeout(() => { held = true; btn.classList.add('holding'); }, HOLD_MS);
  };
  const up = () => {
    if(timer){ clearTimeout(timer); timer = null; }
    if(held && cur){ btn.classList.remove('holding'); cueStop(cur.seg); }
    held = false; cur = null;
  };
  btn.addEventListener('pointerdown', down);
  btn.addEventListener('pointerup', up); btn.addEventListener('pointercancel', up);
  btn.addEventListener('contextmenu', e => e.preventDefault());
  btn.onclick = e => { if(e.detail === 0){ const r = segFn(); if(r) playSeg(r.seg, r.opts || {}); } };   /* 키보드(Space·X)로 누른 경우 */
}
bindCue($('play'), () => { const d = deck[index]; return d ? {seg: d} : null; });
$('stop').onclick = stopAll;''')
rep('''$('cfPlay').onclick = () => $('play').click();''', '''bindCue($('cfPlay'), () => { const d = deck[index]; return d ? {seg: d} : null; });
$('cfStop').onclick = stopAll;''')
# 키: S = 정지
rep('''  else if(k === 'c'){ e.preventDefault(); $('loop').click(); }''', '''  else if(k === 'c'){ e.preventDefault(); $('loop').click(); }
  else if(k === 's'){ e.preventDefault(); stopAll(); }''')

# 3. 노래방(노래 앱): 재생 = 지금 줄(마디 반복 중이면 그 마디) 처음부터, 정지 키
if SONG:
    rep('''       <button class="btn btn-primary" id="knPlay"><svg class="ic fill"><use href="#i-play"/></svg>재생 · 정지</button>
       <button class="btn" id="knNext">''', '''       <button class="btn btn-primary" id="knPlay"><svg class="ic fill"><use href="#i-play"/></svg>재생</button>
       <button class="btn" id="knStop"><svg class="ic fill"><use href="#i-stop"/></svg>정지</button>
       <button class="btn" id="knNext">''')
    rep('''.kara .knav{grid-template-columns:auto 1fr 1.3fr 1fr}''', '''.kara .knav{grid-template-columns:auto 1fr 1.2fr .9fr 1fr;gap:6px}
.kara .knav .btn{font-size:12.5px;padding:8px 4px}''')
    rep('''$('knPlay').onclick = () => $('karaPause').click();''', '''/* 노래방 재생: 마디 반복 중이면 그 마디 처음부터, 아니면 지금 줄 처음부터 */
bindCue($('knPlay'), () => {
  if(BARS.length >= 2 && barAt != null){ const j = Math.min(barAt + barLen, BARS.length - 1); return {seg: {id: -1, s: BARS[barAt], e: BARS[j]}, opts: {loop: true, exact: true}}; }
  const i = karaAt(karaNow()); const d = DATA[i < 0 ? 0 : i]; return d ? {seg: d} : null;
});
$('knStop').onclick = stopAll;''')
open(path, 'w', encoding='utf-8').write(h); print('cue-patched', path, N)
