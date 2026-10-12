import io, json, os, re, subprocess, sys
S = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, os.path.join(S, 'seg.py')], check=True, stdout=subprocess.DEVNULL)   # 분할을 먼저
OUT = os.path.join(os.path.dirname(S), 'Japanese-Haenali48-Cards.html')
VID = 'qRzf-bi_FSI'

# 장면 = 영상 설명란의 공식 타임라인(TIMELINE). 일본어 카드가 있는 장면만 둔다
# (키, 시작초, 한국어, 일본어)
SCENES = [
 ('self',   66,   '일본어 자기소개 (01:06)',        '日本語で自己紹介'),
 ('sound',  381,  '일본어 발음 (06:21)',            '日本語の発音'),
 ('anime',  607,  '애니로 청해 공부하는 법 (10:07)', 'アニメで聴解を勉強する方法'),
 ('talk',   800,  '실전회화 (13:20)',               '実践会話'),
 ('qa',     921,  'Q&A (15:21)',                   'Q&A'),
 ('end',    1117, '마무리 (18:37)',                 'まとめ'),
]

# 화자. 영상은 해날이 혼자 말하고, 10:59~11:31 에 애니 「あたしンち」 장면을 틀어 들려준다
SPEAKERS = [
 ('Hae',   'ヘナリ',            '해날이',              1),
 ('Anime', 'アニメ「あたしンち」', '애니 「あたしンち」', 1),
 ('',      '不明',              '화자 미상',            0),
 ('Cap',   '画面テロップ',       '화면 자막',            0),
]

