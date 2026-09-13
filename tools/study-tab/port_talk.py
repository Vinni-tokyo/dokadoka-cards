#!/usr/bin/env python3
"""토크쇼·인터뷰 앱 이식: mika-cards 에 적용한 학습 탭 개편(4단계 스테퍼·세션·복습)·큐 버튼·읽어주기·버튼 정리를
라벨 언어·필드가 다른 템플릿(영어 7종 · korean-cards · japanese-cards)에 옮긴다.

  사용: python3 tools/study-tab/port_talk.py <앱폴더>     (src/tpl.html 제자리 수정, 한 번만)
"""
import sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
app = sys.argv[1].strip('/')
path = os.path.join(ROOT, app, 'src', 'tpl.html')
h = open(path, encoding='utf-8').read()
assert 'id="cardfoot"' not in h, '이미 이식된 템플릿'
N = 0

EN = dict(L1='ko', L2='en', SRC='en', MEAN='ko', FILT='filt', PK=False)
CFG = {
  'english-cards': EN, 'altman-cards': EN, 'feifei-cards': EN, 'harris-cards': EN, 'social-cards': EN, 'think-cards': EN, 'tipping-cards': EN,
  'korean-cards':   dict(L1='ja', L2='ko', SRC='ko', MEAN='ja', FILT='sceneKey', PK=True),
  'japanese-cards': dict(L1='ko', L2='ja', SRC='ja', MEAN='ko', FILT='filt', PK=False),
}[app]
SRC, MEAN, L1, L2, FILT, PK = CFG['SRC'], CFG['MEAN'], CFG['L1'], CFG['L2'], CFG['FILT'], CFG['PK']

T = {
 'ko': dict(today='오늘', review='복습', list='목록', guide='학습법', back='돌아가기', settings='설정 ⚙', start='시작', resume='이어서', again='다시',
            done='완료', all='전부', expr='표현', word='단어', drill='드릴', quiz='퀴즈', reviewStart='복습 시작', listenOnly='듣기만',
            play='재생', stop='정지', loop='반복', prev='이전', next='다음', tts='읽어주기', slow='천천히', x3='3회', minutes='분', lines='대사',
            stages=['듣기', '확인', '따라 하기', '점검'], st1='장 · 뜻 가리고 재생', st2='예문과 함께', st3='장 · 구간 반복하며 소리 내기', st4='오늘 분량 퀴즈',
            items='문항', streak='연속 {n}일', reviewWait='복습 대기', dayDone='DAY {n} 완료', dueTag='기한', wrongTag='오답', checkTag='체크',
            noReview='오늘 복습할 것이 없습니다', allDrill='표현·단어 전부', reviewDrill='복습 · 드릴', reviewListen='복습 · 듣기만',
            seeMean='뜻 보기', heard='들었다', onceMore='한 번 더', said='따라 말했다', finish='끝내기', repeatN='반복 {a}회 중 {b}회째'),
 'ja': dict(today='今日', review='復習', list='一覧', guide='学習法', back='戻る', settings='設定 ⚙', start='始める', resume='続き', again='もう一度',
            done='完了', all='全部', expr='表現', word='単語', drill='ドリル', quiz='クイズ', reviewStart='復習を始める', listenOnly='聞くだけ',
            play='再生', stop='停止', loop='リピート', prev='前へ', next='次へ', tts='読み上げ', slow='ゆっくり', x3='3回', minutes='分', lines='台詞',
            stages=['聞く', '確かめる', '真似る', '試す'], st1='行 · 意味を隠して再生', st2='例文と一緒に', st3='行 · 区間リピートで声に出す', st4='今日の分のクイズ',
            items='問', streak='{n}日連続', reviewWait='復習待ち', dayDone='DAY {n} 完了', dueTag='期限', wrongTag='不正解', checkTag='チェック',
            noReview='今日の復習はありません', allDrill='表現・単語 全部', reviewDrill='復習 · ドリル', reviewListen='復習 · 聞くだけ',
            seeMean='意味を見る', heard='聞けた', onceMore='もう一度', said='真似た', finish='終える', repeatN='リピート {a}回中 {b}回目'),
 'en': dict(today='Today', review='Review', list='List', guide='How to', back='Back', settings='Settings ⚙', start='Start', resume='Resume', again='Again',
            done='Done', all='All', expr='Expressions', word='Words', drill='Drill', quiz='Quiz', reviewStart='Start review', listenOnly='Listen only',
            play='Play', stop='Stop', loop='Loop', prev='Prev', next='Next', tts='Read aloud', slow='Slow', x3='×3', minutes='min', lines='lines',
            stages=['Listen', 'Check', 'Imitate', 'Test'], st1='lines · meaning hidden', st2='with example lines', st3='lines · loop and speak over', st4="quiz on today's set",
            items='questions', streak='{n}-day streak', reviewWait='to review', dayDone='DAY {n} done', dueTag='due', wrongTag='missed', checkTag='checked',
            noReview='Nothing to review today', allDrill='all expressions & words', reviewDrill='Review · drill', reviewListen='Review · listen',
            seeMean='Show meaning', heard='Got it', onceMore='Once more', said='Said it', finish='Finish', repeatN='loop {b} of {a}'),
}
A, B = T[L1], T[L2]
def bl(k): return A[k] + ' · ' + B[k]
def lbl(k): return '<span class="lbl">%s<span class="sub" lang="%s">%s</span></span>' % (A[k], L2, B[k])

def rep(old, new, count=1):
    global h, N
    c = h.count(old)
    assert c == count, f'[{N}] expected {count}, found {c}: {old[:80]!r}'
    h = h.replace(old, new); N += 1
def rep_re(pat, new, count=1, flags=0):
    global h, N
    c = len(re.findall(pat, h, flags))
    assert c == count, f'[{N}] regex expected {count}, found {c}: {pat[:80]!r}'
    h = re.sub(pat, lambda m: m.expand(new) if '\\' in new and not new.startswith('RAW:') else new, h, count=count, flags=flags); N += 1
def slice_rep(start, end, new, inclusive_end=False):
    global h, N
    a = h.index(start); b = h.index(end, a + len(start))
    if inclusive_end: b += len(end)
    h = h[:a] + new + h[b:]; N += 1

