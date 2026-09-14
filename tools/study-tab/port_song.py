#!/usr/bin/env python3
"""노래 앱 이식: firstlove-cards 에 적용한 학습 탭 개편·큐 버튼·읽어주기·버튼 정리·노래방 통합을
다른 계열의 노래 템플릿(reasons·vitaminme·saranghagi)에 옮긴다. 라벨 언어·가사 필드·드릴 유무는 CFG 로.

  사용: python3 tools/study-tab/port_song.py <앱폴더>     (src/tpl.html 을 제자리에서 고친다. 한 번만.)
"""
import sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
app = sys.argv[1].strip('/')
path = os.path.join(ROOT, app, 'src', 'tpl.html')
h = open(path, encoding='utf-8').read()
assert 'id="cardfoot"' not in h, '이미 이식된 템플릿'
N = 0

CFG = {
  'reasons-cards':   dict(L1='ko', L2='en', SRC='en', MEAN='ko', RD=False, DRILL=False, PK=False, KRD_OPT=None, KRD_EL=None, VOICE='en', PACE_PH=True),
  'vitaminme-cards': dict(L1='ja', L2='ko', SRC='ko', MEAN='ja', RD=True,  DRILL=False, PK=True,  KRD_OPT='karaRd',    KRD_EL='karaRdLine', VOICE='ko', PACE_PH=False),
  'saranghagi-cards':dict(L1='ja', L2='ko', SRC='ko', MEAN='ja', RD=False, DRILL=True,  PK=True,  KRD_OPT='karaRdOpt', KRD_EL='karaRd',     VOICE='ko', PACE_PH=False),
}[app]
SRC, MEAN, L1, L2 = CFG['SRC'], CFG['MEAN'], CFG['L1'], CFG['L2']
DRILL, PK = CFG['DRILL'], CFG['PK']

T = {
 'ko': dict(today='오늘', review='복습', list='목록', guide='학습법', back='돌아가기', settings='설정 ⚙', start='시작', resume='이어서', again='다시',
            done='완료', all='전부', expr='표현', word='단어', drill='드릴', quiz='퀴즈', reviewStart='복습 시작', listenOnly='듣기만',
            play='재생', stop='정지', loop='반복', prev='이전', next='다음', prevLine='이전 줄', nextLine='다음 줄', toCards='카드로',
            onceMore='한 번 더', fromHere='이 줄부터 다시', sang='불렀다', read='읽었다', finish='끝내기', hideMean='뜻 끄기', hideRd='읽기 끄기', firstChar='첫 글자만',
            fine='미세 조정', length='길이', speed='속도', tts='읽어주기', slow='천천히', x3='3회', minutes='분', lines='줄',
            stages=['들으며 읽기', '마디 따라 부르기', '가사 가리고 부르기', '표현 · 단어'],
            st1meta='줄 · 읽기·뜻 보며 한 번', st2meta='줄 · 줄마다 마디 반복 · 2 › 4 › 8마디', st3meta='줄 · 뜻 끄기 › 읽기 끄기 › 첫 글자만',
            st4drill='드릴', st4quiz='퀴즈', streak='연속 {n}일', reviewWait='복습 대기', partDone='PART {n} 완료', dueTag='기한', wrongTag='오답', checkTag='체크',
            noReview='오늘 복습할 것이 없습니다', thisLineBars='이 줄의 마디', barStart='마디 시작', minus1='−1마디', plus1='＋1마디',
            beatM='−1박', beatP='+1박', allDrill='표현·단어 전부', reviewDrill='복습 · 드릴', reviewListen='복습 · 듣기만', reviewQuiz='복습 · 퀴즈',
            karaTap='지금 줄을 누르면 그 줄의 마디를 반복합니다.',
            gTitle='노래 한 곡을 「부를 수 있는 말」로 바꾸는 4단계',
            gNote='이 교재는 교과서가 아니라 <b>노래 가사</b>입니다. 멜로디에 실린 말은 문장보다 오래 남습니다. 「읽어서 이해」로 끝내지 말고 <b>따라 부를 수 있을 때까지</b> 가는 것이 목표입니다. 「오늘」 탭이 절·후렴 단위로 4단계를 안내합니다.',
            gsteps=[('들으며 읽기', '읽기·뜻을 켜고 단락을 한 번 듣는다. 어디서 숨을 쉬는지, 어느 말이 길게 늘어나는지 본다.'),
                    ('마디 따라 부르기', '줄마다 마디 반복을 걸고 소리 내어 겹친다. 2 → 4 → 8마디, 0.75 → 1×.'),
                    ('가사 가리고 부르기', '뜻 끄기 → 읽기 끄기 → 첫 글자만. 막힘 없이 부를 수 있으면 「불렀다」.'),
                    ('표현 · 단어', '가사에서 뽑은 표현·단어를 따로 익힌다. 틀린 것은 복습 탭으로 간다.')],
            gtips=[('한 단락씩', '한 곡을 한 번에 외우려 하지 마세요. 「오늘」 탭이 <b>절·후렴 단위</b>로 잘라 줍니다. 후렴부터 시작해도 좋습니다.'),
                   ('마디로 쪼개기', '노래방 탭에서 <b>지금 줄을 누르면 그 줄의 마디만 반복</b>됩니다. 2마디 → 4마디 → 8마디로 늘리고, 속도는 0.75× 에서 1× 로 올리세요.'),
                   ('소리 내어 겹치기', '듣기만 하면 늘지 않습니다. 반복되는 동안 <b>원곡 위에 목소리를 겹쳐</b> 부르세요. 음정보다 <b>박자와 발음</b>이 먼저입니다.'),
                   ('가사를 가리기', '3단계는 <b>뜻 끄기 → 읽기 끄기 → 첫 글자만</b> 순으로 가립니다. 막히는 줄은 「한 번 더」, 막힘 없이 부를 수 있으면 「불렀다」.'),
                   ('틀린 것이 보물', '틀린 항목과 체크한 줄은 「복습」 탭에 모입니다. <b>다음 날 맨 처음</b>에 그것만 다시 부르세요.')]),
 'ja': dict(today='今日', review='復習', list='一覧', guide='学習法', back='戻る', settings='設定 ⚙', start='始める', resume='続き', again='もう一度',
            done='完了', all='全部', expr='表現', word='単語', drill='ドリル', quiz='クイズ', reviewStart='復習を始める', listenOnly='聞くだけ',
            play='再生', stop='停止', loop='リピート', prev='前へ', next='次へ', prevLine='前の行', nextLine='次の行', toCards='カードへ',
            onceMore='もう一度', fromHere='この行から', sang='歌えた', read='読めた', finish='終える', hideMean='意味なし', hideRd='読みなし', firstChar='頭文字だけ',
            fine='微調整', length='長さ', speed='速さ', tts='読み上げ', slow='ゆっくり', x3='3回', minutes='分', lines='行',
            stages=['聞いて読む', '小節で歌う', '歌詞を隠す', '表現・単語'],
            st1meta='行 · 読み・意味を見ながら一度', st2meta='行 · 行ごとに小節リピート · 2 › 4 › 8小節', st3meta='行 · 意味なし › 読みなし › 頭文字だけ',
            st4drill='ドリル', st4quiz='クイズ', streak='{n}日連続', reviewWait='復習待ち', partDone='PART {n} 完了', dueTag='期限', wrongTag='不正解', checkTag='チェック',
            noReview='今日の復習はありません', thisLineBars='この行の小節', barStart='小節の頭', minus1='−1小節', plus1='＋1小節',
            beatM='−1拍', beatP='+1拍', allDrill='表現・単語 全部', reviewDrill='復習 · ドリル', reviewListen='復習 · 聞くだけ', reviewQuiz='復習 · クイズ',
            karaTap='今の行をタップするとその小節をリピートします。',
            gTitle='歌1曲を「歌える言葉」に変える4ステップ',
            gNote='この教材は教科書ではなく<b>歌詞</b>です。メロディーに乗った言葉は文より長く残ります。「読んで分かる」で終わらせず、<b>歌えるようになるまで</b>が目標です。「今日」タブが1番・サビの単位で4ステップを案内します。',
            gsteps=[('聞いて読む', '読みと意味を表示して1番を一度聞く。どこで息を継ぎ、どの言葉が伸びるかを見る。'),
                    ('小節で歌う', '行ごとに小節リピートをかけて声を重ねる。2 → 4 → 8小節、0.75 → 1×。'),
                    ('歌詞を隠す', '意味なし → 読みなし → 頭文字だけ。詰まらず歌えたら「歌えた」。'),
                    ('表現・単語', '歌詞から拾った表現・単語を別に覚える。間違いは復習タブへ。')],
            gtips=[('1番ずつ', '1曲を一度に覚えようとしないで。「今日」タブが<b>1番・サビの単位</b>に切ってくれます。サビから始めても構いません。'),
                   ('小節で刻む', 'カラオケタブで<b>今の行をタップするとその小節だけリピート</b>。2 → 4 → 8小節と伸ばし、速さは 0.75× から 1× へ。'),
                   ('声を重ねる', '聞くだけでは伸びません。リピート中に<b>原曲に声を重ねて</b>歌ってください。音程より<b>リズムと発音</b>が先です。'),
                   ('歌詞を隠す', '3ステップ目は<b>意味なし → 読みなし → 頭文字だけ</b>の順に隠します。詰まる行は「もう一度」、詰まらず歌えたら「歌えた」。'),
                   ('間違いは宝', '間違えた項目とチェックした行は「復習」タブに集まります。<b>翌日の最初</b>にそこだけ歌い直しましょう。')]),
 'en': dict(today='Today', review='Review', list='List', guide='How to', back='Back', settings='Settings ⚙', start='Start', resume='Resume', again='Again',
            done='Done', all='All', expr='Expressions', word='Words', drill='Drill', quiz='Quiz', reviewStart='Start review', listenOnly='Listen only',
            play='Play', stop='Stop', loop='Loop', prev='Prev', next='Next', prevLine='Prev line', nextLine='Next line', toCards='Cards',
            onceMore='Once more', fromHere='From this line', sang='Sang it', read='Read it', finish='Finish', hideMean='No meaning', hideRd='No reading', firstChar='First letters',
            fine='Fine-tune', length='Length', speed='Speed', tts='Read aloud', slow='Slow', x3='×3', minutes='min', lines='lines',
            stages=['Listen & read', 'Sing by bars', 'Sing with lyrics hidden', 'Expressions & words'],
            st1meta='lines · once, with meaning shown', st2meta='lines · loop the bars of each line · 2 › 4 › 8 bars', st3meta='lines · hide meaning › first letters only',
            st4drill='drill', st4quiz='quiz', streak='{n}-day streak', reviewWait='to review', partDone='PART {n} done', dueTag='due', wrongTag='missed', checkTag='checked',
            noReview='Nothing to review today', thisLineBars='Bars of this line', barStart='Bar start', minus1='−1 bar', plus1='+1 bar',
            beatM='−1 beat', beatP='+1 beat', allDrill='all expressions & words', reviewDrill='Review · drill', reviewListen='Review · listen', reviewQuiz='Review · quiz',
            karaTap='Tap the current line to loop its bars.',
            gTitle='Four steps from a song to words you can sing',
            gNote='These are <b>song lyrics</b>, not a textbook. Words carried by a melody stay longer than sentences. Do not stop at understanding; the goal is <b>to be able to sing along</b>. The Today tab guides you through four steps, one verse or chorus at a time.',
            gsteps=[('Listen & read', 'Show reading and meaning and listen to the section once. Notice where the breaths are and which words are stretched.'),
                    ('Sing by bars', 'Loop the bars of each line and sing over the original. 2 → 4 → 8 bars, 0.75 → 1×.'),
                    ('Lyrics hidden', 'Hide the meaning, then keep only the first letters. When you can sing it without stalling, press Sang it.'),
                    ('Expressions & words', 'Learn the expressions and words picked from the lyrics separately. Misses go to the Review tab.')],
            gtips=[('One section at a time', 'Do not try to memorize the whole song at once. The Today tab splits it into <b>verses and choruses</b>. Starting from the chorus is fine.'),
                   ('Cut it into bars', 'In the karaoke tab, <b>tap the current line to loop just its bars</b>. Grow from 2 to 4 to 8 bars and raise the speed from 0.75× to 1×.'),
                   ('Sing over it', 'Listening alone will not do it. While the loop runs, <b>sing over the original</b>. Rhythm and pronunciation come before pitch.'),
                   ('Hide the lyrics', 'Step 3 hides the meaning, then shows only first letters. Use Once more when you stall, Sang it when you get through.'),
                   ('Misses are treasure', 'Missed items and checked lines gather in the Review tab. <b>Start the next day</b> by singing just those.')]),
}
A, B = T[L1], T[L2]
def bl(k): return A[k] + ' · ' + B[k]
def lbl(k): return '<span class="lbl">%s<span class="sub" lang="%s">%s</span></span>' % (A[k], L2, B[k])
def sub2(a, b): return '%s<span class="sub" lang="%s">%s</span>' % (a, L2, b)

