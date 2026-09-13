"""학습 탭 개편 패치 (P1+P2): 하위 탭 4개 · 오늘 홈 4단계 스테퍼 · 세션 모드 · 복습 탭 · 드릴 하단 고정 채점 · 모바일 미니 플레이어.
사용: python3 patch_study.py <tpl.html>   (각 치환은 정확히 1회 일치해야 한다)
"""
import sys, re

path = sys.argv[1]
h = open(path, encoding='utf-8').read()
orig = h
N = 0

def rep(old, new, count=1):
    global h, N
    c = h.count(old)
    assert c == count, f'[{N}] expected {count}, found {c}: {old[:70]!r}'
    h = h.replace(old, new)
    N += 1

# ───────────────────────── 1. 마크업 ─────────────────────────
# 1a. 하위 탭 6 → 4
rep('''      <button class="tab" id="sbDrill" aria-pressed="true"><span class="lbl">드릴<span class="sub" lang="ja">ドリル</span></span><b id="nDrill">—</b></button>
      <button class="tab" id="sbDay" aria-pressed="false"><span class="lbl">오늘<span class="sub" lang="ja">今日</span></span><b id="nDay">—</b></button>
      <button class="tab" id="sbExpr" aria-pressed="false"><span class="lbl">표현<span class="sub" lang="ja">表現</span></span><b id="nExpr">0</b></button>
      <button class="tab" id="sbWord" aria-pressed="false"><span class="lbl">단어<span class="sub" lang="ja">単語</span></span><b id="nWord">0</b></button>
      <button class="tab" id="sbQuiz" aria-pressed="false"><span class="lbl">퀴즈<span class="sub" lang="ja">クイズ</span></span></button>
''', '''      <button class="tab" id="sbDay" aria-pressed="true"><span class="lbl">오늘<span class="sub" lang="ja">今日</span></span><b id="nDay">—</b></button>
      <button class="tab" id="sbReview" aria-pressed="false"><span class="lbl">복습<span class="sub" lang="ja">復習</span></span><b id="nReview">0</b></button>
      <button class="tab" id="sbList" aria-pressed="false"><span class="lbl">목록<span class="sub" lang="ja">一覧</span></span><b id="nList">0</b></button>
''')

# 1b. 드릴 패널: 상단 바 + 설정 접기 + 채점 하단 바(dfoot)
rep('''     <div id="drillPane">
      <div class="dsetup" id="dsetup">
       <div class="qrow">
        <span class="cap">범위</span>
        <div class="seg" id="dScope">
         <button data-v="E" aria-pressed="true">표현</button>
         <button data-v="V" aria-pressed="false">단어</button>
         <button data-v="A" aria-pressed="false">전부</button>
         <button data-v="D" aria-pressed="false">오늘 분량</button>
        </div>''', '''     <div id="drillPane" hidden>
      <div class="dbar">
       <button class="btn btn-sm" id="dBackBtn"><svg class="ic"><use href="#i-left"/></svg>돌아가기</button>
       <span class="t" id="dTitle">드릴</span>
       <button class="btn btn-sm" id="dSetBtn" aria-pressed="false">설정 ⚙</button>
      </div>
      <div class="dsetup" id="dsetup" hidden>
       <div class="qrow">
        <span class="cap">범위</span>
        <div class="seg" id="dScope">
         <button data-v="E" aria-pressed="true">표현</button>
         <button data-v="V" aria-pressed="false">단어</button>
         <button data-v="A" aria-pressed="false">전부</button>
         <button data-v="D" aria-pressed="false">오늘 분량</button>
         <button data-v="W" aria-pressed="false">복습</button>
        </div>''')
rep('''       <div class="dbtns">
        <button class="btn btn-primary" id="dReveal">''', '''       <div class="dfoot">
       <div class="dbtns">
        <button class="btn btn-primary" id="dReveal">''')
rep('''        <button class="btn g3" id="dG3">알아<small>3</small></button>
       </div>
       <div class="dhint">''', '''        <button class="btn g3" id="dG3">알아<small>3</small></button>
       </div>
       </div>
       <div class="dhint">''')
rep('''        <button class="btn btn-primary" id="dRestartMiss">틀린 것만 다시</button>
        <button class="btn" id="dRestartAll">처음부터</button>
       </div>''', '''        <button class="btn btn-primary" id="dRestartMiss">틀린 것만 다시</button>
        <button class="btn" id="dRestartAll">처음부터</button>
        <button class="btn" id="dDoneBack">돌아가기</button>
       </div>''')

# 1c. 오늘 홈: 흐름 띠·버튼 → 4단계 스테퍼, Day 이전/다음 화살표, 진행 바, 배지
rep('''     <div id="dayPane" hidden>
      <div class="dayctl">''', '''     <div id="dayPane">
      <div class="dayctl">''')
rep('''      <div class="dayhead">
       <div class="dayttl">
        <span class="dno">DAY <b id="dayNo">1</b><i>/<span id="dayTot">8</span></i></span>
        <h3 id="dayTitle">—</h3>
        <p class="daymeta" id="dayMeta">—</p>
       </div>
       <button class="btn btn-sm" id="dayDone"><svg class="ic"><use href="#i-check"/></svg>
        <span class="lbl">완료<span class="sub" lang="ja">完了</span></span></button>
      </div>

      <div class="flow">
       <div class="flowsteps" id="steps"></div>
       <div class="flowacts">
        <button class="btn btn-primary btn-sm" id="dayCards"><svg class="ic fill"><use href="#i-play"/></svg>카드로 · カードで学ぶ</button>
        <button class="btn btn-sm" id="dayQuiz"><svg class="ic"><use href="#i-check"/></svg>오늘 퀴즈 · 今日の分で出題</button>
       </div>
      </div>
''', '''      <div class="dayhead">
       <button class="btn btn-sm dayarr" id="dayPrev" title="이전 Day"><svg class="ic"><use href="#i-left"/></svg></button>
       <div class="dayttl">
        <span class="dno">DAY <b id="dayNo">1</b><i>/<span id="dayTot">8</span></i></span>
        <h3 id="dayTitle">—</h3>
        <p class="daymeta" id="dayMeta">—</p>
        <div class="daybar"><i id="dayBar" style="width:0"></i></div>
       </div>
       <button class="btn btn-sm dayarr" id="dayNext" title="다음 Day"><svg class="ic"><use href="#i-right"/></svg></button>
       <button class="btn btn-sm" id="dayDone" title="이 Day 를 끝낸 것으로 표시 / 手動で完了"><svg class="ic"><use href="#i-check"/></svg>
        <span class="lbl">완료<span class="sub" lang="ja">完了</span></span></button>
      </div>
      <div class="badges" id="dayBadges"></div>
      <div class="stages" id="stages"></div>
''')

