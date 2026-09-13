"""노래 앱 전용 패치 (P3). patch_study.py 를 먼저 적용한 tpl.html 에 덧씌운다.
 - 단락(절·후렴) = Day. 4단계: 들으며 읽기 → 마디 따라 부르기 → 가사 가리고 부르기 → 표현·단어
 - 마디 반복 패널을 노래방 뷰 하단으로 옮기고 한 줄로 압축(±1마디·±1박·이 줄의 마디는 「미세 조정」)
 - 노래방 줄을 탭하면 그 줄의 마디 반복, 가사 가리기 3단(뜻 끄기 › 읽기 끄기 › 첫 글자만)
 - 학습법 탭을 노래용으로 교체
사용: python3 patch_song.py <tpl.html> [노래 제목]
"""
import sys, re

path = sys.argv[1]
title = sys.argv[2] if len(sys.argv) > 2 else '노래 한 곡'
h = open(path, encoding='utf-8').read()
N = 0

def rep(old, new, count=1):
    global h, N
    c = h.count(old)
    assert c == count, f'[{N}] expected {count}, found {c}: {old[:70]!r}'
    h = h.replace(old, new)
    N += 1

# ── 1. 카드 뷰의 마디 반복 상자 제거 → 「노래방에서 마디 반복」 버튼
a = h.index('     <div class="bars" id="barBox" hidden>')
b = h.index('     <div class="edit" id="editBox" hidden>')
h = h[:a] + h[b:]; N += 1
rep('''       <span class="lbl">구간 반복<span class="sub" lang="ja">リピート</span></span></button>
      <button class="btn" id="check" aria-pressed="false">''', '''       <span class="lbl">구간 반복<span class="sub" lang="ja">リピート</span></span></button>
      <button class="btn" id="toKara" title="노래방 탭에서 이 줄의 마디를 반복"><svg class="ic"><use href="#i-sound"/></svg>
       <span class="lbl">마디 반복<span class="sub" lang="ja">小節リピート</span></span></button>
      <button class="btn" id="check" aria-pressed="false">''')

# ── 2. 노래방 뷰: 세션 바 · 가리기 단계 · 마디 바(한 줄) · 세션 하단 바
rep('''      <span class="meta" id="karaPos">—</span>
     </div>
     <div class="kara-prev" id="karaPrev"></div>''', '''      <span class="meta" id="karaPos">—</span>
     </div>
     <div class="sessbar" id="ksbar" hidden>
      <button class="btn btn-sm" id="ksQuit" title="학습 탭으로 / 学習タブへ"><svg class="ic"><use href="#i-x"/></svg></button>
      <b id="ksName">—</b>
      <div class="bar"><span id="ksBar" style="width:0"></span></div>
      <span class="meta" id="ksPos">0 / 0</span>
     </div>
     <div class="seg kmask" id="kmask" hidden>
      <button data-v="1" aria-pressed="true" title="意味なし">뜻 끄기</button><button data-v="2" aria-pressed="false" title="読みなし">읽기 끄기</button><button data-v="3" aria-pressed="false" title="頭文字だけ">첫 글자만</button>
     </div>
     <div class="kara-prev" id="karaPrev"></div>''')