def rep(old, new, count=1):
    global h, N
    c = h.count(old)
    assert c == count, f'[{N}] expected {count}, found {c}: {old[:80]!r}'
    h = h.replace(old, new); N += 1
def rep_re(pat, new, count=1, flags=0):
    global h, N
    c = len(re.findall(pat, h, flags))
    assert c == count, f'[{N}] regex expected {count}, found {c}: {pat[:80]!r}'
    h = re.sub(pat, new, h, count=count, flags=flags); N += 1
def slice_rep(start, end, new, inclusive_end=False):
    global h, N
    a = h.index(start); b = h.index(end, a + len(start))
    if inclusive_end: b += len(end)
    h = h[:a] + new + h[b:]; N += 1

def has_id(i): return ('id="%s"' % i) in h

# ══════════════════ 1. 아이콘 · 홈 버튼 · 상단 탭 ══════════════════
rep('''<symbol id="i-info" viewBox="0 0 24 24">''', '''<symbol id="i-home" viewBox="0 0 24 24"><path d="M3 11.5L12 4l9 7.5M5.5 10v10h13V10"/></symbol>
<symbol id="i-stop" viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="1.5"/></symbol>
<symbol id="i-bars" viewBox="0 0 24 24"><path d="M4 5v14M10 5v14M16 5v14M22 5v14M4 12h18"/></symbol>
<symbol id="i-info" viewBox="0 0 24 24">''')
rep('''   <div class="tabs">
    <button class="tab" id="tabCard" aria-pressed="true">''', '''   <div class="tabs">
    <a class="tab home" href="../" title="메인으로 · 모든 학습 콘텐츠 / メインへ / Home" aria-label="home"><svg class="ic"><use href="#i-home"/></svg></a>
    <button class="tab" id="tabCard" aria-pressed="true">''')

# ══════════════════ 2. 카드 뷰: 상단 아이콘(체크·편집·마디), 읽어주기 줄, 조작 줄 ══════════════════
rep('''      <span class="meta"><span id="pos">0 / 0</span> · <span id="time">0:00</span></span>
     </div>''', '''      <span class="ctl">
       <span class="meta"><span id="pos">0 / 0</span> · <span id="time">0:00</span></span>
       <button class="ibtn" id="check" aria-pressed="false" title="%s"><svg class="ic"><use href="#i-check"/></svg></button>
       <button class="ibtn" id="edit" title="%s"><svg class="ic"><use href="#i-pencil"/></svg></button>
       <button class="ibtn ibtn-kara" id="toKara" title="%s"><svg class="ic"><use href="#i-bars"/></svg></button>
      </span>
     </div>''' % (bl('checkTag'), '편집 / 編集 / Edit', bl('thisLineBars')))
