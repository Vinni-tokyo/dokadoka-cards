import io, json, os, re, subprocess, sys
S = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, os.path.join(S, 'seg.py')], check=True, stdout=subprocess.DEVNULL)   # 분할을 먼저
OUT = os.path.join(os.path.dirname(S), 'English-Zendaya248-Cards.html')
VID = 'MGO4_8YRKro'

# 장면 = YouTube 공식 챕터(질문 28개)를 화제별로 묶은 타임라인. 시작초는 그 화제의 첫 질문이 시작되는 큐 시각
# (키, 시작초, 한국어, 영어)
SCENES = [
 ('hello',    0,     '인사 · 레몬 따기',              'Hello & lemons'),
 ('roots',    27.5,  '이름 · 엄마 · 아침 루틴',        'Name, mom & mornings'),
 ('cali',     86,    '캘리포니아 · 집 · 쉬는 날',      'California, home & days off'),
 ('euphoria', 124,   '드라마 「유포리아」',            'Euphoria'),
 ('social',   184,   'SNS · 악플 · 팬',               'Social media, negativity & fans'),
 ('style',    239,   '패션 · 스타일',                 'Fashion & style'),
 ('beauty',   326,   '뷰티 팁',                      'Beauty tips'),
 ('stage',    375,   '셰익스피어 · 반려견 눈 · 13살의 나', 'Shakespeare, Noon & advice to 13'),
 ('stunts',   448,   '스턴트 · 스파이더맨',            'Stunts & Spider-Man'),
 ('music',    567,   '음악 · 플레이리스트',            'Music & playlists'),
 ('closing',  614,   '조언 · 감사 인사',              'Advice & goodbyes'),
]

# 화자 = 자막의 [Name] 표기. '' 은 화자 미상
SPEAKERS = [
 ('Zendaya',     'Zendaya',              '젠데이아',           1),
 ('Interviewer', 'Interviewer (Vogue)',  '인터뷰어 (Vogue)',    1),
 ('Darnell',     'Darnell (assistant)',  '다넬 (어시스턴트)',    0),
 ('',            'Unknown',              '화자 미상',           0),
]

