import io, json, os, re, subprocess, sys, base64
S = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, os.path.join(S, 'seg.py')], check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, os.path.join(S, 'align_start.py')], check=True, stdout=subprocess.DEVNULL)
OUT = os.path.join(os.path.dirname(S), 'Japanese-Mika640-Cards.html')
VID = 'Joa5MSfh_Ho'

# 장면 = 화면 자막과 화제 전환을 기준으로 나눈 타임라인 (키, 시작초, 한국어, 일본어)
SCENES = [
 ('open',    0,     '오프닝 · 오늘의 게스트',        'オープニング · 今日のゲスト'),
 ('greet',   29,    '첫인사 · 가고시마 술 선물',      'ご挨拶 · 鹿児島のお酒'),
 ('meal',    62,    '닭곰탕 · 김치 맛보기',          'タッコムタン · キムチを味わう'),
 ('fame',    164,   '한국어와 「눈의 꽃」',           '韓国語と「雪の華」'),
 ('concert', 293,   '6월 한국 콘서트 · 무대 불안',    '６月の韓国コンサート · 舞台の不安'),
 ('rice',    424,   '흰쌀밥 사랑 · 하루 2홉',        '白米が好き · １日２合'),
 ('korea',   506,   '한국 음식과 맛집 이야기',        '韓国の食と店の話'),
 ('home',    645,   '고향 가고시마 · 온천',          '故郷の鹿児島 · 温泉'),
 ('debut',   782,   '18살 상경 · 데뷔 이야기',       '18歳で上京 · デビューの話'),
 ('stage',   852,   '긴장과 모니터 · 인이어',        '緊張とモニター · イヤモニ'),
 ('cover',   1080,  '한국 노래 커버 · 「I Believe」', '韓国の歌のカバー ·「I Believe」'),
 ('plan',    1296,  '공연 이야기 · 마무리',          '公演の話 · しめくくり'),
 ('bonus',   1499,  '보너스 · 선곡',                'おまけ · 選曲'),
]

# 화자
SPEAKERS = [
 ('S',  'ソン・シギョン', '성시경',        1),
 ('M',  '中島美嘉',      '나카시마 미카',  1),
 ('C',  '画面テロップ',   '화면 자막',      0),
 ('',   '不明',          '화자 미상',      0),
]

KANJI_RE = re.compile(r'[一-鿿々]')

