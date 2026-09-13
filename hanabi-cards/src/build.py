#!/usr/bin/env python3
"""일본어 노래 → 한국어 학습자용 노래 카드 앱 (yubisaki-cards 템플릿 + 노래방·마디 반복).
   src 에 두는 것
     lyrics.txt      가사 원문(줄 = 카드, 빈 줄 = 구간 경계)
     subtitles.srt   줄별 시각 (align.py 가 음성 인식 단어 시각에서 만든 것)
     ko.txt          `id|뜻|읽기|주석`
     study.txt       `E or V|일본어|읽기|뜻|메모`
     words.txt / kanji.txt   한자 풀이 사전
     beats.json      beats.py 출력 (BPM·박 그리드) — 마디 반복용
     audio/          tools/make_study_audio.py 가 만든 학습 음원"""
import io, json, os, re
S = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(S), 'Japanese-Hanabi44-Cards.html')
VID = '-tKVN2mAKRI'

# 구간(빈 줄로 나뉜 덩어리) 순서대로. (키, 한국어, 일본어)
SECTIONS = [
 ('v1',     '1절 · 그날의 물가',          '1番 · あの日の渚'),
 ('cho1',   '후렴 1 · 불꽃을 보고 있었어', 'サビ 1 · 花火を見ていた'),
 ('v2',     '2절 · 앞으로 몇 번',          '2番 · あと何度'),
 ('bridge', '브릿지 · 사라질 것 같은 빛',  'Cメロ · 消えちゃいそうな光'),
 ('cho2',   '후렴 2 · 밤에 피었어',        'サビ 2 · 夜に咲いた'),
 ('cho3',   '마지막 · 그날의 물가',        'ラスト · あの日の渚'),
]
SPEAKERS = [('Singer', 'DAOKO × 米津玄師', 'DAOKO × 요네즈 켄시', 1), ('', '不明', '화자 미상', 0)]