# 1d. 복습 패널 (guidePane 앞에)
rep('''     <div id="guidePane" hidden>''', '''     <div id="reviewPane" hidden>
      <div class="rvhead">
       <span class="meta" id="rvInfo">—</span>
       <button class="btn btn-primary btn-sm" id="rvDrill"><svg class="ic fill"><use href="#i-play"/></svg><span class="lbl">복습 시작<span class="sub" lang="ja">復習を始める</span></span></button>
       <button class="btn btn-sm" id="rvListen"><svg class="ic"><use href="#i-sound"/></svg>듣기만 · 聞くだけ</button>
      </div>
      <div class="slist" id="rvList"></div>
     </div>

     <div id="guidePane" hidden>''')

# 1e. 목록 패널: 표현/단어/전부 토글 + 드릴·퀴즈 버튼
rep('''       <span class="meta" id="sCount">0</span>
       <label class="dauto"><input type="checkbox" id="lWithMean" checked><span>뜻과 함께</span></label>''',
    '''       <span class="meta" id="sCount">0</span>
       <div class="seg" id="lKind"><button data-v="A" aria-pressed="true">전부</button><button data-v="E" aria-pressed="false">표현</button><button data-v="V" aria-pressed="false">단어</button></div>
       <button class="btn btn-sm btn-primary" id="lDrill"><svg class="ic fill"><use href="#i-play"/></svg>드릴</button>
       <button class="btn btn-sm" id="lQuiz"><svg class="ic"><use href="#i-check"/></svg>퀴즈</button>
       <label class="dauto"><input type="checkbox" id="lWithMean" checked><span>뜻과 함께</span></label>''')

# 1f. 퀴즈 패널: 상단 바 + 설정 접기
rep('''     <div id="quizPane" hidden>
      <div class="qsetup" id="qsetup">''', '''     <div id="quizPane" hidden>
      <div class="dbar">
       <button class="btn btn-sm" id="qBackBtn"><svg class="ic"><use href="#i-left"/></svg>돌아가기</button>
       <span class="t" id="qTitle">퀴즈</span>
       <button class="btn btn-sm" id="qSetBtn" aria-pressed="false">설정 ⚙</button>
      </div>
      <div class="qsetup" id="qsetup" hidden>''')

# 1g. 카드 뷰: 세션 바(상단) + 세션 하단 바
rep('''   <div id="cardView">
    <div class="card">
     <div class="card-top">''', '''   <div id="cardView">
    <div class="card">
     <div class="sessbar" id="sessbar" hidden>
      <button class="btn btn-sm" id="sessQuit" title="학습 탭으로 / 学習タブへ"><svg class="ic"><use href="#i-x"/></svg></button>
      <b id="sessName">1 듣기</b>
      <div class="bar"><span id="sessBar" style="width:0"></span></div>
      <span class="meta" id="sessPos">0 / 0</span>
     </div>
     <div class="card-top">''')
rep('''     <div class="opts">
      <label><input type="checkbox" id="optAuto">''', '''     <div class="sessfoot" id="sessfoot" hidden>
      <button class="btn" id="sessA"><svg class="ic"><use href="#i-eye"/></svg>뜻 보기</button>
      <button class="btn btn-primary" id="sessB">들었다 · 다음 ›</button>
     </div>

     <div class="opts">
      <label><input type="checkbox" id="optAuto">''')

# 1h. 플레이어 박스: 모바일 미니 바
rep('''   <div class="player-box">
    <div class="ratio" id="ratio"><div id="player"></div></div>''', '''   <div class="player-box">
    <div class="minibar" id="minibar" hidden>
     <button class="pl" id="mbToggle" title="재생 / 일시정지">▶</button>
     <button class="t" id="mbOpen" title="영상 펼치기(카드 탭)"><b id="mbTitle">영상</b><span id="mbSub">탭하면 영상을 펼칩니다 · 学習中は小さく</span></button>
     <span class="meta" id="mbTime">0:00</span>
    </div>
    <div class="ratio" id="ratio"><div id="player"></div></div>''')