# ══════════════════ 1. 아이콘 · 홈 버튼 ══════════════════
rep('''<symbol id="i-info" viewBox="0 0 24 24">''', '''<symbol id="i-home" viewBox="0 0 24 24"><path d="M3 11.5L12 4l9 7.5M5.5 10v10h13V10"/></symbol>
<symbol id="i-stop" viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="1.5"/></symbol>
<symbol id="i-info" viewBox="0 0 24 24">''')
rep('''   <div class="tabs">
    <button class="tab" id="tabCard" aria-pressed="true">''', '''   <div class="tabs">
    <a class="tab home" href="../" title="메인으로 · 모든 학습 콘텐츠 / メインへ / Home" aria-label="home"><svg class="ic"><use href="#i-home"/></svg></a>
    <button class="tab" id="tabCard" aria-pressed="true">''')

# ══════════════════ 2. 카드 뷰 ══════════════════
rep('''      <span class="meta"><span id="pos">0 / 0</span> · <span id="time">0:00</span></span>
     </div>''', '''      <span class="ctl">
       <span class="meta"><span id="pos">0 / 0</span> · <span id="time">0:00</span></span>
       <button class="ibtn" id="check" aria-pressed="false" title="%s"><svg class="ic"><use href="#i-check"/></svg></button>
       <button class="ibtn" id="edit" title="편집 / 編集 / Edit"><svg class="ic"><use href="#i-pencil"/></svg></button>
      </span>
     </div>''' % bl('checkTag'))
rep_re(r'      <button class="btn" id="check" aria-pressed="false">.*?</button>\n      <button class="btn" id="edit">.*?</button>\n', '', flags=re.S)
# 세션 바 (카드 맨 위)
rep_re(r'(   <div id="cardView">\n    <div class="card">\n)(     <div class="card-top">)', r'''\1     <div class="sessbar" id="sessbar" hidden>
      <button class="btn btn-sm" id="sessQuit"><svg class="ic"><use href="#i-x"/></svg></button>
      <b id="sessName">—</b>
      <div class="bar"><span id="sessBar" style="width:0"></span></div>
      <span class="meta" id="sessPos">0 / 0</span>
     </div>
\2''')
# 읽어주기 줄: 본문(+읽기, +원문) 아래
m = re.search(r'     <div class="%s" id="%s" lang="%s">[^<]*</div>\n(?:     <p class="rd"[^\n]*\n)?(?:     <p class="raw"[^\n]*\n)?' % (SRC, SRC, SRC), h)
assert m, '본문 요소'
h = h[:m.end()] + '''     <div class="ttsrow">
      <button class="btn btn-sm" id="ttsPlay" title="T"><svg class="ic"><use href="#i-sound"/></svg>%s</button>
      <button class="btn btn-sm" id="ttsSlow" title="0.75×">%s</button>
      <button class="btn btn-sm" id="ttsRep" title="×3">%s</button>
      <button class="btn btn-sm" id="ttsStop"><svg class="ic fill"><use href="#i-stop"/></svg></button>
     </div>
''' % (A['tts'], A['slow'], A['x3']) + h[m.end():]; N += 1
# 조작 줄 + 세션 하단 바
rep('''     <div class="opts">
      <label><input type="checkbox" id="optAuto">''', '''     <div class="cardfoot" id="cardfoot">
      <button class="btn" id="cfPrev"><svg class="ic"><use href="#i-left"/></svg><span class="txt">%s</span></button>
      <button class="btn btn-primary" id="cfPlay"><svg class="ic fill"><use href="#i-play"/></svg>%s</button>
      <button class="btn" id="cfStop"><svg class="ic fill"><use href="#i-stop"/></svg>%s</button>
      <button class="btn" id="cfLoop" aria-pressed="false"><svg class="ic"><use href="#i-repeat"/></svg>%s</button>
      <button class="btn" id="cfNext"><span class="txt">%s</span><svg class="ic"><use href="#i-right"/></svg></button>
     </div>
     <div class="sessfoot" id="sessfoot" hidden>
      <button class="btn" id="sessA"><svg class="ic"><use href="#i-eye"/></svg>%s</button>
      <button class="btn btn-primary" id="sessB">%s · %s ›</button>
     </div>

     <div class="opts">
      <label><input type="checkbox" id="optAuto">''' % (A['prev'], A['play'], A['stop'], A['loop'], A['next'], A['seeMean'], A['heard'], A['next']))
rep('''   <div class="player-box">
    <div class="ratio" id="ratio"><div id="player"></div></div>''', '''   <div class="player-box">
    <div class="minibar" id="minibar" hidden>
     <button class="pl" id="mbToggle">▶</button>
     <button class="t" id="mbOpen"><b id="mbTitle">—</b><span id="mbSub">▶</span></button>
     <span class="meta" id="mbTime">0:00</span>
    </div>
    <div class="ratio" id="ratio"><div id="player"></div></div>''')

# ══════════════════ 3. 학습 탭 마크업 ══════════════════
slice_rep('     <div class="subtabs">', '     </div>\n', '''     <div class="subtabs">
      <button class="tab" id="sbDay" aria-pressed="true">%s<b id="nDay">—</b></button>
      <button class="tab" id="sbReview" aria-pressed="false">%s<b id="nReview">0</b></button>
      <button class="tab" id="sbList" aria-pressed="false">%s<b id="nList">0</b></button>
      <button class="tab" id="sbGuide" aria-pressed="false"><svg class="ic"><use href="#i-info"/></svg>%s</button>
     </div>
''' % (lbl('today'), lbl('review'), lbl('list'), lbl('guide')), inclusive_end=True)
DBAR = lambda idb, idt, ids, title: '''      <div class="dbar">
       <button class="btn btn-sm" id="%s"><svg class="ic"><use href="#i-left"/></svg>%s</button>
       <span class="t" id="%s">%s</span>
       <button class="btn btn-sm" id="%s" aria-pressed="false">%s</button>
      </div>
''' % (idb, A['back'], idt, title, ids, A['settings'])
rep('''     <div id="drillPane">
      <div class="dsetup" id="dsetup">''', '''     <div id="drillPane" hidden>
''' + DBAR('dBackBtn', 'dTitle', 'dSetBtn', A['drill']) + '''      <div class="dsetup" id="dsetup" hidden>''')
i0 = h.index('id="dScope"'); j0 = h.index('        </div>', i0)
h = h[:j0] + '         <button data-v="W" aria-pressed="false">%s</button>\n' % A['review'] + h[j0:]; N += 1
rep('''       <div class="dbtns">
        <button class="btn btn-primary" id="dReveal">''', '''       <div class="dfoot">
       <div class="dbtns">
        <button class="btn btn-primary" id="dReveal">''')
