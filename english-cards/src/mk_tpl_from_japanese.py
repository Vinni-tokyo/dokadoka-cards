"""japanese-cards/src/tpl.html → english-cards/src/tpl.html 변환.
   1) 구조 변경(읽기·화면자막 UI 제거, ja→en, 퀴즈 모드 키) 은 정확 문자열 치환으로,
   2) 일본어 부제는 긴 것부터 영어로 치환한다. 끝에 일본어 문자가 남지 않았는지 검사한다."""
import re, sys, os
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'japanese-cards', 'src', 'tpl.html')   # 변환 원본(2026-09-11 15:53 판 기준)
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tpl.html')
h = open(SRC, encoding='utf-8').read()

def rep(old, new, count=1):
    global h
    n = h.count(old)
    assert n == count, f'{n}회 발견(기대 {count}): {old[:70]!r}'
    h = h.replace(old, new)

# ---------------------------------------------------------------- 1. 구조 변경
rep('<title>도카도카 일본어 공부 · ドカドカ日本語</title>', '<title>도카도카 영어 공부 · Dokadoka English</title>')
rep('font-family:"Noto Sans KR","Noto Sans JP",system-ui,-apple-system,"Segoe UI",sans-serif;',
    'font-family:"Noto Sans KR",system-ui,-apple-system,"Segoe UI",sans-serif;')
rep('[lang=ja]{font-family:"Noto Sans JP","Hiragino Sans","Yu Gothic","Meiryo","Noto Sans KR",system-ui,sans-serif}',
    '[lang=en]{font-family:"Inter","Segoe UI",system-ui,-apple-system,Roboto,"Noto Sans KR",sans-serif}')
rep('/* 二段ラベル: 한국어=주, 일본어=부 */', '/* two-line labels: Korean primary, English secondary */')

# 읽기(히라가나) UI 제거 — 영어에는 읽기 줄이 없다
rep('     <p class="rd" id="rd" hidden><b>읽기</b><span lang="ja" id="rdText"></span></p>\n', '')
rep('''      <div>
       <div class="cap">읽기(히라가나) · 読み</div>
       <textarea id="edRd" lang="ja" spellcheck="false" style="min-height:48px"></textarea>
      </div>
''', '')
rep('      <label><input type="checkbox" id="optRead"><span>읽기(히라가나) 표시<br><span class="inl" lang="ja">読みを表示</span></span></label>\n', '')
rep('      <label><input type="checkbox" id="optCap"><span>화면 자막도 카드에 포함<br><span class="inl" lang="ja">画面テロップもカードに含める</span></span></label>\n', '')
rep('<i><kbd>C</kbd> 반복 · リピート</i><i><kbd>R</kbd> 읽기 · 読み</i><i><kbd>V</kbd><kbd>→</kbd> 다음 · 次</i>',
    '<i><kbd>C</kbd> 반복 · Repeat</i><i><kbd>V</kbd><kbd>→</kbd> 다음 · Next</i>')
rep("  if(!d){ $('ja').textContent = '해당 대사가 없습니다 / 該当する台詞がありません'; $('rd').hidden = true; return; }",
    "  if(!d){ $('ja').textContent = '해당 대사가 없습니다 / No matching line'; return; }")
rep("  $('rd').hidden = !($('optRead').checked && v.rd);\n  $('rdText').textContent = ' ' + (v.rd || '');\n", '')
rep("  const showRd = $('optRead').checked;\n", '')
rep('<div class="k" lang="ja"></div><div class="r" lang="ja"></div><div class="j"></div>', '<div class="k" lang="ja"></div><div class="j"></div>')
rep("    const r = el.querySelector('.r'); r.textContent = v.rd || ''; r.hidden = !(showRd && v.rd);\n", '')
rep("  $('edJa').value = v.ja; $('edRd').value = v.rd || ''; $('edKo').value = v.ko;", "  $('edEn').value = v.ja; $('edKo').value = v.ko;")
rep("  const ja = $('edJa').value.trim(), rd = $('edRd').value.trim(), ko = $('edKo').value.trim();",
    "  const ja = $('edEn').value.trim(), ko = $('edKo').value.trim();")
