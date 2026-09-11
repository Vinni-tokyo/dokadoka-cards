"""ko.txt 초안 생성: id|한국어(자동 정렬, 공식 자막)|읽기(자동, fugashi)|주석(비움)
사람이 다듬을 출발점. 실행 후 src/epN/ko.txt 를 편집한다(이미 있으면 건드리지 않음)."""
import json, os, sys
S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
from srtlib import build_lines, align_ko
from reading import reading
from seg import EPS


def make(ep, force=False):
    out_path = os.path.join(S, f'ep{ep}', 'ko.txt')
    if os.path.exists(out_path) and not force:
        print(f'ep{ep}: ko.txt 이미 있음, 건너뜀')
        return
    vid = EPS[ep]
    ja_lines = build_lines(os.path.join(S, 'raw', f'ep{ep}', f'{vid}.ja.srt'))
    ko_lines = build_lines(os.path.join(S, 'raw', f'ep{ep}', f'{vid}.ko.srt'))
    aligned = align_ko(ja_lines, ko_lines)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('# 형식: id|한국어 뜻|읽기(히라가나, 띄어쓰기)|주석  (자동초안 - 검수 필요)\n')
        for i, (j, k) in enumerate(zip(ja_lines, aligned), 1):
            rd = reading(j['text'])
            k = k.replace('|', '/').strip()
            f.write(f'{i}|{k}|{rd}|\n')
    print(f'ep{ep}: {len(ja_lines)}줄 초안 작성 -> {out_path}')


if __name__ == '__main__':
    force = '--force' in sys.argv
    for ep in range(1, 8):
        make(ep, force=force)