rep_re(r'(        <button class="btn g3" id="dG3">[^\n]*\n       </div>\n)(       <div class="dhint">)', r'\1       </div>\n\2')
rep_re(r'(        <button class="btn" id="dRestartAll">[^<]*</button>\n)', r'\1        <button class="btn" id="dDoneBack">%s</button>\n' % A['back'])
rep_re(r'     <div id="dayPane"( hidden)?>', '     <div id="dayPane">')
slice_rep('      <div class="dayhead">', '      <div class="daycols">', '''      <div class="dayhead">
       <button class="btn btn-sm dayarr" id="dayPrev"><svg class="ic"><use href="#i-left"/></svg></button>
       <div class="dayttl">
        <span class="dno">DAY <b id="dayNo">1</b><i>/<span id="dayTot">7</span></i></span>
        <h3 id="dayTitle">—</h3>
        <p class="daymeta" id="dayMeta">—</p>
        <div class="daybar"><i id="dayBar" style="width:0"></i></div>
       </div>
       <button class="btn btn-sm dayarr" id="dayNext"><svg class="ic"><use href="#i-right"/></svg></button>
       <button class="btn btn-sm" id="dayDone" title="%s"><svg class="ic"><use href="#i-check"/></svg>%s</button>
      </div>
      <div class="badges" id="dayBadges"></div>
      <div class="stages" id="stages"></div>

''' % (bl('done'), lbl('done')))
rep('''     <div id="guidePane" hidden>''', '''     <div id="reviewPane" hidden>
      <div class="rvhead">
       <span class="meta" id="rvInfo">—</span>
       <button class="btn btn-primary btn-sm" id="rvDrill"><svg class="ic fill"><use href="#i-play"/></svg>%s</button>
       <button class="btn btn-sm" id="rvListen"><svg class="ic"><use href="#i-sound"/></svg>%s</button>
      </div>
      <div class="slist" id="rvList"></div>
     </div>

     <div id="guidePane" hidden>''' % (lbl('reviewStart'), bl('listenOnly')))
rep('''       <span class="meta" id="sCount">0</span>''', '''       <span class="meta" id="sCount">0</span>
       <div class="seg" id="lKind"><button data-v="A" aria-pressed="true">%s</button><button data-v="E" aria-pressed="false">%s</button><button data-v="V" aria-pressed="false">%s</button></div>
       <button class="btn btn-sm btn-primary" id="lDrill"><svg class="ic fill"><use href="#i-play"/></svg>%s</button>
       <button class="btn btn-sm" id="lQuiz"><svg class="ic"><use href="#i-check"/></svg>%s</button>''' % (A['all'], A['expr'], A['word'], A['drill'], A['quiz']))
rep('''     <div id="quizPane" hidden>
      <div class="qsetup" id="qsetup">''', '''     <div id="quizPane" hidden>
''' + DBAR('qBackBtn', 'qTitle', 'qSetBtn', A['quiz']) + '''      <div class="qsetup" id="qsetup" hidden>''')
# 학습법 단계 태그 → 「오늘 › n」
a_ = h.index('  const G = ['); b_ = h.index('  ];', a_)
rows = h[a_:b_].split("],\n")
rows = [re.sub(r", '[^']*'\]?$", ", '%s › %d']" % (A['today'], i + 1), r.rstrip()) for i, r in enumerate(rows)]
h = h[:a_] + ",\n".join(rows) + "\n" + h[b_:]; N += 1

# ══════════════════ 4. CSS ══════════════════
rep('''.tab[aria-pressed="true"]{background:var(--surface);color:var(--brand);font-weight:600;box-shadow:var(--sh-1)}''',
    '''.tab[aria-pressed="true"]{background:var(--surface);color:var(--brand);font-weight:600;box-shadow:var(--sh-1)}
.tab.home{flex:0 0 auto;padding:6px 10px;text-decoration:none;color:var(--ink-3);border-right:1px solid var(--line-2);border-radius:7px 0 0 7px;margin-right:2px}
.tab.home:hover{color:var(--brand)}''')
rep('''.tabs{margin-left:0;width:100%}.tab{flex:1;justify-content:center;padding:6px 8px}''',
    '''.tabs{margin-left:0;width:100%;gap:2px}.tab{flex:1;justify-content:center;padding:6px 4px;gap:0}.tab>.ic{display:none}.tab.home{flex:0 0 auto;padding:6px 9px}.tab.home>.ic{display:block}''')
rep_re(r'\.subtabs \.tab\{flex:1 1 30%[^}]*\}', '.subtabs .tab{flex:1 1 0;justify-content:center;padding:7px 2px;gap:4px}')
CSS = '''
/* ---- 학습 탭 개편 · 세션 · 조작 줄 · 읽어주기 · 미니 플레이어 (port_talk) ---- */
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
.cardfoot{display:grid;grid-template-columns:auto 1.3fr 1fr 1fr auto;gap:8px;margin-top:16px}
.cardfoot .btn{justify-content:center;min-height:44px;white-space:nowrap;padding:8px 6px;gap:5px;font-size:13px}
.card .nav{display:none}
#play,#loop{display:none}
.playrow{margin:0}.playrow .btn{margin-top:14px}
.card.sess .cardfoot{display:none}
.btn.holding{background:var(--accent);border-color:var(--accent);color:#fff}
.cue{touch-action:manipulation;user-select:none;-webkit-user-select:none;-webkit-touch-callout:none}
.ttsrow{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:12px 0 0}
.ttsrow .btn[aria-pressed=true]{background:var(--brand-soft);border-color:var(--brand-line);color:var(--brand)}
.card-top .ctl{display:inline-flex;align-items:center;gap:6px;flex:none}
.ibtn{display:inline-grid;place-items:center;width:30px;height:30px;padding:0;border-radius:8px;border:1px solid var(--line-2);background:var(--surface);color:var(--ink-2)}
.ibtn .ic{width:15px;height:15px}
.ibtn:hover{color:var(--brand);border-color:var(--brand-line)}
.ibtn[aria-pressed=true]{background:var(--brand);border-color:var(--brand);color:#fff}
.daystrip{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:thin;padding-bottom:2px;max-width:100%}
.daystrip .dbtn{flex:none}
@media(max-width:600px){
 body.mini .player-box .ratio{position:absolute;width:1px;height:1px;min-height:0;opacity:0;pointer-events:none;overflow:hidden;aspect-ratio:auto;box-shadow:none}
 body.mini .player-box{position:static;padding:0;margin:0}
 body.mini .minibar{display:flex;align-items:center;gap:10px;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:6px 8px;margin-bottom:10px;font-size:12px;color:var(--ink-2)}
 .minibar .t{flex:1;min-width:0;overflow:hidden;text-align:left;padding:0;border:0;background:none;color:var(--ink-2);font:inherit}
 .minibar .t b{display:block;font-size:12.5px;color:var(--ink);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
 .minibar .t span{display:block;font-size:10.5px;color:var(--ink-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
 .minibar .pl{width:34px;height:34px;border-radius:50%;background:var(--brand);color:#fff;border:0;display:grid;place-items:center;flex:none;font-size:12px}
 .stages{grid-template-columns:1fr;padding:10px 12px}
 .stg{padding:10px 10px}
 .daystrip{display:none}
 .dayhead{flex-wrap:nowrap;align-items:center}
 .dayhead #dayDone .lbl{display:none}
 .dfoot{position:fixed;left:0;right:0;bottom:0;z-index:7;background:var(--surface);border-top:1px solid var(--line);padding:10px 12px calc(10px + env(safe-area-inset-bottom));margin:0;gap:8px}
 .dfoot .dbtns .btn{flex:1}
 .dplay{padding-bottom:150px}
 .dgrade{grid-template-columns:repeat(3,1fr)}
 .rvhead .btn{flex:1 1 40%}
 .searchrow{flex-wrap:wrap;gap:8px}.searchrow input{flex:1 1 100%;order:-1}.searchrow .ic{display:none}.searchrow .seg{flex:1 1 100%}.searchrow .seg button{flex:1}
 .searchrow .btn{flex:1 1 40%}.searchrow .dauto{flex:1 1 40%}
 .cardfoot{position:fixed;left:0;right:0;bottom:0;z-index:7;background:var(--surface);border-top:1px solid var(--line);padding:10px 12px calc(10px + env(safe-area-inset-bottom));margin:0}
 .cardfoot .txt{display:none}.cardfoot #cfPrev,.cardfoot #cfNext{padding:8px 12px}
 .card{padding-bottom:96px}
 .card.sess .sessfoot{position:fixed;left:0;right:0;bottom:0;z-index:7;background:var(--surface);border-top:1px solid var(--line);padding:10px 12px calc(10px + env(safe-area-inset-bottom));margin:0}
 .card.sess .opts,.card .keys{display:none}
 .playrow .btn{flex:1 1 100%;margin-top:12px}
}
</style>'''
rep('\n</style>', CSS)

