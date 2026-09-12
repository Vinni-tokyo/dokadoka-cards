#!/usr/bin/env python3
"""TED 강연 → 한국어 학습자용 영어 카드 앱.

   TED 자막은 CC BY-NC-ND 4.0 으로 공개되어 있고, 영어·한국어 모두 TED 가 만든 공식 자막이다.
   그래서 번역을 새로 만들지 않고 TED 한국어 자막을 시각으로 맞춰 붙인다(뜻은 TED 의 것, 학습 메모만 직접 씀).

   src 에 두는 것
     subtitles.srt  TED 공식 영어 자막   (yt-dlp --sub-langs en)
     ko.srt         TED 공식 한국어 자막 (yt-dlp --sub-langs ko)
     study.txt      학습 표현·단어  `E or V|영어|뜻|메모`
     notes.txt      (선택) 카드별 문법 메모  `id|메모`
"""
import io, json, os, re, subprocess, sys

S = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, os.path.join(S, 'seg.py')], check=True, stdout=subprocess.DEVNULL)
ROOT = os.path.dirname(S)
VID  = '3lPnN8omdPA'
NICK = 'Thinking'
TITLE_KO = 'AI 가 사고력을 앗아가지 않게 하려면'
TITLE_EN = 'How to Stop AI from Killing Your Critical Thinking'
SPEAKER  = ('Sarkar', 'Advait Sarkar', '아드바이트 사카르', 1)

# 장면 = 강연의 논지 전환 (키, 시작초, 한국어, 영어)
SCENES = [
 ('open',   0,   '도입 · 계산기의 교훈',        'Opening: the lesson of the calculator'),
 ('auto',   150, '자동화가 앗아가는 것',        'What automation takes away'),
 ('meta',   330, '메타인지 · 생각하는 법을 잊다', 'Metacognition: forgetting how to think'),
 ('use',    520, 'AI 를 제대로 쓰는 법',        'Using AI well'),
 ('close',  760, '맺음 · 우리가 지킬 것',       'Closing: what to protect'),
]

def read_srt(path):
    out = []
    for b in re.split(r'\n\s*\n', io.open(path, encoding='utf-8-sig').read().strip()):
        L = [l.rstrip() for l in b.strip().split('\n') if l.strip()]
        if len(L) < 3: continue
        m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', L[1])
        if not m: continue
        g = list(map(int, m.groups()))
        t = re.sub(r'\s+', ' ', ' '.join(L[2:])).strip()
        t = re.sub(r'^\s*(번역|검토)\s*:\s*[^:]+?(?=(저는|이|우리|그|오늘|[A-Z가-힣]{2,}\s))', '', t)   # TED 번역자 크레딧 제거
        t = re.sub(r'^\s*(번역|검토)\s*:.*$', '', t).strip()
        if t: out.append({'s': g[0]*3600+g[1]*60+g[2]+g[3]/1000, 'e': g[4]*3600+g[5]*60+g[6]+g[7]/1000, 't': t})
    return out

segs = json.load(io.open(os.path.join(S, 'segs.json'), encoding='utf-8'))
kocues = read_srt(os.path.join(S, 'ko.srt'))

def ko_for(s, e):
    """카드 구간과 겹치는 한국어 자막 큐를 모아 붙인다(겹침이 큐 길이의 40% 이상일 때만)"""
    parts = []
    for c in kocues:
        ov = min(e, c['e']) - max(s, c['s'])
        if ov > 0 and ov >= 0.4 * min(c['e'] - c['s'], e - s):
            parts.append(c['t'])
    return ' '.join(parts).strip()

