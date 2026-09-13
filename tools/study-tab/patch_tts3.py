"""읽어주기 줄을 뜻 영역에서 문장(읽기 줄) 바로 아래로 옮긴다. patch_layout.py 뒤에 적용."""
import sys, re
path = sys.argv[1]; h = open(path, encoding='utf-8').read(); N = 0
def rep(old, new):
    global h, N
    assert h.count(old) == 1, f'[{N}] {h.count(old)} matches: {old[:60]!r}'
    h = h.replace(old, new); N += 1
a = h.index('      <div class="ttsrow">'); b = h.index('      <p class="ko" id="ko"></p>')
row = h[a:b]; h = h[:a] + h[b:]; N += 1
row = row.replace('      <div class="ttsrow">', '     <div class="ttsrow">').replace('\n       ', '\n      ').replace('      </div>\n', '     </div>\n')
rep('''     <p class="rd" id="rd" hidden><b>읽기</b><span lang="ja" id="rdText"></span></p>
''', '''     <p class="rd" id="rd" hidden><b>읽기</b><span lang="ja" id="rdText"></span></p>
''' + row)
rep('''.ttsrow{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:0 0 10px}''', '''.ttsrow{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:12px 0 0}''')
rep('''  else if(k === 't'){ e.preventDefault(); if(!$('answer').hidden) ttsLine(1, 1); }''', '''  else if(k === 't'){ e.preventDefault(); ttsLine(1, 1); }''')
open(path, 'w', encoding='utf-8').write(h); print('tts3-patched', path, N)