# ───────────────────────── 2. CSS ─────────────────────────
rep('''.srow[aria-current=true]{background:var(--brand-soft);box-shadow:inset 3px 0 0 var(--brand)}
</style>''', '''.srow[aria-current=true]{background:var(--brand-soft);box-shadow:inset 3px 0 0 var(--brand)}

/* ---- 학습 탭 개편: 4단계 스테퍼 · 복습 · 세션 · 미니 플레이어 · 하단 고정 바 ---- */
.dayhead{align-items:center}
.dayhead .dayttl{flex:1}
.dayarr{padding:6px 8px;min-height:34px}
.daybar{height:5px;background:var(--surface-3);border-radius:3px;overflow:hidden;margin-top:9px;max-width:420px}
.daybar i{display:block;height:100%;background:var(--brand);border-radius:3px}
.badges{display:flex;gap:6px;flex-wrap:wrap;padding:0 18px 10px}
.bdg{font-size:11px;padding:3px 9px;border-radius:999px;background:var(--surface-2);border:1px solid var(--line);color:var(--ink-2);white-space:nowrap}
.bdg.ok{background:#e4f2ea;color:#2f7d5b;border-color:transparent}
.bdg.acc{background:var(--accent-soft);color:var(--accent);border-color:transparent}
.stages{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:10px 18px 14px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:var(--surface-2)}
.stg{display:grid;grid-template-columns:30px minmax(0,1fr) auto;gap:10px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:10px 12px;text-align:left}
.stg .no{width:26px;height:26px;border-radius:50%;border:1.5px solid var(--line-2);display:grid;place-items:center;font-size:12px;font-weight:700;color:var(--ink-3)}
.stg.done .no{background:#2f7d5b;border-color:#2f7d5b;color:#fff}
.stg.now .no{background:var(--brand);border-color:var(--brand);color:#fff}
.stg.now{border-color:var(--brand-line);box-shadow:0 0 0 3px var(--brand-soft)}
.stg .ti{font-size:14px;font-weight:700;line-height:1.2}
.stg .ti small{font-weight:400;font-size:11px;color:var(--ink-3);margin-left:5px}
.stg .mt{font-size:11.5px;color:var(--ink-3);margin-top:3px;word-break:keep-all}
.stg .pb{height:4px;background:var(--surface-3);border-radius:2px;overflow:hidden;margin-top:6px;max-width:170px}
.stg .pb i{display:block;height:100%;background:var(--brand)}
.stg .rt{display:flex;flex-direction:column;align-items:flex-end;gap:5px}
.stg .st{font-size:11px;color:var(--ink-3);white-space:nowrap}
.stg.done .st{color:#2f7d5b}
.dbar{display:flex;align-items:center;gap:10px;padding:10px 14px;border-bottom:1px solid var(--line);font-size:13px;background:var(--surface-2)}
.dbar .t{flex:1;min-width:0;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dbar .t small{font-weight:400;color:var(--ink-3);margin-left:6px}
.dfoot{display:flex;flex-direction:column;gap:10px}
.rvhead{display:flex;gap:8px;flex-wrap:wrap;align-items:center;padding:12px 16px;border-bottom:1px solid var(--line);background:var(--surface-2)}
.rvhead .meta{flex:1;min-width:0}
.srow .src{font-size:10.5px;font-weight:700;letter-spacing:.06em;color:var(--brand);background:var(--brand-soft);padding:1px 7px;border-radius:20px;margin-left:6px;vertical-align:2px}
.sessbar{display:flex;align-items:center;gap:10px;margin-bottom:14px;padding:8px 10px;border:1px solid var(--brand-line);background:var(--brand-soft);border-radius:10px;font-size:12.5px;color:var(--brand)}
.sessbar .bar{flex:1 0 70px;margin:0;background:var(--surface)}
.sessbar .bar span{display:block;height:100%;background:var(--brand)}
.sessbar b{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sessbar .meta{white-space:nowrap}
.sessfoot{display:grid;grid-template-columns:1fr 1.4fr;gap:8px;margin-top:14px}
.sessfoot .btn{min-height:46px;justify-content:center}
.minibar{display:none}
.daystrip{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:thin;padding-bottom:2px;max-width:100%}
.daystrip .dbtn{flex:none}
@media(max-width:600px){
 body.mini .player-box .ratio{position:absolute;width:1px;height:1px;min-height:0;opacity:0;pointer-events:none;overflow:hidden;aspect-ratio:auto;box-shadow:none}
 body.mini .minibar{display:flex;align-items:center;gap:10px;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:6px 8px;margin-bottom:10px;font-size:12px;color:var(--ink-2)}
 .minibar .t{flex:1;min-width:0;overflow:hidden;text-align:left;padding:0;border:0;background:none;color:var(--ink-2);font:inherit}
 .minibar .t b{display:block;font-size:12.5px;color:var(--ink);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
 .minibar .t span{display:block;font-size:10.5px;color:var(--ink-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
 .minibar .pl{width:34px;height:34px;border-radius:50%;background:var(--brand);color:#fff;border:0;display:grid;place-items:center;flex:none;font-size:12px}
 .subtabs .tab{flex:1 1 0;padding:7px 2px}
 .stages{grid-template-columns:1fr;padding:10px 12px}
 .stg{padding:10px 10px}
 .daystrip{display:none}
 .dayhead{flex-wrap:nowrap;align-items:center}
 .dayhead #dayDone .lbl{display:none}
 .dfoot{position:fixed;left:0;right:0;bottom:0;z-index:7;background:var(--surface);border-top:1px solid var(--line);padding:10px 12px calc(10px + env(safe-area-inset-bottom));margin:0;gap:8px}
 .dfoot .dbtns .btn{flex:1}
 .dplay{padding-bottom:150px}
 .dgrade{grid-template-columns:repeat(3,1fr)}
 .card.sess .sessfoot{position:fixed;left:0;right:0;bottom:0;z-index:7;background:var(--surface);border-top:1px solid var(--line);padding:10px 12px calc(10px + env(safe-area-inset-bottom));margin:0}
 .card.sess{padding-bottom:96px}
 .card.sess .opts,.card.sess .keys{display:none}
 .rvhead .btn{flex:1 1 40%}
 .searchrow{flex-wrap:wrap;gap:8px}.searchrow input{flex:1 1 100%;order:-1}.searchrow .ic{display:none}.searchrow .seg{flex:1 1 100%}.searchrow .seg button{flex:1}
 .searchrow .btn{flex:1 1 40%}.searchrow .dauto{flex:1 1 40%}
}
</style>''')

# ───────────────────────── 3. JS ─────────────────────────
# 3a. 필터: 세션 덱
rep('''  if(filt === 'day') return dayIds.includes(d.id);''', '''  if(filt === 'day') return dayIds.includes(d.id);
  if(filt === 'sess') return !!sess && sess.ids.includes(d.id);''')
rep('''  deck = filt === 'day' ? DATA.filter(matches) : pool().filter(matches);
  if($('optShuffle').checked){''', '''  deck = (filt === 'day' || filt === 'sess') ? DATA.filter(matches) : pool().filter(matches);
  if($('optShuffle').checked && filt !== 'sess'){''')
rep('''  if(filt !== 'day' && ![...$('scenes').children].some(b => b.dataset && b.dataset.key === filt)){ filt = 'all'; store.set('filt', 'all'); }''',
    '''  if(filt !== 'day' && filt !== 'sess' && ![...$('scenes').children].some(b => b.dataset && b.dataset.key === filt)){ filt = 'all'; store.set('filt', 'all'); }''')
rep('''  if(filt === 'day'){ ko = 'Day ' + dayCur + ' 대사'; ja = 'Day ' + dayCur + ' の台詞'; }''',
    '''  if(filt === 'day'){ ko = 'Day ' + dayCur + ' 대사'; ja = 'Day ' + dayCur + ' の台詞'; }
  if(filt === 'sess' && sess){ ko = 'DAY ' + sess.day + ' · ' + (sess.stage === 1 ? '듣기' : '따라 하기'); ja = (sess.stage === 1 ? '聞く' : '真似る'); }''')

# 3b. 카드: 세션 중 1단계는 뜻을 가린다 + 세션 바 갱신
rep('''  setReveal($('optShow').checked);
  highlight(d.id);
}''', '''  setReveal($('optShow').checked && !(sess && sess.stage === 1));
  highlight(d.id);
  if(sess) sessPaint();
}''')

