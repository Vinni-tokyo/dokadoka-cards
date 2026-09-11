"""Vogue 공식 영어 자막(전문 캡션) → 카드 분할.
   자막 형식:  '- [Interviewer] 대사'  화자 태그가 붙은 새 발화
              '- 대사'                 태그 없는 새 발화(화자 교대). 2인 인터뷰이므로 직전 화자의 상대로 추정한다(inf=1)
              '대사'                   같은 큐 안(또는 앞 큐에서) 이어지는 말
              '[dog barks]'            효과음 — 카드에서 제외
   한 큐에 '- A / - B' 처럼 두 발화가 들어 있으면 줄 단위로 나눈다.
   추정이 틀린 줄은 LINE_FIX(줄 원문 → 화자)로 고친다. 태그 오기(Darrel)는 ALIAS 로 통일한다.
   긴 대답은 문장 끝에서 SPLIT_AT 자 안팎으로 나눈다(시각은 줄 단위 큐 시각에서 가져온다)."""
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
    cues.append({'n': int(L[0]), 's': g[0]*3600+g[1]*60+g[2]+g[3]/1000,
                 'e': g[4]*3600+g[5]*60+g[6]+g[7]/1000, 'lines': L[2:]})

MAIN = ('Interviewer', 'Zendaya')                 # 태그 없는 새 발화는 이 둘이 번갈아 말하는 것으로 본다
ALIAS = {'Darrel': 'Darnell'}                     # 자막의 표기 오류
# 줄 원문 → 화자.  (a) 대시 없이 이어지는 줄인데 화자가 바뀐 곳  (b) 교대 추정이 틀린 곳
LINE_FIX = {
 'And, I see': 'Interviewer',                     # 큐10: "Let's do it." 은 Zendaya, 이어지는 질문은 Interviewer
 '- Hey, Darnell. Can you take these for me?': 'Zendaya',
 '- This is Darnell,': 'Zendaya',
 '- Thank you.': 'Zendaya',                       # 큐59: Darnell 에게 (큐393 도 Zendaya 라 같은 규칙)
 'Mmm, looks delicious.': 'Interviewer',          # 큐278: 레모네이드를 받은 쪽
 '- When life gives you': 'Zendaya',              # 큐343: Darnell 의 "That's my cue!" 다음
}
SFX = re.compile(r'^\[[^\]]*\]$')

# 조각 = 한 화자의 연속 발화. frags 에 (시작, 끝, 본문) 을 줄 단위로 쌓아 두었다가 긴 대답을 나눌 때 시각으로 쓴다
pieces, n_sfx = [], 0
last = ''
def add_frag(p, c, body): p['frags'].append([c['s'], c['e'], body]); p['e'] = c['e']
for c in cues:
    cur = None
    for ln in c['lines']:
        t = ln.strip()
        if SFX.match(t): n_sfx += 1; continue
        t = re.sub(r'\s*\[[a-z][^\]]*\]\s*', ' ', t).strip()          # 줄 끝의 효과음 [dog barks]
        if not t: continue
        spk, inf = None, 0
        if t.startswith('-'):
            body = t[1:].strip()
            m = re.match(r'^\[([A-Za-z]+)\]\s*(.*)$', body)
            if m: spk, body = ALIAS.get(m.group(1), m.group(1)), m.group(2).strip()
            elif ln.strip() in LINE_FIX: spk = LINE_FIX[ln.strip()]
            else: spk, inf = (MAIN[1] if last == MAIN[0] else MAIN[0]), 1
        else:
            body = t
            if ln.strip() in LINE_FIX: spk = LINE_FIX[ln.strip()]
            elif cur is not None: add_frag(cur, c, body); continue
            elif pieces: add_frag(pieces[-1], c, body); continue
            else: spk = MAIN[0]
        if not body: continue
        cur = {'n': c['n'], 's': c['s'], 'e': c['e'], 'spk': spk, 'inf': inf, 'frags': [[c['s'], c['e'], body]]}
        pieces.append(cur); last = spk

