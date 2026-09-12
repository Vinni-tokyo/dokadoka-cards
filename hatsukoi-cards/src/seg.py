"""분할: raw/asr.json(faster-whisper 인식 결과) + fixes.txt(교정) -> segs.json

이 영상은 자막이 하나도 없어(수동·자동 모두) 음성 인식으로 대본을 만들었다.
whisper 가 VAD 로 끊어 준 구간이 이미 문장 단위에 가깝고 서로 겹치지 않아 그대로 카드로 쓴다.
 - 40자가 넘는 구간만 문장 끝(。？!)에서 한 번 더 나눈다(시각은 글자수 비례).
 - 오인식은 fixes.txt(`id|교정문`)로 고치고, 원문은 raw 로 남겨 앱에 병기한다.
"""
import json, os, re

S = os.path.dirname(os.path.abspath(__file__))
SPLIT_AT = 40


def load_fixes():
    fixes = {}
    path = os.path.join(S, 'fixes.txt')
    if not os.path.exists(path):
        return fixes
    for ln in open(path, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln.strip() or ln.lstrip().startswith('#'):
            continue
        i, text = ln.split('|', 1)
        fixes[int(i)] = text.strip()
    return fixes


def split_long(text):
    """40자 넘는 줄을 문장 끝에서 나눈다. 문장 끝이 없으면 그대로 둔다."""
    if len(text) <= SPLIT_AT:
        return [text]
    parts, buf = [], ''
    for piece in re.split(r'(?<=[。？！?!])', text):
        if not piece:
            continue
        if buf and len(buf) + len(piece) > SPLIT_AT:
            parts.append(buf)
            buf = piece
        else:
            buf += piece
    if buf:
        parts.append(buf)
    return parts or [text]


def build():
    asr = json.load(open(os.path.join(S, 'raw', 'asr.json'), encoding='utf-8'))
    fixes = load_fixes()
    segs, cid = [], 1
    for i, a in enumerate(asr, 1):
        raw = a['ja'].strip()
        text = fixes.get(i, raw)
        parts = split_long(text)
        total = sum(len(p) for p in parts) or 1
        t0, span = a['s'], a['e'] - a['s']
        for k, p in enumerate(parts):
            st = t0
            en = a['e'] if k == len(parts) - 1 else t0 + span * len(p) / total
            row = {'id': cid, 's': round(st, 2), 'e': round(en, 2), 'ja': p}
            if i in fixes and len(parts) == 1 and p != raw:
                row['raw'] = raw                      # 교정 전 원문(앱에 병기)
            segs.append(row)
            t0, cid = en, cid + 1
    json.dump(segs, open(os.path.join(S, 'segs.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    return segs, fixes


if __name__ == '__main__':
    segs, fixes = build()
    print('카드:', len(segs), '| 인식 구간:', len(json.load(open(os.path.join(S, 'raw', 'asr.json'), encoding='utf-8'))),
          '| 교정:', len(fixes), '건')
