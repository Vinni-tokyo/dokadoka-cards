import io, json, os, re, subprocess, sys
S = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, os.path.join(S, 'seg.py')], check=True, stdout=subprocess.DEVNULL)   # 분할을 먼저
OUT = os.path.join(os.path.dirname(S), 'Japanese-SnowMan105-Cards.html')
VID = 'H1w7GqBt2VI'

# 장면 = 영상 속 화면 자막(연도·행사)을 기준으로 나눈 타임라인
# (키, 시작초, 한국어, 일본어)
SCENES = [
 ('debut',    0,     '데뷔 (2019.8 ~ 2020.1)',            'デビュー (2019.8〜2020.1)'),
 ('pandemic', 43.8,  '팬데믹 · 데뷔 투어 중지 (2020)',      'パンデミック · デビューツアー中止 (2020)'),
 ('first',    134.3, '무관객 라이브 · 데뷔 후 첫 무대 (2020.10)', '無観客ライブ · デビュー後初のステージ (2020.10)'),
 ('mania',    190.1, 'LIVE TOUR 2021 Mania (2021.10)',      'LIVE TOUR 2021 Mania (2021.10)'),
 ('labo',     268.4, 'LIVE TOUR 2022 Labo. · 환호 복귀 (2022.11)', 'LIVE TOUR 2022 Labo. · 歓声が戻る (2022.11)'),
 ('dome',     329.1, '첫 돔 투어 i DO ME (2023.5)',         '1st DOME tour i DO ME (2023.5)'),
 ('nye',      394.1, '섣달그믐 생방송 라이브 (2023.12.31)',   '大晦日 生配信ライブ (2023.12.31)'),
 ('rays',     443.6, 'EMPIRE MV · Dome Tour 2024 RAYS',    'EMPIRE MV · Dome Tour 2024 RAYS'),
]

# 화자 = 자막의 'Name:' 표기. Cap 은 화면 자막(대사 아님), '' 은 화자 미상
SPEAKERS = [
 ('Iwamoto',  '岩本照',   '이와모토 히카루', 1),
 ('Fukazawa', '深澤辰哉', '후카자와 타츠야', 1),
 ('Raul',     'ラウール', '라울',           1),
 ('Watanabe', '渡辺翔太', '와타나베 쇼타',   1),
 ('Mukai',    '向井康二', '무카이 코지',     1),
 ('Abe',      '阿部亮平', '아베 료헤이',     1),
 ('Meguro',   '目黒蓮',   '메구로 렌',       1),
 ('Miyadate', '宮舘涼太', '미야다테 료타',   1),
 ('Sakuma',   '佐久間大介', '사쿠마 다이스케', 1),
 ('All',      '全員',     '전원',           0),
 ('Fans',     'ファン',   '팬',             0),
 ('Fan',      'ファン',   '팬',             0),
 ('Staff',    'スタッフ', '스태프',          0),
 ('',         '不明',     '화자 미상',        0),
 ('Cap',      '画面テロップ', '화면 자막',    0),
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

data = []
for s in segs:
    k, rd, note = ko[s['id']]
    row = {'id': s['id'], 's': s['s'], 'e': s['e'], 'ja': s['ja'], 'rd': rd, 'ko': k,
           'spk': s['spk'], 'scene': scene_of(s['s'])}
    if note: row['note'] = note
    data.append(row)

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
open(OUT, 'w', encoding='utf-8').write(html)

print('생성:', OUT)
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
