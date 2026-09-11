#!/usr/bin/env python3
"""字幕(SRT) → 学習アプリ HTML。src/series/<id>/ ごとに 1 シリーズを組み立てる。

  各シリーズのフォルダに置くもの
    meta.json     … 動画ID・タイトル・章立て・結合指定
    subtitles.srt … YouTube の自動生成字幕
    ja.txt        … 日本語訳      `カードid|訳|注記`
    fixes.txt     … 字幕の手直し  `カードid|直した本文`
    study.txt     … 表現と単語    `E or V|韓国語|日本語|メモ`
"""
import io, json, os, re, sys

S    = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(S)
OUT  = os.path.join(ROOT, 'Korean-Cliff389-Cards.html')
SDIR = os.path.join(S, 'series')

# ---------------------------------------------------------------- 字幕 → カード
GAP, MAXLEN = 1.0, 60
TAG = re.compile(r'\[[^\]]*\]')

def read_cues(path):
    raw = io.open(path, encoding='utf-8-sig').read()
    cues = []
    for b in re.split(r'\n\s*\n', raw.strip()):
        L = [l for l in b.strip().split('\n') if l.strip()]
        if len(L) < 3: continue
        m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', L[1])
        if not m: continue
        g = list(map(int, m.groups()))
        cues.append({'s': g[0]*3600+g[1]*60+g[2]+g[3]/1000,
                     'e': g[4]*3600+g[5]*60+g[6]+g[7]/1000,
                     't': ' '.join(L[2:]).strip()})
    # yt-dlp の自動字幕は終了時刻が次の開始に食い込む(転がし表示)。次の開始で切りそろえる
    for i in range(len(cues)-1):
        if cues[i]['e'] > cues[i+1]['s']: cues[i]['e'] = cues[i+1]['s']
    return cues