rep_re(r'      <button class="btn" id="check" aria-pressed="false">.*?</button>\n      <button class="btn" id="edit">.*?</button>\n', '', flags=re.S)
# 읽어주기 줄: 본문(+읽기, +원문) 바로 아래
m = re.search(r'     <div class="%s" id="%s" lang="%s">[^<]*</div>\n(?:     <p class="rd"[^\n]*\n)?(?:     <p class="raw"[^\n]*\n)?' % (SRC, SRC, SRC), h)
assert m, '본문 요소를 못 찾음'
TTSROW = '''     <div class="ttsrow">
      <button class="btn btn-sm" id="ttsPlay" title="T"><svg class="ic"><use href="#i-sound"/></svg>%s</button>
      <button class="btn btn-sm" id="ttsSlow" title="0.75×">%s</button>
      <button class="btn btn-sm" id="ttsRep" title="×3">%s</button>
      <button class="btn btn-sm" id="ttsVol" title="읽어주기 음량">🔉</button>
      <button class="btn btn-sm" id="ttsStop"><svg class="ic fill"><use href="#i-stop"/></svg></button>
     </div>
''' % (A['tts'], A['slow'], A['x3'])
h = h[:m.end()] + TTSROW + h[m.end():]; N += 1
# 마디 반복 상자는 카드에서 빼서 노래방으로
a_ = h.index('     <div class="bars" id="barBox" hidden>'); b_ = h.index('     <div class="edit" id="editBox" hidden>')
h = h[:a_] + h[b_:]; N += 1
# 조작 줄(‹ 재생 정지 반복 ›)
rep('''     <div class="opts">
      <label><input type="checkbox" id="optAuto">''', '''     <div class="cardfoot" id="cardfoot">
      <button class="btn" id="cfPrev"><svg class="ic"><use href="#i-left"/></svg><span class="txt">%s</span></button>
      <button class="btn btn-primary" id="cfPlay"><svg class="ic fill"><use href="#i-play"/></svg>%s</button>
      <button class="btn" id="cfStop"><svg class="ic fill"><use href="#i-stop"/></svg>%s</button>
      <button class="btn" id="cfLoop" aria-pressed="false"><svg class="ic"><use href="#i-repeat"/></svg>%s</button>
      <button class="btn" id="cfNext"><span class="txt">%s</span><svg class="ic"><use href="#i-right"/></svg></button>
     </div>

     <div class="opts">
      <label><input type="checkbox" id="optAuto">''' % (A['prev'], A['play'], A['stop'], A['loop'], A['next']))
# 플레이어: 모바일 미니 바
rep('''   <div class="player-box">
    <div class="ratio" id="ratio"><div id="player"></div></div>''', '''   <div class="player-box">
    <div class="minibar" id="minibar" hidden>
     <button class="pl" id="mbToggle">▶</button>
     <button class="t" id="mbOpen"><b id="mbTitle">—</b><span id="mbSub">▶ %s</span></button>
     <span class="meta" id="mbTime">0:00</span>
    </div>
    <div class="ratio" id="ratio"><div id="player"></div></div>''' % bl('toCards'))

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
if DRILL:
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
        <span class="dno">PART <b id="dayNo">1</b><i>/<span id="dayTot">5</span></i></span>
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
RV_BTNS = ('''       <button class="btn btn-primary btn-sm" id="rvDrill"><svg class="ic fill"><use href="#i-play"/></svg>%s</button>''' % lbl('reviewStart')) if DRILL else \
          ('''       <button class="btn btn-primary btn-sm" id="rvQuiz"><svg class="ic"><use href="#i-check"/></svg>%s</button>''' % lbl('reviewQuiz'))
rep('''     <div id="guidePane" hidden>''', '''     <div id="reviewPane" hidden>
      <div class="rvhead">
       <span class="meta" id="rvInfo">—</span>
%s
       <button class="btn btn-sm" id="rvListen"><svg class="ic"><use href="#i-sound"/></svg>%s</button>
      </div>
      <div class="slist" id="rvList"></div>
     </div>

     <div id="guidePane" hidden>''' % (RV_BTNS, bl('listenOnly')))
rep('''       <span class="meta" id="sCount">0</span>''', '''       <span class="meta" id="sCount">0</span>
       <div class="seg" id="lKind"><button data-v="A" aria-pressed="true">%s</button><button data-v="E" aria-pressed="false">%s</button><button data-v="V" aria-pressed="false">%s</button></div>
%s       <button class="btn btn-sm%s" id="lQuiz"><svg class="ic"><use href="#i-check"/></svg>%s</button>''' % (
    A['all'], A['expr'], A['word'],
    ('       <button class="btn btn-sm btn-primary" id="lDrill"><svg class="ic fill"><use href="#i-play"/></svg>%s</button>\n' % A['drill']) if DRILL else '',
    '' if DRILL else ' btn-primary', A['quiz']))
rep('''     <div id="quizPane" hidden>
      <div class="qsetup" id="qsetup">''', '''     <div id="quizPane" hidden>
''' + DBAR('qBackBtn', 'qTitle', 'qSetBtn', A['quiz']) + '''      <div class="qsetup" id="qsetup" hidden>''')

# 학습법: 노래용
slice_rep('       <div class="gintro">', '       <div class="gsteps" id="gsteps"></div>', '''       <div class="gintro">
        <p class="eyebrow">How to study</p>
        <h3>%s</h3>
        <p lang="%s">%s</p>
        <p class="gnote">%s<span lang="%s">%s</span></p>
       </div>
''' % (A['gTitle'], L2, B['gTitle'], A['gNote'], L2, B['gNote']))
tips = ''.join('''        <div class="gtip"><h5>%s · %s</h5>
         <p>%s<span lang="%s">%s</span></p></div>
''' % (a[0], b[0], a[1], L2, b[1]) for a, b in zip(A['gtips'], B['gtips']))
slice_rep('       <div class="gtips">', '     <div id="listPane" hidden>', '''       <div class="gtips">
%s       </div>
      </div>
     </div>

''' % tips)
G = ',\n'.join("    ['%s', '%s', '%s', '%s', '%s › %d']" % (a[0], b[0], a[1].replace("'", "’"), b[1].replace("'", "’"), A['today'], i + 1)
               for i, (a, b) in enumerate(zip(A['gsteps'], B['gsteps'])))
slice_rep('  const G = [', '  ];', '  const G = [\n' + G + '\n  ];', inclusive_end=True)

# ══════════════════ 4. 노래방 마크업 ══════════════════
rep('''     <div class="kara-top">
      <button class="btn btn-primary btn-sm" id="karaStart">''', '''     <div class="kara-top">
      <button class="btn btn-sm" id="karaBack"><svg class="ic"><use href="#i-left"/></svg>%s</button>
      <button class="btn btn-primary btn-sm" id="karaStart">''' % lbl('toCards'))
rep('''      <span class="meta" id="karaPos">—</span>
     </div>''', '''      <span class="meta" id="karaPos">—</span>
     </div>
     <div class="sessbar" id="ksbar" hidden>
      <button class="btn btn-sm" id="ksQuit"><svg class="ic"><use href="#i-x"/></svg></button>
      <b id="ksName">—</b>
      <div class="bar"><span id="ksBar" style="width:0"></span></div>
      <span class="meta" id="ksPos">0 / 0</span>
     </div>
     <div class="seg kmask" id="kmask" hidden>
      <button data-v="1" aria-pressed="true">%s</button><button data-v="2" aria-pressed="false">%s</button><button data-v="3" aria-pressed="false">%s</button>
     </div>''' % (A['hideMean'], A['hideRd'], A['firstChar']))
