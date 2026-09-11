#!/usr/bin/env python3
"""歌詞字幕(公式 MV の ko/ja 字幕) → 歌で学ぶ韓国語カードアプリ。
   korean-cards と同じテンプレート(SERIES 1本)を使う。

   src に置くもの
     subtitles.ko.srt / subtitles.ja.srt   公式 MV の韓国語・日本語字幕(行が 1:1 で対応)
     rd.txt                                 `id|読み(カナ)|注記`   ハングル行の読みと文法メモ
     study.txt                              `E or V|韓国語|日本語|メモ`
"""
import io, json, os, re

S    = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(S)
VID  = 'sLk8zWUuYTA'
NICK = 'VitaminME'

# 曲の構成 = シーン (キー, 開始秒, 日本語, 韓国語)
SCENES = [
 ('intro',  0,     'イントロ',            '인트로'),
 ('v1',     11.6,  '1番 Aメロ',           '1절'),
 ('pre1',   27.3,  '1番 Bメロ',           '1절 프리코러스'),
 ('cho1',   40.0,  '1番 サビ',            '1절 후렴'),
 ('hook1',  58.7,  'フック (Not A,B,C)',   '훅'),
 ('v2',     77.1,  '2番 Aメロ',           '2절'),
 ('pre2',   93.3,  '2番 Bメロ',           '2절 프리코러스'),
 ('cho2',   105.7, '2番 サビ',            '2절 후렴'),
 ('hook2',  124.4, 'フック 2',            '훅 2'),
 ('bridge', 143.2, 'ブリッジ',            '브릿지'),
 ('cho3',   162.5, 'ラストサビ',          '마지막 후렴'),
 ('hook3',  173.5, 'アウトロ · フック',    '아웃트로'),
]

def read_srt(path):
    raw = io.open(path, encoding='utf-8-sig').read()
    out = []
    for b in re.split(r'\n\s*\n', raw.strip()):
        L = [l for l in b.strip().split('\n') if l.strip()]
        if len(L) < 3: continue
        m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', L[1])
        if not m: continue
        g = list(map(int, m.groups()))
        out.append({'s': round(g[0]*3600+g[1]*60+g[2]+g[3]/1000, 2), 'e': round(g[4]*3600+g[5]*60+g[6]+g[7]/1000, 2),
                    't': re.sub(r'\s+', ' ', ' '.join(x.strip() for x in L[2:])).strip()})
    return out

ko = read_srt(os.path.join(S, 'subtitles.ko.srt'))
ja = read_srt(os.path.join(S, 'subtitles.ja.srt'))
assert len(ko) == len(ja), f'ko {len(ko)}行 / ja {len(ja)}行 — 行数が合わない'
for a, b in zip(ko, ja):
    assert abs(a['s'] - b['s']) < 0.5, f'時刻ずれ: {a} / {b}'

rd = {}
for ln in io.open(os.path.join(S, 'rd.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'): continue
    p = ln.split('|')
    rd[int(p[0])] = (p[1].strip(), p[2].strip() if len(p) > 2 else '')

HANGUL = re.compile(r'[가-힣]')
def scene_of(sec):
    k = SCENES[0][0]
    for key, at, _j, _k in SCENES:
        if sec >= at: k = key
    return k

data = []
for i, (k, j) in enumerate(zip(ko, ja), 1):
    row = {'id': i, 's': k['s'], 'e': k['e'], 'ko': k['t'], 'ja': j['t'], 'scene': scene_of(k['s'])}
    if not HANGUL.search(k['t']): row['en'] = 1                     # 英語だけの行(歌えるが学習語彙ではない)
    r, note = rd.get(i, ('', ''))
    if r: row['rd'] = r
    if note: row['note'] = note
    data.append(row)
missing_rd = [d['id'] for d in data if not d.get('en') and 'rd' not in d]
assert not missing_rd, f'読みがないハングル行: {missing_rd}'
extra = sorted(set(rd) - {d['id'] for d in data})
assert not extra, f'カードにない id: {extra}'

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
        s = 10 if 6 <= n <= 30 else (n - 6 if n < 6 else -(n - 30) * 0.3)
        if best_score is None or s > best_score: best, best_score = i, s
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

series = {
 'id': 'vitaminme', 'videoId': VID, 'seal': '歌',
 'title': 'Vitamin ME', 'titleKo': 'fromis_9 (프로미스나인) — Vitamin ME',
 'subtitle': 'fromis_9 · アルバム「Glow ME」タイトル曲 · 公式MV', 'subtitleKo': '프로미스나인 · 앨범 「Glow ME」 타이틀곡 · 공식 MV',
 'scenes': [{'key': k, 'label': j, 'ko': kk, 'itv': False, 'at': at} for k, at, j, kk in SCENES],
 'data': data, 'study': study,
}
bp = os.path.join(S, 'beats.json')
if os.path.exists(bp):
    b = json.load(io.open(bp, encoding='utf-8'))
    series.update({'bpm': b['bpm'], 'phase': b['phase'], 'beats': b['beats']})     # 小節リピート用の拍グリッド(beats.py 出力)
N = len(data)
OUT = os.path.join(ROOT, 'Korean-%s%d-Cards.html' % (NICK, N))
tpl = io.open(os.path.join(S, 'tpl.html'), encoding='utf-8').read()
html = tpl.replace('/*__SERIES__*/', json.dumps([series], ensure_ascii=False, separators=(',', ':')))
io.open(OUT, 'w', encoding='utf-8').write(html)

print('生成:', OUT, '(%.1f KB)' % (os.path.getsize(OUT)/1024))
print('カード:', N, '| ハングル行:', sum(1 for d in data if not d.get('en')), '| 英語だけの行:', sum(1 for d in data if d.get('en')),
      '| 読みあり:', sum(1 for d in data if 'rd' in d), '| 注記あり:', sum(1 for d in data if 'note' in d))
print('拍グリッド:', ('BPM %.1f · 拍 %d · 位相 %d' % (series['bpm'], len(series['beats']), series['phase'])) if 'beats' in series else 'なし')
print('学習:', len(study), '件 (表現', sum(1 for r in study if r['t']=='E'), '/ 単語', sum(1 for r in study if r['t']=='V'), ')',
      '· 連結', sum(1 for r in study if r['cids']), '件 / クリップ', sum(len(r['cids']) for r in study), '本')
print('  0件:', ', '.join(r['ko'] for r in study if not r['cids']) or 'なし')
for k, at, j, kk in SCENES:
    print('  %-7s %02d:%02d %-18s %2d行' % (k, at//60, at%60, j, sum(1 for d in data if d['scene'] == k)))
