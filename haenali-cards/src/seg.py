"""lines.txt(음성 인식을 손으로 확정한 원문) → segs.json. id 는 시간순 1부터."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
segs = []
for ln in open(os.path.join(HERE, 'lines.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'): continue
    s, e, spk, ja = ln.split('|', 3)
    segs.append({'s': float(s), 'e': float(e), 'spk': spk.strip(), 'ja': ja.strip()})
segs.sort(key=lambda x: x['s'])
for i, x in enumerate(segs, 1):
    assert x['e'] > x['s'], x
    x['id'] = i
for a, b in zip(segs, segs[1:]):
    assert a['e'] <= b['s'] + .05, (a, b)                  # 카드끼리 겹치지 않는다
json.dump(segs, open(os.path.join(HERE, 'segs.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('카드', len(segs))