rep('''     <div class="kara-bar"><span id="karaBar"></span></div>
    </div>''', '''     <div class="kara-bar"><span id="karaBar"></span></div>
     <div class="kfix" id="kfix">
      <div class="bars" id="barBox" hidden>
       <div class="bars-row">
        <span class="cap">길이</span>
        <div class="seg" id="barLen"><button data-v="1" aria-pressed="false">1</button><button data-v="2" aria-pressed="true">2</button><button data-v="4" aria-pressed="false">4</button><button data-v="8" aria-pressed="false">8</button></div>
        <span class="cap">속도</span>
        <div class="seg" id="rate"><button data-v="0.5">0.5</button><button data-v="0.75">0.75</button><button data-v="1" aria-pressed="true">1×</button></div>
        <button class="btn btn-sm" id="barPrev" title="이전 마디 / 前の小節">◀</button><button class="btn btn-sm" id="barNext" title="다음 마디 / 次の小節">▶</button>
        <button class="btn btn-sm" id="barStop" disabled title="반복 정지 / 停止">■</button>
        <button class="btn btn-sm" id="barFine" aria-pressed="false">미세 조정 ▾</button>
        <span class="meta" id="barInfo">—</span>
       </div>
       <div class="bars-row" id="barFineRow" hidden>
        <button class="btn btn-sm btn-primary" id="barLine"><svg class="ic"><use href="#i-repeat"/></svg><span class="lbl">이 줄의 마디<span class="sub" lang="ja">この行の小節</span></span></button>
        <button class="btn btn-sm" id="barLess" title="루프 1마디 줄이기">−1마디</button><button class="btn btn-sm" id="barMore" title="루프 1마디 늘이기">＋1마디</button>
        <span class="cap" style="margin-left:6px">마디 시작 · 小節の頭</span>
        <button class="btn btn-sm" id="barShiftM" title="마디 시작을 한 박 앞으로">−1박</button><button class="btn btn-sm" id="barShiftP" title="마디 시작을 한 박 뒤로">+1박</button>
       </div>
       <div class="barlyrics" id="barLyrics"></div>
      </div>
      <div class="sessfoot" id="ksfoot" hidden>
       <button class="btn" id="ksA">한 번 더</button>
       <button class="btn btn-primary" id="ksB">불렀다 · 다음 ›</button>
      </div>
     </div>
    </div>''')
rep('''    <div class="status">가사는 줄의 시작·끝 시각에 맞춰 왼쪽부터 채워집니다(줄 단위 등속). 줄을 누르면 그 줄부터 재생.
     <span class="sub" lang="ja">歌詞は行の開始・終了時刻に合わせて左から塗られます(行ごとに等速)。行をタップするとそこから再生。</span></div>''',
    '''    <div class="status">가사는 줄의 시작·끝 시각에 맞춰 왼쪽부터 채워집니다. 앞·뒤 줄을 누르면 그 줄부터 재생, <b>지금 줄을 누르면 그 줄의 마디를 반복</b>합니다.
     <span class="sub" lang="ja">歌詞は行の開始・終了時刻に合わせて左から塗られます。前後の行をタップするとそこから再生、<b>今の行をタップするとその小節をリピート</b>。</span></div>''')

rep('''     <div class="kara-top">
      <button class="btn btn-primary btn-sm" id="karaStart">''', '''     <div class="kara-top">
      <button class="btn btn-sm" id="karaBack" title="카드 탭으로 / カードへ"><svg class="ic"><use href="#i-left"/></svg><span class="lbl">카드로<span class="sub" lang="ja">カードへ</span></span></button>
      <button class="btn btn-primary btn-sm" id="karaStart">''')

# ── 3. CSS
rep('''.kara-bar span{display:block;height:100%;width:0;background:#ffd166}''', '''.kara-bar span{display:block;height:100%;width:0;background:#ffd166}
/* 노래방 안의 마디 바 · 세션 바 (어두운 배경용) */
.kara .kfix{display:flex;flex-direction:column;gap:8px;margin-top:10px}
.kara .bars{margin:0;padding:8px 10px;border:1px solid #2c3150;background:#1d2138;border-radius:10px}
.kara .bars .cap{color:#8d93b3;letter-spacing:.08em}
.kara .bars .meta{color:#8d93b3;margin-left:auto;font-size:11px}
.kara .bars .btn{background:#232838;border-color:#2f364a;color:#e9ecf5;min-height:30px;padding:4px 9px}
.kara .bars .btn-primary{background:#4b5aa0;border-color:#4b5aa0;color:#fff}
.kara .bars .btn:disabled{opacity:.35}
.kara .seg{background:#14171f;padding:2px}
.kara .seg button{color:#aab0c8;padding:5px 9px;font-size:12px;font-variant-numeric:tabular-nums}
.kara .seg button[aria-pressed=true]{background:#4b5aa0;color:#fff;box-shadow:none}
.kara .barlyrics{display:none}
.kara .sessbar{background:#232838;border-color:#3a4260;color:#e9ecf5;margin-bottom:6px}
.kara .sessbar .btn{background:#14171f;border-color:#2f364a;color:#e9ecf5}
.kara .sessbar .bar{background:#14171f}.kara .sessbar .bar span{background:#ffd166}
.kara .sessbar .meta{color:#aab0c8}
.kara .kmask{align-self:flex-start;margin-bottom:4px}
.kara .sessfoot{margin-top:0}
.kara .sessfoot .btn{background:#232838;border-color:#2f364a;color:#e9ecf5}
.kara .sessfoot .btn-primary{background:#4b5aa0;border-color:#4b5aa0;color:#fff}
.kara-line{cursor:pointer}
@media(max-width:600px){
 #karaView .kfix{position:fixed;left:0;right:0;bottom:0;z-index:7;background:#14171f;border-top:1px solid #2c3150;padding:8px 10px calc(8px + env(safe-area-inset-bottom));margin:0;gap:6px}
 #karaView .kara{padding-bottom:150px}
 .kara .bars .meta{flex:1 1 100%;margin-left:0}
 .kara .kmask{align-self:stretch}.kara .kmask button{flex:1;padding:6px 4px;font-size:11px}
}''')