rep('''     <div class="kara-bar"><span id="karaBar"></span></div>
    </div>''', '''     <div class="kara-bar"><span id="karaBar"></span></div>
     <div class="kfix" id="kfix">
      <div class="bars" id="barBox" hidden>
       <div class="bars-row">
        <span class="cap">%s</span>
        <div class="seg" id="barLen"><button data-v="1" aria-pressed="false">1</button><button data-v="2" aria-pressed="true">2</button><button data-v="4" aria-pressed="false">4</button><button data-v="8" aria-pressed="false">8</button></div>
        <span class="cap">%s</span>
        <div class="seg" id="rate"><button data-v="0.5">0.5</button><button data-v="0.75">0.75</button><button data-v="1" aria-pressed="true">1×</button></div>
        <button class="btn btn-sm" id="barPrev">◀</button><button class="btn btn-sm" id="barNext">▶</button>
        <button class="btn btn-sm" id="barStop" disabled>■</button>
        <button class="btn btn-sm" id="barFine" aria-pressed="false">%s ▾</button>
        <span class="meta" id="barInfo">—</span>
       </div>
       <div class="bars-row" id="barFineRow" hidden>
        <button class="btn btn-sm btn-primary" id="barLine"><svg class="ic"><use href="#i-repeat"/></svg>%s</button>
        <button class="btn btn-sm" id="barLess">%s</button><button class="btn btn-sm" id="barMore">%s</button>
        <span class="cap" style="margin-left:6px">%s</span>
        <button class="btn btn-sm" id="barShiftM">%s</button><button class="btn btn-sm" id="barShiftP">%s</button>
       </div>
       <div class="barlyrics" id="barLyrics"></div>
      </div>
      <div class="sessfoot knav" id="knav">
       <button class="btn knback" id="knBack"><svg class="ic"><use href="#i-left"/></svg></button>
       <button class="btn" id="knPrev"><svg class="ic"><use href="#i-left"/></svg>%s</button>
       <button class="btn btn-primary" id="knPlay"><svg class="ic fill"><use href="#i-play"/></svg>%s</button>
       <button class="btn" id="knStop"><svg class="ic fill"><use href="#i-stop"/></svg>%s</button>
       <button class="btn" id="knNext">%s<svg class="ic"><use href="#i-right"/></svg></button>
      </div>
      <div class="sessfoot" id="ksfoot" hidden>
       <button class="btn" id="ksA">%s</button>
       <button class="btn btn-primary" id="ksB">%s</button>
      </div>
     </div>
    </div>''' % (A['length'], A['speed'], A['fine'], A['thisLineBars'], A['minus1'], A['plus1'], A['barStart'], A['beatM'], A['beatP'],
                 A['prevLine'], A['play'], A['stop'], A['nextLine'], A['onceMore'], A['sang']))
rep_re(r'    <div class="status">(가사는|歌詞は)[^\n]*\n[^\n]*</div>', '    <div class="status">%s <span class="sub" lang="%s">%s</span></div>' % (A['karaTap'], L2, B['karaTap']), flags=re.S)

# ══════════════════ 5. CSS ══════════════════
rep('''.tab[aria-pressed="true"]{background:var(--surface);color:var(--brand);font-weight:600;box-shadow:var(--sh-1)}''',
    '''.tab[aria-pressed="true"]{background:var(--surface);color:var(--brand);font-weight:600;box-shadow:var(--sh-1)}
.tab.home{flex:0 0 auto;padding:6px 10px;text-decoration:none;color:var(--ink-3);border-right:1px solid var(--line-2);border-radius:7px 0 0 7px;margin-right:2px}
.tab.home:hover{color:var(--brand)}''')
rep('''.tabs{margin-left:0;width:100%}.tab{flex:1;justify-content:center;padding:6px 8px}''',
    '''.tabs{margin-left:0;width:100%;gap:2px}.tab{flex:1;justify-content:center;padding:6px 4px;gap:0}.tab>.ic{display:none}.tab.home{flex:0 0 auto;padding:6px 9px}.tab.home>.ic{display:block}''')
rep_re(r'\.subtabs \.tab\{flex:1 1 30%[^}]*\}', '.subtabs .tab{flex:1 1 0;justify-content:center;padding:7px 2px;gap:4px}')
rep_re(r'\.kara-line\{([^}]*?)\n color:#b8bfd2;background-image:[^\n]*\n[^\n]*\}', r'''.kara-line{\1 color:#b8bfd2}
.kara-line .kc{color:#b8bfd2}
.kara-line .kc.on{color:#ffd166}
.kara-line .kc.part{background-image:linear-gradient(90deg,#ffd166 0,#ffd166 var(--q,0%),#b8bfd2 var(--q,0%),#b8bfd2 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}''')
rep('''.kara-bar span{display:block;height:100%;width:0;background:#ffd166}''', '''.kara-bar span{display:block;height:100%;width:0;background:#ffd166}
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
.kara .knav{grid-template-columns:auto 1fr 1.2fr .9fr 1fr;gap:6px}
.kara .knav .knback{padding:0 10px}
.kara .knav .btn{min-height:42px;justify-content:center;font-size:12.5px;padding:8px 4px}
.kara-line{cursor:pointer}
@media(max-width:600px){
 #karaView .kfix{position:fixed;left:0;right:0;bottom:0;z-index:7;background:#14171f;border-top:1px solid #2c3150;padding:8px 10px calc(8px + env(safe-area-inset-bottom));margin:0;gap:6px}
 #karaView .kara{padding-bottom:150px}
 .kara .bars .meta{flex:1 1 100%;margin-left:0}
 .kara .kmask{align-self:stretch}.kara .kmask button{flex:1;padding:6px 4px;font-size:11px}
}''')
CSS = '''
/* ---- 학습 탭 개편 · 조작 줄 · 읽어주기 · 미니 플레이어 (port_song) ---- */
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
.btn.holding{background:var(--accent);border-color:var(--accent);color:#fff}
.cue{touch-action:manipulation;user-select:none;-webkit-user-select:none;-webkit-touch-callout:none}
.ttsrow{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:12px 0 0}
.ttsrow .btn[aria-pressed=true]{background:var(--brand-soft);border-color:var(--brand-line);color:var(--brand)}
.card-top .ctl{display:inline-flex;align-items:center;gap:6px;flex:none}
.ibtn{display:inline-grid;place-items:center;width:30px;height:30px;padding:0;border-radius:8px;border:1px solid var(--line-2);background:var(--surface);color:var(--ink-2)}
.ibtn .ic{width:15px;height:15px}
.ibtn:hover{color:var(--brand);border-color:var(--brand-line)}
.ibtn[aria-pressed=true]{background:var(--brand);border-color:var(--brand);color:#fff}
.ibtn-kara{background:var(--brand-soft);border-color:var(--brand-line);color:var(--brand)}
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
 .card .keys{display:none}
 .playrow .btn{flex:1 1 100%;margin-top:12px}
}
</style>'''
rep('\n</style>', CSS)

# ══════════════════ 6. JS: 플레이어·카드 ══════════════════
rep_re(r"(if\(e\.data === YT\.PlayerState\.PLAYING\) \$\('playStatus'\)\.innerHTML = bi\([^\n]*;)",
       r"\1\n        $('mbToggle').textContent = e.data === YT.PlayerState.PLAYING ? '❚❚' : '▶';")
