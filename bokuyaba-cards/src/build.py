import io, json, os, re, subprocess, sys
S = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, os.path.join(S, 'seg.py')], check=True, stdout=subprocess.DEVNULL)   # 분할을 먼저
OUT = os.path.join(os.path.dirname(S), 'Japanese-BokuYaba184-Cards.html')
VID = 'JjL9MmaIJhE'

# 장면 = 이야기의 흐름(장소·시간 전환)으로 나눈 타임라인
# (키, 시작초, 한국어, 일본어)
SCENES = [
 ('intro',  0,     '프롤로그 · 살의의 망상',      'プロローグ · 殺意の妄想'),
 ('lib1',   112,   '도서실 · 커터를 빌려주다',     '図書室 · カッターを貸す'),
 ('class',  402,   '연구 발표 · 눈물',           '研究発表 · 涙'),
 ('boys',   550,   '남학생들의 잡담',            '男子のバカ話'),
 ('lib2',   614,   '도서실 · 고백과 고양이',      '図書室 · 告白と猫'),
 ('shop',   818,   '서점 · 잡지',               '書店 · 雑誌'),
 ('next',   1022,  '다음 날 · LINE 소동',        '翌日 · LINE騒動'),
 ('bike',   1212,  '자전거 · 「面白いね」',       '自転車 · 「面白いね」'),
]

# 화자 = 자막의 （이름） 표기. '' 은 화자 미상
SPEAKERS = [
 ('市川',   '市川 京太郎', '이치카와 쿄타로', 1),
 ('山田',   '山田 杏奈',   '야마다 안나',    1),
 ('小林',   '小林 ちひろ', '코바야시 치히로', 1),
 ('モエ',   '吉田 萌子',   '요시다 모에코',  1),
 ('神崎',   '神崎',        '칸자키',        1),
 ('南条',   '南条',        '난조',          1),
 ('足立',   '足立',        '아다치',        1),
 ('先生',   '先生',        '선생님',        0),
 ('店員',   '店員',        '점원',          0),
 ('男子',   '男子',        '남학생',        0),
 ('女子',   '女子',        '여학생',        0),
 ('',       '不明',        '화자 미상',      0),
]