rep("  if(rd !== (d.rd || '')) e.rd = rd;\n", '')
rep("(typeof row.ja === 'string' || typeof row.ko === 'string' || typeof row.rd === 'string')", "(typeof row.ja === 'string' || typeof row.ko === 'string')")
rep("$('optRead').onchange = () => { store.set('read', $('optRead').checked); showCard(); buildScript(); };\n", '')
rep("$('optCap').onchange = () => { store.set('cap', $('optCap').checked); buildScenes(); buildDeck(); };\n", '')
rep("  else if(k === 'r'){ e.preventDefault(); $('optRead').checked = !$('optRead').checked; $('optRead').onchange(); }\n", '')
rep("$('optRead').checked = store.get('read', true);\n$('optCap').checked = store.get('cap', true);\n", '')
rep("    if(r.rd && r.rd !== r.ja){ const sm = document.createElement('small'); sm.textContent = r.rd; k.appendChild(sm); }\n", '')
rep("      if(it.rd && it.rd !== it.ja){ const sm = document.createElement('small'); sm.textContent = it.rd; k.appendChild(sm); }\n", '')
rep("    b.querySelector('.jj').textContent = (r.rd && r.rd !== r.ja ? r.rd + ' · ' : '') + r.ko;", "    b.querySelector('.jj').textContent = r.ko;")
rep("  const rd = q.item.rd && q.item.rd !== q.item.ja ? '（' + q.item.rd + '）' : '';\n", '')
rep("""    + '<span lang="ja"></span><span lang="ja" style="color:var(--ink-3)"></span> — <span></span>';
  line.children[1].textContent = q.item.ja; line.children[2].textContent = rd; line.children[3].textContent = q.item.ko;""",
    """    + '<span lang="ja"></span> — <span></span>';
  line.children[1].textContent = q.item.ja; line.children[2].textContent = q.item.ko;""")
rep(', rd: edited(c).rd', '', 2)
rep(', rd: r.rd', '', 2)
rep("(r.ja + ' ' + r.rd + ' ' + r.ko + ' ' + (r.note || ''))", "(r.ja + ' ' + r.ko + ' ' + (r.note || ''))")
rep('placeholder="일본어·읽기·한국어로 검색 / 日本語・読み・韓国語で絞り込み"', 'placeholder="영어·한국어로 검색 / Search in English or Korean"')
rep("'읽기와 뜻을 가리고 재생. 먼저 귀로만 도전. 몰라도 괜찮다.'", "'뜻을 가리고 재생. 먼저 귀로만 도전. 몰라도 괜찮다.'")
rep("'읽기·뜻을 열어 답 맞추기. 표현·단어는 예문과 함께 외운다.'", "'뜻을 열어 답 맞추기. 표현·단어는 예문과 함께 외운다.'")
rep('.rd{display:flex;gap:8px;margin:8px 0 0;font-size:14px;line-height:1.6;color:var(--ink-2)}\n', '')
rep('.rd b{flex:none;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--brand);padding-top:3px}\n', '')

# 화면 자막(Cap) 개념 제거 — 이 영상에는 없다
rep("const isCap = d => d.spk === 'Cap';\n", '')
rep("  if(s.key === 'Cap') return;\n", '')
rep("const pool = () => $('optCap').checked ? DATA : DATA.filter(d => !isCap(d));", 'const pool = () => DATA;')
rep("  $('who').className = 'chip ' + (isCap(d) ? 'cap' : 'spk');", "  $('who').className = 'chip spk';")
rep("    const who = el.querySelector('.who'); who.textContent = sp.ko; if(isCap(d)) who.classList.add('cap');", "    el.querySelector('.who').textContent = sp.ko;")
rep('DATA.filter(c => !isCap(c))', 'DATA', 1)
rep('d.cards.filter(c => !isCap(c))', 'd.cards', 1)