rep_re(r"(  const t = player\.getCurrentTime\(\);\n)(  if\(loopSeg && loopSeg\.from != null\) syncBarLyric\(dispT\(t\)\);)",
       r"\1  if(!$('minibar').hidden){ $('mbTime').textContent = fmt(t); const d = deck[index]; $('mbTitle').textContent = (stopAt !== null && d) ? edited(d).%s : document.title.split(' — ')[0].split(' · ')[0]; }\n\2" % SRC)
rep_re(r"(  if\(v === 'script' && deck\[index\]\) highlight\(deck\[index\]\.id\);\n(?:  if\(v === 'kara'\)[^\n]*\n)?)\}", r"\1  paintMini();\n}")
rep("$('tabKara').onclick = () => switchView('kara');", '''$('tabKara').onclick = () => switchView('kara');
const mqMobile = window.matchMedia('(max-width:600px)');
function paintMini(){
  const on = view === 'study' && mqMobile.matches && !OFFLINE;
  document.body.classList.toggle('mini', on);
  $('minibar').hidden = !on;
}
mqMobile.addEventListener('change', paintMini);
$('mbToggle').onclick = () => { if(!(player && ready)) return; player.getPlayerState() === 1 ? player.pauseVideo() : player.playVideo(); };
$('mbOpen').onclick = () => switchView('card');''')
rep('''  $('prev').disabled = index === 0;
  $('next').disabled = index === deck.length-1;''', '''  $('prev').disabled = index === 0;
  $('next').disabled = index === deck.length-1;
  $('cfPrev').disabled = index === 0; $('cfNext').disabled = index === deck.length-1;''')
rep('''  $('loop').setAttribute('aria-pressed', String(!!loopSeg));
}''', '''  $('loop').setAttribute('aria-pressed', String(!!loopSeg));
  $('cfLoop').setAttribute('aria-pressed', String(!!loopSeg));
}''')

# 음원 엔진: 없는 앱(reasons·vitaminme)에는 최소 엔진(로컬 음원 + 브라우저 음성)을 넣는다
if 'function aPlay(' not in h:
    ENGINE = '''
/* ====================== 음원 / 音源 ====================== */
const AUDIO = /*__AUDIO__*/;
const aKey = t => (t || '').replace(/[〜～]/g, '').replace(/[（(][^）)]*[）)]/g, '').replace(/\\s+/g, ' ').trim();
let aCur = null, aSeq = 0, aVoices = [];
if('speechSynthesis' in window){ aVoices = speechSynthesis.getVoices(); speechSynthesis.onvoiceschanged = () => { aVoices = speechSynthesis.getVoices(); }; }
function aStopAll(){ aSeq++; if(aCur){ try{ aCur.pause(); }catch(e){} aCur = null; } if('speechSynthesis' in window) speechSynthesis.cancel(); }
function dSpeakText(text, which, cb, rate){
  if(!('speechSynthesis' in window) || !text){ if(cb) cb(); return; }
  speechSynthesis.cancel();
  const want = which === 1 ? '%s' : '%s';
  const u = new SpeechSynthesisUtterance(aKey(text));
  const v = aVoices.find(x => x.lang && x.lang.toLowerCase().startsWith(want) && /Natural|Neural|Google/i.test(x.name)) || aVoices.find(x => x.lang && x.lang.toLowerCase().startsWith(want)) || null;
  if(v) u.voice = v; u.lang = v ? v.lang : (want === 'ja' ? 'ja-JP' : want === 'ko' ? 'ko-KR' : 'en-US'); u.rate = rate || 1; u.volume = aVolTTS();
  let done = false; const fin = () => { if(!done){ done = true; if(cb) cb(); } };
  u.onend = fin; u.onerror = fin; speechSynthesis.speak(u); setTimeout(fin, 12000);
}
/* 읽어주기 음량: 음원은 -22 LUFS 로 정규화돼 있고, 여기에 사용자 설정(🔈 버튼, 저장)을 곱한다 */
const A_VOLS = [0.3, 0.6, 1.0];
function aVol(){ return Number(store.get('avol', 0.6)) || 0.6; }
function aVolTTS(){ return Math.min(1, aVol() + 0.2); }
function aVolCycle(){ const v = A_VOLS[(A_VOLS.indexOf(aVol()) + 1) % A_VOLS.length]; store.set('avol', v); if(aCur){ try{ aCur.volume = v; }catch(e){} } aVolPaint(); }
function aVolPaint(){ const b = document.getElementById('ttsVol'); if(!b) return; const v = aVol(); b.textContent = v <= 0.3 ? '🔈' : v <= 0.6 ? '🔉' : '🔊'; b.title = '읽어주기 음량 ' + Math.round(v * 100) + '% (누르면 바뀜)'; }
function aPlay(text, times, gap, cb, which, rate){
  aStopAll(); const my = aSeq; times = Math.max(1, times || 1); gap = gap == null ? 350 : gap; which = which || 2;
  const src = AUDIO[(which === 1 ? 'm:' : '') + aKey(text)]; let n = 0;
  const done = () => { if(my === aSeq && cb) cb(); };
  const step = () => {
    if(my !== aSeq) return;
    const after = () => { n++; if(my !== aSeq) return; if(n < times) setTimeout(step, gap); else done(); };
    if(src){ const a = new Audio(src); aCur = a; a.playbackRate = rate || 1; a.volume = aVol(); a.onended = after; a.onerror = after; a.play().catch(after); }
    else dSpeakText(text, which, after, rate);
  };
  step();
}
const aRep = () => 3;
''' % (MEAN, SRC)
    rep("document.addEventListener('keydown', e => {", ENGINE + "\ndocument.addEventListener('keydown', e => {")