# ── 4. 학습법: 노래용
a = h.index('       <div class="gintro">')
b = h.index('       <div class="gsteps" id="gsteps"></div>')
h = h[:a] + '''       <div class="gintro">
        <p class="eyebrow">How to study</p>
        <h3>노래 한 곡을 「부를 수 있는 일본어」로 바꾸는 4단계</h3>
        <p lang="ja">歌1曲を「歌える日本語」に変える4ステップ</p>
        <p class="gnote">이 교재는 교과서가 아니라 <b>노래 가사</b>입니다. 멜로디에 실린 말은 문장보다 오래 남습니다.
         그래서 「읽어서 이해」로 끝내지 말고 <b>따라 부를 수 있을 때까지</b> 가는 것이 목표입니다. 「오늘」 탭이 절·후렴 단위로 4단계를 안내합니다.
         <span lang="ja">この教材は教科書ではなく<b>歌詞</b>です。メロディーに乗った言葉は文より長く残ります。
          だから「読んで分かる」で終わらせず、<b>歌えるようになるまで</b>が目標です。「今日」タブが1番・サビの単位で4ステップを案内します。</span></p>
       </div>
''' + h[b:]; N += 1
a = h.index('       <div class="gtips">')
b = h.index('     <div id="listPane" hidden>')
h = h[:a] + '''       <div class="gtips">
        <div class="gtip"><h5>한 단락씩 · 1番ずつ</h5>
         <p>한 곡을 한 번에 외우려 하지 마세요. 「오늘」 탭이 <b>절·후렴 단위</b>로 잘라 줍니다. 후렴부터 시작해도 좋습니다.
          <span lang="ja">1曲を一度に覚えようとしないで。「今日」タブが<b>1番・サビの単位</b>に切ってくれます。サビから始めても構いません。</span></p></div>
        <div class="gtip"><h5>마디로 쪼개기 · 小節で刻む</h5>
         <p>노래방 탭에서 <b>지금 줄을 누르면 그 줄의 마디만 반복</b>됩니다. 2마디 → 4마디 → 8마디로 늘리고, 속도는 0.75× 에서 1× 로 올리세요.
          <span lang="ja">カラオケタブで<b>今の行をタップするとその小節だけリピート</b>。2 → 4 → 8小節と伸ばし、速さは 0.75× から 1× へ。</span></p></div>
        <div class="gtip"><h5>소리 내어 겹치기 · 声を重ねる</h5>
         <p>듣기만 하면 늘지 않습니다. 반복되는 동안 <b>원곡 위에 목소리를 겹쳐</b> 부르세요. 음정보다 <b>박자와 발음</b>이 먼저입니다.
          <span lang="ja">聞くだけでは伸びません。リピート中に<b>原曲に声を重ねて</b>歌ってください。音程より<b>リズムと発音</b>が先です。</span></p></div>
        <div class="gtip"><h5>가사를 가리기 · 歌詞を隠す</h5>
         <p>3단계는 <b>뜻 끄기 → 읽기 끄기 → 첫 글자만</b> 순으로 가립니다. 막히는 줄은 「한 번 더」로 되돌리고, 막힘 없이 부를 수 있으면 「불렀다」.
          <span lang="ja">3ステップ目は<b>意味なし → 読みなし → 頭文字だけ</b>の順に隠します。詰まる行は「もう一度」、詰まらず歌えたら「歌えた」。</span></p></div>
        <div class="gtip"><h5>표현은 노래 밖으로 · 表現は歌の外へ</h5>
         <p>가사의 표현·단어는 드릴로 따로 외웁니다. 노래에서 익힌 말은 <b>회화에서도 그대로</b> 씁니다(〜がした · 〜ても · いつか).
          <span lang="ja">歌詞の表現・単語はドリルで別に覚えます。歌で覚えた言葉は<b>会話でもそのまま</b>使えます。</span></p></div>
        <div class="gtip"><h5>틀린 것이 보물 · 間違いは宝</h5>
         <p>드릴에서 「몰라」로 채점한 항목과 체크한 줄은 「복습」 탭에 모입니다. <b>다음 날 맨 처음</b>에 그것만 다시 부르세요.
          <span lang="ja">ドリルで「分からない」と採点した項目とチェックした行は「復習」タブに集まります。<b>翌日の最初</b>にそこだけ歌い直しましょう。</span></p></div>
       </div>
      </div>
     </div>

''' + h[b:]; N += 1
rep('''  const G = [
    ['듣기', '聞く', '읽기와 뜻을 가리고 재생. 먼저 귀로만 도전. 몰라도 괜찮다.',
     '読みと意味を隠して再生。まず耳だけで挑む。分からなくて当たり前。', '오늘 › 1'],
    ['확인', '確かめる', '읽기·뜻을 열어 답 맞추기. 표현·단어는 예문과 함께 외운다.',
     '読みと意味を開いて答え合わせ。表現・単語は例文とセットで覚える。', '오늘 › 2'],
    ['따라 하기', '真似る', '반복으로 같은 구간을 되풀이하며 소리 내어 겹친다. 억양째 따라 한다.',
     'リピートで同じ区間を繰り返し、声に出して重ねる。抑揚ごと写す。', '오늘 › 3'],
    ['점검', '試す', '퀴즈로 오늘 범위만 출제. 틀린 것은 다음 날 복습 목록이 된다.',
     'クイズで今日の範囲だけ出題。間違いは翌日の復習リストになる。', '오늘 › 4']
  ];''', '''  const G = [
    ['들으며 읽기', '聞いて読む', '읽기·뜻을 켜고 단락을 한 번 듣는다. 어디서 숨을 쉬는지, 어느 말이 길게 늘어나는지 본다.',
     '読みと意味を表示して1番を一度聞く。どこで息を継ぎ、どの言葉が伸びるかを見る。', '오늘 › 1'],
    ['마디 따라 부르기', '小節で歌う', '줄마다 마디 반복을 걸고 소리 내어 겹친다. 2 → 4 → 8마디, 0.75 → 1×.',
     '行ごとに小節リピートをかけて声を重ねる。2 → 4 → 8小節、0.75 → 1×。', '오늘 › 2'],
    ['가사 가리고 부르기', '歌詞を隠す', '뜻 끄기 → 읽기 끄기 → 첫 글자만. 막힘 없이 부를 수 있으면 「불렀다」.',
     '意味なし → 読みなし → 頭文字だけ。詰まらず歌えたら「歌えた」。', '오늘 › 3'],
    ['표현 · 단어', '表現・単語', '가사에서 뽑은 표현·단어를 드릴로. 틀린 것은 복습 탭으로 간다.',
     '歌詞から拾った表現・単語をドリルで。間違いは復習タブへ。', '오늘 › 4']
  ];''')

