"""노래 앱: 「마디 반복」을 카드 상단 체크·편집 옆 작은 아이콘으로. patch_layout2.py 뒤에 적용."""
import sys
path = sys.argv[1]; h = open(path, encoding='utf-8').read(); N = 0
def rep(old, new):
    global h, N
    assert h.count(old) == 1, f'[{N}] {h.count(old)} matches: {old[:60]!r}'
    h = h.replace(old, new); N += 1
if 'id="toKara"' in h:
    rep('''      <button class="btn" id="toKara" title="노래방 탭에서 이 줄의 마디를 반복"><svg class="ic"><use href="#i-sound"/></svg>
       <span class="lbl">마디 반복<span class="sub" lang="ja">小節リピート</span></span></button>
''', '')
    rep('''       <button class="ibtn" id="edit" title="편집 / 編集"><svg class="ic"><use href="#i-pencil"/></svg></button>''',
        '''       <button class="ibtn" id="edit" title="편집 / 編集"><svg class="ic"><use href="#i-pencil"/></svg></button>
       <button class="ibtn ibtn-kara" id="toKara" title="마디 반복 · 노래방에서 이 줄의 마디를 되풀이 / 小節リピート"><svg class="ic"><use href="#i-bars"/></svg></button>''')
    rep('''<symbol id="i-stop" viewBox="0 0 24 24">''', '''<symbol id="i-bars" viewBox="0 0 24 24"><path d="M4 5v14M10 5v14M16 5v14M22 5v14M4 12h18"/></symbol>
<symbol id="i-stop" viewBox="0 0 24 24">''')
    rep('''.ibtn[aria-pressed=true]{background:var(--brand);border-color:var(--brand);color:#fff}''',
        '''.ibtn[aria-pressed=true]{background:var(--brand);border-color:var(--brand);color:#fff}
.ibtn-kara{background:var(--brand-soft);border-color:var(--brand-line);color:var(--brand)}''')
open(path, 'w', encoding='utf-8').write(h); print('layout3-patched', path, N)