notes = {}
np_ = os.path.join(S, 'notes.txt')
if os.path.exists(np_):
    for ln in io.open(np_, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln.strip() or ln.lstrip().startswith('#'): continue
        p = ln.split('|', 1)
        if len(p) == 2: notes[int(p[0])] = p[1].strip()

def scene_of(sec):
    k = SCENES[0][0]
    for key, at, _a, _b in SCENES:
        if sec >= at: k = key
    return k

data, empty = [], []
for s_ in segs:
    ko = ko_for(s_['s'], s_['e'])
    if not ko: empty.append(s_['id'])
    row = {'id': s_['id'], 's': s_['s'], 'e': s_['e'], 'en': s_['en'], 'ko': ko,
           'spk': SPEAKER[0], 'scene': scene_of(s_['s'])}
    if s_['id'] in notes: row['note'] = notes[s_['id']]
    data.append(row)

# --- 학습 항목 (english-cards 와 같은 규칙) ---
SUFFIX = r"(?:'?s|es|ed|d|ing|er|est|ly)?"
def phrase_of(term):
    t = re.sub(r'\([^)]*\)', ' ', term); t = re.sub(r'[,.!?"]', ' ', t)
    return max([p.strip(" ?.!,") for p in re.split(r'[~…]', t)], key=len).lower()
def pattern_of(phrase):
    return re.compile(r'\b' + r'\W+'.join(re.escape(w) + (SUFFIX if len(w) >= 3 else '') for w in phrase.split()) + r'\b', re.I)
def find_hits(term, cards):
    pat = pattern_of(phrase_of(term))
    return [(c['id'], pat.search(c['en'])) for c in cards if pat.search(c['en'])]
def pick_example(hits, by_id):
    best, bs = None, None
    for i, m in hits:
        n = len(by_id[i]['en']); sc = 10 if 25 <= n <= 110 else (n - 25 if n < 25 else -(n - 110) * 0.3)
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

N = len(data); PACE = [-(-N // d) for d in (14, 10, 7, 5)]
OUT = os.path.join(ROOT, 'English-%s%d-Cards.html' % (NICK, N))
tpl = io.open(os.path.join(S, 'tpl.html'), encoding='utf-8').read()
html = (tpl
    .replace('/*__DATA__*/',     json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__SCENES__*/',   json.dumps([{'key': k, 'ko': a, 'en': b, 'at': at} for k, at, a, b in SCENES], ensure_ascii=False))
    .replace('/*__SPEAKERS__*/', json.dumps([{'key': SPEAKER[0], 'en': SPEAKER[1], 'ko': SPEAKER[2], 'member': True},
                                             {'key': '', 'en': 'Unknown', 'ko': '화자 미상', 'member': False}], ensure_ascii=False))
    .replace('/*__STUDY__*/',    json.dumps(STUDY, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__VID__*/',      VID)
    .replace('__N__', str(N)).replace('__YK__', '0')
    .replace('__P1__', str(PACE[0])).replace('__P2__', str(PACE[1])).replace('__P3__', str(PACE[2])).replace('__P4__', str(PACE[3])))
# 학습 음원(src/audio/*.mp3)이 있으면 심고, 없으면 빈 객체 → 앱이 브라우저 TTS 로 폴백
import base64
_adir = os.path.join(S, 'audio'); _amap = {}
if os.path.isdir(_adir):
    for _f in os.listdir(_adir):
        if _f.endswith('.mp3'):
            _amap[os.path.splitext(_f)[0]] = 'data:audio/mpeg;base64,' + base64.b64encode(open(os.path.join(_adir, _f), 'rb').read()).decode()
html = html.replace('/*__AUDIO__*/', json.dumps(_amap, ensure_ascii=False))

io.open(OUT, 'w', encoding='utf-8').write(html)

print('생성:', OUT, '(%.1f KB)' % (os.path.getsize(OUT)/1024))
print('카드:', N, '| 뜻 붙음:', N - len(empty), '| 뜻 없음:', len(empty), (empty[:12] if empty else ''))
print('학습:', len(STUDY), '건 (표현', sum(1 for r in STUDY if r['t']=='E'), '/ 단어', sum(1 for r in STUDY if r['t']=='V'), ')',
      '· 연결', sum(1 for r in STUDY if r['cids']), '건 / 클립', sum(len(r['cids']) for r in STUDY))
print('  0개:', ', '.join(r['en'] for r in STUDY if not r['cids']) or '없음')
for k, at, a, b in SCENES:
    print('  %-7s %02d:%02d %-26s %3d장' % (k, at//60, at%60, a, sum(1 for d in data if d['scene'] == k)))
