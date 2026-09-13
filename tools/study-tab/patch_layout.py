"""카드 버튼 정리: 체크·편집은 카드 상단 작은 아이콘으로, 모바일은 하단 고정 바(‹ 재생 정지 반복 ›)만 남기고
카드 안의 재생·정지·구간 반복은 숨긴다(중복). patch_tts2.py 뒤에 적용. 사용: python3 patch_layout.py <tpl.html>"""
import sys
path = sys.argv[1]; h = open(path, encoding='utf-8').read(); N = 0
def rep(old, new):
    global h, N
    assert h.count(old) == 1, f'[{N}] {h.count(old)} matches: {old[:60]!r}'
    h = h.replace(old, new); N += 1
# 1. 체크·편집 → 카드 상단 오른쪽 아이콘
rep('''      <span class="meta"><span id="pos">0 / 0</span> · <span id="time">0:00</span></span>
     </div>''', '''      <span class="ctl">
       <span class="meta"><span id="pos">0 / 0</span> · <span id="time">0:00</span></span>
       <button class="ibtn" id="check" aria-pressed="false" title="체크 / チェック"><svg class="ic"><use href="#i-check"/></svg></button>
       <button class="ibtn" id="edit" title="편집 / 編集"><svg class="ic"><use href="#i-pencil"/></svg></button>
      </span>
     </div>''')
rep('''      <button class="btn" id="check" aria-pressed="false"><svg class="ic"><use href="#i-check"/></svg>
       <span class="lbl">체크<span class="sub" lang="ja">チェック</span></span></button>
      <button class="btn" id="edit"><svg class="ic"><use href="#i-pencil"/></svg>
       <span class="lbl">편집<span class="sub" lang="ja">編集</span></span></button>
''', '')
# 2. 하단 바에 구간 반복
rep('''      <button class="btn" id="cfStop"><svg class="ic fill"><use href="#i-stop"/></svg>정지</button>
      <button class="btn" id="cfNext">다음<svg class="ic"><use href="#i-right"/></svg></button>''',
    '''      <button class="btn" id="cfStop"><svg class="ic fill"><use href="#i-stop"/></svg>정지</button>
      <button class="btn" id="cfLoop" aria-pressed="false"><svg class="ic"><use href="#i-repeat"/></svg>반복</button>
      <button class="btn" id="cfNext"><span class="txt">다음</span><svg class="ic"><use href="#i-right"/></svg></button>''')
rep('''      <button class="btn" id="cfPrev"><svg class="ic"><use href="#i-left"/></svg>이전</button>''',
    '''      <button class="btn" id="cfPrev"><svg class="ic"><use href="#i-left"/></svg><span class="txt">이전</span></button>''')
rep('''$('cfStop').onclick = stopAll;''', '''$('cfStop').onclick = stopAll;
$('cfLoop').onclick = () => $('loop').click();''')
rep('''  $('loop').setAttribute('aria-pressed', String(!!loopSeg));
}''', '''  $('loop').setAttribute('aria-pressed', String(!!loopSeg));
  $('cfLoop').setAttribute('aria-pressed', String(!!loopSeg));
}''')
# 3. CSS
rep('''\n.cardfoot{display:none}\n''', '''\n.cardfoot{display:none}
.card-top .ctl{display:inline-flex;align-items:center;gap:6px;flex:none}
.ibtn{display:inline-grid;place-items:center;width:30px;height:30px;padding:0;border-radius:8px;border:1px solid var(--line-2);background:var(--surface);color:var(--ink-2)}
.ibtn .ic{width:15px;height:15px}
.ibtn:hover{color:var(--brand);border-color:var(--brand-line)}
.ibtn[aria-pressed=true]{background:var(--brand);border-color:var(--brand);color:#fff}''')
rep(''' .cardfoot{display:grid;grid-template-columns:1fr 1.3fr 1fr 1fr;''', ''' .cardfoot{display:grid;grid-template-columns:auto 1.3fr 1fr 1fr auto;''')
rep(''' .cardfoot .btn{min-height:46px;justify-content:center;flex:none;padding:8px 4px;gap:4px;font-size:12.5px;white-space:nowrap}''',
    ''' .cardfoot .btn{min-height:46px;justify-content:center;flex:none;padding:8px 4px;gap:4px;font-size:12.5px;white-space:nowrap}
 .cardfoot .txt{display:none}.cardfoot #cfPrev,.cardfoot #cfNext{padding:8px 12px}
 .playrow #play,.playrow #stop,.playrow #loop{display:none}.playrow{margin:12px 0 0}.playrow .btn{flex:1 1 100%}
 .card .keys{display:none}''')
open(path, 'w', encoding='utf-8').write(h); print('layout-patched', path, N)
