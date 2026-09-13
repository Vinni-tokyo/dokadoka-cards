"""카드 안 「이 장면 재생·정지·구간 반복」 삭제 — PC 에서도 하단 조작 줄(‹ 재생 정지 반복 ›) 하나만. patch_tts3.py 뒤에 적용."""
import sys
path = sys.argv[1]; h = open(path, encoding='utf-8').read(); N = 0
def rep(old, new):
    global h, N
    assert h.count(old) == 1, f'[{N}] {h.count(old)} matches: {old[:60]!r}'
    h = h.replace(old, new); N += 1
rep('''\n.cardfoot{display:none}\n''', '''\n.cardfoot{display:grid;grid-template-columns:auto 1.3fr 1fr 1fr auto;gap:8px;margin-top:16px}
.cardfoot .btn{justify-content:center;min-height:44px;white-space:nowrap;padding:8px 6px;gap:5px;font-size:13px}
.card .nav{display:none}
#play,#stop,#loop{display:none}
.playrow{margin:0}.playrow .btn{margin-top:14px}
''')
rep(''' .playrow #play,.playrow #stop,.playrow #loop{display:none}.playrow{margin:12px 0 0}.playrow .btn{flex:1 1 100%}''',
    ''' .playrow .btn{flex:1 1 100%;margin-top:12px}''')
rep(''' .card:not(.sess){padding-bottom:96px}
 .card:not(.sess) .nav{display:none}''', ''' .card:not(.sess){padding-bottom:96px}''')
open(path, 'w', encoding='utf-8').write(h); print('layout2-patched', path, N)