# ── 5. JS: 단락 = Day
rep('''function buildDays(){
  const chunks = [];
  for(let i = 0; i < DATA.length; i += dayPace) chunks.push(DATA.slice(i, i + dayPace));
  const pos = new Map(DATA.map((c, i) => [c.id, i]));
  const firstAt = r => Math.min(...(r.cids || []).map(id => pos.has(id) ? pos.get(id) : 1e9), 1e9);
  const deal = kind => {
    const items = STUDY.filter(r => r.t === kind).sort((a, b) => firstAt(a) - firstAt(b));
    const out = chunks.map(() => []);
    items.forEach((r, i) => out[Math.floor(i * chunks.length / items.length)].push(r));
    return out;
  };
  const E = deal('E'), V = deal('V');
  DAYS = chunks.map((cards, i) => ({ n: i + 1, cards, expr: E[i], word: V[i] }));
  if(dayCur > DAYS.length) dayCur = DAYS.length;
  $('dayTot').textContent = DAYS.length;
  $('nDay').textContent = dayCur + '/' + DAYS.length;
  $('paceInfo').textContent = DATA.length + '장을 ' + DAYS.length + '일에 · ' + DAYS.length + '日で完成';
}''', '''/* 노래는 날짜가 아니라 단락(절·후렴)으로 나눈다. 표현·단어는 첫 등장 줄이 속한 단락에 */
function buildDays(){
  const pos = new Map(DATA.map((c, i) => [c.id, i]));
  const firstAt = r => Math.min(...(r.cids || []).map(id => pos.has(id) ? pos.get(id) : 1e9), 1e9);
  DAYS = SCENES.map((s, i) => ({ n: i + 1, cards: DATA.filter(c => c.scene === s.key), expr: [], word: [], scene: s })).filter(d => d.cards.length);
  DAYS.forEach((d, i) => d.n = i + 1);
  ['E', 'V'].forEach(kind => STUDY.filter(r => r.t === kind).forEach(r => {
    const at = firstAt(r), c = at < 1e9 ? DATA[at] : null;
    const d = (c && DAYS.find(x => x.scene.key === c.scene)) || DAYS[0];
    (kind === 'E' ? d.expr : d.word).push(r);
  }));
  if(dayCur > DAYS.length) dayCur = DAYS.length;
  $('dayTot').textContent = DAYS.length;
  $('nDay').textContent = dayCur + '/' + DAYS.length;
  $('qPace').hidden = true;
  $('paceInfo').textContent = DATA.length + '줄 · ' + DAYS.length + '단락 · ' + DAYS.length + 'パート';
}''')

