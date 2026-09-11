"""화별 분할: raw/epN/*.ja.srt -> src/epN/segs.json
카드 경계 = 자막 큐를 '-' 기준으로 쪼갠 발화 하나하나.
"""
import json, os, sys
S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
from srtlib import build_lines

EPS = {
    1: 'iHd7eWUXuLU', 2: 'FGtvnG98mQs', 3: 'QbfPKfEuqCY', 4: '8F7aVVep4e8',
    5: 'UqEgW4dUHuc', 6: 'ZzdzjkKl2zE', 7: 'uMGK0gZgJn8',
}


def make(ep):
    vid = EPS[ep]
    ja_path = os.path.join(S, 'raw', f'ep{ep}', f'{vid}.ja.srt')
    lines = build_lines(ja_path)
    segs = []
    for i, ln in enumerate(lines, 1):
        segs.append({'id': i, 's': ln['s'], 'e': ln['e'], 'ja': ln['text']})
    out_dir = os.path.join(S, f'ep{ep}')
    os.makedirs(out_dir, exist_ok=True)
    json.dump(segs, open(os.path.join(out_dir, 'segs.json'), 'w', encoding='utf-8'),
               ensure_ascii=False, indent=1)
    return segs


if __name__ == '__main__':
    for ep in range(1, 8):
        segs = make(ep)
        print(f'ep{ep}: {len(segs)}장')
