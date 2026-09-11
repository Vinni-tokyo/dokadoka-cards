#!/usr/bin/env python3
"""영어 노래 → 한국어 학습자용 노래 카드 앱 (english-cards 템플릿 + 노래 기능).
   src 에 두는 것
     lyrics.txt      가사 원문(줄 = 카드, 빈 줄 = 구간 경계)
     subtitles.srt   줄별 시각 (align.py 가 음성 인식 단어 시각에서 만든 것)
     ko.txt          `id|뜻|주석`
     study.txt       `E or V|영어|뜻|메모`
     beats.json      beats.py 출력 (BPM·박 그리드) — 마디 반복용"""
import io, json, os, re

S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(S)
VID = 'DXDGE_lRI0E'
NICK = 'Reasons'

# 구간(빈 줄로 나뉜 덩어리) 순서대로 라벨. (키, 한국어, 영어)
SECTIONS = [
 ('cho1',   '후렴 1',           'Chorus 1'),
 ('v1',     '1절 · 새 날',        'Verse 1 · A new day'),
 ('cho2',   '후렴 2',           'Chorus 2'),
 ('v2',     '2절 · 만 가지 이유',   'Verse 2 · Ten thousand reasons'),
 ('cho3',   '후렴 3',           'Chorus 3'),
 ('v3',     '3절 · 그날에',       'Verse 3 · On that day'),
 ('cho4',   '후렴 4',           'Chorus 4'),
 ('cho5',   '후렴 5',           'Chorus 5'),
 ('bridge', '브릿지 · Yes, Lord', 'Bridge · Yes, Lord'),
 ('outro',  '아웃트로 · 예수님',    'Outro · Jesus'),
]
SPEAKERS = [('Singer', 'Matt Redman', '매트 레드먼', 1), ('', 'Unknown', '화자 미상', 0)]