# ── 6. JS: 노래 4단계 + 노래방 세션
a = h.index('const STAGES = [')
b = h.index('function renderDay(){')
h = h[:a] + '''const STAGES = [
  ['들으며 읽기', '聞いて読む', d => d.cards.length + '줄 · 읽기·뜻 보며 한 번', d => Math.max(1, Math.round((d.cards[d.cards.length - 1].e - d.cards[0].s) / 60 + 0.5))],
  ['마디 따라 부르기', '小節で歌う', d => d.cards.length + '줄 · 줄마다 마디 반복 · 2 › 4 › 8마디', d => Math.max(2, d.cards.length)],
  ['가사 가리고 부르기', '歌詞を隠す', d => d.cards.length + '줄 · 뜻 끄기 › 읽기 끄기 › 첫 글자만', d => Math.max(2, d.cards.length)],
  ['표현 · 단어', '表現・単語', d => '표현 ' + d.expr.length + ' · 단어 ' + d.word.length + ' · 드릴', d => Math.max(1, Math.round((d.expr.length + d.word.length) * 0.7))]
];
function startStage(n){
  const d = DAYS[dayCur - 1]; if(!d) return;
  const s = stGet(d.n, n), resume = (s.total && s.done < s.total) ? s.done : 0;
  if(n <= 3){ karaSessStart(n, d, resume); return; }
  const cnt = openDrill('D', 'D', '4 표현 · 단어 · 表現・単語', 4);
  if(!cnt){ stSet(d.n, 4, 1, 1); setSub('D'); return; }
  dStart(false);
}
''' + h[b:]; N += 1