lines, sec_of, sec, prev_blank = [], [], 0, False
for ln in io.open(os.path.join(S, 'lyrics.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if ln.startswith('#'): continue
    if not ln.strip():
        if lines: prev_blank = True
        continue
    if prev_blank: sec += 1; prev_blank = False
    lines.append(ln.strip()); sec_of.append(sec)
assert sec + 1 == len(SECTIONS), f'구간 수 {sec+1} ≠ SECTIONS {len(SECTIONS)}'

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
    p = [x.strip() for x in ln.split('|')] + ['', '', '']
    ko[int(p[0])] = (p[1], p[2], p[3])
missing = [i for i in range(1, len(lines) + 1) if i not in ko]
assert not missing, f'번역 없음: {missing}'

# --- 한자 풀이 사전 (yubisaki-cards 와 같은 규칙) ---------------------------------
KJ = {}
for ln in io.open(os.path.join(S, 'kanji.txt'), encoding='utf-8'):
    ln = ln.strip()
    if not ln or ln.startswith('#'): continue
    ch, hun = ln.split('|', 1); KJ[ch.strip()] = hun.strip()
WORDS = []
for ln in io.open(os.path.join(S, 'words.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'): continue
    p = [x.strip() for x in ln.split('|')]
    assert len(p) == 5, ln
    for stem in p[0].split(','): WORDS.append((stem.strip(), p[1], p[2], p[3], p[4]))
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
for i, text in enumerate(lines, 1):
    s, e = tim[i]; k, rd, note = ko[i]
    row = {'id': i, 's': s, 'e': e, 'ja': text, 'rd': rd, 'ko': k, 'spk': 'Singer', 'scene': SECTIONS[sec_of[i - 1]][0]}
    if note: row['note'] = note
    kj, left = kanji_notes(text)
    if kj: row['kj'] = kj
    if left: uncovered.append((i, ''.join(left)))
    data.append(row)
assert not uncovered, f'사전에 없는 한자: {uncovered}'
missing_kj = sorted({c for w in WORDS for c in w[1] if KANJI_RE.match(c) and c not in KJ})
assert not missing_kj, f'kanji.txt 에 없는 한자: {missing_kj}'
SCENES = []
for key, k_, j_ in SECTIONS:
    first = next(d for d in data if d['scene'] == key)
    SCENES.append({'key': key, 'ko': k_, 'ja': j_, 'at': first['s']})

# --- 학습 항목 (yubisaki-cards 와 같은 규칙 + 영어 구절은 대소문자 무시) ---
KANJI1 = re.compile(r'^[一-鿿]$')
def keys_of(term):
    t = term.split('〜')[0].strip() or term.replace('〜', '').strip()
    t = re.sub(r'\(.*?\)', '', t).strip()
    ks = []
    for n in range(len(t), max(len(t) - 3, 0), -1):
        k = t[:n]
        if len(k) >= 2 or KANJI1.match(k): ks.append(k)
    return ks
def find_hits(term, cards):
    for k in keys_of(term):
        ids = [c['id'] for c in cards if k.lower() in c['ja'].lower()]
        if ids: return ids, k
    return [], ''
def pick_example(ids, by_id):
    best, bs = None, None
    for i in ids:
        n = len(by_id[i]['ja']); sc = 10 if 6 <= n <= 30 else (n - 6 if n < 6 else -(n - 30) * 0.3)
        if bs is None or sc > bs: best, bs = i, sc
    return best
STUDY = []; by_id = {c['id']: c for c in data}
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

beats = {}
bp = os.path.join(S, 'beats.json')
if os.path.exists(bp):
    b = json.load(io.open(bp, encoding='utf-8')); beats = {'bpm': b['bpm'], 'phase': b['phase'], 'beats': b['beats']}

tpl = io.open(os.path.join(S, 'tpl.html'), encoding='utf-8').read()
html = (tpl
    .replace('/*__DATA__*/',     json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__SCENES__*/',   json.dumps(SCENES, ensure_ascii=False))
    .replace('/*__SPEAKERS__*/', json.dumps([{'key': k, 'ja': j_, 'ko': k_, 'member': bool(m)} for k, j_, k_, m in SPEAKERS], ensure_ascii=False))
    .replace('/*__STUDY__*/',    json.dumps(STUDY, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__BEATS__*/',    json.dumps(beats, separators=(',', ':')))
    .replace('/*__VID__*/',      VID))
# 학습 음원(src/audio) 을 data URI 로 심는다
_adir = os.path.join(S, 'audio'); _amap = {}
if os.path.exists(os.path.join(_adir, 'index.json')):
    import base64
    for _k, _fn in json.load(io.open(os.path.join(_adir, 'index.json'), encoding='utf-8')).items():
        _fp = os.path.join(_adir, _fn)
        if os.path.exists(_fp): _amap[_k] = 'data:audio/mpeg;base64,' + base64.b64encode(open(_fp, 'rb').read()).decode()
html = html.replace('/*__AUDIO__*/', json.dumps(_amap, ensure_ascii=False))
io.open(OUT, 'w', encoding='utf-8').write(html)

N = len(data)
print('생성:', OUT, '(%.1f KB)' % (os.path.getsize(OUT)/1024))
print('카드:', N, '| 읽기 있음:', sum(1 for d in data if d['rd']), '| 주석:', sum(1 for d in data if 'note' in d), '| 한자 풀이:', sum(len(d.get('kj', [])) for d in data), '건',
      '| 박 그리드:', ('BPM %.1f · 박 %d · 위상 %d' % (beats['bpm'], len(beats['beats']), beats['phase'])) if beats else '없음', '| 학습 음원:', len(_amap))
print('학습:', len(STUDY), '건 (표현', sum(1 for r in STUDY if r['t']=='E'), '/ 단어', sum(1 for r in STUDY if r['t']=='V'), ') · 연결', sum(1 for r in STUDY if r['cids']), '건')
print('  0개:', ', '.join(r['ja'] for r in STUDY if not r['cids']) or '없음')
for s_ in SCENES: print('  %-5s %02d:%02d %-24s %2d줄' % (s_['key'], s_['at']//60, s_['at']%60, s_['ko'], sum(1 for d in data if d['scene'] == s_['key'])))