# 퀴즈 방식 키·라벨
rep('<button data-v="ja2ko" aria-pressed="true">日 → 韓</button>', '<button data-v="en2ko" aria-pressed="true">EN → KO</button>')
rep('<button data-v="ko2ja" aria-pressed="false">韓 → 日</button>', '<button data-v="ko2en" aria-pressed="false">KO → EN</button>')
rep("let qScope = 'E', qMode = 'ja2ko', qLen = 10;", "let qScope = 'E', qMode = 'en2ko', qLen = 10;")
rep("qMode === 'ko2ja' ? 'ja' : 'ko';       /* 고를 것: 日→韓·듣기는 한국어 뜻, 韓→日은 일본어 */",
    "qMode === 'ko2en' ? 'ja' : 'ko';       /* what to pick: EN→KO and listening → Korean meaning, KO→EN → English */")
rep("""qMode = 'ja2ko'; pickSeg($('qMode')); $('qMode').querySelector('[data-v="ja2ko"]')""", """qMode = 'en2ko'; pickSeg($('qMode')); $('qMode').querySelector('[data-v="en2ko"]')""")
rep("  } else if(qMode === 'ko2ja'){", "  } else if(qMode === 'ko2en'){")

# 저장 키·내보내기 파일명·페이스
rep("const LS = 'jp-sm5';", "const LS = 'en-zd73';")
rep("/* {카드id: {ja, rd, ko}} 직접 고친 내용 */", "/* {카드id: {en, ko}} 직접 고친 내용 */")
rep("a.download = 'japanese-snowman5-edits.json';", "a.download = 'english-zendaya73-edits.json';")
rep('''        <button data-v="10" aria-pressed="false">천천히</button>
        <button data-v="15" aria-pressed="true">보통</button>
        <button data-v="21" aria-pressed="false">빠르게</button>
        <button data-v="35" aria-pressed="false">집중</button>''',
    '''        <button data-v="__P1__" aria-pressed="false">천천히</button>
        <button data-v="__P2__" aria-pressed="true">보통</button>
        <button data-v="__P3__" aria-pressed="false">빠르게</button>
        <button data-v="__P4__" aria-pressed="false">집중</button>''')
rep("let dayPace = store.get('pace', 15);", "let dayPace = store.get('pace', __P2__);")

# 사이드바 브랜드·출처 문구
rep('''  <div class="brand"><div class="seal">日</div>
   <div><strong>도카도카 일본어 공부<span class="sub" lang="ja">ドカドカ日本語</span></strong>
    <small>Snow Man 5년의 기록 · <span class="n">—</span>문장<br><span lang="ja">Snow Man 5年の記録 · <span class="n">—</span>フレーズ</span></small></div></div>''',
    '''  <div class="brand"><div class="seal">E</div>
   <div><strong>도카도카 영어 공부<span class="sub" lang="ja">Dokadoka English</span></strong>
    <small>젠데이아에게 73가지 질문 · <span class="n">—</span>문장<br><span lang="ja">73 Questions With Zendaya · <span class="n">—</span> lines</span></small></div></div>''')
rep('''    자막은 영상에 붙은 공식 일본어 자막(화자명 포함)입니다. 읽기·번역은 직접 작성한 것이라 오류가 있을 수 있습니다.<br>
    <span lang="ja">字幕は動画の公式日本語字幕。読み・訳は手作業のため誤りがあり得ます。</span></p>''',
    '''    자막은 Vogue 가 영상에 붙인 공식 영어 자막(화자 표시 포함)입니다. 번역·주석은 직접 작성한 것이라 오류가 있을 수 있습니다.<br>
    <span lang="ja">Captions are Vogue’s official English captions (with speaker tags). Translations and notes are hand-written and may contain errors.</span></p>''')