# 카드 뷰 세션(sessStart)은 노래에서 안 쓰지만 함수는 남겨 둔다. 노래방 세션을 추가
rep('''/* ---------- 기동 / 起動 ---------- */''', '''/* ====================== 노래방 세션: 1 들으며 읽기 · 2 마디 따라 부르기 · 3 가사 가리기 ====================== */
let ksess = null;                                  /* {stage, day, ids, i, level} */
function maskLine(s){
  return s.split(/(\\s+)/).map(tok => /^\\s+$/.test(tok) ? tok : (tok.length <= 1 ? tok : tok[0] + '＿'.repeat(Math.min(tok.length - 1, 4)))).join('');
}
const karaNow = () => (player && ready && typeof player.getCurrentTime === 'function') ? player.getCurrentTime() : 0;
function ksReset(){ barAt = null; stopAt = null; loopSeg = null; paintLoop(); paintBars(); paintBarLyrics(); }
function ksPlayFrom(c){ if(!(player && ready) || !c) return; ksReset(); player.seekTo(Math.max(0, c.s - 0.3), true); player.playVideo(); }
function karaSessStart(stage, d, from){
  const ids = d.cards.map(c => c.id);
  if(!ids.length){ stSet(d.n, stage, 1, 1); return; }
  ksess = {stage, day: d.n, ids, i: Math.min(from || 0, ids.length - 1), level: Number(store.get('maskLv', 1)) || 1};
  switchView('kara'); window.scrollTo({top: 0});
  if(stage === 1){ $('karaRdOpt').checked = true; $('karaJa').checked = true; karaLast = -2; karaSessPaint(); ksPlayFrom(cardOf(ids[ksess.i])); }
  else ksLine();
}
function ksLine(){
  const c = cardOf(ksess.ids[ksess.i]); if(!c) return;
  const k = deck.findIndex(x => x.id === c.id); if(k >= 0){ index = k; showCard(); }
  karaLast = -2; karaSessPaint();
  if(!(player && ready)) return;
  if(BARS.length >= 2) $('barLine').click(); else playSeg(c, {loop: true});
  karaPaint(c.s + 0.01);
}
function karaSessPaint(){
  const on = !!ksess;
  $('ksbar').hidden = !on; $('ksfoot').hidden = !on; $('kmask').hidden = !(on && ksess.stage === 3);
  if(!on) return;
  const n = ksess.ids.length, d = DAYS[ksess.day - 1];
  const names = ['1 들으며 읽기 · 聞いて読む', '2 마디 따라 부르기 · 小節で歌う', '3 가사 가리기 · 歌詞を隠す'];
  $('ksName').textContent = (d && d.scene ? d.scene.ko + ' · ' : '') + names[ksess.stage - 1];
  $('ksPos').textContent = (ksess.i + 1) + ' / ' + n;
  $('ksBar').style.width = Math.round(ksess.i / n * 100) + '%';
  $('ksA').textContent = ksess.stage === 1 ? '이 줄부터 다시 · この行から' : '한 번 더 · もう一度';
  $('ksB').textContent = (ksess.stage === 1 ? '읽었다' : '불렀다') + (ksess.i < n - 1 ? ' · 다음 ›' : ' · 끝내기 ✓');
  [...$('kmask').querySelectorAll('button')].forEach(b => b.setAttribute('aria-pressed', String(Number(b.dataset.v) === ksess.level)));
}
function ksNext(){
  if(!ksess) return;
  const n = ksess.ids.length;
  stSet(ksess.day, ksess.stage, Math.min(n, ksess.i + 1), n);
  if(ksess.i >= n - 1){ ksEnd(); return; }
  ksess.i++;
  if(ksess.stage === 1){
    karaSessPaint();
    const c = cardOf(ksess.ids[ksess.i]), t = karaNow();
    if(c && (t < c.s - 1 || t > c.e + 1)) ksPlayFrom(c);
  } else ksLine();
}
function ksEnd(){
  if(!ksess) return;
  ksReset(); if(player && ready){ try{ player.pauseVideo(); }catch(e){} }
  ksess = null; karaSessPaint(); karaLast = -2;
  switchView('study'); setSub('D');
}
$('ksQuit').onclick = () => ksEnd();
$('ksA').onclick = () => { if(!ksess) return; if(ksess.stage === 1) ksPlayFrom(cardOf(ksess.ids[ksess.i])); else ksLine(); };
$('ksB').onclick = () => ksNext();
segWire('kmask', v => { if(!ksess) return; ksess.level = Number(v); store.set('maskLv', ksess.level); karaLast = -2; karaPaint(karaNow()); karaSessPaint(); });
/* 노래방의 지금 줄을 누르면 그 줄의 마디 반복 */
$('karaLine').onclick = () => { if(BARS.length >= 2 && player && ready) $('barLine').click(); };
$('toKara').onclick = () => { switchView('kara'); window.scrollTo({top: 0}); try{ history.pushState({kara: 1}, ''); }catch(e){} if(BARS.length >= 2 && player && ready) $('barLine').click(); };
function karaBack(){ if(ksess) ksEnd(); else { if(barAt != null) $('barStop').click(); switchView('card'); window.scrollTo({top: 0}); } }
$('karaBack').onclick = karaBack;
window.addEventListener('popstate', () => { if(view === 'kara') karaBack(); });
$('barFine').onclick = () => { const o = $('barFineRow').hidden; $('barFineRow').hidden = !o; $('barFine').setAttribute('aria-pressed', String(o)); };
document.addEventListener('keydown', e => {
  const t = e.target;
  if(t && (t.tagName === 'INPUT' || t.tagName === 'SELECT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
  if(view !== 'kara' || e.metaKey || e.ctrlKey || e.altKey) return;
  if(e.key === 'Enter' && ksess){ e.preventDefault(); ksNext(); }
  else if(e.key === '['){ e.preventDefault(); $('barPrev').click(); }
  else if(e.key === ']'){ e.preventDefault(); $('barNext').click(); }
});

/* ---------- 기동 / 起動 ---------- */''')