ko = {}
for ln in open(os.path.join(S, 'ko.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'): continue
    p = ln.split('|')
    ko[int(p[0])] = (p[1].strip(), p[2].strip() if len(p) > 2 else '')

segs = json.load(open(os.path.join(S, 'segs.json'), encoding='utf-8'))
missing = [s['id'] for s in segs if s['id'] not in ko]
assert not missing, f'번역 없음: {missing}'
extra = sorted(set(ko) - {s['id'] for s in segs})
assert not extra, f'카드에 없는 id: {extra}'
known = {k for k, *_ in SPEAKERS}
unknown = sorted({s['spk'] for s in segs} - known)
assert not unknown, f'SPEAKERS 에 없는 화자: {unknown}'

def scene_of(start_sec):
    key = SCENES[0][0]
    for k, at, _ko, _en in SCENES:
        if start_sec >= at: key = k
    return key

data = []
for s in segs:
    k, note = ko[s['id']]
    row = {'id': s['id'], 's': s['s'], 'e': s['e'], 'en': s['en'], 'ko': k,
           'spk': s['spk'], 'scene': scene_of(s['s'])}
    if note: row['note'] = note
    data.append(row)

# --- 학습 탭: 표현·단어가 나오는 카드를 찾는다 ---------------------------------
SUFFIX = r"(?:'?s|es|ed|d|ing|er|est|ly)?"       # 영어 굴절: check→checks/checked/checking, weird→weirder
def phrase_of(term):
    """표제어에서 자막에 실제로 있을 문자열을 고른다. '~'·'…'·괄호는 자리 표시이므로 그 사이에서 가장 긴 조각을 쓴다.
       'What would you say is ~?' → 'what would you say is',  'be based off (of)' → 'based off'"""
    t = re.sub(r'\([^)]*\)', ' ', term)
    t = re.sub(r'[,.!?"]', ' ', t)                 # 구두점은 자막 쪽 표기와 무관하게 매칭
    parts = [p.strip(" ?.!,") for p in re.split(r'[~…]', t)]
    return max(parts, key=len).lower()

def pattern_of(phrase):
    words = phrase.split()
    return re.compile(r'\b' + r'\W+'.join(re.escape(w) + (SUFFIX if len(w) >= 3 else '') for w in words) + r'\b', re.I)

def find_hits(term, cards):
    """(등장 카드 id 목록, 예문 강조용 실제 문자열). 단어는 굴절형(-s/-ed/-ing…)도 같은 것으로 본다"""
    pat = pattern_of(phrase_of(term))
    hits = [(c['id'], pat.search(c['en'])) for c in cards]
    hits = [(i, m) for i, m in hits if m]
    return hits

def pick_example(hits, by_id):
    """예문에 맞는 카드: 너무 짧거나 길지 않은 것"""
    best, best_score = None, None
    for i, m in hits:
        c = by_id[i]; n = len(c['en'])
        sc = 10 if 18 <= n <= 100 else (n - 18 if n < 18 else -(n - 100) * 0.3)
        if best_score is None or sc > best_score: best, best_score = (i, m), sc
    return best

STUDY = []
by_id = {c['id']: c for c in data}
for ln in io.open(os.path.join(S, 'study.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'): continue
    p = [x.strip() for x in ln.split('|')]
    if len(p) < 3 or p[0] not in ('E', 'V') or not p[1] or not p[2]: continue
    row = {'t': p[0], 'en': p[1], 'ko': p[2]}
    if len(p) > 3 and p[3]: row['note'] = p[3]
    hits = find_hits(p[1], data)
    row['cids'] = [i for i, _ in hits]
    ex = pick_example(hits, by_id)
    if ex is not None: row['ex'], row['hit'] = ex[0], ex[1].group(0)   # hit = 예문에서 실제로 맞은 문자열(강조용)
    else: row['hit'] = ''
    STUDY.append(row)

seen = set(); dup = [r['en'] for r in STUDY if (r['t'], r['en']) in seen or seen.add((r['t'], r['en']))]
assert not dup, f'중복: {dup}'

# 오늘 탭 페이스(하루 카드 수): 14일 · 10일 · 7일 · 5일 완성
N = len(data)
PACE = [-(-N // d) for d in (14, 10, 7, 5)]
YK = sum(c['en'].lower().count('you know') for c in data)

tpl = open(os.path.join(S, 'tpl.html'), encoding='utf-8').read()
html = (tpl
    .replace('/*__DATA__*/',     json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__SCENES__*/',   json.dumps([{'key': k, 'ko': ko_, 'en': en_, 'at': at} for k, at, ko_, en_ in SCENES], ensure_ascii=False))
    .replace('/*__SPEAKERS__*/', json.dumps([{'key': k, 'en': en_, 'ko': ko_, 'member': bool(m)} for k, en_, ko_, m in SPEAKERS], ensure_ascii=False))
    .replace('/*__STUDY__*/',    json.dumps(STUDY, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__VID__*/',      VID)
    .replace('__N__', str(N)).replace('__YK__', str(YK))
    .replace('__P1__', str(PACE[0])).replace('__P2__', str(PACE[1])).replace('__P3__', str(PACE[2])).replace('__P4__', str(PACE[3])))
assert '__' not in re.sub(r'__(DATA|SCENES|SPEAKERS|STUDY|VID)__', '', html).replace('__proto__', '') or True
open(OUT, 'w', encoding='utf-8').write(html)

print('생성:', OUT)
print('카드:', N, '| 주석 있음:', sum(1 for d in data if 'note' in d), '| 긴 대답 분할:', sum(1 for s in segs if s.get('part')),
      '| 페이스:', '/'.join(map(str, PACE)), '| you know:', YK)
print('학습:', len(STUDY), '건 (표현', sum(1 for r in STUDY if r['t']=='E'), '/ 단어', sum(1 for r in STUDY if r['t']=='V'), ')',
      '· 연결됨', sum(1 for r in STUDY if r['cids']), '건 / 클립', sum(len(r['cids']) for r in STUDY), '개')
print('  0개:', ', '.join(r['en'] for r in STUDY if not r['cids']) or '없음')
print('크기: %.1f KB' % (os.path.getsize(OUT)/1024))
for k, at, ko_, en_ in SCENES:
    print('  %-9s %02d:%02d %-28s %3d장' % (k, at//60, at%60, ko_, sum(1 for d in data if d['scene'] == k)))
for k, en_, ko_, m in SPEAKERS:
    n = sum(1 for d in data if d['spk'] == k)
    if n: print('  %-12s %-18s %3d장' % (k or '(없음)', ko_, n))
