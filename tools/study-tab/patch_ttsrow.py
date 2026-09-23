#!/usr/bin/env python3
"""읽어주기 줄 여섯 버튼을 한 줄에 넣는다.

문제: 카드 아래 「읽어주기 · 천천히 · 3회 · 전부 · 🔉 · ■」 여섯이 폰에서 두 줄로 접히고,
      정지(■) 혼자 다음 줄에 남아 보기 사납다. 실측(390px): 버튼합 366px / 들어갈 칸 336px.

고침: ① 첫 버튼의 글자를 「읽어주기」→「읽기」로 줄인다(무엇을 하는지는 title 에 그대로 남는다).
      ② 430px 이하에서만 이 줄의 좌우 여백과 버튼 사이를 조인다.
      둘을 같이 해야 들어간다 — 이름만 줄이면 340px 로 390px 화면에서 4px 모자란다.
      실측(고친 뒤): 360px 299 / 306, 390px 299 / 336, 412px 299 / 358 — 셋 다 한 줄.

일본어 화면인 앱은 같은 자리가 「読み上げ」다. 둘 다 본다.
사용: python3 patch_ttsrow.py <앱폴더>/src/tpl.html [...]
"""
import io
import sys

CSS = ('\n@media(max-width:430px){.ttsrow{gap:5px}.ttsrow .btn{padding-left:8px;padding-right:8px}}'
       '   /* 여섯 버튼이 한 줄에 들어가게 — 정지가 혼자 다음 줄로 떨어지던 것을 막는다 */'
       '\n@media(max-width:340px){.ttsrow #ttsPlay>.ic{display:none}.ttsrow .btn{padding-left:6px;padding-right:6px}}'
       '   /* 320px 짜리 옛 폰에서는 아이콘까지 뺀다 */')

LABELS = [('</svg>읽어주기</button>', '</svg>읽기</button>'),
          ('</svg>読み上げ</button>', '</svg>読み</button>')]


def patch(path):
    h = io.open(path, encoding='utf-8').read()
    if '.ttsrow .btn{padding-left:8px' in h:
        print('  건너뜀(이미 적용):', path)
        return
    n = 0
    for old, new in LABELS:
        if old in h:
            assert h.count(old) == 1, f'{path}: {old} 가 {h.count(old)} 개'
            h = h.replace(old, new, 1)
            n += 1
    assert n == 1, f'{path}: 읽어주기 버튼을 {n} 개 찾았다'

    anchor = '.ttsrow .btn[aria-pressed=true]{'
    i = h.index(anchor)
    j = h.index('\n', i)
    h = h[:j] + CSS + h[j:]

    io.open(path, 'w', encoding='utf-8').write(h)
    print('  고침:', path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for p in sys.argv[1:]:
        patch(p)
