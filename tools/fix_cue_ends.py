#!/usr/bin/env python3
"""잘린 줄 끝 시각을 노래의 실제 속도로 되돌린다.

align.py 는 줄의 끝을 「음성 인식이 잡은 마지막 단어의 끝」으로 찍는다.
인식이 줄 앞부분만 잡으면 끝이 일찍 찍히고, 노래방에서 가사가 후루룩 다 채워진 뒤
멈춰 선다(사랑하기 때문에 8·22·33번이 그랬다. 글자당 0.40초 — 곡 중앙값의 60%).

고침: 글자당 시간이 이 곡 중앙값의 62% 미만인 줄만, 중앙값 속도로 끝을 다시 잡는다.
      다음 줄 시작보다 0.15초 앞을 넘지 않는다. 시작 시각과 나머지 줄은 건드리지 않는다.
      길게 끄는 줄(중앙값보다 느린 줄)은 일부러 그런 것일 수 있어 손대지 않는다.

사용: python3 tools/fix_cue_ends.py <앱폴더>/src/subtitles.srt [--dry]
"""
import io
import re
import statistics as st
import sys

SLOW_ENOUGH = 0.62      # 중앙값 대비 이 비율 미만이면 잘린 것으로 본다
GAP = 0.15              # 다음 줄 시작과의 최소 간격
TAIL = 2.0              # 마지막 줄이 늘어날 수 있는 여유


def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')


def main(path, dry=False):
    order, cues = [], {}
    for blk in re.split(r'\n\s*\n', io.open(path, encoding='utf-8').read().strip()):
        L = [x for x in blk.strip().split('\n') if x.strip()]
        if len(L) < 3:
            continue
        i = int(L[0])
        m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', L[1])
        g = list(map(int, m.groups()))
        cues[i] = [g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000,
                   g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000, '\n'.join(L[2:])]
        order.append(i)

    # 글자 수는 노래로 불리는 글자만 (한글·가나·한자)
    nch = lambda s: max(1, len(re.sub(r'[^가-힣぀-ヿ一-鿿]', '', s)))
    rate = st.median([(c[1] - c[0]) / nch(c[2]) for c in cues.values()])
    end_all = max(c[1] for c in cues.values()) + TAIL
    print(f'{len(order)}줄 · 글자당 시간 중앙값 {rate:.3f}초')

    changed = []
    for k, i in enumerate(order):
        s, e, t = cues[i]
        c = nch(t)
        if (e - s) / c >= rate * SLOW_ENOUGH:
            continue                                   # 속도가 정상이면 두고 본다
        nxt = cues[order[k + 1]][0] if k + 1 < len(order) else end_all
        new = min(s + c * rate, nxt - GAP)
        if new - e >= 0.3:
            changed.append((i, e, new, round((e - s) / c, 2), round((new - s) / c, 2)))
            cues[i][1] = new

    if not changed:
        print('잘린 줄 없음 — 그대로 둡니다')
        return 0
    print('\n 줄   끝 시각          글자당 시간        늘어난 만큼')
    for i, old, new, r0, r1 in changed:
        print(f'{i:>3}  {old:>6.1f} → {new:>6.1f}   {r0:.2f} → {r1:.2f}초      +{new - old:.1f}초')

    bad = [i for k, i in enumerate(order[:-1]) if cues[i][1] > cues[order[k + 1]][0]]
    assert not bad, f'겹침 발생: {bad}'
    print(f'\n고친 줄 {len(changed)}개 · 겹침 없음')
    if dry:
        print('(--dry 라 파일은 그대로)')
        return 0
    with io.open(path, 'w', encoding='utf-8') as f:
        for i in order:
            s, e, t = cues[i]
            f.write(f'{i}\n{ts(s)} --> {ts(e)}\n{t}\n\n')
    print(f'{path} 갱신')
    return 0


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--dry']
    if not args:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(args[0], '--dry' in sys.argv))