else:
    rep_re(r'function aPlay\(text, times, gap, cb, which\)\{', 'function aPlay(text, times, gap, cb, which, rate){')
    rep('''    if(src){ const a = new Audio(src); aCur = a; a.onended = after; a.onerror = after; a.play().catch(after); }
    else dSpeakText(text, which, after);''', '''    if(src){ const a = new Audio(src); aCur = a; a.playbackRate = rate || 1; a.volume = aVol(); a.onended = after; a.onerror = after; a.play().catch(after); }
    else dSpeakText(text, which, after, rate);''')
    rep('''function dSpeakText(text, which, cb){''', '''function dSpeakText(text, which, cb, rate){''')
    rep('''  u.rate = Number($('dRate').value) || 1;''', '''  u.rate = rate || Number($('dRate').value) || 1;
  u.volume = aVolTTS();''')

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
  if(typeof barAt !== 'undefined' && barAt != null){ barAt = null; paintBars(); paintBarLyrics(); }
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
/* 읽어주기: 카드 원문을 로컬 음원(있으면) 또는 브라우저 음성으로 */
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
$('ttsVol').onclick = aVolCycle; aVolPaint();
$('ttsStop').onclick = () => { aStopAll(); ttsMark(null); };''' % SRC)
rep('''  else if(k === 'c'){ e.preventDefault(); $('loop').click(); }''', '''  else if(k === 'c'){ e.preventDefault(); $('loop').click(); }
  else if(k === 's'){ e.preventDefault(); stopAll(); }
  else if(k === 't'){ e.preventDefault(); ttsLine(1, 1); }''')
# 체크 토글 → 복습 수
i0 = h.index("$('check').onclick"); j0 = h.index('  paintProgress();', i0)
h = h[:j0] + '  paintProgress(); paintReview();' + h[j0 + len('  paintProgress();'):]; N += 1

# ══════════════════ 7. JS: 학습 탭 (하위 탭·복습·단락·4단계·노래방 세션) ══════════════════
rep('''let sKind = 'E';''', '''let sKind = 'A';''')
rep('''  $('nExpr').textContent = STUDY.filter(r => r.t === 'E').length;
  $('nWord').textContent = STUDY.filter(r => r.t === 'V').length;
  renderList();''', '''  $('nList').textContent = STUDY.length;
  renderList();''')
rep('''  const rows = STUDY.filter(r => r.t === sKind)''', '''  const rows = STUDY.filter(r => sKind === 'A' || r.t === sKind)''')

SK = "const SK = k => (typeof pk === 'function' ? pk(k) : k);" if PK else "const SK = k => k;"
OPEN_DRILL = '''function openDrill(from, scope, title, stage){
  dFrom = from; dStage = stage || 0; dScope = scope; pickSeg2($('dScope'), scope);
  if(stage){ dMode = 'fwd'; dSize = 0; pickSeg2($('dMode'), 'fwd'); pickSeg2($('dSize'), '0'); }
  $('dTitle').textContent = title; $('dsetup').hidden = true; $('dSetBtn').setAttribute('aria-pressed', 'false');
  dStats(); showPane('drillPane');
  return dPool().length;
}
$('dBackBtn').onclick = () => { dActive = false; drillStopAuto(); dStage = 0; setSub(dFrom); };
$('dSetBtn').onclick = () => { const o = $('dsetup').hidden; $('dsetup').hidden = !o; $('dSetBtn').setAttribute('aria-pressed', String(o)); if(o){ $('dStats').hidden = false; dStats(); } };
$('lDrill').onclick = () => { if(openDrill('L', sKind, '%s · ' + ({A:'%s', E:'%s', V:'%s'})[sKind])) dStart(false); };
$('rvDrill').onclick = () => { if(openDrill('W', 'W', '%s')) dStart(false); };
$('rvListen').onclick = () => { if(openDrill('W', 'W', '%s')) dAutoStart(aRep()); };''' % (A['drill'], A['allDrill'], A['expr'], A['word'], A['reviewDrill'], A['reviewListen']) if DRILL else '''
$('rvQuiz').onclick = () => { if(openQuiz('W', 'W', '%s')) $('qStart').click(); };
let lOn = false, lIdx = 0;
function lStop(){ lOn = false; aStopAll(); $('rvListen').setAttribute('aria-pressed', 'false'); }
$('rvListen').onclick = () => {                                   /* 복습 목록을 차례로 읽어 준다 */
  if(lOn){ lStop(); return; }
  const rows = reviewPool(); if(!rows.length) return; lOn = true; lIdx = 0; $('rvListen').setAttribute('aria-pressed', 'true');
  const step = () => { if(!lOn) return; if(lIdx >= rows.length){ lStop(); return; } const r = rows[lIdx++];
    aPlay(r.%s, 1, 0, () => { if(!lOn) return; setTimeout(() => aPlay(r.%s, 1, 0, () => setTimeout(step, 700), 1), 400); }, 2); };
  step();
};''' % (A['reviewQuiz'], SRC, MEAN)
NEW_SETSUB = '''/* 하위 탭 4개(오늘·복습·목록·학습법). 드릴·퀴즈 패널은 단계·버튼에서 열리고 「돌아가기」는 연 곳으로 */
const PANES = ['dayPane','reviewPane','listPane','guidePane'%s,'quizPane'];
let subCur = 'D', dFrom = 'D', qFrom = 'D', dStage = 0, qStage = 0;
%s
function showPane(id){
  PANES.forEach(p => $(p).hidden = p !== id);
  %s
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
function openQuiz(from, scope, title, stage){
  qFrom = from; qStage = stage || 0; qScope = scope; pickSeg2($('qScope'), scope);
  if(stage){ qMode = '%s2%s'; qLen = 10; pickSeg2($('qMode'), qMode); pickSeg2($('qLen'), '10'); }
  $('qTitle').textContent = title; $('qsetup').hidden = true; $('qSetBtn').setAttribute('aria-pressed', 'false');
  $('qplay').hidden = true; $('qdone').hidden = true;
  syncQuizUI(); showPane('quizPane');
  return !$('qStart').disabled;
}
$('qBackBtn').onclick = () => { qStage = 0; setSub(qFrom); };
$('qSetBtn').onclick = () => { const o = $('qsetup').hidden; $('qsetup').hidden = !o; $('qSetBtn').setAttribute('aria-pressed', String(o)); };
$('lQuiz').onclick = () => { if(openQuiz('L', sKind === 'A' ? 'E' : sKind, '%s · ' + ({A:'%s', E:'%s', V:'%s'})[sKind])) $('qStart').click(); };
%s

/* ====================== 복습: 기한 항목 + 퀴즈 오답 + 체크한 줄 ====================== */
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
  const push = (it, src) => { const k = rvKey(it); if(seen.has(k)) return; seen.add(k); it.src = src; out.push(it); };
  if(typeof dState !== 'undefined') Object.entries(dState).forEach(([k, st]) => { if(st.due <= now){ const it = itemOfKey(k); if(it) push(it, '%s'); } });
  wrongs.forEach(k => { const it = itemOfKey(k); if(it) push(it, '%s'); });
  [...checked].forEach(id => { const c = DATA.find(x => x.id === id); if(c && !(typeof dState !== 'undefined' && dState['S|' + edited(c).%s])) push(sentItem(c), '%s'); });
  return out;
}
function paintReview(){ const n = reviewPool().length; $('nReview').textContent = n; return n; }
function renderReview(){
  const rows = reviewPool(); paintReview();
  $('rvInfo').textContent = rows.length ? ('%s ' + rows.length) : '%s';
  [...document.querySelectorAll('.rvhead .btn')].forEach(b => b.disabled = !rows.length);
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
      b.onclick = () => { const c = DATA.find(x => x.id === r.cids[0]); if(c) playSeg(c); }; el.appendChild(b);
    }
    box.appendChild(el);
  });
}