# 같은 화자가 바로 이어 말한 짧은 조각은 한 장으로 합친다 (앞 조각이 문장 끝이면 끊는다)
GAP, MAXLEN = 0.8, 110
text = lambda p: ' '.join(f[2] for f in p['frags'])
segs = []
for p in pieces:
    prev = segs[-1] if segs else None
    if (prev and prev['spk'] == p['spk'] and p['s'] - prev['e'] <= GAP
            and len(text(prev)) + len(text(p)) + 1 <= MAXLEN
            and not re.search(r'[.!?…"]\s*$', text(prev))):
        prev['frags'] += p['frags']; prev['e'] = p['e']
    else:
        segs.append(dict(p))

# 긴 대답은 문장 끝에서 나눈다. 시각은 그 문장이 시작/끝나는 줄(frag)의 큐 시각
SPLIT_AT = 120
END = re.compile(r'(?<=[.!?…"])\s+(?=[A-Z"\'])')
def split_long(g):
    full = text(g)
    if len(full) <= SPLIT_AT: return [g]
    sents = END.split(full)
    chunks, cur = [], ''
    for s in sents:
        if cur and len(cur) + 1 + len(s) > SPLIT_AT: chunks.append(cur); cur = s
        else: cur = (cur + ' ' + s).strip()
    if cur: chunks.append(cur)
    if len(chunks) == 1: return [g]
    # 각 chunk 의 문자 구간 → frag 위치로 시각 추정
    spans, pos = [], 0
    for f in g['frags']: spans.append((pos, pos + len(f[2]), f[0], f[1])); pos += len(f[2]) + 1
    def t_at(ch, tail=False):
        """문자 위치 → 시각. 줄(frag) 안에서는 글자 비율로 보간한다"""
        for a, b, s, e in spans:
            if a <= ch <= b:
                r = (ch - a) / max(b - a, 1)
                if tail: return round(e if r > 0.85 else s + (e - s) * min(1.0, r + 0.1), 2)
                return round(s if r < 0.15 else s + (e - s) * r, 2)
        return spans[-1][3] if tail else spans[0][2]
    out, at = [], 0
    for ch in chunks:
        a = full.index(ch, at); b = a + len(ch); at = b
        out.append({'n': g['n'], 's': t_at(a), 'e': t_at(b - 1, True), 'spk': g['spk'], 'inf': g['inf'],
                    'frags': [[t_at(a), t_at(b - 1, True), ch]], 'part': 1})
    for x, y in zip(out, out[1:]):                       # 앞 조각의 끝은 뒤 조각의 시작을 넘지 않게
        if y['s'] > x['s'] + 0.5: x['e'] = min(x['e'], y['s']); x['frags'][0][1] = x['e']
    return out
segs = [x for g in segs for x in split_long(g)]

def tidy(t):
    t = re.sub(r'\s+', ' ', t).strip()
    return re.sub(r'\s+([,.!?])', r'\1', t)
out = []
for i, g in enumerate(segs, 1):
    row = {'id': i, 's': round(g['s'], 2), 'e': round(g['e'], 2), 'en': tidy(text(g)), 'spk': g['spk'], 'cue': g['n']}
    if g['inf']: row['inf'] = 1
    if g.get('part'): row['part'] = 1        # 긴 대답을 나눈 조각
    out.append(row)
json.dump(out, open(os.path.join(HERE, 'segs.json'), 'w'), ensure_ascii=False, indent=1)
if __name__ == '__main__':
    print('큐:', len(cues), '| 효과음 제외:', n_sfx, '| 조각:', len(pieces), '→ 카드:', len(out), '(긴 대답 분할', sum(1 for o in out if o.get('part')), '장)')
    L = [len(o['en']) for o in out]
    print('길이(자): 평균 %.1f 중앙 %d 최대 %d | 화자 추정 %d' % (sum(L)/len(L), sorted(L)[len(L)//2], max(L), sum(1 for o in out if o.get('inf'))))
    from collections import Counter
    print('화자:', dict(Counter(o['spk'] for o in out)))
