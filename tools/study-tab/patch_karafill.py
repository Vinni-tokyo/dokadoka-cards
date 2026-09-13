"""노래방 채우기: 줄이 두 줄로 꺾여도 글자 순서대로 채운다(글자별 span). patch_layout3.py 뒤에 적용(노래 앱)."""
import sys
path = sys.argv[1]; h = open(path, encoding='utf-8').read(); N = 0
def rep(old, new):
    global h, N
    assert h.count(old) == 1, f'[{N}] {h.count(old)} matches: {old[:60]!r}'
    h = h.replace(old, new); N += 1
rep(''' color:#b8bfd2;background-image:linear-gradient(90deg,#ffd166 0,#ffd166 var(--p,0%),#b8bfd2 var(--p,0%),#b8bfd2 100%);
 -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}''',
    ''' color:#b8bfd2}
.kara-line .kc{color:#b8bfd2}
.kara-line .kc.on{color:#ffd166}
.kara-line .kc.part{background-image:linear-gradient(90deg,#ffd166 0,#ffd166 var(--q,0%),#b8bfd2 var(--q,0%),#b8bfd2 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}''')
rep('''    if(cur){ const v = edited(cur); $('karaLine').textContent = lv >= 3 ? maskLine(v.ja) : v.ja;''',
    '''    if(cur){ const v = edited(cur); setKaraLine(lv >= 3 ? maskLine(v.ja) : v.ja);''')
rep('''    else { $('karaLine').textContent = '♪';''', '''    else { setKaraLine('♪');''')
rep('''  $('karaLine').style.setProperty('--p', (p * 100).toFixed(1) + '%');''', '''  paintKaraFill(p);''')
rep('''function karaPaint(t){''', '''/* 글자별 span 으로 채운다: 줄이 화면에서 두 줄로 꺾여도 앞 글자부터 순서대로 물든다 */
let karaChars = [], karaFillLast = -1;
function setKaraLine(text){
  const el = $('karaLine'); el.textContent = ''; karaChars = []; karaFillLast = -1;
  [...text].forEach(ch => { const s = document.createElement('span'); s.className = 'kc'; s.textContent = ch; el.appendChild(s); karaChars.push(s); });
}
function paintKaraFill(p){
  const n = karaChars.length; if(!n) return;
  const f = Math.max(0, Math.min(1, p)) * n, k = Math.floor(f), frac = f - k;
  const key = k * 100 + Math.round(frac * 10);
  if(key === karaFillLast) return; karaFillLast = key;
  karaChars.forEach((s, i) => {
    if(i < k){ s.className = 'kc on'; s.style.removeProperty('--q'); }
    else if(i === k && frac > 0.05 && k < n){ s.className = 'kc part'; s.style.setProperty('--q', (frac * 100).toFixed(0) + '%'); }
    else { s.className = 'kc'; s.style.removeProperty('--q'); }
  });
}
function karaPaint(t){''')
open(path, 'w', encoding='utf-8').write(h); print('karafill-patched', path, N)