# 3c. 플레이어 상태 → 미니 바
rep('''        if(e.data === YT.PlayerState.PLAYING) $('playStatus').innerHTML = bi('재생 중…', '再生中…');''',
    '''        if(e.data === YT.PlayerState.PLAYING) $('playStatus').innerHTML = bi('재생 중…', '再生中…');
        $('mbToggle').textContent = e.data === YT.PlayerState.PLAYING ? '❚❚' : '▶';''')
_mini = '''  if(!$('minibar').hidden){ $('mbTime').textContent = fmt(t); const d = deck[index]; $('mbTitle').textContent = (stopAt !== null && d) ? edited(d).ja : document.title.split(' — ')[0].split(' · ')[0]; }
'''
if h.count('''  const t = player.getCurrentTime();
  if(loopSeg && loopSeg.from != null) syncBarLyric(dispT(t));''') == 1:
    rep('''  const t = player.getCurrentTime();
  if(loopSeg && loopSeg.from != null) syncBarLyric(dispT(t));''', '''  const t = player.getCurrentTime();
''' + _mini + '''  if(loopSeg && loopSeg.from != null) syncBarLyric(dispT(t));''')
else:
    rep('''  const t = player.getCurrentTime();
  if(view === 'script' && follow && stopAt === null){''', '''  const t = player.getCurrentTime();
''' + _mini + '''  if(view === 'script' && follow && stopAt === null){''')

# 3d. 뷰 전환 시 미니 바
rep('''  if(v === 'script' && deck[index]) highlight(deck[index].id);
}''', '''  if(v === 'script' && deck[index]) highlight(deck[index].id);
  paintMini();
}
const mqMobile = window.matchMedia('(max-width:600px)');
function paintMini(){
  const on = view === 'study' && mqMobile.matches && !OFFLINE;
  document.body.classList.toggle('mini', on);
  $('minibar').hidden = !on;
}
mqMobile.addEventListener('change', paintMini);
$('mbToggle').onclick = () => { if(!(player && ready)) return; player.getPlayerState() === 1 ? player.pauseVideo() : player.playVideo(); };
$('mbOpen').onclick = () => switchView('card');''')

# 3e. 학습법 태그
rep("'読みと意味を隠して再生。まず耳だけで挑む。分からなくて当たり前。', '카드'],", "'読みと意味を隠して再生。まず耳だけで挑む。分からなくて当たり前。', '오늘 › 1'],")
rep("'読みと意味を開いて答え合わせ。表現・単語は例文とセットで覚える。', '표현 · 단어'],", "'読みと意味を開いて答え合わせ。表現・単語は例文とセットで覚える。', '오늘 › 2'],")
rep("'リピートで同じ区間を繰り返し、声に出して重ねる。抑揚ごと写す。', '반복 C'],", "'リピートで同じ区間を繰り返し、声に出して重ねる。抑揚ごと写す。', '오늘 › 3'],")
rep("'クイズで今日の範囲だけ出題。間違いは翌日の復習リストになる。', '퀴즈']", "'クイズで今日の範囲だけ出題。間違いは翌日の復習リストになる。', '오늘 › 4']")

# 3f. 목록: 전부/표현/단어
rep('''let sKind = 'E';''', '''let sKind = 'A';''')
rep('''function buildStudy(){
  $('nExpr').textContent = STUDY.filter(r => r.t === 'E').length;
  $('nWord').textContent = STUDY.filter(r => r.t === 'V').length;
  renderList();
}''', '''function buildStudy(){
  $('nList').textContent = STUDY.length;
  renderList();
}''')
rep('''  const rows = STUDY.filter(r => r.t === sKind)''', '''  const rows = STUDY.filter(r => sKind === 'A' || r.t === sKind)''')

