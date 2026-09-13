"""뜻 영역의 한자 풀이(단어)·표현 풀이 각 줄에 읽어주기 버튼 + 「전부」(문장 → 표현 → 단어 순서로 이어 읽기).
patch_tts.py 뒤에 적용. 사용: python3 patch_tts2.py <tpl.html>"""
import sys
path = sys.argv[1]; h = open(path, encoding='utf-8').read(); N = 0
def rep(old, new):
    global h, N
    assert h.count(old) == 1, f'[{N}] {h.count(old)} matches: {old[:60]!r}'
    h = h.replace(old, new); N += 1
rep('''       <button class="btn btn-sm" id="ttsRep" title="3번 반복">3회</button>''', '''       <button class="btn btn-sm" id="ttsRep" title="3번 반복">3회</button>
       <button class="btn btn-sm" id="ttsAll" title="문장 → 표현 → 단어 순서로 전부 읽기">전부</button>''')
rep('''.ttsrow .btn[aria-pressed=true]{background:var(--brand-soft);border-color:var(--brand-line);color:var(--brand)}''',
    '''.ttsrow .btn[aria-pressed=true]{background:var(--brand-soft);border-color:var(--brand-line);color:var(--brand)}
.tts-mini{display:inline-grid;place-items:center;width:24px;height:24px;padding:0;margin-left:6px;border-radius:50%;border:1px solid var(--line-2);background:var(--surface);color:var(--ink-2);vertical-align:middle;flex:none}
.tts-mini .ic{width:13px;height:13px}
.tts-mini:hover,.tts-mini[aria-pressed=true]{background:var(--brand-soft);border-color:var(--brand-line);color:var(--brand)}
.kjrow .w{white-space:normal}''')
# 한자 풀이 줄: 표제어 옆에 버튼
rep('''    const w = document.createElement('div'); w.className = 'w'; w.lang = 'ja'; w.textContent = head;
    const r = document.createElement('small'); r.textContent = rd; w.appendChild(r);''',
    '''    const w = document.createElement('div'); w.className = 'w'; w.lang = 'ja'; w.textContent = head;
    w.appendChild(ttsBtn(rd || head));   /* 읽어주기는 훈독(사전 읽기)으로 */
    const r = document.createElement('small'); r.textContent = rd; w.appendChild(r);''')
# 표현 풀이 줄: 표현 옆에 버튼
rep('''    const b = document.createElement('b'); b.lang = 'ja'; b.textContent = r.ja;
    row.appendChild(b);''', '''    const b = document.createElement('b'); b.lang = 'ja'; b.textContent = r.ja;
    row.appendChild(b); row.appendChild(ttsBtn(r.ja));''')
rep('''$('ttsPlay').onclick = () => ttsLine(1, 1);''', '''/* 단어·표현 옆의 작은 읽어주기 버튼 */
function ttsBtn(text){
  const b = document.createElement('button'); b.type = 'button'; b.className = 'tts-mini'; b.title = '읽어주기 / 読み上げ';
  b.innerHTML = '<svg class="ic"><use href="#i-sound"/></svg>';
  b.onclick = e => { e.stopPropagation(); ttsMark(b); ttsPause(); aPlay(text, 1, 0, () => b.setAttribute('aria-pressed', 'false'), 2, 1); };
  return b;
}
function ttsPause(){ if(!OFFLINE && player && ready){ try{ if(player.getPlayerState() === 1) player.pauseVideo(); }catch(e){} } }
function ttsMark(el){ document.querySelectorAll('.tts-mini[aria-pressed=true],.ttsrow .btn[aria-pressed=true]').forEach(x => x.setAttribute('aria-pressed', 'false')); if(el) el.setAttribute('aria-pressed', 'true'); }
/* 전부: 문장 → 이 문장의 표현 → 한자 풀이 단어 순서로 이어 읽는다 */
let ttsGen = 0;
function ttsAll(){
  const d = deck[index]; if(!d) return;
  const v = edited(d), list = [[v.ja, $('ttsAll')]];
  document.querySelectorAll('#explList .tts-mini').forEach(b => list.push([b.dataset.t, b]));
  document.querySelectorAll('#kanjiList .tts-mini').forEach(b => list.push([b.dataset.t, b]));
  ttsPause(); const my = ++ttsGen;
  const step = i => {
    if(my !== ttsGen || i >= list.length){ ttsMark(null); return; }
    ttsMark(list[i][1]); if(i === 0) $('ttsAll').setAttribute('aria-pressed', 'true');
    aPlay(list[i][0], 1, 0, () => setTimeout(() => step(i + 1), 380), 2, 1);
  };
  step(0);
}
$('ttsAll').onclick = ttsAll;
$('ttsPlay').onclick = () => ttsLine(1, 1);''')
rep('''  b.innerHTML = '<svg class="ic"><use href="#i-sound"/></svg>';
  b.onclick = e => { e.stopPropagation(); ttsMark(b);''', '''  b.innerHTML = '<svg class="ic"><use href="#i-sound"/></svg>'; b.dataset.t = text;
  b.onclick = e => { e.stopPropagation(); ttsGen++; ttsMark(b);''')
rep('''$('ttsStop').onclick = () => { aStopAll(); ['ttsPlay','ttsSlow','ttsRep'].forEach(id => $(id).setAttribute('aria-pressed', 'false')); };''',
    '''$('ttsStop').onclick = () => { ttsGen++; aStopAll(); ttsMark(null); };''')
rep('''  const btn = times > 1 ? $('ttsRep') : rate < 1 ? $('ttsSlow') : $('ttsPlay');
  ['ttsPlay','ttsSlow','ttsRep'].forEach(id => $(id).setAttribute('aria-pressed', 'false'));
  btn.setAttribute('aria-pressed', 'true');''', '''  const btn = times > 1 ? $('ttsRep') : rate < 1 ? $('ttsSlow') : $('ttsPlay');
  ttsGen++; ttsMark(btn);''')
open(path, 'w', encoding='utf-8').write(h); print('tts2-patched', path, N)
