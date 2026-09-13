"""모바일 카드 탭 하단 고정 바(이전·재생·다음). 노래 앱이면 노래방에도 이전 줄·재생·다음 줄 바.
patch_study.py 뒤에 적용. 사용: python3 patch_foot.py <tpl.html>"""
import sys
path = sys.argv[1]; h = open(path, encoding='utf-8').read(); N = 0
def rep(old, new):
    global h, N
    assert h.count(old) == 1, f'[{N}] {h.count(old)} matches: {old[:60]!r}'
    h = h.replace(old, new); N += 1

# 카드 뷰: nav 아래에 고정 바
rep('''     <div class="sessfoot" id="sessfoot" hidden>''', '''     <div class="cardfoot" id="cardfoot">
      <button class="btn" id="cfPrev"><svg class="ic"><use href="#i-left"/></svg>이전</button>
      <button class="btn btn-primary" id="cfPlay"><svg class="ic fill"><use href="#i-play"/></svg>재생</button>
      <button class="btn" id="cfNext">다음<svg class="ic"><use href="#i-right"/></svg></button>
     </div>
     <div class="sessfoot" id="sessfoot" hidden>''')
rep('''.minibar{display:none}
.daystrip{''', '''.minibar{display:none}
.cardfoot{display:none}
.daystrip{''')
rep(''' .card.sess .sessfoot{position:fixed;''', ''' .cardfoot{display:grid;grid-template-columns:1fr 1.3fr 1fr;gap:8px;position:fixed;left:0;right:0;bottom:0;z-index:7;background:var(--surface);border-top:1px solid var(--line);padding:10px 12px calc(10px + env(safe-area-inset-bottom))}
 .cardfoot .btn{min-height:46px;justify-content:center;flex:none}
 .card:not(.sess){padding-bottom:96px}
 .card:not(.sess) .nav{display:none}
 .card.sess .cardfoot{display:none}
 .card.sess .sessfoot{position:fixed;''')
rep('''  $('prev').disabled = index === 0;
  $('next').disabled = index === deck.length-1;''', '''  $('prev').disabled = index === 0;
  $('next').disabled = index === deck.length-1;
  $('cfPrev').disabled = index === 0; $('cfNext').disabled = index === deck.length-1;''')
rep('''$('reveal').onclick = () => setReveal(true);''', '''$('cfPrev').onclick = () => $('prev').click();
$('cfNext').onclick = () => $('next').click();
$('cfPlay').onclick = () => $('play').click();
$('reveal').onclick = () => setReveal(true);''')

# 노래방(노래 앱만): 세션이 아닐 때 이전 줄 · 재생/일시정지 · 다음 줄
if 'id="kfix"' in h:
    rep('''      <div class="sessfoot" id="ksfoot" hidden>''', '''      <div class="sessfoot knav" id="knav">
       <button class="btn knback" id="knBack" title="카드 탭으로"><svg class="ic"><use href="#i-left"/></svg></button>
       <button class="btn" id="knPrev"><svg class="ic"><use href="#i-left"/></svg>이전 줄</button>
       <button class="btn btn-primary" id="knPlay"><svg class="ic fill"><use href="#i-play"/></svg>재생 · 정지</button>
       <button class="btn" id="knNext">다음 줄<svg class="ic"><use href="#i-right"/></svg></button>
      </div>
      <div class="sessfoot" id="ksfoot" hidden>''')
    rep('''.kara .sessfoot{margin-top:0}''', '''.kara .sessfoot{margin-top:0}
.kara .knav{grid-template-columns:auto 1fr 1.3fr 1fr}
.kara .knav .knback{padding:0 10px}
.kara .knav .btn{min-height:42px;justify-content:center}''')
    rep('''  $('ksbar').hidden = !on; $('ksfoot').hidden = !on; $('kmask').hidden = !(on && ksess.stage === 3);''',
        '''  $('ksbar').hidden = !on; $('ksfoot').hidden = !on; $('knav').hidden = on; $('kmask').hidden = !(on && ksess.stage === 3);''')
    rep('''$('karaLine').onclick = () => {''', '''function karaStep(dir){
  if(!(player && ready)) return;
  const i = karaAt(karaNow()), j = Math.max(0, Math.min(DATA.length - 1, (i < 0 ? 0 : i) + dir));
  ksReset(); player.seekTo(Math.max(0, DATA[j].s - 0.3), true); player.playVideo(); karaLast = -2;
}
$('knPrev').onclick = () => karaStep(-1);
$('knNext').onclick = () => karaStep(1);
$('knPlay').onclick = () => $('karaPause').click();
$('knBack').onclick = karaBack;
$('karaLine').onclick = () => {''')
open(path, 'w', encoding='utf-8').write(h); print('foot-patched', path, N)
