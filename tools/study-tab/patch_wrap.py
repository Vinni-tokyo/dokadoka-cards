#!/usr/bin/env python3
"""노래방·감상 화면의 긴 가사 줄이 화면 밖으로 나가던 것을 막는다.

문제: 가사 줄에 word-break:keep-all 이 걸려 있다. 한국어에는 맞는 규칙이지만
      (낱말을 쪼개지 않는다) 일본어에는 띄어쓰기가 없어서 끊을 자리가 아예 없다.
      그래서 한 줄이 통째로 오른쪽으로 삐져나간다.
      실측(390px): 「I love you 今だけは悲しい歌聞きたくないよ」가 59px 밖으로 나갔다.
      좁을수록 심하다 — 360px 에서 89px.

고침: 가사 줄에 overflow-wrap:anywhere 을 준다(넘칠 때만 끊는다 — 한국어 낱말은 그대로).
      lang="ja" 가 붙은 줄은 word-break:normal 로 일본어 줄바꿈 규칙을 쓴다
      (작은 가나·문장부호가 줄머리에 오지 않는다).

사용: python3 patch_wrap.py <앱폴더>/src/tpl.html [...]
"""
import io
import sys

CSS = ('\n.kara-line,.kara-prev,.kara-next,.kara-next2,.kara-rd,.kara-ja,'
       '.watch-line,.watch-prev,.watch-next{overflow-wrap:anywhere}'
       '\n.kara-line:lang(ja),.watch-line:lang(ja){word-break:normal}'
       '   /* 일본어는 띄어쓰기가 없어 keep-all 이면 줄을 못 바꾼다 */')


def patch(path):
    h = io.open(path, encoding='utf-8').read()
    if '.kara-line:lang(ja)' in h:
        print('  건너뜀(이미 적용):', path)
        return
    # 감상 화면이 없는 앱(노래 앱 일부)에는 .watch-* 줄이 없다 — 그때는 가사 줄 뒤에 붙인다.
    for anchor in ('.watch-prev,.watch-next{', '.kara-line .kc.part{'):
        if h.count(anchor) == 1:
            break
    else:
        raise AssertionError(f'{path}: 기준 줄을 못 찾았다')
    j = h.index('\n', h.index(anchor))
    io.open(path, 'w', encoding='utf-8').write(h[:j] + CSS + h[j:])
    print('  고침:', path)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for p in sys.argv[1:]:
        patch(p)
