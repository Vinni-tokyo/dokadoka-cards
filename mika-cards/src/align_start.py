"""카드별 재생 시작점 보정 -> starts.json

공식 수동 자막은 큐가 빈틈없이 이어진다(앞 큐 끝 = 다음 큐 시작). 자막은 발화보다 조금 먼저
뜨기 때문에, 큐 시작에서 그대로 재생하면 앞 사람 말끝이 다음 카드 앞에 딸려 들어온다.

그래서 같은 영상의 음성 인식 자막(ja-orig, 실제 음성의 시작 시각)을 대조해
카드마다 '진짜 발화가 시작되는 시각'을 찾아 시작점을 뒤로 민다.
 - 화면 자막(cap) 카드는 발화가 아니므로 건드리지 않는다.
 - 보정은 [0.08초, 1.2초] 범위만. 그 밖은 대조 실패로 보고 원래 시각을 쓴다.
 - 카드 끝에서 최소 0.4초는 남긴다(너무 밀어 첫 음절이 잘리지 않게).
"""
import json, os, re, sys

S = os.path.dirname(os.path.abspath(__file__))
ASR = os.path.join(S, 'raw', 'asr_Joa5MSfh_Ho.ja-orig.srt')
MIN_SHIFT, MAX_SHIFT, KEEP_TAIL = 0.08, 1.2, 0.4
# 음성 인식이 앞 발화와 묶어버려 시작점을 못 찾은 카드에 주는 기본 보정.
# 이 영상에서 자막이 실제 발화보다 앞서는 양의 중앙값(+0.14초)에서 가져왔다.
FALLBACK, FALLBACK_MIN_LEN = 0.15, 0.5
PUNCT = re.compile(r'[\s、。！？!?…・「」（）()［］\[\]~〜ー-]')


def load_srt(path):
    raw = open(path, encoding='utf-8-sig').read()
    out = []
    for block in re.split(r'\n\s*\n', raw.strip()):
        lines = block.split('\n')
        if len(lines) < 3:
            continue
        m = re.match(r'(\d+):(\d+):(\d+)[,.](\d+)', lines[1])
        if not m:
            continue
        g = list(map(int, m.groups()))
        text = ' '.join(lines[2:]).strip()
        if text and not re.fullmatch(r'(\[[^\]]*\]\s*)+', text):
            out.append((g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000, text))
    return out


def sim(a, b):
    """글자 겹침 비율. ASR 오인식이 있어도 같은 발화면 꽤 겹친다."""
    A, B = PUNCT.sub('', a), PUNCT.sub('', b)
    if not A or not B:
        return 0.0
    from collections import Counter
    ca, cb = Counter(A), Counter(B)
    common = sum((ca & cb).values())
    return common / min(len(A), len(B))


def main():
    asr = load_srt(ASR)
    segs = json.load(open(os.path.join(S, 'segs.json'), encoding='utf-8'))
    starts, shifts, fallbacks = {}, [], 0
    for s in segs:
        if s.get('cap'):
            continue
        lo, hi = s['s'] - 0.3, min(s['s'] + MAX_SHIFT, s['e'] - KEEP_TAIL)
        if hi <= lo:
            continue
        cands = [(t, x) for t, x in asr if lo <= t <= hi]
        if not cands:                              # 대조 실패 -> 기본 보정만
            t = s['s'] + FALLBACK
            if s['e'] - t >= FALLBACK_MIN_LEN:
                starts[str(s['id'])] = round(t, 2)
                fallbacks += 1
            continue
        scored = [(sim(s['ja'], x), -abs(t - s['s']), t) for t, x in cands]
        scored.sort(reverse=True)
        best_sim, _, t = scored[0]
        if best_sim < 0.25:                       # 대조가 약하면 시간만 보고 가장 가까운 것
            t = min((c[0] for c in cands), key=lambda v: abs(v - s['s']))
        shift = t - s['s']
        if MIN_SHIFT <= shift <= MAX_SHIFT:
            starts[str(s['id'])] = round(t, 2)
            shifts.append(shift)
    json.dump(starts, open(os.path.join(S, 'starts.json'), 'w', encoding='utf-8'), indent=1)
    import statistics
    print('대사 카드', sum(1 for s in segs if not s.get('cap')),
          '| 음성 대조 보정', len(shifts), '| 기본 보정', fallbacks, '| 합계', len(starts),
          '| 평균 %+.2f초 · 중앙값 %+.2f초 · 최대 %+.2f초'
          % (statistics.mean(shifts), statistics.median(shifts), max(shifts)) if shifts else '')


if __name__ == '__main__':
    main()
