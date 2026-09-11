#!/usr/bin/env python3
"""韓国語の歌 → 日本語学習者向けの歌カードアプリ (korean-cards テンプレート・SERIES 1本 + カラオケ・小節リピート).
   src に置くもの
     lyrics.txt      歌詞(歌われる順、空行 = 区切り)。行 = カード
     subtitles.srt   行ごとの時刻 (align.py が音声認識の単語時刻から作ったもの)
     ja.txt          `id|日本語訳|注記`
     rd.txt          `id|読み(カタカナ)`
     study.txt       `E or V|韓国語|日本語|メモ`
     beats.json      beats.py 出力 (BPM・拍グリッド) — 小節リピート用
     audio/          tools/make_study_audio.py が作った学習音源"""
import io, json, os, re
S = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(S)
VID = 'MzKzs5DnQT8'; NICK = 'Saranghagi'

# 区切り(空行)の順に. (キー, 日本語, 韓国語)
SECTIONS = [
 ('v1',   '1番',              '1절'),
 ('cho1', 'サビ 1',            '후렴 1'),
 ('v2',   '2番',              '2절'),
 ('cho2', 'サビ 2',            '후렴 2'),
 ('cho3', 'ラストサビ · アウトロ', '마지막 후렴 · 아웃트로'),
]