# karaPaint: 가리기 + 1단계 자동 진행
rep('''function karaSet(el, d){
  if(!d){ el.textContent = ''; el.onclick = null; return; }
  el.textContent = edited(d).ja;''', '''function karaSet(el, d, mask){
  if(!d){ el.textContent = ''; el.onclick = null; return; }
  el.textContent = mask ? maskLine(edited(d).ja) : edited(d).ja;''')
rep('''  if(i !== karaLast){
    karaLast = i;
    karaSet($('karaPrev'), prv);
    if(cur){ const v = edited(cur); $('karaLine').textContent = v.ja; $('karaRd').textContent = $('karaRdOpt').checked && v.rd ? v.rd : ''; $('karaJaLine').textContent = $('karaJa').checked ? v.ko : ''; }
    else { $('karaLine').textContent = '♪'; $('karaRd').textContent = ''; $('karaJaLine').textContent = ''; }
    karaSet($('karaNext'), nxt); karaSet($('karaNext2'), nxt2);''', '''  if(ksess && ksess.stage === 1 && cur){
    const p = ksess.ids.indexOf(cur.id);
    if(p > ksess.i){ ksess.i = p; stSet(ksess.day, 1, p, ksess.ids.length); karaSessPaint(); }
    const last = cardOf(ksess.ids[ksess.ids.length - 1]);
    if(last && t > last.e + 0.3 && cur.id !== last.id){ stSet(ksess.day, 1, ksess.ids.length, ksess.ids.length); ksEnd(); return; }
  }
  const lv = (ksess && ksess.stage === 3) ? ksess.level : 0;
  if(i !== karaLast){
    karaLast = i;
    karaSet($('karaPrev'), prv);
    if(cur){ const v = edited(cur); $('karaLine').textContent = lv >= 3 ? maskLine(v.ja) : v.ja; $('karaRd').textContent = ($('karaRdOpt').checked && lv < 2 && v.rd) ? v.rd : ''; $('karaJaLine').textContent = ($('karaJa').checked && lv < 1) ? v.ko : ''; }
    else { $('karaLine').textContent = '♪'; $('karaRd').textContent = ''; $('karaJaLine').textContent = ''; }
    karaSet($('karaNext'), nxt, lv >= 3); karaSet($('karaNext2'), nxt2, lv >= 3);''')

rep('''<span class="dno">DAY <b id="dayNo">''', '''<span class="dno">PART <b id="dayNo">''')
open(path, 'w', encoding='utf-8').write(h)
print('song-patched', path, 'replacements:', N)