# ══════════════════ 5. JS: 필터·카드·플레이어 ══════════════════
if FILT == 'filt':
    rep('''  if(filt === 'day') return dayIds.includes(d.id);''', '''  if(filt === 'day') return dayIds.includes(d.id);
  if(filt === 'sess') return !!sess && sess.ids.includes(d.id);''')
    rep('''  deck = filt === 'day' ? DATA.filter(matches) : pool().filter(matches);
  if($('optShuffle').checked){''', '''  deck = (filt === 'day' || filt === 'sess') ? DATA.filter(matches) : pool().filter(matches);
  if($('optShuffle').checked && filt !== 'sess'){''')
    rep_re(r"  if\(filt !== 'day' && !\[", "  if(filt !== 'day' && filt !== 'sess' && ![")
    SESS_FILT_ON = "filt = 'sess';"
    SESS_FILT_OFF = "filt = store.get('filt', 'all'); if(filt === 'sess' || filt === 'day') filt = 'all';"
else:
    rep('''  if(sceneKey === '__day'){ const s = new Set(dayIds); deck = DATA.filter(d => s.has(d.id)); }''',
        '''  if(sceneKey === '__sess'){ deck = DATA.filter(d => !!sess && sess.ids.includes(d.id)); }
  else if(sceneKey === '__day'){ const s = new Set(dayIds); deck = DATA.filter(d => s.has(d.id)); }''')
    rep('''  if($('optShuffle').checked){
    for(let i = deck.length-1; i > 0; i--){''', '''  if($('optShuffle').checked && sceneKey !== '__sess'){
    for(let i = deck.length-1; i > 0; i--){''')
    SESS_FILT_ON = "sceneKey = '__sess';"
    SESS_FILT_OFF = "sceneKey = 'all';"
rep('''  setReveal($('optShow').checked);
  highlight(d.id);
}''', '''  setReveal($('optShow').checked && !(sess && sess.stage === 1));
  highlight(d.id);
  if(sess) sessPaint();
}''')
rep('''  $('prev').disabled = index === 0;
  $('next').disabled = index === deck.length-1;''', '''  $('prev').disabled = index === 0;
  $('next').disabled = index === deck.length-1;
  $('cfPrev').disabled = index === 0; $('cfNext').disabled = index === deck.length-1;''')
rep('''  $('loop').setAttribute('aria-pressed', String(!!loopSeg));
}''', '''  $('loop').setAttribute('aria-pressed', String(!!loopSeg));
  $('cfLoop').setAttribute('aria-pressed', String(!!loopSeg));
}''')
rep_re(r"(if\(e\.data === YT\.PlayerState\.PLAYING\) \$\('playStatus'\)\.innerHTML = bi\([^\n]*;)",
       r"\1\n        $('mbToggle').textContent = e.data === YT.PlayerState.PLAYING ? '❚❚' : '▶';")
rep('''  const t = player.getCurrentTime();
  if(view === 'script' && follow && stopAt === null){''', '''  const t = player.getCurrentTime();
  if(!$('minibar').hidden){ $('mbTime').textContent = fmt(t); const d = deck[index]; $('mbTitle').textContent = (stopAt !== null && d) ? edited(d).%s : document.title.split(' — ')[0].split(' · ')[0]; }
  if(view === 'script' && follow && stopAt === null){''' % SRC)