lines, sec_of, sec, prev_blank = [], [], 0, False
for ln in io.open(os.path.join(S, 'lyrics.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if ln.startswith('#'): continue
    if not ln.strip():
        if lines: prev_blank = True
        continue
    if prev_blank: sec += 1; prev_blank = False
    lines.append(ln.strip()); sec_of.append(sec)
assert sec + 1 == len(SECTIONS), f'区切り数 {sec+1} ≠ SECTIONS {len(SECTIONS)}'

def read_srt(path):
    out = {}
    for b in re.split(r'\n\s*\n', io.open(path, encoding='utf-8-sig').read().strip()):
        L = [l for l in b.strip().split('\n') if l.strip()]
        if len(L) < 3: continue
        m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', L[1]); g = list(map(int, m.groups()))
        out[int(L[0])] = (round(g[0]*3600+g[1]*60+g[2]+g[3]/1000, 2), round(g[4]*3600+g[5]*60+g[6]+g[7]/1000, 2))
    return out
tim = read_srt(os.path.join(S, 'subtitles.srt'))
assert set(tim) == set(range(1, len(lines) + 1)), '字幕 id と歌詞の行数が違う'

def read_kv(name, n):
    out = {}
    for ln in io.open(os.path.join(S, name), encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln.strip() or ln.lstrip().startswith('#'): continue
        p = [x.strip() for x in ln.split('|')] + [''] * n
        out[int(p[0])] = tuple(p[1:1 + n])
    return out
ja = read_kv('ja.txt', 2); rd = read_kv('rd.txt', 1)
missing = [i for i in range(1, len(lines) + 1) if i not in ja]
assert not missing, f'訳なし: {missing}'
HANGUL = re.compile(r'[가-힣]')

data = []
for i, text in enumerate(lines, 1):
    s, e = tim[i]; j, note = ja[i]
    row = {'id': i, 's': s, 'e': e, 'ko': text, 'ja': j, 'scene': SECTIONS[sec_of[i - 1]][0]}
    if not HANGUL.search(text): row['en'] = 1
    r = rd.get(i, ('',))[0]
    if r: row['rd'] = r
    if note: row['note'] = note
    data.append(row)
missing_rd = [d['id'] for d in data if not d.get('en') and 'rd' not in d]
assert not missing_rd, f'読みがないハングル行: {missing_rd}'

# --- 学習データ (korean-cards と同じ照合規則) ------------------------------------
_TAIL1 = ('', '은','는','이','가','을','를','에','에서','에게','한테','으로','로','와','과','의',
          '도','만','까지','부터','보다','처럼','이나','나','야','아','요','고','서','이야','예요',
          '이에요','입니다','이랑','랑','밖에','마다','께','께서','이다','이었어','였어')
def find_hits(kind, term, cards):
    ids = []
    for c in cards:
        txt, hit = c['ko'], False
        if kind == 'E' or len(term) >= 2:
            hit = term in txt
        else:
            for tok in re.findall(r'[가-힣]+', txt):
                if not tok.startswith(term): continue
                rest = tok[len(term):]
                hit = rest in _TAIL1 or (rest.startswith('들') and rest[1:] in _TAIL1)
                if hit: break
        if hit: ids.append(c['id'])
    return ids
def pick_example(ids, by_id):
    best, best_score = None, None
    for i in ids:
        c = by_id[i]; n = len(c['ko'])
        sc = 10 if 6 <= n <= 30 else (n - 6 if n < 6 else -(n - 30) * 0.3)
        if best_score is None or sc > best_score: best, best_score = i, sc
    return best
by_id = {c['id']: c for c in data}
study = []
for ln in io.open(os.path.join(S, 'study.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'): continue
    p = [x.strip() for x in ln.split('|')]
    if len(p) < 3 or p[0] not in ('E', 'V') or not p[1] or not p[2]: continue
    row = {'t': p[0], 'ko': p[1], 'ja': p[2]}
    if len(p) > 3 and p[3]: row['note'] = p[3]
    row['cids'] = find_hits(p[0], p[1], data)
    ex = pick_example(row['cids'], by_id)
    if ex is not None: row['ex'] = ex
    study.append(row)
seen = set(); dup = [r['ko'] for r in study if (r['t'], r['ko']) in seen or seen.add((r['t'], r['ko']))]
assert not dup, f'重複: {dup}'

scenes = []
for key, j_, k_ in SECTIONS:
    first = next(d for d in data if d['scene'] == key)
    scenes.append({'key': key, 'label': j_, 'ko': k_, 'itv': False, 'at': first['s']})
series = {
 'id': 'saranghagi', 'videoId': VID, 'seal': '歌',
 'title': '愛するがゆえに (사랑하기 때문에)', 'titleKo': '유재하 「사랑하기 때문에」 — cover by 지원 (fromis_9)',
 'subtitle': 'ユ・ジェハ(1987)の名曲を fromis_9 ジウォンがカバー · 公式 fl▶ylist', 'subtitleKo': '유재하(1987) 명곡을 프로미스나인 지원이 커버 · 공식 fl▶ylist',
 'scenes': scenes, 'data': data, 'study': study,
}
bp = os.path.join(S, 'beats.json')
if os.path.exists(bp):
    b = json.load(io.open(bp, encoding='utf-8'))
    series.update({'bpm': b['bpm'], 'phase': b['phase'], 'beats': b['beats']})
N = len(data)
OUT = os.path.join(ROOT, 'Korean-%s%d-Cards.html' % (NICK, N))
tpl = io.open(os.path.join(S, 'tpl.html'), encoding='utf-8').read()
html = tpl.replace('/*__SERIES__*/', json.dumps([series], ensure_ascii=False, separators=(',', ':')))
_adir = os.path.join(S, 'audio'); _amap = {}
if os.path.exists(os.path.join(_adir, 'index.json')):
    import base64
    for _k, _fn in json.load(io.open(os.path.join(_adir, 'index.json'), encoding='utf-8')).items():
        _fp = os.path.join(_adir, _fn)
        if os.path.exists(_fp): _amap[_k] = 'data:audio/mpeg;base64,' + base64.b64encode(open(_fp, 'rb').read()).decode()
html = html.replace('/*__AUDIO__*/', json.dumps(_amap, ensure_ascii=False))
io.open(OUT, 'w', encoding='utf-8').write(html)
print('生成:', OUT, '(%.1f KB)' % (os.path.getsize(OUT)/1024))
print('カード:', N, '| ハングル行:', sum(1 for d in data if not d.get('en')), '| 読みあり:', sum(1 for d in data if 'rd' in d), '| 注記:', sum(1 for d in data if 'note' in d),
      '| 拍グリッド:', ('BPM %.1f · 拍 %d · 位相 %d' % (series['bpm'], len(series['beats']), series['phase'])) if 'beats' in series else 'なし', '| 学習音源:', len(_amap))
print('学習:', len(study), '件 (表現', sum(1 for r in study if r['t']=='E'), '/ 単語', sum(1 for r in study if r['t']=='V'), ') · 連結', sum(1 for r in study if r['cids']), '件')
print('  0件:', ', '.join(r['ko'] for r in study if not r['cids']) or 'なし')
for s_ in scenes: print('  %-5s %02d:%02d %-22s %2d行' % (s_['key'], s_['at']//60, s_['at']%60, s_['label'], sum(1 for d in data if d['scene'] == s_['key'])))