def read_transcript(path):
    """YouTube の書き起こしパネル形式。`0:1717 seconds本文` のように時刻と読み上げ用ラベルが続く。
       終了時刻が無いので次の行の開始を終わりとみなす。"""
    def label(m, s):
        p = []
        if m: p.append('%d minute%s' % (m, '' if m == 1 else 's'))
        if s or not m: p.append('%d second%s' % (s, '' if s == 1 else 's'))
        return ', '.join(p)
    rows = []
    for ln in io.open(path, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln.strip(): continue
        m = re.match(r'(\d+):(\d\d)', ln)
        if not m: continue
        mi, se = int(m.group(1)), int(m.group(2))
        rest = ln[m.end():]
        lab  = label(mi, se)
        if rest.startswith(lab): rest = rest[len(lab):]
        rest = rest.strip()
        if rest: rows.append({'s': mi*60 + se, 't': rest})
    # 同じ秒に2行並ぶことがあるので、次の「より後の」開始を終わりにする
    for i, r in enumerate(rows):
        nxt = next((x['s'] for x in rows[i+1:] if x['s'] > r['s']), None)
        r['e'] = nxt if nxt is not None else r['s'] + 5
    return rows

def segment_lines(cues):
    """書き起こしは1行がすでにカード大なので、そのまま1枚として扱う"""
    RATE, DEAD_MIN = 4.5, 1.2
    out = []
    for i, c in enumerate(cues, 1):
        body = re.sub(r'\s+', ' ', TAG.sub(' ', c['t'])).strip()
        if not body: continue
        est  = max(0.5, len(re.sub(r'\s+', '', body))/RATE)
        dead = (c['e'] - c['s']) - est
        pe   = max(c['e'] - (dead if dead > DEAD_MIN else 0.0), c['s'] + 0.8)
        row = {'id': i, 's': round(c['s'], 2), 'e': round(c['e'], 2), 'ko': body}
        if row['e'] - pe > 0.05: row['pe'] = round(pe, 2)
        out.append(row)
    return out

# 手動(公式)字幕は `>>` も間も無く 2〜3 秒ごとに続く。文末の終結語尾で切る
_FINAL = re.compile(r'(요|다|어|아|지|네|죠|잖아|거든|습니다|세요|까|야|대|래|구나|군|게|ㅎ+|ㅋ+)[?!.…~"”’)\]]*$')
_PUNCT = re.compile(r'[?!.…]["”’]?$|["”’]$')

def segment_manual(cues, target=22, hard=48, gap=0.6):
    """目安の長さに達し、かつ行末が終結語尾/句読点なら切る。間が空いても切る"""
    RATE, DEAD_MIN = 4.5, 1.2
    segs, cur = [], None
    for i, c in enumerate(cues):
        body = re.sub(r'\s+', ' ', TAG.sub(' ', c['t'])).strip()
        if not body: continue
        nxt = cues[i+1] if i+1 < len(cues) else None
        if cur is None: cur = {'s': c['s'], 'e': c['e'], 't': body, 'last': c}
        else: cur['t'] += ' ' + body; cur['e'] = c['e']; cur['last'] = c
        n = len(cur['t']); tail = body.split()[-1]
        fin = bool(_PUNCT.search(body) or _FINAL.search(tail))
        if nxt is None or (nxt['s'] - c['e']) > gap or n >= hard or (n >= target and fin):
            segs.append(cur); cur = None
    if cur: segs.append(cur)
    out = []
    for i, g in enumerate(segs, 1):
        last = g['last']
        lbody = re.sub(r'\s+', '', TAG.sub('', last['t']))
        est  = max(0.5, len(lbody)/RATE); dead = (last['e'] - last['s']) - est
        pe   = max(last['e'] - (dead if dead > DEAD_MIN else 0.0), last['s'] + 0.4, g['s'] + 0.8)
        row = {'id': i, 's': round(g['s'], 2), 'e': round(g['e'], 2), 'ko': g['t']}
        if row['e'] - pe > 0.05: row['pe'] = round(pe, 2)
        out.append(row)
    return out

def segment(cues):
    """話者マーカー `>>`・1秒以上の間・長さ上限で切る"""
    segs, cur = [], None
    for c in cues:
        txt = c['t']
        newspk  = txt.lstrip().startswith('>>')
        gap     = cur is not None and (c['s'] - cur['e']) > GAP
        toolong = cur is not None and len(cur['t']) >= MAXLEN
        ended   = cur is not None and re.search(r'[.!?？！]\s*$', cur['t'])
        if cur is None or newspk or gap or (toolong and ended) or (toolong and len(cur['t']) >= MAXLEN*1.6):
            if cur: segs.append(cur)
            cur = {'s': c['s'], 'e': c['e'], 't': txt, 'cues': [c]}
        else:
            cur['t'] = (cur['t'] + ' ' + txt).strip(); cur['e'] = c['e']; cur['cues'].append(c)
    if cur: segs.append(cur)

    RATE, DEAD_MIN = 4.5, 1.2          # 字数密度で「発話の終わり」を推す
    out = []
    for i, g in enumerate(segs, 1):
        body = re.sub(r'\s+', ' ', TAG.sub(' ', g['t'].replace('>>', ' '))).strip()
        if not body: continue
        last  = g['cues'][-1]
        lbody = re.sub(r'\s+', '', TAG.sub('', last['t'].replace('>>', ''))).strip()
        est   = max(0.5, len(lbody)/RATE)
        dead  = (last['e'] - last['s']) - est
        pe    = max(last['e'] - (dead if dead > DEAD_MIN else 0.0), last['s'] + 0.4, g['s'] + 0.8)
        row = {'id': i, 's': round(g['s'], 2), 'e': round(g['e'], 2), 'ko': body}
        if row['e'] - pe > 0.05: row['pe'] = round(pe, 2)
        out.append(row)
    return out

# ---------------------------------------------------------------- 学習データ
_TAIL1 = ('', '은','는','이','가','을','를','에','에서','에게','한테','으로','로','와','과','의',
          '도','만','까지','부터','보다','처럼','이나','나','야','아','요','고','서','이야','예요',
          '이에요','입니다','이랑','랑','밖에','마다','께','께서','이다','이었어','였어')

def find_hits(kind, term, cards):
    """その表現/単語が出てくるカード id を全部返す(「운」が「운동」に当たらないよう長さで規則を変える)"""
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
    """例文に向くカードを選ぶ。広告パートは代わりが無い時だけ使う"""
    pool = [i for i in ids if by_id[i]['scene'] != 'pr'] or list(ids)
    best, best_score = None, None
    for i in pool:
        c = by_id[i]; n = len(c['ko'])
        s = 10 if 8 <= n <= 40 else (n - 8 if n < 8 else -(n - 40) * 0.3)
        if re.search(r'[.?!]\s*$', c['ko']): s += 3
        if c.get('raw'): s += 1
        if best_score is None or s > best_score: best, best_score = i, s
    return best

def read_pairs(path):
    rows = {}
    if not os.path.exists(path): return rows
    for ln in io.open(path, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln.strip() or ln.lstrip().startswith('#'): continue
        p = ln.split('|')
        if len(p) < 2: continue
        rows[int(p[0])] = (p[1].strip(), p[2].strip() if len(p) > 2 else '')
    return rows

# ---------------------------------------------------------------- 1シリーズ分
def build_series(d):
    meta = json.load(io.open(os.path.join(d, 'meta.json'), encoding='utf-8'))
    chapters = meta['chapters']
    def scene_of(sec):
        k = chapters[0][0]
        for key, at, _l, _ko, _itv in chapters:
            if sec >= at: k = key
        return k

    src = meta.get('source')
    if src == 'transcript':
        segs = segment_lines(read_transcript(os.path.join(d, 'transcript.txt')))
    elif src == 'manual':
        segs = segment_manual(read_cues(os.path.join(d, 'subtitles.srt')))
    else:
        segs = segment(read_cues(os.path.join(d, 'subtitles.srt')))
    ja    = read_pairs(os.path.join(d, 'ja.txt'))
    fixes = read_pairs(os.path.join(d, 'fixes.txt'))
    missing = [s['id'] for s in segs if s['id'] not in ja]
    assert not missing, f"{meta['id']}: 訳なし {missing[:10]}"

    data = []
    for s in segs:
        j, note = ja[s['id']]
        row = {'id': s['id'], 's': s['s'], 'e': s['e'], 'ko': s['ko'], 'ja': j, 'scene': scene_of(s['s'])}
        if 'pe' in s: row['pe'] = s['pe']
        if s['id'] in fixes and fixes[s['id']][0] != s['ko']:
            row['ko'] = fixes[s['id']][0]; row['raw'] = s['ko']
        if note: row['note'] = note
        data.append(row)

    # 長さ上限で文の途中に切れたカードを繋ぎ直す(分割し直すと id がずれて訳の対応が壊れるため)
    by = {x['id']: x for x in data}; gone = set()
    for m in meta.get('merges', []):
        parts = [by[i] for i in m['ids'] if i in by]
        if len(parts) != len(m['ids']): continue
        head = parts[0]; head['e'] = parts[-1]['e']
        if 'pe' in parts[-1]: head['pe'] = parts[-1]['pe']
        else: head.pop('pe', None)
        head['ko'] = ' '.join(p['ko'] for p in parts)
        head['ja'] = ''.join(p['ja'] for p in parts if p['id'] not in m.get('ja_skip', []))
        if any('raw' in p for p in parts):
            head['raw'] = ' '.join(p.get('raw', p['ko']) for p in parts)
        notes = [p['note'] for p in parts if 'note' in p]
        if notes: head['note'] = ' / '.join(notes)
        gone.update(m['ids'][1:])
    data = [x for x in data if x['id'] not in gone]

    by_id = {c['id']: c for c in data}
    study = []
    for ln in io.open(os.path.join(d, 'study.txt'), encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln.strip() or ln.lstrip().startswith('#'): continue
        p = ln.split('|')
        if len(p) < 3 or p[0].strip() not in ('E', 'V'): continue
        kind, ko, jp = p[0].strip(), p[1].strip(), p[2].strip()
        if not ko or not jp: continue
        row = {'t': kind, 'ko': ko, 'ja': jp}
        if len(p) > 3 and p[3].strip(): row['note'] = p[3].strip()
        row['cids'] = find_hits(kind, ko, data)
        ex = pick_example(row['cids'], by_id)
        if ex is not None: row['ex'] = ex
        study.append(row)

    scenes = [{'key': k, 'label': l, 'ko': ko, 'itv': bool(itv), 'at': at}
              for k, at, l, ko, itv in chapters]
    info = {k: meta[k] for k in ('id', 'videoId', 'title', 'titleKo', 'subtitle', 'subtitleKo', 'seal') if k in meta}
    print('  %-10s カード %3d · 手直し %2d · 無音カット %3d · 学習 %3d (クリップ %d本)'
          % (meta['id'], len(data), sum(1 for x in data if 'raw' in x),
             sum(1 for x in data if 'pe' in x), len(study), sum(len(r['cids']) for r in study)))
    return {**info, 'scenes': scenes, 'data': data, 'study': study}

# ---------------------------------------------------------------- 出力
if __name__ == '__main__':
    all_dirs = sorted(os.path.join(SDIR, n) for n in os.listdir(SDIR)
                      if os.path.isdir(os.path.join(SDIR, n)))
    dirs, pending = [], []
    for d in all_dirs:
        mp = os.path.join(d, 'meta.json')
        src = 'subtitles.srt'
        if os.path.exists(mp):
            try:
                if json.load(io.open(mp, encoding='utf-8')).get('source') == 'transcript': src = 'transcript.txt'
            except Exception: pass
        need = ('meta.json', src, 'ja.txt', 'study.txt')
        miss = [f for f in need if not os.path.exists(os.path.join(d, f))]
        (pending.append((os.path.basename(d), miss)) if miss else dirs.append(d))
    assert dirs, 'src/series/ に完成したシリーズがありません'
    print('シリーズ', len(dirs), '本' + (' (準備中 %d本)' % len(pending) if pending else ''))
    SERIES = [build_series(d) for d in dirs]
    for name, miss in pending:
        print('  %-10s 準備中 — 足りないもの: %s' % (name, ', '.join(miss)))

    tpl = io.open(os.path.join(S, 'tpl.html'), encoding='utf-8').read()
    html = tpl.replace('/*__SERIES__*/', json.dumps(SERIES, ensure_ascii=False, separators=(',', ':')))
    # 학습 음원(src/audio/*.mp3, tools/make_study_audio.py 가 생성)을 data URI 로 심는다. 없으면 빈 객체 → 앱은 브라우저 TTS 로 폴백
    _adir = os.path.join(S, 'audio'); _amap = {}
    if os.path.exists(os.path.join(_adir, 'index.json')):
        import base64
        for _k, _fn in json.load(open(os.path.join(_adir, 'index.json'), encoding='utf-8')).items():
            _fp = os.path.join(_adir, _fn)
            if os.path.exists(_fp): _amap[_k] = 'data:audio/mpeg;base64,' + base64.b64encode(open(_fp, 'rb').read()).decode()
    html = html.replace('/*__AUDIO__*/', json.dumps(_amap, ensure_ascii=False))
    print('학습 음원:', len(_amap), '건 심음')
    io.open(OUT, 'w', encoding='utf-8').write(html)
    print('生成:', OUT, '(%.1f KB)' % (os.path.getsize(OUT)/1024))