# 가사 줄과 구간
lines, sec_of = [], []
sec = 0; prev_blank = False
for ln in io.open(os.path.join(S, 'lyrics.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if ln.startswith('#'): continue
    if not ln.strip():
        if lines: prev_blank = True
        continue
    if prev_blank: sec += 1; prev_blank = False
    lines.append(ln.strip()); sec_of.append(sec)
assert sec + 1 == len(SECTIONS), f'구간 수 {sec+1} ≠ SECTIONS {len(SECTIONS)}'

# 시각
def read_srt(path):
    out = {}
    for b in re.split(r'\n\s*\n', io.open(path, encoding='utf-8-sig').read().strip()):
        L = [l for l in b.strip().split('\n') if l.strip()]
        if len(L) < 3: continue
        m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', L[1]); g = list(map(int, m.groups()))
        out[int(L[0])] = (round(g[0]*3600+g[1]*60+g[2]+g[3]/1000, 2), round(g[4]*3600+g[5]*60+g[6]+g[7]/1000, 2))
    return out
tim = read_srt(os.path.join(S, 'subtitles.srt'))
assert set(tim) == set(range(1, len(lines) + 1)), '자막 id 와 가사 줄 수가 다르다'

ko = {}
for ln in io.open(os.path.join(S, 'ko.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'): continue
    p = ln.split('|'); ko[int(p[0])] = (p[1].strip(), p[2].strip() if len(p) > 2 else '')
missing = [i for i in range(1, len(lines) + 1) if i not in ko]
assert not missing, f'번역 없음: {missing}'

data = []
for i, text in enumerate(lines, 1):
    s, e = tim[i]; k, note = ko[i]
    row = {'id': i, 's': s, 'e': e, 'en': text, 'ko': k, 'spk': 'Singer', 'scene': SECTIONS[sec_of[i - 1]][0]}
    if note: row['note'] = note
    data.append(row)
SCENES = []
for j, (key, k_, e_) in enumerate(SECTIONS):
    first = next(d for d in data if d['scene'] == key)
    SCENES.append({'key': key, 'ko': k_, 'en': e_, 'at': first['s']})

# --- 학습 항목 (english-cards 와 같은 규칙) ---
SUFFIX = r"(?:'?s|es|ed|d|ing|er|est|ly)?"
def phrase_of(term):
    t = re.sub(r'\([^)]*\)', ' ', term); t = re.sub(r'[,.!?"]', ' ', t)
    return max([p.strip(" ?.!,") for p in re.split(r'[~…]', t)], key=len).lower()
def pattern_of(phrase):
    return re.compile(r'\b' + r'\W+'.join(re.escape(w) + (SUFFIX if len(w) >= 3 else '') for w in phrase.split()) + r'\b', re.I)
def find_hits(term, cards):
    pat = pattern_of(phrase_of(term)); return [(c['id'], pat.search(c['en'])) for c in cards if pat.search(c['en'])]
def pick_example(hits, by_id):
    best, bs = None, None
    for i, m in hits:
        n = len(by_id[i]['en']); sc = 10 if 12 <= n <= 60 else (n - 12 if n < 12 else -(n - 60) * 0.3)
        if bs is None or sc > bs: best, bs = (i, m), sc
    return best
STUDY = []; by_id = {c['id']: c for c in data}
for ln in io.open(os.path.join(S, 'study.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'): continue
    p = [x.strip() for x in ln.split('|')]
    if len(p) < 3 or p[0] not in ('E', 'V') or not p[1] or not p[2]: continue
    row = {'t': p[0], 'en': p[1], 'ko': p[2]}
    if len(p) > 3 and p[3]: row['note'] = p[3]
    hits = find_hits(p[1], data); row['cids'] = [i for i, _ in hits]
    ex = pick_example(hits, by_id)
    if ex is not None: row['ex'], row['hit'] = ex[0], ex[1].group(0)
    else: row['hit'] = ''
    STUDY.append(row)
seen = set(); dup = [r['en'] for r in STUDY if (r['t'], r['en']) in seen or seen.add((r['t'], r['en']))]
assert not dup, f'중복: {dup}'

beats = {}
bp = os.path.join(S, 'beats.json')
if os.path.exists(bp):
    b = json.load(io.open(bp, encoding='utf-8')); beats = {'bpm': b['bpm'], 'phase': b['phase'], 'beats': b['beats']}

N = len(data); PACE = [-(-N // d) for d in (7, 5, 4, 3)]
YK = 0
OUT = os.path.join(ROOT, 'English-%s%d-Cards.html' % (NICK, N))
tpl = io.open(os.path.join(S, 'tpl.html'), encoding='utf-8').read()
html = (tpl
    .replace('/*__DATA__*/',     json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__SCENES__*/',   json.dumps(SCENES, ensure_ascii=False))
    .replace('/*__SPEAKERS__*/', json.dumps([{'key': k, 'en': e_, 'ko': k_, 'member': bool(m)} for k, e_, k_, m in SPEAKERS], ensure_ascii=False))
    .replace('/*__STUDY__*/',    json.dumps(STUDY, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__BEATS__*/',    json.dumps(beats, separators=(',', ':')))
    .replace('/*__VID__*/',      VID)
    .replace('__N__', str(N)).replace('__YK__', str(YK))
    .replace('__P1__', str(PACE[0])).replace('__P2__', str(PACE[1])).replace('__P3__', str(PACE[2])).replace('__P4__', str(PACE[3])))
io.open(OUT, 'w', encoding='utf-8').write(html)
print('생성:', OUT, '(%.1f KB)' % (os.path.getsize(OUT)/1024))
print('카드:', N, '| 주석:', sum(1 for d in data if 'note' in d), '| 박 그리드:', ('BPM %.1f · 박 %d · 위상 %d' % (beats['bpm'], len(beats['beats']), beats['phase'])) if beats else '없음', '| 페이스:', '/'.join(map(str, PACE)))
print('학습:', len(STUDY), '건 (표현', sum(1 for r in STUDY if r['t']=='E'), '/ 단어', sum(1 for r in STUDY if r['t']=='V'), ') · 연결', sum(1 for r in STUDY if r['cids']), '건 / 클립', sum(len(r['cids']) for r in STUDY))
print('  0개:', ', '.join(r['en'] for r in STUDY if not r['cids']) or '없음')
for s_ in SCENES: print('  %-7s %02d:%02d %-16s %2d줄' % (s_['key'], s_['at']//60, s_['at']%60, s_['ko'], sum(1 for d in data if d['scene'] == s_['key'])))