rep_re(r"(  if\(v === 'script' && deck\[index\]\) highlight\(deck\[index\]\.id\);\n(?:  if\(v === 'kara'\)[^\n]*\n)?)\}", r"\1  paintMini();\n}")
rep("$('tabStudy').onclick = () => switchView('study');", '''$('tabStudy').onclick = () => switchView('study');
const mqMobile = window.matchMedia('(max-width:600px)');
function paintMini(){
  const on = view === 'study' && mqMobile.matches && !OFFLINE;
  document.body.classList.toggle('mini', on);
  $('minibar').hidden = !on;
}
mqMobile.addEventListener('change', paintMini);
$('mbToggle').onclick = () => { if(!(player && ready)) return; player.getPlayerState() === 1 ? player.pauseVideo() : player.playVideo(); };
$('mbOpen').onclick = () => switchView('card');''')
# 음원 엔진에 속도 인자
rep_re(r'function aPlay\(text, times, gap, cb, which\)\{', '/* 읽어주기 음량: 내장 음원(edge-tts)은 유튜브보다 훨씬 커서 낮춘다 */
const A_VOL = 0.35, A_VOL_TTS = 0.7;
function aPlay(text, times, gap, cb, which, rate){')
rep('''    if(src){ const a = new Audio(src); aCur = a; a.onended = after; a.onerror = after; a.play().catch(after); }
    else dSpeakText(text, which, after);''', '''    if(src){ const a = new Audio(src); aCur = a; a.playbackRate = rate || 1; a.volume = A_VOL; a.onended = after; a.onerror = after; a.play().catch(after); }
    else dSpeakText(text, which, after, rate);''')
rep('''function dSpeakText(text, which, cb){''', '''function dSpeakText(text, which, cb, rate){''')
rep('''  u.rate = Number($('dRate').value) || 1;''', '''  u.rate = rate || Number($('dRate').value) || 1;
  u.volume = A_VOL_TTS;''')
# 큐 버튼 · 정지 · 읽어주기
rep('''$('play').onclick  = () => { const d = deck[index]; if(d) playSeg(d); };''', '''/* 디제이 큐 버튼: 탭 = 구간 처음부터, 길게 누르면 그동안만 재생하고 떼면 구간 처음으로 */
const HOLD_MS = 350;
function cueStop(seg){
  if(OFFLINE || !(player && ready)) return;
  stopAt = null; loopSeg = null; paintLoop();
  try{ player.pauseVideo(); player.seekTo(headOf(seg), true); }catch(e){}
}
function stopAll(){
  if(OFFLINE || !(player && ready)) return;
  stopAt = null; loopSeg = null; paintLoop();
  try{ player.pauseVideo(); }catch(e){}
  aStopAll();
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
  btn.onclick = e => { if(e.detail === 0){ const r = segFn(); if(r) playSeg(r.seg, r.opts || {}); } };
}
bindCue($('play'), () => { const d = deck[index]; return d ? {seg: d} : null; });
bindCue($('cfPlay'), () => { const d = deck[index]; return d ? {seg: d} : null; });
$('cfStop').onclick = stopAll;
$('cfLoop').onclick = () => $('loop').click();
$('cfPrev').onclick = () => $('prev').click();
$('cfNext').onclick = () => $('next').click();
function ttsMark(el){ document.querySelectorAll('.ttsrow .btn[aria-pressed=true]').forEach(x => x.setAttribute('aria-pressed', 'false')); if(el) el.setAttribute('aria-pressed', 'true'); }
function ttsLine(times, rate){
  const d = deck[index]; if(!d) return;
  if(!OFFLINE && player && ready){ try{ if(player.getPlayerState() === 1) player.pauseVideo(); }catch(e){} }
  const btn = times > 1 ? $('ttsRep') : rate < 1 ? $('ttsSlow') : $('ttsPlay');
  ttsMark(btn);
  aPlay(edited(d).%s, times, 500, () => btn.setAttribute('aria-pressed', 'false'), 2, rate);
}
$('ttsPlay').onclick = () => ttsLine(1, 1);
$('ttsSlow').onclick = () => ttsLine(1, 0.75);
$('ttsRep').onclick  = () => ttsLine(3, 1);
$('ttsStop').onclick = () => { aStopAll(); ttsMark(null); };''' % SRC)
rep('''  else if(k === 'c'){ e.preventDefault(); $('loop').click(); }''', '''  else if(k === 'c'){ e.preventDefault(); $('loop').click(); }
  else if(k === 's'){ e.preventDefault(); stopAll(); }
  else if(k === 't'){ e.preventDefault(); ttsLine(1, 1); }''')
rep('''  else if(e.key === 'ArrowLeft'){ e.preventDefault(); $('prev').click(); }
});''', '''  else if(e.key === 'ArrowLeft'){ e.preventDefault(); $('prev').click(); }
  else if(e.key === 'Enter' && sess && view === 'card'){ e.preventDefault(); sessNext(); }
});''')
i0 = h.index("$('check').onclick"); j0 = h.index('  paintProgress();', i0)
h = h[:j0] + '  paintProgress(); paintReview();' + h[j0 + len('  paintProgress();'):]; N += 1

# ══════════════════ 6. JS: 학습 탭 ══════════════════
rep('''let sKind = 'E';''', '''let sKind = 'A';''')
rep('''  $('nExpr').textContent = STUDY.filter(r => r.t === 'E').length;
  $('nWord').textContent = STUDY.filter(r => r.t === 'V').length;
  renderList();''', '''  $('nList').textContent = STUDY.length;
  renderList();''')
rep('''  const rows = STUDY.filter(r => r.t === sKind)''', '''  const rows = STUDY.filter(r => sKind === 'A' || r.t === sKind)''')
SK = "const SK = k => (typeof pk === 'function' ? pk(k) : k);" if PK else "const SK = k => k;"
NEW_SETSUB = '''/* 하위 탭 4개(오늘·복습·목록·학습법). 드릴·퀴즈 패널은 단계·버튼에서 열리고 「돌아가기」는 연 곳으로 */
const PANES = ['dayPane','reviewPane','listPane','guidePane','drillPane','quizPane'];
let subCur = 'D', dFrom = 'D', qFrom = 'D', dStage = 0, qStage = 0;
%s
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
function openDrill(from, scope, title, stage){
  dFrom = from; dStage = stage || 0; dScope = scope; pickSeg2($('dScope'), scope);
  if(stage){ dMode = 'fwd'; dSize = 0; pickSeg2($('dMode'), 'fwd'); pickSeg2($('dSize'), '0'); }
  $('dTitle').textContent = title; $('dsetup').hidden = true; $('dSetBtn').setAttribute('aria-pressed', 'false');
  dStats(); showPane('drillPane');
  return dPool().length;
}
function openQuiz(from, scope, title, stage){
  qFrom = from; qStage = stage || 0; qScope = scope; pickSeg2($('qScope'), scope);
  if(stage){ qMode = '%s2%s'; qLen = 10; pickSeg2($('qMode'), qMode); pickSeg2($('qLen'), '10'); }
  $('qTitle').textContent = title; $('qsetup').hidden = true; $('qSetBtn').setAttribute('aria-pressed', 'false');
  $('qplay').hidden = true; $('qdone').hidden = true;
  syncQuizUI(); showPane('quizPane');
  return !$('qStart').disabled;
}
$('dBackBtn').onclick = () => { dActive = false; drillStopAuto(); dStage = 0; setSub(dFrom); };
$('dSetBtn').onclick = () => { const o = $('dsetup').hidden; $('dsetup').hidden = !o; $('dSetBtn').setAttribute('aria-pressed', String(o)); if(o){ $('dStats').hidden = false; dStats(); } };
$('qBackBtn').onclick = () => { qStage = 0; setSub(qFrom); };
$('qSetBtn').onclick = () => { const o = $('qsetup').hidden; $('qsetup').hidden = !o; $('qSetBtn').setAttribute('aria-pressed', String(o)); };
$('lDrill').onclick = () => { if(openDrill('L', sKind, '%s · ' + ({A:'%s', E:'%s', V:'%s'})[sKind])) dStart(false); };
$('lQuiz').onclick = () => { if(openQuiz('L', sKind === 'A' ? 'E' : sKind, '%s · ' + ({A:'%s', E:'%s', V:'%s'})[sKind])) $('qStart').click(); };
$('rvDrill').onclick = () => { if(openDrill('W', 'W', '%s')) dStart(false); };
$('rvListen').onclick = () => { if(openDrill('W', 'W', '%s')) dAutoStart(aRep()); };

/* ====================== 복습: SRS 기한 + 퀴즈 오답 + 체크한 대사 ====================== */
let wrongs = [];
const rvKey = it => (it.t || 'S') + '|' + it.%s;
function wrongAdd(it){ const k = rvKey(it); if(!wrongs.includes(k)){ wrongs.push(k); store.set(SK('wrongs'), wrongs); } }
function wrongDel(k){ const i = wrongs.indexOf(k); if(i >= 0){ wrongs.splice(i, 1); store.set(SK('wrongs'), wrongs); } }
const sentItem = c => { const v = edited(c); return {t:'S', %s: v.%s, rd: v.rd || '', %s: v.%s, cids: [c.id], note: c.note || ''}; };
function itemOfKey(k){
  const at = k.indexOf('|'); if(at < 0) return null;
  const t = k.slice(0, at), s = k.slice(at + 1);
  if(t === 'S'){ const c = DATA.find(c => edited(c).%s === s); return c ? sentItem(c) : null; }
  return STUDY.find(r => r.t === t && r.%s === s) || null;
}
function reviewPool(){
  const now = Date.now(), out = [], seen = new Set();
  const push = (it, src) => { const k = dKey(it); if(seen.has(k)) return; seen.add(k); it.src = src; out.push(it); };
  Object.entries(dState).forEach(([k, st]) => { if(st.due <= now){ const it = itemOfKey(k); if(it) push(it, '%s'); } });
  wrongs.forEach(k => { const it = itemOfKey(k); if(it) push(it, '%s'); });
  [...checked].forEach(id => { const c = cardOf(id); if(c && !dState['S|' + edited(c).%s]) push(sentItem(c), '%s'); });
  return out;
}
function paintReview(){ const n = reviewPool().length; $('nReview').textContent = n; return n; }
function renderReview(){
  const rows = reviewPool(); paintReview();
  $('rvInfo').textContent = rows.length ? ('%s ' + rows.length) : '%s';
  $('rvDrill').disabled = !rows.length; $('rvListen').disabled = !rows.length;
  const box = $('rvList'); box.textContent = '';
  rows.forEach(r => {
    const el = document.createElement('div'); el.className = 'srow';
    const tx = document.createElement('div'); tx.className = 'txt';
    const k = document.createElement('div'); k.className = 'k'; k.lang = '%s'; k.textContent = r.%s;
    const s = document.createElement('span'); s.className = 'src'; s.textContent = r.src; k.appendChild(s);
    if(r.rd && r.rd !== r.%s){ const sm = document.createElement('small'); sm.textContent = r.rd; k.appendChild(sm); }
    const j = document.createElement('div'); j.className = 'j'; j.textContent = r.%s;
    tx.append(k, j); el.appendChild(tx);
    if(r.cids && r.cids.length && !OFFLINE){
      const b = document.createElement('button'); b.className = 'btn btn-sm'; b.innerHTML = '<svg class="ic fill"><use href="#i-play"/></svg>';
      b.onclick = () => { const c = cardOf(r.cids[0]); if(c) playSeg(c); }; el.appendChild(b);
    }
    box.appendChild(el);
  });
}

''' % (SK, SRC, MEAN, A['drill'], A['allDrill'], A['expr'], A['word'], A['quiz'], A['expr'], A['expr'], A['word'], A['reviewDrill'], A['reviewListen'],
       SRC, SRC, SRC, MEAN, MEAN, SRC, SRC, A['dueTag'], A['wrongTag'], SRC, A['checkTag'], A['reviewWait'], A['noReview'], SRC, SRC, SRC, MEAN)
a_ = h.index('function setSub(kind){'); b_ = h.index('/* ======================', a_)
h = h[:a_] + NEW_SETSUB + h[b_:]; N += 1
rep('''function buildDays(){''', '''let stages = {}, studyDays = new Set();
function loadProgress(){ stages = store.get(SK('stages'), {}) || {}; wrongs = store.get(SK('wrongs'), []) || []; studyDays = new Set(store.get(SK('studyDays'), []) || []); }
function buildDays(){
  loadProgress();''')

NEW_RENDERDAY = '''/* ---- 4단계: 듣기 → 확인 → 따라 하기 → 점검. 진행은 stages[day][n] = {done,total} ---- */
const stGet = (day, n) => ((stages[day] || {})[n]) || {done: 0, total: 0};
const stDone = (day, n) => { const s = stGet(day, n); return s.total > 0 && s.done >= s.total; };
function stSet(day, n, done, total){
  stages[day] = stages[day] || {}; stages[day][n] = {done, total}; store.set(SK('stages'), stages); logToday();
  if([1,2,3,4].every(k => stDone(day, k)) && !daysDone.has(day)){ daysDone.add(day); store.set(SK('daysDone'), [...daysDone]); }
  if(!$('dayPane').hidden) renderDay();
}
const dayKeyOf = d => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
function logToday(){ const k = dayKeyOf(new Date()); if(!studyDays.has(k)){ studyDays.add(k); store.set(SK('studyDays'), [...studyDays]); } }
function streak(){
  let n = 0; const d = new Date();
  if(!studyDays.has(dayKeyOf(d))) d.setDate(d.getDate() - 1);
  while(studyDays.has(dayKeyOf(d))){ n++; d.setDate(d.getDate() - 1); }
  return n;
}
function stage3Ids(d){
  const want = new Set();
  d.cards.forEach(c => { if(checked.has(c.id)) want.add(c.id); });
  d.expr.forEach(r => { if(r.ex != null && d.cards.some(c => c.id === r.ex)) want.add(r.ex); });
  if(want.size < 3) d.cards.slice(0, 5).forEach(c => want.add(c.id));
  return d.cards.filter(c => want.has(c.id)).map(c => c.id);
}
const sceneName = c => { const s = SCENES.find(x => x.key === c.scene) || {}; return s.%s || s.label || s.ko || ''; };
const STAGES = [
  ['%s', '%s', d => d.cards.length + ' %s', d => Math.max(2, Math.round(d.cards.length * 0.3))],
  ['%s', '%s', d => '%s ' + d.expr.length + ' · %s ' + d.word.length + ' · %s', d => Math.max(1, Math.round((d.expr.length + d.word.length) * 0.7))],
  ['%s', '%s', d => stage3Ids(d).length + ' %s', d => Math.max(2, Math.round(stage3Ids(d).length * 1.2))],
  ['%s', '%s', d => '%s ' + Math.min(10, d.expr.length + d.word.length + d.cards.length) + ' %s', d => 4]
];
function startStage(n){
  const d = DAYS[dayCur - 1]; if(!d) return;
  const s = stGet(d.n, n), resume = (s.total && s.done < s.total) ? s.done : 0;
  if(n === 1) sessStart(1, d.cards.map(c => c.id), resume);
  else if(n === 3) sessStart(3, stage3Ids(d), resume);
  else if(n === 2){
    const cnt = openDrill('D', 'D', '2 %s', 2);
    if(!cnt){ stSet(d.n, 2, 1, 1); setSub('D'); return; }
    dStart(false);
  } else {
    const ok = openQuiz('D', 'D', '4 %s', 4);
    if(!ok){ stSet(d.n, 4, 1, 1); setSub('D'); return; }
    $('qStart').click();
  }
}
function renderDay(){
  const d = DAYS[dayCur - 1]; if(!d) return;
  dayIds = d.cards.map(c => c.id);
  $('dayNo').textContent = d.n;
  $('nDay').textContent = dayCur + '/' + DAYS.length;
  const names = [...new Set(d.cards.map(sceneName).filter(Boolean))];
  $('dayTitle').textContent = names.slice(0, 3).join(' · ') + (names.length > 3 ? ' …' : '');
  const done = d.cards.filter(c => checked.has(c.id)).length;
  $('dayMeta').textContent = fmt(d.cards[0].s) + ' – ' + fmt(d.cards[d.cards.length - 1].e) + (done ? ' · %s ' + done : '');
  $('dayDone').setAttribute('aria-pressed', String(daysDone.has(d.n)));
  $('dayPrev').disabled = dayCur <= 1; $('dayNext').disabled = dayCur >= DAYS.length;
  const prog = [1,2,3,4].reduce((a, n) => { const s = stGet(d.n, n); return a + (s.total ? Math.min(1, s.done / s.total) : 0); }, 0) / 4;
  $('dayBar').style.width = Math.round(prog * 100) + '%%';
  const bd = $('dayBadges'); bd.textContent = '';
  const mkB = (txt, cls) => { const s = document.createElement('span'); s.className = 'bdg' + (cls ? ' ' + cls : ''); s.textContent = txt; bd.appendChild(s); };
  const sk = streak(); if(sk) mkB('%s'.replace('{n}', sk), 'ok');
  mkB('%s ' + d.cards.length + ' · %s ' + d.expr.length + ' · %s ' + d.word.length);
  const rv = paintReview(); if(rv) mkB('%s ' + rv, 'acc');
  if(daysDone.has(d.n)) mkB('%s'.replace('{n}', d.n), 'ok');
  const strip = $('daystrip'); strip.textContent = '';
  DAYS.forEach(x => {
    const b = document.createElement('button');
    b.className = 'dbtn' + (daysDone.has(x.n) ? ' done' : '');
    b.textContent = x.n; b.setAttribute('aria-pressed', String(x.n === dayCur)); b.title = 'Day ' + x.n;
    b.onclick = () => { dayCur = x.n; store.set(SK('dayCur'), dayCur); renderDay(); };
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
    const sm = document.createElement('small'); sm.lang = '%s'; sm.textContent = ja; ti.appendChild(sm);
    el.querySelector('.mt').textContent = metaF(d) + ' · ' + minF(d) + ' %s';
    if(started){ const pb = document.createElement('div'); pb.className = 'pb'; pb.innerHTML = '<i></i>';
      pb.querySelector('i').style.width = Math.round(s.done / s.total * 100) + '%%'; el.querySelector('.bd').appendChild(pb); }
    const rt = el.querySelector('.rt');
    if(isDone){ const st = document.createElement('span'); st.className = 'st'; st.textContent = '%s ' + s.done + ' / ' + s.total; rt.appendChild(st); }
    const b = document.createElement('button'); b.className = 'btn btn-sm' + (now ? ' btn-primary' : '');
    b.textContent = isDone ? '%s' : started ? '%s ' + s.done + ' / ' + s.total : '%s';
    b.onclick = () => startStage(n);
    rt.appendChild(b);
    box.appendChild(el);
  });
  const list = (host, rows, render) => {
    const el = $(host); el.textContent = '';
    rows.forEach(r => { const b = document.createElement('button'); b.className = 'dcRow'; render(b, r); el.appendChild(b); });
    if(!rows.length){ const e = document.createElement('div'); e.className = 'sempty'; e.style.padding = '14px'; e.textContent = '—'; el.appendChild(e); }
  };
  $('dcN').textContent = d.cards.length;
  list('dcList', d.cards, (b, c) => {
    const v = edited(c);
    b.innerHTML = '<span class="tm"></span><span><span class="kk" lang="%s"></span> <span class="jj"></span></span>';
    b.querySelector('.tm').textContent = fmt(c.s);
    b.querySelector('.kk').textContent = v.%s.slice(0, 30);
    b.querySelector('.jj').textContent = (v.%s || '').slice(0, 26);
    b.onclick = () => playSeg(c);
  });
  const wordRow = (b, r) => {
    b.innerHTML = '<span><span class="kk" lang="%s"></span> <span class="jj"></span></span>';
    b.querySelector('.kk').textContent = r.%s;
    b.querySelector('.jj').textContent = (r.rd && r.rd !== r.%s ? r.rd + ' · ' : '') + r.%s;
    b.onclick = () => { const c = cardOf((r.cids || [])[0]); if(c) playSeg(c); };
  };
  $('deN').textContent = d.expr.length; list('deList', d.expr, wordRow);
  $('dvN').textContent = d.word.length; list('dvList', d.word, wordRow);
}
$('dayPrev').onclick = () => { if(dayCur > 1){ dayCur--; store.set(SK('dayCur'), dayCur); renderDay(); } };
$('dayNext').onclick = () => { if(dayCur < DAYS.length){ dayCur++; store.set(SK('dayCur'), dayCur); renderDay(); } };
$('dayDone').onclick = () => {
  daysDone.has(dayCur) ? daysDone.delete(dayCur) : daysDone.add(dayCur);
  store.set(SK('daysDone'), [...daysDone]); renderDay();
};

/* ====================== 세션: 1 듣기 · 3 따라 하기 (카드 뷰 안에서) ====================== */
let sess = null;
function sessStart(stage, ids, from){
  if(!ids.length){ stSet(dayCur, stage, 1, 1); return; }
  sess = {stage, ids, i: Math.min(from || 0, ids.length - 1), day: dayCur};
  %s buildDeck(); index = sess.i; showCard();
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
  $('sessName').textContent = 'DAY ' + sess.day + ' · ' + (sess.stage === 1 ? '1 %s' : '3 %s');
  $('sessPos').textContent = (index + 1) + ' / ' + n;
  $('sessBar').style.width = Math.round(index / n * 100) + '%%';
  $('sessA').innerHTML = sess.stage === 1 ? '<svg class="ic"><use href="#i-eye"/></svg>%s' : '<svg class="ic"><use href="#i-repeat"/></svg>%s';
  $('sessB').textContent = (sess.stage === 1 ? '%s' : '%s') + (index < n - 1 ? ' · %s ›' : ' · %s ✓');
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
  %s
  buildDeck(); switchView('study'); setSub('D');
}
$('sessQuit').onclick = () => sessEnd();
$('sessA').onclick = () => { if(!sess) return; if(sess.stage === 1) setReveal($('answer').hidden); else sessPlay(); };
$('sessB').onclick = () => sessNext();
''' % (
    'label' if L1 == 'ja' else ('ko' if L1 == 'ko' else 'en'),
    A['stages'][0], B['stages'][0], A['st1'],
    A['stages'][1], B['stages'][1], A['expr'], A['word'], A['st2'],
    A['stages'][2], B['stages'][2], A['st3'],
    A['stages'][3], B['stages'][3], A['st4'], A['items'],
    A['stages'][1], A['stages'][3],
    A['checkTag'], A['streak'], A['lines'], A['expr'], A['word'], A['reviewWait'], A['dayDone'],
    L2, A['minutes'], A['done'], A['again'], A['resume'], A['start'],
    SRC, SRC, MEAN, SRC, SRC, SRC, MEAN,
    SESS_FILT_ON, A['stages'][0], A['stages'][2], A['seeMean'], A['onceMore'], A['heard'], A['said'], A['next'], A['finish'], SESS_FILT_OFF)
a_ = h.index('function renderDay(){'); b_ = h.index("segWire('qPace'")
h = h[:a_] + NEW_RENDERDAY + h[b_:]; N += 1

# 퀴즈: 종류(t) · 복습 범위 · 단계 기록 · 오답 → 복습
rep_re(r"\(\{%s: r\.%s, ((?:rd: r\.rd, )?)%s: r\.%s, note: r\.note, cids: r\.cids \|\| \[\]\}\)" % (SRC, SRC, MEAN, MEAN),
       r"({t: r.t, %s: r.%s, \1%s: r.%s, note: r.note, cids: r.cids || []})" % (SRC, SRC, MEAN, MEAN), count=2)
rep_re(r"\(\{%s: edited\(c\)\.%s, ((?:rd: edited\(c\)\.rd, )?)%s: edited\(c\)\.%s, cids: \[c\.id\]\}\)" % (SRC, SRC, MEAN, MEAN),
       r"({t: 'S', %s: edited(c).%s, \1%s: edited(c).%s, cids: [c.id]})" % (SRC, SRC, MEAN, MEAN), count=2)
rep('''function quizPool(){''', '''function quizPool(){
  if(qScope === 'W') return reviewPool().map(r => ({t: r.t, %s: r.%s, rd: r.rd, %s: r.%s, note: r.note, cids: r.cids || []}));''' % (SRC, SRC, MEAN, MEAN))
rep('''function finishQ(){
  $('qplay').hidden = true; $('qdone').hidden = false;''', '''function finishQ(){
  $('qplay').hidden = true; $('qdone').hidden = false;
  qWrong.forEach(it => wrongAdd(it)); paintReview();
  if(qStage){ stSet(dayCur, qStage, qSet.length, qSet.length); qStage = 0; }''')
rep('''$('qQuit').onclick = () => { $('qplay').hidden = true; $('qsetup').hidden = false; };''', '''$('qQuit').onclick = () => { qStage = 0; setSub(qFrom); };''')
rep('''$('rBack').onclick = () => { $('qdone').hidden = true; $('qsetup').hidden = false; };''', '''$('rBack').onclick = () => setSub(qFrom);''')
# 드릴
rep_re(r"(  if\(scope === 'D'\)\{[^\n]*\n)", r"\1  if(scope === 'W') return reviewPool();\n")
rep_re(r"  \$\('nDrill'\)\.textContent = due \+ fresh;\n", "  paintReview();\n")
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
rep_re(r"\(it\.t === 'E' \? '([^']*)' : '([^']*)'\)", r"(it.t === 'E' ? '\1' : it.t === 'S' ? '%s' : '\2')" % A['lines'], count=2)
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
rep_re(r"\$\('dQuit'\)\.onclick = \(\) => \{[^\n]*\n", "$('dQuit').onclick = () => { dActive = false; drillStopAuto(); dStage = 0; setSub(dFrom); };\n")
rep_re(r"\$\('dRestartAll'\)\.onclick = \(\) => \{[^\n]*\n", "$('dRestartAll').onclick = () => { $('ddone').hidden = true; dStart(false); };\n$('dDoneBack').onclick = () => { dStage = 0; setSub(dFrom); };\n")
rep_re(r"  if\(dAutoOn\)\{ drillStopAuto\(\); \$\('dplay'\)\.hidden = true;[^\n]*\n", "  if(dAutoOn){ drillStopAuto(); dStage = 0; setSub(dFrom); return; }\n")

# ══════════════════ 7. 기동 ══════════════════
if 'buildDays(); renderDay(); syncQuizUI(); loadAPI();' in h:
    rep('buildDays(); renderDay(); syncQuizUI(); loadAPI();', "buildDays(); setSub('D'); syncQuizUI(); paintMini(); loadAPI();")
open(path, 'w', encoding='utf-8').write(h)
print('ported', app, 'steps', N)