ko = {}
for ln in open(os.path.join(S, 'ko.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'):
        continue
    p = ln.split('|')
    ko[int(p[0])] = (p[1].strip(), p[2].strip() if len(p) > 2 else '',
                     p[3].strip() if len(p) > 3 else '', p[4].strip() if len(p) > 4 else '')

segs = json.load(open(os.path.join(S, 'segs.json'), encoding='utf-8'))
# 재생 시작점 보정(음성 인식으로 찾은 실제 발화 시작). 자막 큐가 빈틈없이 붙어 있어
# 그대로 재생하면 앞 사람 말끝이 딸려 들어온다.
STARTS = json.load(open(os.path.join(S, 'starts.json'), encoding='utf-8'))
n_shift = 0
for s in segs:
    v = STARTS.get(str(s['id']))
    if v is not None and v > s['s']:
        s['s'] = v
        n_shift += 1
missing = [s['id'] for s in segs if s['id'] not in ko]
assert not missing, f'번역 없음: {missing}'
extra = sorted(set(ko) - {s['id'] for s in segs})
assert not extra, f'카드에 없는 id: {extra}'

KJ = {}
for ln in open(os.path.join(S, 'kanji.txt'), encoding='utf-8'):
    ln = ln.strip()
    if not ln or ln.startswith('#'):
        continue
    ch, hun = ln.split('|', 1)
    KJ[ch.strip()] = hun.strip()
WORDS = []
for ln in open(os.path.join(S, 'words.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'):
        continue
    p = [x.strip() for x in ln.split('|')]
    assert len(p) == 5, ln
    for stem in p[0].split(','):
        WORDS.append((stem.strip(), p[1], p[2], p[3], p[4]))
WORDS.sort(key=lambda w: -len(w[0]))
STEM_RE = re.compile('|'.join(re.escape(w[0]) for w in WORDS))
BY_STEM = {w[0]: w for w in WORDS}


def scene_of(t):
    key = SCENES[0][0]
    for k, at, _ko, _ja in SCENES:
        if t >= at:
            key = k
    return key


def kanji_notes(text):
    out, seen, covered = [], set(), set()
    for m in STEM_RE.finditer(text):
        stem, head, rd, mean, hj = BY_STEM[m.group()]
        covered.update(range(m.start(), m.end()))
        if head in seen:
            continue
        seen.add(head)
        chars = [[c, KJ[c]] for c in head if KANJI_RE.match(c)]
        out.append([head, rd, mean, hj, chars])
    left = [text[i] for i in range(len(text)) if KANJI_RE.match(text[i]) and i not in covered]
    return out, left


data, uncovered = [], []
for s in segs:
    k, rd, note, spk = ko[s['id']]
    row = {'id': s['id'], 's': s['s'], 'e': s['e'], 'ja': s['ja'], 'rd': rd, 'ko': k,
           'spk': spk, 'scene': scene_of(s['s'])}
    if note:
        row['note'] = note
    if s.get('cap'):
        row['th'] = 1          # 화면 자막은 대사와 구분해 표시
    kj, left = kanji_notes(s['ja'])
    if kj:
        row['kj'] = kj
    if left:
        uncovered.append((s['id'], ''.join(left)))
    data.append(row)
assert not uncovered, f'사전에 없는 한자: {uncovered}'
missing_kj = sorted({c for w in WORDS for c in w[1] if KANJI_RE.match(c) and c not in KJ})
assert not missing_kj, f'kanji.txt 에 없는 한자: {missing_kj}'

KANJI1 = re.compile(r'^[一-鿿]$')


def keys_of(term):
    t = term.split('〜')[0].strip() or term.replace('〜', '').strip()
    ks = []
    for n in range(len(t), max(len(t) - 3, 0), -1):
        k = t[:n]
        if len(k) >= 2 or KANJI1.match(k):
            ks.append(k)
    return ks


def find_hits(term, cards):
    for k in keys_of(term):
        ids = [c['id'] for c in cards if k in c['ja']]
        if ids:
            return ids, k
    return [], ''


def pick_example(ids, by_id):
    best, best_score = None, None
    for i in ids:
        c = by_id[i]
        n = len(c['ja'])
        sc = 10 if 6 <= n <= 26 else (n - 6 if n < 6 else -(n - 26) * 0.3)
        if best_score is None or sc > best_score:
            best, best_score = i, sc
    return best


STUDY = []
by_id = {c['id']: c for c in data}
for ln in io.open(os.path.join(S, 'study.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'):
        continue
    p = [x.strip() for x in ln.split('|')]
    if len(p) < 4 or p[0] not in ('E', 'V') or not p[1] or not p[3]:
        continue
    row = {'t': p[0], 'ja': p[1], 'rd': p[2], 'ko': p[3]}
    if len(p) > 4 and p[4]:
        row['note'] = p[4]
    row['cids'], row['hit'] = find_hits(p[1], data)
    ex = pick_example(row['cids'], by_id)
    if ex is not None:
        row['ex'] = ex
    STUDY.append(row)
seen = set()
dup = [r['ja'] for r in STUDY if (r['t'], r['ja']) in seen or seen.add((r['t'], r['ja']))]
assert not dup, f'중복: {dup}'

tpl = open(os.path.join(S, 'tpl.html'), encoding='utf-8').read()
tpl = tpl.replace(
    'ゆびさきと恋々 1화 · <span class="n">—</span>문장<br><span lang="ja">ゆびさきと恋々 第1話 · <span class="n">—</span>フレーズ',
    '성시경의 만날텐데 · 나카시마 미카 · <span class="n">—</span>문장<br><span lang="ja">ソン・シギョンの「会うだろうに」中島美嘉 · <span class="n">—</span>フレーズ')
tpl = tpl.replace('japanese-yubisaki-edits.json', 'japanese-mika-edits.json')
tpl = tpl.replace('<title>도카도카 일본어 공부 · ドカドカ日本語</title>',
                  '<title>도카도카 일본어 공부 · 성시경의 만날텐데 (나카시마 미카)</title>')
tpl = tpl.replace('속마음 〈〉 도 카드에 포함', '화면 자막도 카드에 포함')
tpl = tpl.replace('心の声もカードに含める', '画面テロップも含める')

html = (tpl
    .replace('/*__DATA__*/', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__SCENES__*/', json.dumps([{'key': k, 'ko': ko_, 'ja': ja_, 'at': at} for k, at, ko_, ja_ in SCENES], ensure_ascii=False))
    .replace('/*__SPEAKERS__*/', json.dumps([{'key': k, 'ja': ja_, 'ko': ko_, 'member': bool(m)} for k, ja_, ko_, m in SPEAKERS], ensure_ascii=False))
    .replace('/*__STUDY__*/', json.dumps(STUDY, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__VID__*/', VID))

_adir = os.path.join(S, 'audio')
_amap = {}
if os.path.exists(os.path.join(_adir, 'index.json')):
    for _k, _fn in json.load(open(os.path.join(_adir, 'index.json'), encoding='utf-8')).items():
        _fp = os.path.join(_adir, _fn)
        if os.path.exists(_fp):
            _amap[_k] = 'data:audio/mpeg;base64,' + base64.b64encode(open(_fp, 'rb').read()).decode()
html = html.replace('/*__AUDIO__*/', json.dumps(_amap, ensure_ascii=False))
open(OUT, 'w', encoding='utf-8').write(html)

print('생성:', OUT)
print('학습 음원:', len(_amap), '건')
print('한자 풀이:', sum(len(d.get('kj', [])) for d in data), '건 / 카드', sum(1 for d in data if 'kj' in d),
      '장 · 한자어', len({w[1] for w in WORDS}), '· 한자', len(KJ))
print('시작점 보정:', n_shift, '장')
print('카드:', len(data), '| 대사:', sum(1 for d in data if not d.get('th')),
      '| 화면 자막:', sum(1 for d in data if d.get('th')), '| 읽기 있음:', sum(1 for d in data if d['rd']))
print('학습:', len(STUDY), '건 (표현', sum(1 for r in STUDY if r['t'] == 'E'), '/ 단어', sum(1 for r in STUDY if r['t'] == 'V'), ')',
      '· 연결됨', sum(1 for r in STUDY if r['cids']), '건')
zero = [r['ja'] for r in STUDY if not r['cids']]
if zero:
    print('  0개:', ', '.join(zero))
print('크기: %.1f KB' % (os.path.getsize(OUT) / 1024))
for k, at, ko_, ja_ in SCENES:
    print('  %-8s %02d:%02d %-26s %3d장' % (k, at // 60, at % 60, ko_, sum(1 for d in data if d['scene'] == k)))
for k, ja_, ko_, m in SPEAKERS:
    n = sum(1 for d in data if d['spk'] == k)
    if n:
        print('  %-3s %-12s %3d장' % (k or '(없음)', ko_, n))
