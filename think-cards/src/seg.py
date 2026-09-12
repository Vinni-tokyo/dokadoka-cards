"""문장 단위 캡션(화자 표시 없음) → 카드 분할.
   Bloomberg 류 공식 캡션은 큐가 문장 중간에서 끊기고 화자 표시가 없다.
   1) 큐를 전부 이어 붙여 한 덩어리 텍스트를 만들고(글자 위치 ↔ 큐 시각 대응표 유지),
   2) 문장 끝([.?!] + 대문자) 과 turns.txt 의 「화자 전환 구절」에서 자르고,
   3) 같은 화자의 짧은 문장을 MAXLEN 안에서 한 장으로 합친다.
   turns.txt:  `구절|화자`  — 그 구절이 시작되는 지점부터 화자가 바뀐다(구절은 본문에 정확히 1회 있어야 한다).
   첫 줄의 화자가 영상 첫 문장의 화자다."""
import re, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
raw = open(os.path.join(HERE, 'subtitles.srt'), encoding='utf-8-sig').read()

cues = []
for b in re.split(r'\n\s*\n', raw.strip()):
    L = [l.rstrip() for l in b.strip().split('\n') if l.strip()]
    if len(L) < 3: continue
    m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', L[1])
    if not m: continue
    g = list(map(int, m.groups()))
    t = re.sub(r'\s+', ' ', ' '.join(L[2:])).strip()
    t = re.sub(r'\s*\[[a-z][^\]]*\]\s*', ' ', t).strip()          # [Music] 류 효과음
    if not t: continue
    cues.append({'n': int(L[0]), 's': g[0]*3600+g[1]*60+g[2]+g[3]/1000,
                 'e': g[4]*3600+g[5]*60+g[6]+g[7]/1000, 't': t})

# 전체 텍스트와 글자 위치 → 시각 대응표
T, spans, pos = '', [], 0
for c in cues:
    if T: T += ' '; pos += 1
    spans.append((pos, pos + len(c['t']), c['s'], c['e'])); T += c['t']; pos += len(c['t'])
def t_at(ch):
    for a, b, s, e in spans:
        if a <= ch <= b: return round(s + (e - s) * ((ch - a) / max(b - a, 1)), 2)
    return spans[-1][3]

# 화자 전환 지점. turns.txt 가 없으면 전부 한 화자(강연자)로 본다
TURNS = []
tp = os.path.join(HERE, 'turns.txt')
if not os.path.exists(tp): TURNS = [(0, 'Speaker')]
for ln in (open(tp, encoding='utf-8') if os.path.exists(tp) else []):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.startswith('#'): continue
    phrase, spk = [x.strip() for x in ln.split('|', 1)]
    n = T.count(phrase)
    assert n == 1, f'turns.txt 구절이 본문에 {n}회: {phrase!r}'
    TURNS.append((T.index(phrase), spk))
TURNS.sort()
assert TURNS and TURNS[0][0] == 0, 'turns.txt 첫 구절은 본문 첫머리여야 한다'

# 자르는 지점 = 문장 끝 + 화자 전환
cuts = {m.end() for m in re.finditer(r'(?<!\bDr\.)(?<!\bMr\.)(?<!\bMs\.)(?<=[.?!])\s+(?=[A-Z"\'\[])', T)}
# 200자를 넘는 한 문장은 가운데에 가까운 절 경계(', and ' ', but ' ', because ' ', so ')에서 한 번 더 나눈다
LONG, CLAUSE = 200, re.compile(r', (?:and|but|because|so|which|where) ')
def split_long(a, b):
    if b - a <= LONG: return []
    best = None
    for m in CLAUSE.finditer(T, a, b):
        cut = m.start() + 1                       # 쉼표 뒤에서 자른다
        if best is None or abs(cut - (a + b) / 2) < abs(best - (a + b) / 2): best = cut
    if best is None: return []
    return [best] + split_long(a, best) + split_long(best, b)
cuts |= {p for p, _ in TURNS}; cuts |= {0, len(T)}
cuts = sorted(cuts)
extra = set()
for a, b in zip(cuts, cuts[1:]): extra |= set(split_long(a, b))
cuts = sorted(set(cuts) | extra)
def spk_at(ch):
    s = TURNS[0][1]
    for p, k in TURNS:
        if ch >= p: s = k
    return s
sents = []
for a, b in zip(cuts, cuts[1:]):
    body = T[a:b].strip()
    if not body: continue
    sents.append({'a': a, 'b': a + len(T[a:b].rstrip()), 't': body, 'spk': spk_at(a)})

# 같은 화자의 문장을 MAXLEN 안에서 합친다. 아주 짧은 맞장구(Yeah. Right.)는 다음 문장에 붙인다
MAXLEN = 110
segs = []
for s in sents:
    prev = segs[-1] if segs else None
    if prev and prev['spk'] == s['spk'] and (len(prev['t']) + 1 + len(s['t']) <= MAXLEN or len(prev['t']) < 12):
        prev['t'] += ' ' + s['t']; prev['b'] = s['b']
    else:
        segs.append(dict(s))

out = []
for i, g in enumerate(segs, 1):
    out.append({'id': i, 's': t_at(g['a']), 'e': t_at(g['b']), 'en': g['t'], 'spk': g['spk']})
for x, y in zip(out, out[1:]):
    if x['e'] > y['s']: x['e'] = y['s']
json.dump(out, open(os.path.join(HERE, 'segs.json'), 'w'), ensure_ascii=False, indent=1)
if __name__ == '__main__':
    print('큐:', len(cues), '| 문장:', len(sents), '| 화자 전환:', len(TURNS), '→ 카드:', len(out))
    L = [len(o['en']) for o in out]
    print('길이(자): 평균 %.1f 중앙 %d 최대 %d' % (sum(L)/len(L), sorted(L)[len(L)//2], max(L)))
    from collections import Counter
    print('화자:', dict(Counter(o['spk'] for o in out)))
