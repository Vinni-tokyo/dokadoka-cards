"""분할: raw/Joa5MSfh_Ho.ja.srt(공식 수동 일본어 자막) -> segs.json

공식 자막이라 큐 시각이 깨끗하다(겹침 0, 평균 2.4초). 그래서 큐를 그대로 카드로 쓰되
 - ［...］ 는 화면 자막(대사 아님). 큐 전체가 화면 자막이면 spk='Cap' 카드 한 장,
   화면 자막 + 대사가 섞인 큐는 글자수 비례로 나눠 두 장으로 만든다.
 - '- A - B' 형태(한 큐에 두 화자)는 대시로 나눈다.
"""
import json, os, re

S = os.path.dirname(os.path.abspath(__file__))
VID = 'Joa5MSfh_Ho'
SRT = os.path.join(S, 'raw', f'{VID}.ja.srt')

CAP_RE = re.compile(r'［([^］]*)］')


def parse_srt(path):
    raw = open(path, encoding='utf-8-sig').read()
    out = []
    for block in re.split(r'\n\s*\n', raw.strip()):
        lines = block.split('\n')
        if len(lines) < 3:
            continue
        m = re.match(r'(\d+):(\d+):(\d+)[,.](\d+) --> (\d+):(\d+):(\d+)[,.](\d+)', lines[1])
        if not m:
            continue
        g = list(map(int, m.groups()))
        s = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        e = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        out.append({'s': s, 'e': e, 'text': ' '.join(x.strip() for x in lines[2:]).strip()})
    return out


def split_parts(text):
    """큐 텍스트 -> [(종류, 문자열)] 종류: 'cap'(화면 자막) | 'say'(대사)"""
    parts, pos = [], 0
    for m in CAP_RE.finditer(text):
        before = text[pos:m.start()].strip()
        if before:
            parts.append(('say', before))
        cap = m.group(1).strip()
        if cap:
            parts.append(('cap', cap))
        pos = m.end()
    rest = text[pos:].strip()
    if rest:
        parts.append(('say', rest))
    # 대사 안에 '- A - B' 가 있으면 화자별로 나눈다
    out = []
    for kind, t in parts:
        if kind == 'say' and re.match(r'^-\s', t):
            for piece in re.split(r'\s+-\s+', t.lstrip('- ').strip()):
                piece = piece.strip()
                if piece:
                    out.append(('say', piece))
        else:
            out.append((kind, t))
    return out


def build():
    cues = parse_srt(SRT)
    segs, cid = [], 1
    for c in cues:
        parts = split_parts(c['text'])
        if not parts:
            continue
        total = sum(len(t) for _, t in parts) or 1
        t0, span = c['s'], c['e'] - c['s']
        for i, (kind, text) in enumerate(parts):
            st = t0
            en = c['e'] if i == len(parts) - 1 else t0 + span * len(text) / total
            row = {'id': cid, 's': round(st, 2), 'e': round(en, 2), 'ja': text}
            if kind == 'cap':
                row['cap'] = 1
            segs.append(row)
            t0, cid = en, cid + 1
    json.dump(segs, open(os.path.join(S, 'segs.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    return segs


if __name__ == '__main__':
    segs = build()
    print('카드:', len(segs), '| 화면 자막:', sum(1 for s in segs if s.get('cap')),
          '| 대사:', sum(1 for s in segs if not s.get('cap')))
