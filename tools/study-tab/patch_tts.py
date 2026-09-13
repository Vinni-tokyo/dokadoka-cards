"""뜻 영역에 「읽어주기」(TTS) — 로컬 음원(src/audio, make_study_audio.py --cards)이 있으면 그것을, 없으면 브라우저 음성.
patch_cue.py 뒤에 적용. 사용: python3 patch_tts.py <tpl.html>"""
import sys
path = sys.argv[1]; h = open(path, encoding='utf-8').read(); N = 0
def rep(old, new):
    global h, N
    assert h.count(old) == 1, f'[{N}] {h.count(old)} matches: {old[:60]!r}'
    h = h.replace(old, new); N += 1
rep('''      <p class="ko" id="ko"></p>''', '''      <div class="ttsrow">
       <button class="btn btn-sm" id="ttsPlay" title="원문을 읽어 줍니다 (T)"><svg class="ic"><use href="#i-sound"/></svg>읽어주기</button>
       <button class="btn btn-sm" id="ttsSlow" title="0.75배 속도">천천히</button>
       <button class="btn btn-sm" id="ttsRep" title="3번 반복">3회</button>
       <button class="btn btn-sm" id="ttsStop" title="읽기 멈춤"><svg class="ic fill"><use href="#i-stop"/></svg></button>
      </div>
      <p class="ko" id="ko"></p>''')
rep('''.btn.holding{background:var(--accent);border-color:var(--accent);color:#fff}''', '''.btn.holding{background:var(--accent);border-color:var(--accent);color:#fff}
.ttsrow{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:0 0 10px}
.ttsrow .cap{font-size:10.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin-right:2px}
.ttsrow .btn[aria-pressed=true]{background:var(--brand-soft);border-color:var(--brand-line);color:var(--brand)}''')
# 재생 속도를 받도록
rep('''function aPlay(text, times, gap, cb, which){
  aStopAll(); const my = aSeq; times = Math.max(1, times || 1); gap = gap == null ? 350 : gap; which = which || 2;''',
    '''function aPlay(text, times, gap, cb, which, rate){
  aStopAll(); const my = aSeq; times = Math.max(1, times || 1); gap = gap == null ? 350 : gap; which = which || 2;''')
rep('''    if(src){ const a = new Audio(src); aCur = a; a.onended = after; a.onerror = after; a.play().catch(after); }
    else dSpeakText(text, which, after);''', '''    if(src){ const a = new Audio(src); aCur = a; a.playbackRate = rate || 1; a.onended = after; a.onerror = after; a.play().catch(after); }
    else dSpeakText(text, which, after, rate);''')
rep('''function dSpeakText(text, which, cb){''', '''function dSpeakText(text, which, cb, rate){''')
rep('''  u.rate = Number($('dRate').value) || 1;''', '''  u.rate = rate || Number($('dRate').value) || 1;''')
rep('''$('stop').onclick = stopAll;''', '''$('stop').onclick = stopAll;
/* 뜻 영역의 읽어주기: 카드 원문을 로컬 음원(있으면) 또는 브라우저 음성으로. 영상은 잠시 멈춘다 */
function ttsLine(times, rate){
  const d = deck[index]; if(!d) return;
  if(!OFFLINE && player && ready){ try{ if(player.getPlayerState() === 1) player.pauseVideo(); }catch(e){} }
  const btn = times > 1 ? $('ttsRep') : rate < 1 ? $('ttsSlow') : $('ttsPlay');
  ['ttsPlay','ttsSlow','ttsRep'].forEach(id => $(id).setAttribute('aria-pressed', 'false'));
  btn.setAttribute('aria-pressed', 'true');
  aPlay(edited(d).ja, times, 500, () => btn.setAttribute('aria-pressed', 'false'), 2, rate);
}
$('ttsPlay').onclick = () => ttsLine(1, 1);
$('ttsSlow').onclick = () => ttsLine(1, 0.75);
$('ttsRep').onclick  = () => ttsLine(3, 1);
$('ttsStop').onclick = () => { aStopAll(); ['ttsPlay','ttsSlow','ttsRep'].forEach(id => $(id).setAttribute('aria-pressed', 'false')); };''')
rep('''  try{ player.pauseVideo(); }catch(e){}
  $('playStatus').innerHTML = bi('정지', '停止');''', '''  try{ player.pauseVideo(); }catch(e){}
  aStopAll();
  $('playStatus').innerHTML = bi('정지', '停止');''')
rep('''  else if(k === 's'){ e.preventDefault(); stopAll(); }''', '''  else if(k === 's'){ e.preventDefault(); stopAll(); }
  else if(k === 't'){ e.preventDefault(); if(!$('answer').hidden) ttsLine(1, 1); }''')
open(path, 'w', encoding='utf-8').write(h); print('tts-patched', path, N)