ko = {}
for ln in open(os.path.join(S, 'ko.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'): continue
    p = [x.strip() for x in ln.split('|')] + ['', '', '', '']
    ko[int(p[0])] = (p[1], p[2], p[3], p[4])          # 뜻, 읽기, 주석, 화자
fixes = {}
for ln in open(os.path.join(S, 'fixes.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'): continue
    i, txt = ln.split('|', 1); fixes[int(i)] = txt.strip()

segs = json.load(open(os.path.join(S, 'segs.json'), encoding='utf-8'))
missing = [s['id'] for s in segs if s['id'] not in ko]
assert not missing, f'번역 없음: {missing}'
extra = sorted(set(ko) - {s['id'] for s in segs})
assert not extra, f'카드에 없는 id: {extra}'
# 화자는 자막에 없으므로 ko.txt 의 5번째 칸에서 온다. '市川〈〉'=속마음, 'A·B'=한 카드에 둘 이상(첫 사람을 대표로)
def parse_spk(field):
    names = [x.strip() for x in field.split('·') if x.strip()]
    if not names: return '', 0, ''
    first = names[0]
    th = 1 if first.endswith('〈〉') else 0
    return first.rstrip('〈〉'), th, ' · '.join(n.rstrip('〈〉') + ('(속마음)' if n.endswith('〈〉') else '') for n in names) if len(names) > 1 else ''
known = {k for k, *_ in SPEAKERS}
bad = sorted({parse_spk(v[3])[0] for v in ko.values()} - known)
assert not bad, f'SPEAKERS 에 없는 화자: {bad}'
badfix = sorted(set(fixes) - set(ko))
assert not badfix, f'카드에 없는 fixes id: {badfix}'

def scene_of(start_sec):
    key = SCENES[0][0]
    for k, at, _ko, _ja in SCENES:
        if start_sec >= at: key = k
    return key

# --- 한자 풀이: 한자어 사전(words.txt) + 한자 훈음 사전(kanji.txt) ---------------
KJ = {}
for ln in open(os.path.join(S, 'kanji.txt'), encoding='utf-8'):
    ln = ln.strip()
    if not ln or ln.startswith('#'): continue
    ch, hun = ln.split('|', 1); KJ[ch.strip()] = hun.strip()
WORDS = []           # (어간, 표제, 독음, 뜻, 한자음)
for ln in open(os.path.join(S, 'words.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'): continue
    p = [x.strip() for x in ln.split('|')]
    assert len(p) == 5, ln
    for stem in p[0].split(','):
        WORDS.append((stem.strip(), p[1], p[2], p[3], p[4]))
WORDS.sort(key=lambda w: -len(w[0]))                       # 긴 어간부터
STEM_RE = re.compile('|'.join(re.escape(w[0]) for w in WORDS))
BY_STEM = {w[0]: w for w in WORDS}
KANJI_RE = re.compile(r'[一-鿿々]')

def kanji_notes(text):
    """본문에서 한자어를 찾아 [표제, 독음, 뜻, 한자음, [[漢字, 훈음], ...]] 목록을 만든다. 같은 표제는 한 번만"""
    out, seen, covered = [], set(), set()
    for m in STEM_RE.finditer(text):
        stem, head, rd, mean, hj = BY_STEM[m.group()]
        covered.update(range(m.start(), m.end()))
        if head in seen: continue
        seen.add(head)
        chars = [[c, KJ[c]] for c in head if KANJI_RE.match(c)]
        out.append([head, rd, mean, hj, chars])
    left = [text[i] for i in range(len(text)) if KANJI_RE.match(text[i]) and i not in covered]
    return out, left

data, uncovered = [], []
for s in segs:
    k, rd, note, who = ko[s['id']]
    spk, th, multi = parse_spk(who)
    ja = fixes.get(s['id'], s['ja'])
    row = {'id': s['id'], 's': s['s'], 'e': s['e'], 'ja': ja, 'rd': rd, 'ko': k,
           'spk': spk, 'scene': scene_of(s['s'])}
    if ja != s['ja']: row['raw'] = s['ja']   # 자막 원문(교정 전)
    if th: row['th'] = 1                     # 〈속마음〉
    if multi: note = ('화자: ' + multi) + (' · ' + note if note else '')
    if note: row['note'] = note
    s['ja'] = ja                             # 학습 항목 매칭도 교정문 기준
    kj, left = kanji_notes(s['ja'])
    if kj: row['kj'] = kj
    if left: uncovered.append((s['id'], ''.join(left)))
    data.append(row)
assert not uncovered, f'사전에 없는 한자: {uncovered}'
missing_kj = sorted({c for w in WORDS for c in w[1] if KANJI_RE.match(c) and c not in KJ})
assert not missing_kj, f'kanji.txt 에 없는 한자: {missing_kj}'

# --- 학습 탭: 표현·단어가 나오는 카드를 찾는다 ---------------------------------
KANJI = re.compile(r'^[一-鿿]$')
def keys_of(term):
    """자막에서 찾을 문자열 후보. '〜' 앞부분만 쓰고, 활용형에 맞도록 끝에서 최대 3자까지 떼어 가며 시도한다.
       한 글자는 오탐이 많아 한자일 때만 허용한다."""
    t = term.split('〜')[0].strip() or term.replace('〜', '').strip()
    ks = []
    for n in range(len(t), max(len(t) - 3, 0), -1):
        k = t[:n]
        if len(k) >= 2 or KANJI.match(k): ks.append(k)
    return ks

def find_hits(term, cards):
    for k in keys_of(term):
        ids = [c['id'] for c in cards if k in c['ja']]
        if ids: return ids, k
    return [], ''

def pick_example(ids, by_id):
    """예문에 맞는 카드: 너무 짧거나 길지 않은 것"""
    best, best_score = None, None
    for i in ids:
        c = by_id[i]; n = len(c['ja'])
        sc = 10 if 6 <= n <= 26 else (n - 6 if n < 6 else -(n - 26) * 0.3)
        if best_score is None or sc > best_score: best, best_score = i, sc
    return best

STUDY = []
by_id = {c['id']: c for c in data}
for ln in io.open(os.path.join(S, 'study.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'): continue
    p = [x.strip() for x in ln.split('|')]
    if len(p) < 4 or p[0] not in ('E', 'V') or not p[1] or not p[3]: continue
    row = {'t': p[0], 'ja': p[1], 'rd': p[2], 'ko': p[3]}
    if len(p) > 4 and p[4]: row['note'] = p[4]
    row['cids'], row['hit'] = find_hits(p[1], data)
    ex = pick_example(row['cids'], by_id)
    if ex is not None: row['ex'] = ex
    STUDY.append(row)

seen = set(); dup = [r['ja'] for r in STUDY if (r['t'], r['ja']) in seen or seen.add((r['t'], r['ja']))]
assert not dup, f'중복: {dup}'

tpl = open(os.path.join(S, 'tpl.html'), encoding='utf-8').read()
html = (tpl
    .replace('/*__DATA__*/',     json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__SCENES__*/',   json.dumps([{'key': k, 'ko': ko_, 'ja': ja_, 'at': at} for k, at, ko_, ja_ in SCENES], ensure_ascii=False))
    .replace('/*__SPEAKERS__*/', json.dumps([{'key': k, 'ja': ja_, 'ko': ko_, 'member': bool(m)} for k, ja_, ko_, m in SPEAKERS], ensure_ascii=False))
    .replace('/*__STUDY__*/',    json.dumps(STUDY, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__VID__*/',      VID))
open(OUT, 'w', encoding='utf-8').write(html)

print('생성:', OUT)
print('한자 풀이:', sum(len(d.get('kj', [])) for d in data), '건 / 카드', sum(1 for d in data if 'kj' in d), '장 · 한자어', len({w[1] for w in WORDS}), '· 한자', len(KJ))
print('교정:', sum(1 for d in data if 'raw' in d), '장')
print('카드:', len(data), '| 대사:', sum(1 for d in data if not d.get('th')), '| 속마음:', sum(1 for d in data if d.get('th')),
      '| 주석 있음:', sum(1 for d in data if 'note' in d), '| 읽기 있음:', sum(1 for d in data if d['rd']))
print('학습:', len(STUDY), '건 (표현', sum(1 for r in STUDY if r['t']=='E'), '/ 단어', sum(1 for r in STUDY if r['t']=='V'), ')',
      '· 연결됨', sum(1 for r in STUDY if r['cids']), '건 / 클립', sum(len(r['cids']) for r in STUDY), '개')
print('  0개:', ', '.join(r['ja'] for r in STUDY if not r['cids']) or '없음')
print('크기: %.1f KB' % (os.path.getsize(OUT)/1024))
for k, at, ko_, ja_ in SCENES:
    print('  %-7s %02d:%02d %-24s %3d장' % (k, at//60, at%60, ko_, sum(1 for d in data if d['scene'] == k)))
for k, ja_, ko_, m in SPEAKERS:
    n = sum(1 for d in data if d['spk'] == k)
    if n: print('  %-8s %-12s %3d장' % (k or '(없음)', ko_, n))