# 학습법 — 소재에 맞게 고쳐 쓴 팁 2개
rep('''        <div class="gtip"><h5>한자는 읽기부터 · 漢字は読みから</h5>
         <p>처음엔 읽기(<kbd>R</kbd>)를 켜고 소리 내어 읽으세요. 익숙해지면 읽기를 끄고 <b>한자만 보고</b> 읽어 봅니다. 대본 탭도 같은 스위치로 바뀝니다.
          <span lang="ja">最初は読み(<kbd>R</kbd>)を表示して音読を。慣れたら読みを消し、<b>漢字だけを見て</b>読んでみます。台本タブも同じスイッチで切り替わります。</span></p></div>''',
    '''        <div class="gtip"><h5>축약과 필러에 귀 익히기 · Contractions and fillers</h5>
         <p><b>gonna · wanna · kinda · ’cause · I dunno</b> 같은 축약과 <b>you know · I mean · like · I don’t know</b> 같은 필러는 뜻이 아니라 리듬입니다. 들릴 때마다 뜻을 찾지 말고 흘려 보내는 연습을 하세요. 이 한 편에만 you know 가 __YK__번 나옵니다.
          <span lang="ja">Contractions like <b>gonna · wanna · kinda · ’cause · I dunno</b> and fillers like <b>you know · I mean · like · I don’t know</b> carry rhythm, not meaning. Practice letting them pass instead of looking them up; “you know” alone appears __YK__ times in this one video.</span></p></div>''')
rep('''        <div class="gtip"><h5>반말과 정중어 · タメ口と敬語</h5>
         <p>멤버끼리는 <b>반말</b>(俺·〜ぜ·〜じゃん), 스태프·팬 앞에서는 <b>정중어</b>(です·ます·〜させていただく). 같은 사람의 말끝이 상대에 따라 바뀌는 순간에 주목하면 구분이 몸에 익습니다.
          <span lang="ja">メンバー同士は<b>タメ口</b>(俺・〜ぜ・〜じゃん)、スタッフやファンに向けては<b>敬語</b>(です・ます・〜させていただく)。相手で語尾が変わる瞬間に注目すると、使い分けが体で分かります。</span></p></div>''',
    '''        <div class="gtip"><h5>묻는 말투와 답하는 말투 · Asking vs. answering</h5>
         <p>인터뷰어는 <b>What would you say is…? · How would you describe…? · What’s been…?</b> 처럼 부드럽게 돌려 묻고, 젠데이아는 <b>Yeah, for sure. · Nothing, honestly. · Probably my Converse.</b> 처럼 짧게 답합니다. 질문은 통째로 외워 두면 그대로 쓸 수 있고, 대답은 완전한 문장이 아니어도 된다는 것을 확인하세요.
          <span lang="ja">The interviewer softens questions with <b>What would you say is…? · How would you describe…? · What’s been…?</b>, while Zendaya answers briefly: <b>Yeah, for sure. · Nothing, honestly. · Probably my Converse.</b> Memorize the questions whole, and notice that answers need not be full sentences.</span></p></div>''')
rep('<h3>인터뷰 한 편을 「쓸 수 있는 일본어」로 바꾸는 4단계</h3>\n        <p lang="ja">インタビュー1本を「使える日本語」に変える4ステップ</p>',
    '<h3>인터뷰 한 편을 「쓸 수 있는 영어」로 바꾸는 4단계</h3>\n        <p lang="ja">Four steps to turn one interview into English you can use</p>')
rep('105개 카드를 한 번에 들어도 남지 않습니다.', '__N__개 카드를 한 번에 들어도 남지 않습니다.')