# 3g. 하위 탭 전환 전면 교체
rep('''function setSub(kind){
  const panes = {R:'drillPane', D:'dayPane', G:'guidePane', E:'listPane', V:'listPane', Q:'quizPane'};
  ['drillPane','dayPane','guidePane','listPane','quizPane'].forEach(id => $(id).hidden = panes[kind] !== id);
  if(kind !== 'R') drillStopAuto();
  if(kind !== 'E' && kind !== 'V') lStop();
  [['sbDrill','R'],['sbDay','D'],['sbGuide','G'],['sbExpr','E'],['sbWord','V'],['sbQuiz','Q']]
    .forEach(([id,k]) => $(id).setAttribute('aria-pressed', String(kind === k)));
  if(kind === 'E' || kind === 'V'){ sKind = kind; renderList(); }
  if(kind === 'D') renderDay();
}
$('sbDrill').onclick = () => setSub('R');
$('sbDay').onclick = () => setSub('D');
$('sbGuide').onclick = () => setSub('G');
$('sbExpr').onclick = () => setSub('E');
$('sbWord').onclick = () => setSub('V');
$('sbQuiz').onclick = () => setSub('Q');''', '''/* 하위 탭 4개(오늘·복습·목록·학습법). 드릴·퀴즈 패널은 탭이 아니라 단계·버튼에서 열리고, 「돌아가기」는 연 곳으로 */
const PANES = ['dayPane','reviewPane','listPane','guidePane','drillPane','quizPane'];
let subCur = 'D', dFrom = 'D', qFrom = 'D', dStage = 0, qStage = 0;
function showPane(id){
  PANES.forEach(p => $(p).hidden = p !== id);
  if(id !== 'drillPane') drillStopAuto();
  if(id !== 'listPane') lStop();
  if(id === 'dayPane') renderDay();
  if(id === 'reviewPane') renderReview();
  if(id === 'listPane') renderList();
}
function setSub(kind){
  subCur = kind;
  const map = {D:'dayPane', W:'reviewPane', L:'listPane', G:'guidePane'};
  [['sbDay','D'],['sbReview','W'],['sbList','L'],['sbGuide','G']].forEach(([id,k]) => $(id).setAttribute('aria-pressed', String(kind === k)));
  showPane(map[kind] || 'dayPane');
}
$('sbDay').onclick = () => setSub('D');
$('sbReview').onclick = () => setSub('W');
$('sbList').onclick = () => setSub('L');
$('sbGuide').onclick = () => setSub('G');
segWire('lKind', v => { sKind = v; renderList(); });
/* 드릴·퀴즈 열기(어디서 왔는지 기억) */
function openDrill(from, scope, title, stage){
  dFrom = from; dStage = stage || 0; dScope = scope; pickSeg2($('dScope'), scope);
  if(stage){ dMode = 'fwd'; dSize = 0; pickSeg2($('dMode'), 'fwd'); pickSeg2($('dSize'), '0'); }
  $('dTitle').textContent = title; $('dsetup').hidden = true; $('dSetBtn').setAttribute('aria-pressed', 'false');
  dStats(); showPane('drillPane');
  return dPool().length;
}
function openQuiz(from, scope, title, stage){
  qFrom = from; qStage = stage || 0; qScope = scope; pickSeg2($('qScope'), scope);
  if(stage){ qMode = 'ja2ko'; qLen = 10; pickSeg2($('qMode'), 'ja2ko'); pickSeg2($('qLen'), '10'); }
  $('qTitle').textContent = title; $('qsetup').hidden = true; $('qSetBtn').setAttribute('aria-pressed', 'false');
  $('qplay').hidden = true; $('qdone').hidden = true;
  syncQuizUI(); showPane('quizPane');
  return !$('qStart').disabled;
}
$('dBackBtn').onclick = () => { dActive = false; drillStopAuto(); dStage = 0; setSub(dFrom); };
$('dSetBtn').onclick = () => { const o = $('dsetup').hidden; $('dsetup').hidden = !o; $('dSetBtn').setAttribute('aria-pressed', String(o)); if(o){ $('dStats').hidden = false; dStats(); } };
$('qBackBtn').onclick = () => { qStage = 0; setSub(qFrom); };
$('qSetBtn').onclick = () => { const o = $('qsetup').hidden; $('qsetup').hidden = !o; $('qSetBtn').setAttribute('aria-pressed', String(o)); };
$('lDrill').onclick = () => { if(openDrill('L', sKind, '드릴 · ' + ({A:'표현·단어 전부', E:'표현 전부', V:'단어 전부'})[sKind])) dStart(false); };
$('lQuiz').onclick = () => { if(openQuiz('L', sKind === 'A' ? 'E' : sKind, '퀴즈 · ' + ({A:'표현', E:'표현', V:'단어'})[sKind])) $('qStart').click(); };
$('rvDrill').onclick = () => { if(openDrill('W', 'W', '복습 · 드릴')) dStart(false); };
$('rvListen').onclick = () => { if(openDrill('W', 'W', '복습 · 듣기만')) dAutoStart(aRep()); };

/* ====================== 복습 / 復習 ======================
   SRS 기한이 된 항목 + 퀴즈 오답 + 체크한 대사(아직 채점 안 한 것)를 한 목록으로 */
let wrongs = store.get('wrongs', []);
const wrongKey = it => (it.t || 'S') + '|' + it.ja;
function wrongAdd(it){ const k = wrongKey(it); if(!wrongs.includes(k)){ wrongs.push(k); store.set('wrongs', wrongs); } }
function wrongDel(k){ const i = wrongs.indexOf(k); if(i >= 0){ wrongs.splice(i, 1); store.set('wrongs', wrongs); } }
const sentItem = c => { const v = edited(c); return {t:'S', ja: v.ja, rd: v.rd || '', ko: v.ko, cids: [c.id], note: c.note || ''}; };
function itemOfKey(k){
  const at = k.indexOf('|'); if(at < 0) return null;
  const t = k.slice(0, at), ja = k.slice(at + 1);
  if(t === 'S'){ const c = DATA.find(c => edited(c).ja === ja); return c ? sentItem(c) : null; }
  return STUDY.find(r => r.t === t && r.ja === ja) || null;
}
function reviewPool(){
  const now = Date.now(), out = [], seen = new Set();
  const push = (it, src) => { const k = dKey(it); if(seen.has(k)) return; seen.add(k); it.src = src; out.push(it); };
  Object.entries(dState).forEach(([k, st]) => { if(st.due <= now){ const it = itemOfKey(k); if(it) push(it, 'SRS'); } });
  wrongs.forEach(k => { const it = itemOfKey(k); if(it) push(it, '오답'); });
  [...checked].forEach(id => { const c = cardOf(id); if(c && !dState['S|' + edited(c).ja]) push(sentItem(c), '체크'); });
  return out;
}
function paintReview(){ const n = reviewPool().length; $('nReview').textContent = n; return n; }
function renderReview(){
  const rows = reviewPool(); paintReview();
  const srs = rows.filter(r => r.src === 'SRS').length, wr = rows.filter(r => r.src === '오답').length, ck = rows.filter(r => r.src === '체크').length;
  $('rvInfo').textContent = rows.length ? ('복습 대기 ' + rows.length + ' · 기한 ' + srs + ' · 오답 ' + wr + ' · 체크 ' + ck) : '오늘 복습할 것이 없습니다 · 復習はありません';
  $('rvDrill').disabled = !rows.length; $('rvListen').disabled = !rows.length;
  const box = $('rvList'); box.textContent = '';
  rows.forEach(r => {
    const el = document.createElement('div'); el.className = 'srow';
    const tx = document.createElement('div'); tx.className = 'txt';
    const k = document.createElement('div'); k.className = 'k'; k.lang = 'ja'; k.textContent = r.ja;
    const s = document.createElement('span'); s.className = 'src'; s.textContent = r.src; k.appendChild(s);
    if(r.rd && r.rd !== r.ja){ const sm = document.createElement('small'); sm.textContent = r.rd; k.appendChild(sm); }
    const j = document.createElement('div'); j.className = 'j'; j.textContent = r.ko;
    tx.append(k, j); el.appendChild(tx);
    if(r.cids && r.cids.length && !OFFLINE){
      const b = document.createElement('button'); b.className = 'btn btn-sm'; b.innerHTML = '<svg class="ic fill"><use href="#i-play"/></svg>';
      b.onclick = () => { const c = cardOf(r.cids[0]); if(c) playSeg(c); }; el.appendChild(b);
    }
    box.appendChild(el);
  });
}''')