''' % (",'drillPane'" if DRILL else '', SK,
       "if(id !== 'drillPane') drillStopAuto();\n  if(id !== 'listPane') lStop();" if DRILL else "if(id !== 'reviewPane' && typeof lStop === 'function') lStop();",
       SRC, MEAN, A['quiz'], A['expr'], A['expr'], A['word'], OPEN_DRILL,
       SRC, SRC, SRC, MEAN, MEAN, SRC, SRC, A['dueTag'], A['wrongTag'], SRC, A['checkTag'], A['reviewWait'], A['noReview'], SRC, SRC, SRC, MEAN)
a_ = h.index('function setSub(kind){'); b_ = h.index('/* ======================', a_)
h = h[:a_] + NEW_SETSUB + h[b_:]; N += 1

# 단락(절·후렴) = 오늘 단위
a_ = h.index('function buildDays(){'); b_ = h.index('function renderDay(){')
h = h[:a_] + '''/* 노래는 날짜가 아니라 단락(절·후렴)으로 나눈다. 표현·단어는 첫 등장 줄이 속한 단락에 */
let stages = {}, studyDays = new Set();
function loadProgress(){ stages = store.get(SK('stages'), {}) || {}; wrongs = store.get(SK('wrongs'), []) || []; studyDays = new Set(store.get(SK('studyDays'), []) || []); }
function buildDays(){
  loadProgress();
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
  $('paceInfo').textContent = DATA.length + ' %s · ' + DAYS.length + ' PART';
}
''' % A['lines'] + h[b_:]; N += 1

STG_META = "d => d.cards.length + ' %s'"
NEW_RENDERDAY = '''/* ---- 4단계 진행: stages[part][n] = {done,total} ---- */
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
const sceneName = s => s ? (s.%s || s.label || s.ko || s.key) : '';
const STAGES = [
  ['%s', '%s', d => d.cards.length + ' %s', d => Math.max(1, Math.round((d.cards[d.cards.length - 1].e - d.cards[0].s) / 60 + 0.5))],
  ['%s', '%s', d => d.cards.length + ' %s', d => Math.max(2, d.cards.length)],
  ['%s', '%s', d => d.cards.length + ' %s', d => Math.max(2, d.cards.length)],
  ['%s', '%s', d => '%s ' + d.expr.length + ' · %s ' + d.word.length + ' · %s', d => Math.max(1, Math.round((d.expr.length + d.word.length) * 0.7))]
];
function startStage(n){
  const d = DAYS[dayCur - 1]; if(!d) return;
  const s = stGet(d.n, n), resume = (s.total && s.done < s.total) ? s.done : 0;
  if(n <= 3){ karaSessStart(n, d, resume); return; }
  %s
}
function renderDay(){
  const d = DAYS[dayCur - 1]; if(!d) return;
  dayIds = d.cards.map(c => c.id);
  $('dayNo').textContent = d.n;
  $('nDay').textContent = dayCur + '/' + DAYS.length;
  $('dayTitle').textContent = sceneName(d.scene);
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
    b.textContent = x.n; b.setAttribute('aria-pressed', String(x.n === dayCur)); b.title = sceneName(x.scene);
    b.onclick = () => { dayCur = x.n; store.set(SK('dayCur'), dayCur); renderDay(); };
    strip.appendChild(b);
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
    b.onclick = () => { const c = DATA.find(x => x.id === (r.cids || [])[0]); if(c) playSeg(c); };
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
''' % (
    'label' if L1 == 'ja' else 'ko',
    A['stages'][0], B['stages'][0], A['st1meta'],
    A['stages'][1], B['stages'][1], A['st2meta'],
    A['stages'][2], B['stages'][2], A['st3meta'],
    A['stages'][3], B['stages'][3], A['expr'], A['word'], A['st4drill'] if DRILL else A['st4quiz'],
    ("const cnt = openDrill('D', 'D', '4 %s', 4);\n  if(!cnt){ stSet(d.n, 4, 1, 1); setSub('D'); return; }\n  dStart(false);" % A['stages'][3]) if DRILL else
    ("const ok = openQuiz('D', 'D', '4 %s', 4);\n  if(!ok){ stSet(d.n, 4, 1, 1); setSub('D'); return; }\n  $('qStart').click();" % A['stages'][3]),
    A['checkTag'], A['streak'], A['lines'], A['expr'], A['word'], A['reviewWait'], A['partDone'],
    L2, A['minutes'], A['done'], A['again'], A['resume'], A['start'],
    SRC, SRC, MEAN, SRC, SRC, SRC, MEAN)
a_ = h.index('function renderDay(){'); b_ = h.index("segWire('qPace'")
h = h[:a_] + NEW_RENDERDAY + h[b_:]; N += 1

# 퀴즈: 항목 종류(t) · 복습 범위 · 단계 기록 · 오답 → 복습
rep_re(r"\(\{%s: r\.%s, %s: r\.%s, note: r\.note, cids: r\.cids \|\| \[\]\}\)" % (SRC, SRC, MEAN, MEAN), "({t: r.t, %s: r.%s, %s: r.%s, note: r.note, cids: r.cids || []})" % (SRC, SRC, MEAN, MEAN), count=2)
rep_re(r"\(\{%s: edited\(c\)\.%s, %s: edited\(c\)\.%s, cids: \[c\.id\]\}\)" % (SRC, SRC, MEAN, MEAN), "({t: 'S', %s: edited(c).%s, %s: edited(c).%s, cids: [c.id]})" % (SRC, SRC, MEAN, MEAN), count=2)
rep('''function quizPool(){''', '''function quizPool(){
  if(qScope === 'W') return reviewPool().map(r => ({t: r.t, %s: r.%s, %s: r.%s, note: r.note, cids: r.cids || []}));''' % (SRC, SRC, MEAN, MEAN))
rep('''function finishQ(){
  $('qplay').hidden = true; $('qdone').hidden = false;''', '''function finishQ(){
  $('qplay').hidden = true; $('qdone').hidden = false;
  qWrong.forEach(it => wrongAdd(it)); paintReview();
  if(qStage){ stSet(dayCur, qStage, qSet.length, qSet.length); qStage = 0; }''')
rep('''$('qQuit').onclick = () => { $('qplay').hidden = true; $('qsetup').hidden = false; };''', '''$('qQuit').onclick = () => { qStage = 0; setSub(qFrom); };''')
rep('''$('rBack').onclick = () => { $('qdone').hidden = true; $('qsetup').hidden = false; };''', '''$('rBack').onclick = () => setSub(qFrom);''')
if not DRILL:   # 퀴즈 정답을 맞힌 오답 항목은 복습에서 뺀다
    rep('''  if(ok) qHit++; else { btn.classList.add('ng'); qWrong.push(q.item); }''', '''  if(ok){ qHit++; wrongDel(rvKey(q.item)); } else { btn.classList.add('ng'); qWrong.push(q.item); }''')

# 드릴(saranghagi): 복습 범위 · 대사 항목 · 단계 기록 · 오답 해제 · 돌아가기
if DRILL:
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

# ══════════════════ 8. JS: 노래방 — 글자별 채우기 · 가리기 · 세션 · 마디 바 ══════════════════
KRD_OPT, KRD_EL = CFG['KRD_OPT'], CFG['KRD_EL']
# karaSet: 가리기 인자
a_ = h.index('function karaSet('); b_ = h.index('function karaPaint(')
h = h[:a_] + '''function karaSet(el, d, withRd, mask){
  if(!d){ el.textContent = ''; el.onclick = null; return; }
  const v = edited(d); let t = mask ? maskLine(v.%s) : v.%s;
  %s
  el.textContent = t;
  el.onclick = () => { if(player && ready){ player.seekTo(d.s, true); player.playVideo(); stopAt = null; loopSeg = null; barAt = null; paintLoop(); paintBars(); paintBarLyrics(); } };
}
/* 글자별 span 으로 채운다: 줄이 화면에서 두 줄로 꺾여도 앞 글자부터 순서대로 물든다 */
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
    else if(i === k && frac > 0.05 && k < n){ s.className = 'kc part'; s.style.setProperty('--q', (frac * 100).toFixed(0) + '%%'); }
    else { s.className = 'kc'; s.style.removeProperty('--q'); }
  });
}
''' % (SRC, SRC, ("if(withRd && !mask && $('%s').checked && v.rd) t += '　' + v.rd;" % KRD_OPT) if (KRD_OPT and app == 'vitaminme-cards') else '') + h[b_:]; N += 1
rep_re(r"    karaSet\(\$\('karaNext'\), nxt(, true)?\); karaSet\(\$\('karaNext2'\), nxt2(, false)?\);",
       "    karaSet($('karaNext'), nxt, true, lv >= 3); karaSet($('karaNext2'), nxt2, false, lv >= 3);")
rep_re(r"    karaSet\(\$\('karaPrev'\), prv(, false)?\);", "    karaSet($('karaPrev'), prv, false, false);")
rep_re(r"\$\('karaLine'\)\.textContent = v\.%s;" % SRC, "setKaraLine(lv >= 3 ? maskLine(v.%s) : v.%s);" % (SRC, SRC))
rep_re(r"\$\('karaLine'\)\.textContent = '♪';", "setKaraLine('♪');")
if KRD_EL:
    rep_re(r"(\$\('%s'\)\.textContent = )(\(?)\$\('%s'\)\.checked" % (KRD_EL, KRD_OPT), r"\1\2lv < 2 && $('%s').checked" % KRD_OPT)
rep_re(r"(\$\('karaJaLine'\)\.textContent = )(\(?)\$\('karaJa'\)\.checked", r"\1\2lv < 1 && $('karaJa').checked")
rep_re(r"  \$\('karaLine'\)\.style\.setProperty\('--p', \(p \* 100\)\.toFixed\(1\) \+ '%'\);", "  paintKaraFill(p);")
# karaPaint 머리: 1단계 자동 진행 + 가리기 단계
i0 = h.index('function karaPaint(t){'); j0 = h.index('  if(i !== karaLast){', i0)
h = h[:j0] + '''  if(ksess && ksess.stage === 1 && cur){
    const p = ksess.ids.indexOf(cur.id);
    if(p > ksess.i){ ksess.i = p; stSet(ksess.day, 1, p, ksess.ids.length); karaSessPaint(); }
    const last = DATA.find(x => x.id === ksess.ids[ksess.ids.length - 1]);
    if(last && t > last.e + 0.3 && cur.id !== last.id){ stSet(ksess.day, 1, ksess.ids.length, ksess.ids.length); ksEnd(); return; }
  }
  const lv = (ksess && ksess.stage === 3) ? ksess.level : 0;
''' + h[j0:]; N += 1
KSESS = '''
/* ====================== 노래방 세션: 1 들으며 읽기 · 2 마디 따라 부르기 · 3 가사 가리기 ====================== */
let ksess = null;
function maskLine(s){
  return s.split(/(\\s+)/).map(tok => /^\\s+$/.test(tok) ? tok : (tok.length <= 1 ? tok : tok[0] + '＿'.repeat(Math.min(tok.length - 1, 4)))).join('');
}
const karaNow = () => (player && ready && typeof player.getCurrentTime === 'function') ? player.getCurrentTime() : 0;
function ksReset(){ barAt = null; stopAt = null; loopSeg = null; paintLoop(); paintBars(); paintBarLyrics(); }
function ksPlayFrom(c){ if(!(player && ready) || !c) return; ksReset(); player.seekTo(Math.max(0, c.s - 0.3), true); player.playVideo(); }
function karaSessStart(stage, d, from){
  const ids = d.cards.map(c => c.id);
  if(!ids.length){ stSet(d.n, stage, 1, 1); return; }
  ksess = {stage, day: d.n, ids, i: Math.min(from || 0, ids.length - 1), level: Number(store.get(SK('maskLv'), 1)) || 1};
  switchView('kara'); window.scrollTo({top: 0});
  if(stage === 1){ %s$('karaJa').checked = true; karaLast = -2; karaSessPaint(); ksPlayFrom(DATA.find(x => x.id === ids[ksess.i])); }
  else ksLine();
}
function ksLine(){
  const c = DATA.find(x => x.id === ksess.ids[ksess.i]); if(!c) return;
  const k = deck.findIndex(x => x.id === c.id); if(k >= 0){ index = k; showCard(); }
  karaLast = -2; karaSessPaint();
  if(!(player && ready)) return;
  if(BARS.length >= 2) $('barLine').click(); else playSeg(c, {loop: true});
  karaPaint(c.s + 0.01);
}
function karaSessPaint(){
  const on = !!ksess;
  $('ksbar').hidden = !on; $('ksfoot').hidden = !on; $('knav').hidden = on; $('kmask').hidden = !(on && ksess.stage === 3);
  if(!on) return;
  const n = ksess.ids.length, d = DAYS[ksess.day - 1];
  const names = ['1 %s', '2 %s', '3 %s'];
  $('ksName').textContent = (d && d.scene ? sceneName(d.scene) + ' · ' : '') + names[ksess.stage - 1];
  $('ksPos').textContent = (ksess.i + 1) + ' / ' + n;
  $('ksBar').style.width = Math.round(ksess.i / n * 100) + '%%';
  $('ksA').textContent = ksess.stage === 1 ? '%s' : '%s';
  $('ksB').textContent = (ksess.stage === 1 ? '%s' : '%s') + (ksess.i < n - 1 ? ' · %s ›' : ' · %s ✓');
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
    const c = DATA.find(x => x.id === ksess.ids[ksess.i]), t = karaNow();
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
$('ksA').onclick = () => { if(!ksess) return; if(ksess.stage === 1) ksPlayFrom(DATA.find(x => x.id === ksess.ids[ksess.i])); else ksLine(); };
$('ksB').onclick = () => ksNext();
segWire('kmask', v => { if(!ksess) return; ksess.level = Number(v); store.set(SK('maskLv'), ksess.level); karaLast = -2; karaPaint(karaNow()); karaSessPaint(); });
function karaStep(dir){
  if(!(player && ready)) return;
  const i = karaAt(karaNow()), j = Math.max(0, Math.min(DATA.length - 1, (i < 0 ? 0 : i) + dir));
  ksReset(); player.seekTo(Math.max(0, DATA[j].s - 0.3), true); player.playVideo(); karaLast = -2;
}
$('knPrev').onclick = () => karaStep(-1);
$('knNext').onclick = () => karaStep(1);
bindCue($('knPlay'), () => {
  if(BARS.length >= 2 && barAt != null){ const j = Math.min(barAt + barLen, BARS.length - 1); return {seg: {id: -1, s: BARS[barAt], e: BARS[j]}, opts: {loop: true, exact: true}}; }
  const i = karaAt(karaNow()); const d = DATA[i < 0 ? 0 : i]; return d ? {seg: d} : null;
});
$('knStop').onclick = stopAll;
function karaBack(){ if(ksess) ksEnd(); else { if(barAt != null) $('barStop').click(); switchView('card'); window.scrollTo({top: 0}); } }
$('karaBack').onclick = karaBack;
$('knBack').onclick = karaBack;
window.addEventListener('popstate', () => { if(view === 'kara') karaBack(); });
$('karaLine').onclick = () => { if(BARS.length >= 2 && player && ready) $('barLine').click(); };
$('toKara').onclick = () => { switchView('kara'); window.scrollTo({top: 0}); try{ history.pushState({kara: 1}, ''); }catch(e){} if(BARS.length >= 2 && player && ready) $('barLine').click(); };
$('barFine').onclick = () => { const o = $('barFineRow').hidden; $('barFineRow').hidden = !o; $('barFine').setAttribute('aria-pressed', String(o)); };
document.addEventListener('keydown', e => {
  const t = e.target;
  if(t && (t.tagName === 'INPUT' || t.tagName === 'SELECT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
  if(view !== 'kara' || e.metaKey || e.ctrlKey || e.altKey) return;
  if(e.key === 'Enter' && ksess){ e.preventDefault(); ksNext(); }
  else if(e.key === '['){ e.preventDefault(); $('barPrev').click(); }
  else if(e.key === ']'){ e.preventDefault(); $('barNext').click(); }
});
''' % (("$('%s').checked = true; " % KRD_OPT) if KRD_OPT else '', A['stages'][0], A['stages'][1], A['stages'][2],
       A['fromHere'], A['onceMore'], A['read'], A['sang'], A['next'], A['finish'])
# karaPaint 정의 뒤(닫는 rAF 루프 뒤)에 세션 코드를 둔다: `$('karaPause').onclick` 앞
i0 = h.index("\n$('karaPause').onclick = "); h = h[:i0] + KSESS + h[i0:]; N += 1
# 마디 bars 가 카드에서 노래방으로 옮겨졌으므로 barBox hidden 판정은 그대로(rebuildBars) 동작

# ══════════════════ 9. 기동 ══════════════════
if 'buildScenes(); paintProgress(); paintEditCount(); buildDeck(); buildStudy(); buildGuide(); buildDays(); renderDay(); syncQuizUI(); loadAPI();' in h:
    rep('buildScenes(); paintProgress(); paintEditCount(); buildDeck(); buildStudy(); buildGuide(); buildDays(); renderDay(); syncQuizUI(); loadAPI();',
        "buildScenes(); paintProgress(); paintEditCount(); buildDeck(); buildStudy(); buildGuide(); buildDays(); setSub('D'); syncQuizUI(); paintMini(); loadAPI();")
open(path, 'w', encoding='utf-8').write(h)
print('ported', app, 'steps', N)