# ---------------------------------------------------------------- 2. 일본어 부제 → 영어 (긴 것부터)
M = {
 '/* ---------- 필터 / フィルター ---------- */': '/* ---------- filters ---------- */',
 '/* ---------- 사이드바 / サイドバー ---------- */': '/* ---------- sidebar ---------- */',
 '/* ---------- 덱 / デッキ ---------- */': '/* ---------- deck ---------- */',
 '/* ---------- 카드 / カード ---------- */': '/* ---------- card ---------- */',
 '/* ---------- 대본 / 台本 ---------- */': '/* ---------- script ---------- */',
 '/* ---------- 조작 / 操作 ---------- */': '/* ---------- controls ---------- */',
 '/* ---------- 직접 수정 / 手直し ---------- */': '/* ---------- manual edits ---------- */',
 '/* ====================== 학습 탭 / 学習タブ ====================== */': '/* ====================== study tab ====================== */',
 '/* ====================== 매일 분량 / 毎日の分量 ====================== */': '/* ====================== daily portions ====================== */',
 '/* ---------- 퀴즈 / クイズ ---------- */': '/* ---------- quiz ---------- */',
 '/* ---------- 기동 / 起動 ---------- */': '/* ---------- boot ---------- */',
 ')で開いています。YouTube は出所のないページへの埋め込み再生を拒否します(Error 153)。': '). YouTube refuses embedded playback from a page with no origin (Error 153).',
 'カード・台本・編集はそのまま使え、再生ボタンは YouTube をその台詞の位置から開きます。ページ内で再生するには同梱の': 'Cards, script and editing still work, and the play button opens YouTube at that line. To play inside the page, run the bundled',
 '105枚を一度に浴びても定着しません。「今日」タブが分量を切ってくれます。': '__N__ cards in one sitting will not stick. The Today tab slices them for you.',
 '再生を。聞き取れなかった所だけ意味を開くと、記憶に残りやすくなります。': '. Opening the meaning only where you could not catch it makes it stick.',
 'です。作られた例文にはない言いよどみ・略し方・相づちが詰まっています。': '. It is full of the hesitations, contractions and back-channels that invented examples never have.',
 '行をクリックすると、その台詞の位置から再生します。再生中は自動で追いかけます。': 'Click a line to play from there. While playing, the list follows along.',
 '読みと意味を隠して再生。まず耳だけで挑む。分からなくて当たり前。': 'Play with the meaning hidden. Ears first. Not getting it is normal.',
 '読みと意味を開いて答え合わせ。表現・単語は例文とセットで覚える。': 'Open the meaning and check. Learn expressions and words with their example line.',
 'リピートで同じ区間を繰り返し、声に出して重ねる。抑揚ごと写す。': 'Loop the same span with Repeat and speak over it. Copy the intonation.',
 'クイズで今日の範囲だけ出題。間違いは翌日の復習リストになる。': 'Quiz only today’s range. Misses become tomorrow’s review list.',
 'クイズで間違えた項目はそのまま復習リストになります。': 'Items you miss in the quiz become your review list.',
 '듣기는 file:// 에서 쓸 수 없습니다 · 聞き取りは file:// では使えません': '듣기는 file:// 에서 쓸 수 없습니다 · Listening is unavailable on file://',
 'ください。抑揚ごと写すのが一番効きます。': '. Copying the intonation, not just the words, works best.',
 'だからこそ「読んで分かる」だけでは足りません。': 'That is why “understanding on paper” is not enough. ',
 '再生ボタンで YouTube を該当の位置から開きます': 'The play button opens YouTube at that position',
 '学習用の個人利用を前提としたページです。': 'This page is intended for personal study use.',
 '準備完了。台詞の位置から再生できます。': 'Ready. You can play from any line.',
 'プレーヤーがまだ準備できていません。': 'The player is not ready yet.',
 'YouTube API を読み込めませんでした。': 'Could not load the YouTube API.',
 '학습 진행 방법 / 学習の進め方': '학습 진행 방법 / How to study',
 '🔊 듣고 뜻 고르기 · 聞いて意味を選ぶ': '🔊 듣고 뜻 고르기 · Listen and choose',
 'この場面の再生が終わりました。': 'Finished playing this line.',
 'カードと台本はそのまま使えます。': 'Cards and script still work.',
 '해당 대사가 없습니다 / 該当する台詞がありません': '해당 대사가 없습니다 / No matching line',
 '이 예문 재생 / この例文を再生': '이 예문 재생 / Play this example',
 '오늘 퀴즈 · 今日の分で出題': '오늘 퀴즈 · Quiz on today’s set',
 '하루 20분이면 된다 · 1日20分でいい': '하루 20분이면 된다 · 20 minutes a day is enough',
 '소리 내어 따라 하기 · 口に出す': '소리 내어 따라 하기 · Say it out loud',
 '뜻보다 소리 먼저 · 意味より先に音': '뜻보다 소리 먼저 · Sound before meaning',
 '틀린 것이 보물 · 間違いは宝': '틀린 것이 보물 · Mistakes are treasure',
 '— 복습해 봅시다 · 復習しましょう': '— 복습해 봅시다 · Time to review',
 '— 훌륭합니다 · よくできました': '— 훌륭합니다 · Well done',
 '틀린 항목 · 間違えた項目 (': '틀린 항목 · Missed items (',
 '다시 듣기 · もう一度聞く': '다시 듣기 · Play again',
 'プレーヤーを読み込んでいます…': 'Loading player…',
 'ページ内では再生できません': 'Cannot play inside this page',
 'リピートを解除しました。': 'Repeat off.',
 '動画IDを読み取れません。': 'Cannot read the video ID.',
 '動画を再生できません (エラー': 'Cannot play the video (error',
 '개 · 出題できる項目 ': '개 · Available items ',
 '— 조금만 더 · もう一息': '— 조금만 더 · Almost there',
 '일본어 대사 · 日本語の台詞': '영어 대사 · English line',
 '한국어 뜻 · 韓国語の意味': '한국어 뜻 · Korean meaning',
 '오늘 분량 · 今日の分': '오늘 분량 · Today’s set',
 '카드로 · カードで学ぶ': '카드로 · Study as cards',
 'YouTube 영상 ID / 動画ID': 'YouTube 영상 ID / Video ID',
 '내보내기 · 書き出し': '내보내기 · Export',
 '가져오기 · 読み込み': '가져오기 · Import',
 '動画を差し替えました。': 'Video replaced.',
 '件を読み込みました。': ' items imported.',
 '読み込めませんでした。': 'Could not import.',
 '次のカードを自動再生': 'Auto-play next card',
 '意味を最初から表示': 'Show meaning from the start',
 'インタビュー1本を「使える日本語」に変える4ステップ': 'Four steps to turn one interview into English you can use',
 'この教材は台本ではなく': 'This is not a scripted textbook but a',
 '설정으로 · 設定へ': '설정으로 · Settings',
 '수정함 · 編集済み': '수정함 · Edited',
 '해당 없음 · 該当なし': '해당 없음 · No results',
 '順番をシャッフル': 'Shuffle order',
 '出題範囲': 'Scope', '出題方式': 'Mode', '問題数': 'Questions',
 '되돌리기 · 元に戻す': '되돌리기 · Reset',
 '취소 · キャンセル': '취소 · Cancel',
 '— 만점 · 満点': '— 만점 · Perfect',
 '이전 · 前': '이전 · Prev', '다음 · 次へ': '다음 · Next', '다음 · 次': '다음 · Next',
 '재생 · 再生': '재생 · Play', '반복 · リピート': '반복 · Repeat', '읽기 · 読み': '읽기 · Reading',
 '결과 · 結果': '결과 · Results', '정답 · 正解': '정답 · Correct', '그만 · やめる': '그만 · Quit',
 '다시 · もう一度': '다시 · Again', '시작 · 始める': '시작 · Start', '전체 · 全部': '전체 · All',
 '듣기 · 聞き取り': '듣기 · Listening', '대사 · 台詞': '대사 · Lines', '표현 · 表現': '표현 · Expressions', '단어 · 単語': '단어 · Words',
 '저장 · 保存': '저장 · Save', '숨기기 · 隠す': '숨기기 · Hide', '뜻 · 意味': '뜻 · Meaning', '예문 · 例文': '예문 · Example',
 '검색 / 検索': '검색 / Search',
 '0.3초 · 0.3秒': '0.3초 · 0.3 s', '0.5초 · 0.5秒': '0.5초 · 0.5 s', '0.8초 · 0.8秒': '0.8초 · 0.8 s', '1초 · 1秒': '1초 · 1 s',
 'ローカルファイル(': 'Opened as a local file (',
 'を実行してください。': '.',
 '(Windows) か': '(Windows) or',
 '実際のインタビュー': 'real interview',
 '音とセットで覚える': 'Learning it together with the sound',
 'のが近道です。': ' is the shortcut.',
 'が唯一の近道です。': ' is the only shortcut.',
 '毎日少しずつ': 'A little every day',
 '意味を隠したまま': 'with the meaning hidden',
 'カードはまず': 'Play each card first ',
 ')で同じ区間を繰り返し、': ') to loop the same span and ',
 '声に出して重ねて': 'speak over it',
 'リピート(': 'Use Repeat (',
 'にそこだけ聞き直しましょう。': ', listen to just those again.',
 '翌日の最初': 'First thing the next day',
 '台詞・映像出典': 'Source of lines and video',
 'チェック済み': 'checked', '枚を手直し': 'cards edited',
 'この場面を再生': 'Play this line', '意味を見る': 'Show meaning', '再生の余裕': 'Playback margin',
 'リピート再生中': 'Repeating', '再生中': 'Playing', '一時停止': 'Paused',
 'YouTube を ': 'Opened YouTube at ', ' から開きました。': '.',
 '（発話 ': '(speech ', '秒 + 余裕 ': ' s + margin ', '秒）': ' s)',
 '台詞が空です。': 'The line is empty.', '保存しました。': 'Saved.', '元に戻しました。': 'Reset to original.',
 'YouTube で開く': 'Open on YouTube',
 '　/　台詞 ': '　/　Lines ', ' · 表現 ': ' · Expressions ', ' · 単語 ': ' · Words ',
 '表現・単語': 'Expressions & words', '復習': 'Review',
 ' の台詞': ' lines', '日で完成': ' days', '回': ' times', ' 件': '',
 '聞く': 'Listen', '確かめる': 'Check', '真似る': 'Imitate', '試す': 'Test',
 '学習法': 'How to', '学習': 'Study', '今日': 'Today', '表現': 'Expressions', '単語': 'Words', 'クイズ': 'Quiz', '完了': 'Done',
 'すべて': 'All', 'カード': 'Cards', '台本': 'Script', 'シーン': 'Scenes', '話者': 'Speakers',
 '適用': 'Apply', 'リピート': 'Repeat', 'チェック': 'Check', '編集': 'Edit', '前へ': 'Prev', '次へ': 'Next',
 '① 대사 · 台詞': '① 대사 · Lines',
}
for k in sorted(M, key=len, reverse=True):
    h = h.replace(k, M[k])
h = h.replace('\u3000', ' ')

# ---------------------------------------------------------------- 3. ja → en (식별자·lang·id·클래스)
h = h.replace('edJa', 'edEn').replace('detailJa', 'detailEn')
h = re.sub(r'\bja\b', 'en', h)

left = sorted(set(re.findall(r'[぀-ヿ一-鿿・　]', h)))
assert not left, f'일본어 문자 남음: {left}'
left_rd = [h[max(0,x.start()-60):x.end()+40] for x in re.finditer(r'\brd\b', h)]
assert not left_rd, f'rd 남음: {left_rd}'
open(DST, 'w', encoding='utf-8').write(h)
print('생성:', DST, '%.1f KB' % (len(h.encode())/1024))