# 3h. 오늘 홈: renderDay 전면 교체 (+ 스테퍼 · 세션 · 연속일)
start = h.index('function renderDay(){')
end = h.index("segWire('qPace', v => {")
h = h[:start] + '''/* ---- 4단계: 듣기 → 확인 → 따라 하기 → 점검. 진행은 stages[day][n] = {done,total} ---- */
let stages = store.get('stages', {});
const stGet = (day, n) => ((stages[day] || {})[n]) || {done: 0, total: 0};
const stDone = (day, n) => { const s = stGet(day, n); return s.total > 0 && s.done >= s.total; };
function stSet(day, n, done, total){
  stages[day] = stages[day] || {}; stages[day][n] = {done, total}; store.set('stages', stages); logToday();
  if([1,2,3,4].every(k => stDone(day, k)) && !daysDone.has(day)){ daysDone.add(day); store.set('daysDone', [...daysDone]); }
  if(!$('dayPane').hidden) renderDay();
}
const dayKeyOf = d => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
let studyDays = new Set(store.get('studyDays', []));
function logToday(){ const k = dayKeyOf(new Date()); if(!studyDays.has(k)){ studyDays.add(k); store.set('studyDays', [...studyDays]); } }
function streak(){
  let n = 0; const d = new Date();
  if(!studyDays.has(dayKeyOf(d))) d.setDate(d.getDate() - 1);
  while(studyDays.has(dayKeyOf(d))){ n++; d.setDate(d.getDate() - 1); }
  return n;
}
/* 3단계 재료: 체크한 대사 + 오늘 표현의 예문 대사. 3장 미만이면 앞 대사로 채운다 */
function stage3Ids(d){
  const want = new Set();
  d.cards.forEach(c => { if(checked.has(c.id)) want.add(c.id); });
  d.expr.forEach(r => { if(r.ex != null && d.cards.some(c => c.id === r.ex)) want.add(r.ex); });
  if(want.size < 3) d.cards.slice(0, 5).forEach(c => want.add(c.id));
  return d.cards.filter(c => want.has(c.id)).map(c => c.id);
}
const STAGES = [
  ['듣기', '聞く', d => '대사 ' + d.cards.length + '장 · 뜻 가리고 재생', d => Math.max(2, Math.round(d.cards.length * 0.3))],
  ['확인', '確かめる', d => '표현 ' + d.expr.length + ' · 단어 ' + d.word.length + ' · 예문과 함께', d => Math.max(1, Math.round((d.expr.length + d.word.length) * 0.7))],
  ['따라 하기', '真似る', d => '대사 ' + stage3Ids(d).length + '장 · 구간 반복하며 소리 내기', d => Math.max(2, Math.round(stage3Ids(d).length * 1.2))],
  ['점검', '試す', d => '오늘 분량 퀴즈 ' + Math.min(10, d.expr.length + d.word.length + d.cards.length) + '문항', d => 4]
];
function startStage(n){
  const d = DAYS[dayCur - 1]; if(!d) return;
  const s = stGet(d.n, n), resume = (s.total && s.done < s.total) ? s.done : 0;
  if(n === 1) sessStart(1, d.cards.map(c => c.id), resume);
  else if(n === 3) sessStart(3, stage3Ids(d), resume);
  else if(n === 2){
    const cnt = openDrill('D', 'D', '2 확인 · 오늘 표현·단어 · 確かめる', 2);
    if(!cnt){ stSet(d.n, 2, 1, 1); setSub('D'); return; }
    dStart(false);
  } else {
    const ok = openQuiz('D', 'D', '4 점검 · 오늘 퀴즈 · 試す', 4);
    if(!ok){ stSet(d.n, 4, 1, 1); setSub('D'); return; }
    $('qStart').click();
  }
}
function renderDay(){
  const d = DAYS[dayCur - 1]; if(!d) return;
  dayIds = d.cards.map(c => c.id);
  $('dayNo').textContent = d.n;
  $('nDay').textContent = dayCur + '/' + DAYS.length;
  const names = [...new Set(d.cards.map(c => (SCENES.find(s => s.key === c.scene) || {}).ko).filter(Boolean))];
  $('dayTitle').textContent = names.slice(0, 3).join(' · ') + (names.length > 3 ? ' 외' : '');
  const done = d.cards.filter(c => checked.has(c.id)).length;
  $('dayMeta').textContent = fmt(d.cards[0].s) + ' – ' + fmt(d.cards[d.cards.length - 1].e) + (done ? ' · 체크 ' + done : '');
  $('dayDone').setAttribute('aria-pressed', String(daysDone.has(d.n)));
  $('dayPrev').disabled = dayCur <= 1; $('dayNext').disabled = dayCur >= DAYS.length;
  const prog = [1,2,3,4].reduce((a, n) => { const s = stGet(d.n, n); return a + (s.total ? Math.min(1, s.done / s.total) : 0); }, 0) / 4;
  $('dayBar').style.width = Math.round(prog * 100) + '%';

  const bd = $('dayBadges'); bd.textContent = '';
  const mkB = (txt, cls) => { const s = document.createElement('span'); s.className = 'bdg' + (cls ? ' ' + cls : ''); s.textContent = txt; bd.appendChild(s); };
  const sk = streak(); if(sk) mkB('연속 ' + sk + '일 · ' + sk + '日連続', 'ok');
  mkB('대사 ' + d.cards.length + ' · 표현 ' + d.expr.length + ' · 단어 ' + d.word.length);
  const rv = paintReview(); if(rv) mkB('복습 대기 ' + rv, 'acc');
  if(daysDone.has(d.n)) mkB('DAY ' + d.n + ' 완료', 'ok');

  const strip = $('daystrip'); strip.textContent = '';
  DAYS.forEach(x => {
    const b = document.createElement('button');
    b.className = 'dbtn' + (daysDone.has(x.n) ? ' done' : '');
    b.textContent = x.n; b.setAttribute('aria-pressed', String(x.n === dayCur));
    b.title = 'Day ' + x.n;
    b.onclick = () => { dayCur = x.n; store.set('dayCur', dayCur); renderDay(); };
    strip.appendChild(b);
    if(x.n === dayCur) requestAnimationFrame(() => { try{ b.scrollIntoView({block: 'nearest', inline: 'center'}); }catch(e){} });
  });

  const box = $('stages'); box.textContent = '';
  let nowSet = false;
  STAGES.forEach(([ko, ja, metaF, minF], i) => {
    const n = i + 1, s = stGet(d.n, n), isDone = stDone(d.n, n), started = s.done > 0 && !isDone;
    const el = document.createElement('div'); el.className = 'stg' + (isDone ? ' done' : '');
    const now = !isDone && !nowSet; if(now){ el.classList.add('now'); nowSet = true; }
    el.innerHTML = '<span class="no"></span><span class="bd"><div class="ti"></div><div class="mt"></div></span><span class="rt"></span>';
    el.querySelector('.no').textContent = isDone ? '✓' : n;
    const ti = el.querySelector('.ti'); ti.textContent = ko;
    const sm = document.createElement('small'); sm.lang = 'ja'; sm.textContent = ja; ti.appendChild(sm);
    el.querySelector('.mt').textContent = metaF(d) + ' · 약 ' + minF(d) + '분';
    if(started){ const pb = document.createElement('div'); pb.className = 'pb'; pb.innerHTML = '<i></i>';
      pb.querySelector('i').style.width = Math.round(s.done / s.total * 100) + '%'; el.querySelector('.bd').appendChild(pb); }
    const rt = el.querySelector('.rt');
    if(isDone){ const st = document.createElement('span'); st.className = 'st'; st.textContent = '완료 ' + s.done + ' / ' + s.total; rt.appendChild(st); }
    const b = document.createElement('button'); b.className = 'btn btn-sm' + (now ? ' btn-primary' : '');
    b.textContent = isDone ? '다시' : started ? '이어서 ' + s.done + ' / ' + s.total : '시작';
    b.onclick = () => startStage(n);
    rt.appendChild(b);
    box.appendChild(el);
  });

  const list = (host, rows, render) => {
    const el = $(host); el.textContent = '';
    rows.forEach(r => { const b = document.createElement('button'); b.className = 'dcRow'; render(b, r); el.appendChild(b); });
    if(!rows.length){ const e = document.createElement('div'); e.className = 'sempty'; e.style.padding = '14px';
      e.textContent = '—'; el.appendChild(e); }
  };
  $('dcN').textContent = d.cards.length;
  list('dcList', d.cards, (b, c) => {
    const v = edited(c);
    b.innerHTML = '<span class="tm"></span><span><span class="kk" lang="ja"></span> <span class="jj"></span></span>';
    b.querySelector('.tm').textContent = fmt(c.s);
    b.querySelector('.kk').textContent = v.ja.slice(0, 30);
    b.querySelector('.jj').textContent = v.ko.slice(0, 26);
    b.onclick = () => playSeg(c);
  });
  const wordRow = (b, r) => {
    b.innerHTML = '<span><span class="kk" lang="ja"></span> <span class="jj"></span></span>';
    b.querySelector('.kk').textContent = r.ja;
    b.querySelector('.jj').textContent = (r.rd && r.rd !== r.ja ? r.rd + ' · ' : '') + r.ko;
    b.onclick = () => { const c = cardOf((r.cids || [])[0]); if(c) playSeg(c); };
  };
  $('deN').textContent = d.expr.length; list('deList', d.expr, wordRow);
  $('dvN').textContent = d.word.length; list('dvList', d.word, wordRow);
}
$('dayPrev').onclick = () => { if(dayCur > 1){ dayCur--; store.set('dayCur', dayCur); renderDay(); } };
$('dayNext').onclick = () => { if(dayCur < DAYS.length){ dayCur++; store.set('dayCur', dayCur); renderDay(); } };
$('dayDone').onclick = () => {
  daysDone.has(dayCur) ? daysDone.delete(dayCur) : daysDone.add(dayCur);
  store.set('daysDone', [...daysDone]); renderDay();
};

/* ====================== 세션: 1 듣기 · 3 따라 하기 (카드 뷰 안에서) ====================== */
let sess = null;                                  /* {stage, ids, i, day} */
function sessStart(stage, ids, from){
  if(!ids.length){ stSet(dayCur, stage, 1, 1); return; }
  sess = {stage, ids, i: Math.min(from || 0, ids.length - 1), day: dayCur};
  filt = 'sess'; buildDeck(); index = sess.i; showCard();
  switchView('card'); sessPaint();
  window.scrollTo({top: 0});
  if(!OFFLINE && ready) sessPlay();
}
function sessPlay(){ const d = deck[index]; if(!d || OFFLINE) return; playSeg(d, {loop: sess.stage === 3}); }
function sessPaint(){
  const on = !!sess;
  $('sessbar').hidden = !on; $('sessfoot').hidden = !on;
  document.querySelector('.card').classList.toggle('sess', on);
  if(!on) return;
  const n = sess.ids.length; sess.i = index;
  $('sessName').textContent = 'DAY ' + sess.day + ' · ' + (sess.stage === 1 ? '1 듣기 · 聞く' : '3 따라 하기 · 真似る');
  $('sessPos').textContent = (index + 1) + ' / ' + n;
  $('sessBar').style.width = Math.round(index / n * 100) + '%';
  $('sessA').innerHTML = sess.stage === 1 ? '<svg class="ic"><use href="#i-eye"/></svg>뜻 보기 · 意味' : '<svg class="ic"><use href="#i-repeat"/></svg>한 번 더 · もう一度';
  $('sessB').textContent = (sess.stage === 1 ? '들었다' : '따라 말했다') + (index < n - 1 ? ' · 다음 ›' : ' · 끝내기 ✓');
}
function sessNext(){
  if(!sess) return;
  const n = sess.ids.length;
  stSet(sess.day, sess.stage, Math.min(n, index + 1), n);
  if(index < n - 1){ index++; showCard(); sessPaint(); sessPlay(); }
  else sessEnd();
}
function sessEnd(){
  if(!sess) return;
  stopAt = null; loopSeg = null; paintLoop();
  if(player && ready && !OFFLINE){ try{ player.pauseVideo(); }catch(e){} }
  sess = null; sessPaint();
  filt = store.get('filt', 'all'); if(filt === 'sess' || filt === 'day') filt = 'all';
  buildDeck(); switchView('study'); setSub('D');
}
$('sessQuit').onclick = () => sessEnd();
$('sessA').onclick = () => { if(!sess) return; if(sess.stage === 1) setReveal($('answer').hidden); else sessPlay(); };
$('sessB').onclick = () => sessNext();
''' + h[end:]
N += 1
rep('''$('sSearch').oninput = renderList;''', '''$('sSearch').oninput = renderList;''')  # 존재 확인만