ko = {}
for ln in open(os.path.join(S, 'ko.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'): continue
    p = ln.split('|')
    ko[int(p[0])] = (p[1].strip(), p[2].strip() if len(p) > 2 else '', p[3].strip() if len(p) > 3 else '')

segs = json.load(open(os.path.join(S, 'segs.json'), encoding='utf-8'))
missing = [s['id'] for s in segs if s['id'] not in ko]
assert not missing, f'번역 없음: {missing}'
extra = sorted(set(ko) - {s['id'] for s in segs})
assert not extra, f'카드에 없는 id: {extra}'

def scene_of(start_sec):
    key = SCENES[0][0]
    for k, at, _ko, _ja in SCENES:
        if start_sec >= at: key = k
    return key

# --- 한자 풀이 사전 (yubisaki-cards 와 같은 규칙) ---------------------------------
KJ = {}
for _ln in io.open(os.path.join(S, 'kanji.txt'), encoding='utf-8'):
    _ln = _ln.strip()
    if not _ln or _ln.startswith('#'): continue
    _ch, _hun = _ln.split('|', 1); KJ[_ch.strip()] = _hun.strip()
WORDS = []
for _ln in io.open(os.path.join(S, 'words.txt'), encoding='utf-8'):
    _ln = _ln.rstrip('\n')
    if not _ln.strip() or _ln.lstrip().startswith('#'): continue
    _p = [x.strip() for x in _ln.split('|')]
    assert len(_p) == 5, _ln
    for _stem in _p[0].split(','): WORDS.append((_stem.strip(), _p[1], _p[2], _p[3], _p[4]))
WORDS.sort(key=lambda w: -len(w[0]))
STEM_RE = re.compile('|'.join(re.escape(w[0]) for w in WORDS)) if WORDS else None
BY_STEM = {w[0]: w for w in WORDS}
KANJI_RE = re.compile(r'[一-鿿々]')
def kanji_notes(text):
    out, seen, covered = [], set(), set()
    if STEM_RE:
        for m in STEM_RE.finditer(text):
            stem, head, rd, mean, hj = BY_STEM[m.group()]
            covered.update(range(m.start(), m.end()))
            if head in seen: continue
            seen.add(head); out.append([head, rd, mean, hj, [[c, KJ[c]] for c in head if KANJI_RE.match(c)]])
    left = [text[i] for i in range(len(text)) if KANJI_RE.match(text[i]) and i not in covered]
    return out, left


data, uncovered = [], []
for s in segs:
    k, rd, note = ko[s['id']]
    row = {'id': s['id'], 's': s['s'], 'e': s['e'], 'ja': s['ja'], 'rd': rd, 'ko': k,
           'spk': s['spk'], 'scene': scene_of(s['s'])}
    if note: row['note'] = note
    _kj, _left = kanji_notes(s['ja'])
    if _kj: row['kj'] = _kj
    if _left: uncovered.append((s['id'], ''.join(_left)))
    data.append(row)

assert not uncovered, f'사전에 없는 한자: {uncovered}'
_missing_kj = sorted({c for w in WORDS for c in w[1] if KANJI_RE.match(c) and c not in KJ})
assert not _missing_kj, f'kanji.txt 에 없는 한자: {_missing_kj}'

# --- 학습 탭: 표현·단어가 나오는 카드를 찾는다 ---------------------------------
KANJI = re.compile(r'^[\u4e00-\u9fff]$')
def keys_of(term):
    """자막에서 찾을 문자열 후보. '〜' 앞부분만 쓰고(1ミリも〜ない → 1ミリも),
       활용형에 맞도록 끝에서 최대 3자까지 떼어 가며 시도한다(巡ってくる → 巡って).
       한 글자는 오탐이 많아 한자일 때만 허용한다(姿)."""
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
    """예문에 맞는 카드: 너무 짧거나 길지 않고, 화면 자막보다 대사를 우선"""
    best, best_score = None, None
    for i in ids:
        c = by_id[i]; n = len(c['ja'])
        sc = 10 if 8 <= n <= 34 else (n - 8 if n < 8 else -(n - 34) * 0.3)
        if c['spk'] == 'Cap': sc -= 4
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
    row['cids'], row['hit'] = find_hits(p[1], data)    # hit = 실제로 자막에서 맞은 문자열(강조용)
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
# 학습 음원(src/audio/*.mp3, tools/make_study_audio.py 가 생성)을 data URI 로 심는다. 없으면 빈 객체 → 앱은 브라우저 TTS 로 폴백
_adir = os.path.join(S, 'audio'); _amap = {}
if os.path.exists(os.path.join(_adir, 'index.json')):
    import base64
    for _k, _fn in json.load(open(os.path.join(_adir, 'index.json'), encoding='utf-8')).items():
        _fp = os.path.join(_adir, _fn)
        if os.path.exists(_fp): _amap[_k] = 'data:audio/mpeg;base64,' + base64.b64encode(open(_fp, 'rb').read()).decode()
html = html.replace('/*__AUDIO__*/', json.dumps(_amap, ensure_ascii=False))
print('학습 음원:', len(_amap), '건 심음')
open(OUT, 'w', encoding='utf-8').write(html)

print('생성:', OUT)
print('한자 풀이:', sum(len(d.get('kj', [])) for d in data), '건')
print('카드:', len(data), '| 대사:', sum(1 for d in data if d['spk'] != 'Cap'), '| 화면 자막:', sum(1 for d in data if d['spk'] == 'Cap'),
      '| 주석 있음:', sum(1 for d in data if 'note' in d), '| 읽기 있음:', sum(1 for d in data if d['rd']))
print('학습:', len(STUDY), '건 (표현', sum(1 for r in STUDY if r['t']=='E'), '/ 단어', sum(1 for r in STUDY if r['t']=='V'), ')',
      '· 연결됨', sum(1 for r in STUDY if r['cids']), '건 / 클립', sum(len(r['cids']) for r in STUDY), '개')
print('  0개:', ', '.join(r['ja'] for r in STUDY if not r['cids']) or '없음')
print('크기: %.1f KB' % (os.path.getsize(OUT)/1024))
for k, at, ko_, ja_ in SCENES:
    print('  %-9s %02d:%02d %-42s %3d장' % (k, at//60, at%60, ko_, sum(1 for d in data if d['scene'] == k)))
for k, ja_, ko_, m in SPEAKERS:
    n = sum(1 for d in data if d['spk'] == k)
    if n: print('  %-9s %-14s %3d장' % (k or '(없음)', ko_, n))