# 3i. 퀴즈: 오늘 풀에 종류(t) 부여, 끝나면 단계 기록 + 오답을 복습으로
rep('''    return [...d.expr, ...d.word].map(r => ({ja: r.ja, rd: r.rd, ko: r.ko, note: r.note, cids: r.cids || []}))
      .concat(d.cards.map(c => ({ja: edited(c).ja, rd: edited(c).rd, ko: edited(c).ko, cids: [c.id]})));''',
    '''    return [...d.expr, ...d.word].map(r => ({t: r.t, ja: r.ja, rd: r.rd, ko: r.ko, note: r.note, cids: r.cids || []}))
      .concat(d.cards.map(c => ({t: 'S', ja: edited(c).ja, rd: edited(c).rd, ko: edited(c).ko, cids: [c.id]})));''')
rep('''  if(qScope === 'S') return DATA.map(c => ({ja: edited(c).ja, rd: edited(c).rd, ko: edited(c).ko, cids: [c.id]}));''',
    '''  if(qScope === 'S') return DATA.map(c => ({t: 'S', ja: edited(c).ja, rd: edited(c).rd, ko: edited(c).ko, cids: [c.id]}));''')
rep('''  return STUDY.filter(r => r.t === qScope).map(r => ({ja: r.ja, rd: r.rd, ko: r.ko, note: r.note, cids: r.cids || []}));''',
    '''  return STUDY.filter(r => r.t === qScope).map(r => ({t: r.t, ja: r.ja, rd: r.rd, ko: r.ko, note: r.note, cids: r.cids || []}));''')
rep('''function finishQ(){
  $('qplay').hidden = true; $('qdone').hidden = false;''', '''function finishQ(){
  $('qplay').hidden = true; $('qdone').hidden = false;
  qWrong.forEach(it => wrongAdd(it)); paintReview();
  if(qStage){ stSet(dayCur, qStage, qSet.length, qSet.length); qStage = 0; }''')
rep('''$('qQuit').onclick = () => { $('qplay').hidden = true; $('qsetup').hidden = false; };
$('rAgain').onclick = () => $('qStart').click();
$('rBack').onclick = () => { $('qdone').hidden = true; $('qsetup').hidden = false; };''',
    '''$('qQuit').onclick = () => { qStage = 0; setSub(qFrom); };
$('rAgain').onclick = () => $('qStart').click();
$('rBack').onclick = () => setSub(qFrom);''')

# 3j. 드릴: 복습 범위, 대사 항목, 단계 기록, 오답 해제, 돌아가기
rep('''  if(scope === 'D'){ const d = (typeof DAYS !== 'undefined' && DAYS[dayCur - 1]) || null; return d ? [...d.expr, ...d.word] : []; }''',
    '''  if(scope === 'D'){ const d = (typeof DAYS !== 'undefined' && DAYS[dayCur - 1]) || null; return d ? [...d.expr, ...d.word] : []; }
  if(scope === 'W') return reviewPool();''')
rep('''  $('nDrill').textContent = due + fresh;
  $('dStart').disabled = pool.length === 0;''', '''  paintReview();
  $('dStart').disabled = pool.length === 0;''')
rep('''function dStart(onlyMissed){
  dQueue = dBuildQueue(onlyMissed);
  if(!dQueue.length) return;
  dKnownN = 0; dRedoN = 0; dSeen = 0; dMissed = []; dActive = true;''', '''let dTotalN = 0, dGraded = new Set();
function dStart(onlyMissed){
  dQueue = dBuildQueue(onlyMissed);
  if(!dQueue.length) return;
  dKnownN = 0; dRedoN = 0; dSeen = 0; dMissed = []; dActive = true;
  dTotalN = dQueue.length; dGraded = new Set();
  if(dStage) stSet(dayCur, dStage, 0, dTotalN);''')
rep('''  $('dKind').textContent = (it.t === 'E' ? '표현' : '단어') + (dCur.again ? ' · 다시 ' + dCur.again : '');''',
    '''  $('dKind').textContent = (it.t === 'E' ? '표현' : it.t === 'S' ? '대사' : '단어') + (dCur.again ? ' · 다시 ' + dCur.again : '');''')
rep('''  $('dKind').textContent = (it.t === 'E' ? '표현' : '단어') + ' · ' + (dQueue.length + 1);''',
    '''  $('dKind').textContent = (it.t === 'E' ? '표현' : it.t === 'S' ? '대사' : '단어') + ' · ' + (dQueue.length + 1);''')
rep('''  dState[k] = st; dSave();
  dNext();
}''', '''  dState[k] = st; dSave();
  if(g === 3) wrongDel(k);
  dGraded.add(k); logToday();
  if(dStage) stSet(dayCur, dStage, Math.min(dGraded.size, dTotalN), dTotalN);
  dNext();
}''')
rep('''  $('dRestartMiss').hidden = !dMissed.length;
  dStats(); $('dStats').hidden = false;
}''', '''  $('dRestartMiss').hidden = !dMissed.length;
  if(dStage){ stSet(dayCur, dStage, dTotalN, dTotalN); }
  dStats(); $('dStats').hidden = false;
}''')
rep('''$('dQuit').onclick = () => { dActive = false; drillStopAuto(); $('dplay').hidden = true; $('dsetup').hidden = false; $('dStats').hidden = false; dStats(); };
$('dRestartMiss').onclick = () => dStart(true);
$('dRestartAll').onclick = () => { $('ddone').hidden = true; $('dsetup').hidden = false; $('dStats').hidden = false; };''',
    '''$('dQuit').onclick = () => { dActive = false; drillStopAuto(); dStage = 0; setSub(dFrom); };
$('dRestartMiss').onclick = () => dStart(true);
$('dRestartAll').onclick = () => { $('ddone').hidden = true; dStart(false); };
$('dDoneBack').onclick = () => { dStage = 0; setSub(dFrom); };''')
rep('''  if(dAutoOn){ drillStopAuto(); $('dplay').hidden = true; $('dsetup').hidden = false; $('dStats').hidden = false; return; }''',
    '''  if(dAutoOn){ drillStopAuto(); dStage = 0; setSub(dFrom); return; }''')

# 3k. 키보드: 세션 중 Enter = 다음
rep('''  else if(e.key === 'ArrowLeft'){ e.preventDefault(); $('prev').click(); }
});''', '''  else if(e.key === 'ArrowLeft'){ e.preventDefault(); $('prev').click(); }
  else if(e.key === 'Enter' && sess && view === 'card'){ e.preventDefault(); sessNext(); }
});''')

# 3l. 기동
rep('''buildScenes(); paintProgress(); paintEditCount(); buildDeck(); buildStudy(); buildDrill(); buildGuide(); buildDays(); renderDay(); syncQuizUI(); loadAPI();''',
    '''buildScenes(); paintProgress(); paintEditCount(); buildDeck(); buildStudy(); buildDrill(); buildGuide(); buildDays(); setSub('D'); syncQuizUI(); paintMini(); loadAPI();''')

# 체크 토글 시 복습 수 갱신
rep('''  $('check').setAttribute('aria-pressed', String(checked.has(d.id)));
  paintProgress();
};''', '''  $('check').setAttribute('aria-pressed', String(checked.has(d.id)));
  paintProgress(); paintReview();
};''')

assert h != orig
open(path, 'w', encoding='utf-8').write(h)
print('patched', path, 'replacements:', N)
