#!/usr/bin/env python3
"""「블록 연습」 페이지(<앱>/blocks.html)를 만든다 — 노래를 마디(블록) 단위 코드 격자로 보여 주고,
영상에 맞춰 지금 블록을 켜고, 블록을 눌러 듣기·멈추기·반복(🔁 이 칸 / 줄 4마디)을 한다. 가사는 싣지 않는다.

재료: <앱>/src/chords.json (tools/chord_simple.py) · <앱>/src/beats.json (앱의 beats.py, 있으면) · src/build.py 의 VID.
블록: beats.json 의 마디(bars)를 쓴다. 박자 격자가 코드 템포의 두 배로 잡혔으면(발라드를 8분음표로 센 경우)
     이웃 두 마디를 한 블록으로 묶는다 — 어느 쪽부터 묶을지는 코드가 바뀌는 자리와 더 잘 맞는 쪽.
     beats.json 이 없으면 코드 경계에 가장 잘 맞는 반 마디 격자를 잰다(courage-guitar 와 같은 방법).
     블록마다 앞·뒤 반에서 울리는 코드를 적는다(같으면 하나).
화면: tools/block-practice/tpl.html (공용). 카포·운지: tools/make_chord_sheet.py 와 같은 규칙·데이터.

사용: python3 tools/make_block_practice.py <앱폴더> --title 곡명 --artist 가수 --src "출처 문구" [--back 앱.html] [--out blocks.html]
"""
import argparse
import glob
import io
import json
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from make_chord_sheet import FING, NOTES, name, pick_capo   # noqa: E402

def srt_cues(path):
    out = []
    for b in io.open(path, encoding='utf-8').read().strip().split('\n\n'):
        L = b.split('\n')
        m = re.findall(r'(\d+):(\d+):(\d+),(\d+)', L[1]) if len(L) > 2 else []
        if len(m) < 2: continue
        f = lambda g: int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 1000
        out.append((round(f(m[0]), 2), round(f(m[1]), 2), ' '.join(L[2:]).strip()))
    return out


def app_lines(S):
    """노래 앱에 이미 있는 가사 줄(subtitles.srt)·뜻·읽기(ko.txt)·단어(words.txt) → 막대에 보일 줄 목록.
    가사를 새로 만들지 않는다 — 앱 본문이 쓰는 데이터를 그대로 가져온다. 없거나 줄 수가 안 맞으면 [] (막대에 가사 없음)."""
    sp, kp = os.path.join(S, 'subtitles.srt'), os.path.join(S, 'ko.txt')
    if not (os.path.exists(sp) and os.path.exists(kp)): return []
    cues = srt_cues(sp)
    ko = {}
    for ln in io.open(kp, encoding='utf-8'):
        q = ln.rstrip('\n').split('|')
        if ln.startswith('#') or len(q) < 3 or not q[0].strip().isdigit(): continue
        ko[int(q[0])] = (q[1].strip(), q[2].strip())
    if len(ko) != len(cues): return []
    words = []
    wp = os.path.join(S, 'words.txt')
    if os.path.exists(wp):
        for ln in io.open(wp, encoding='utf-8'):
            q = [x.strip() for x in ln.rstrip('\n').split('|')]
            if ln.startswith('#') or len(q) < 4: continue
            words.append((q[0].split(','), q[1], q[2], q[3]))
    out = []
    for i, (s, e, ja) in enumerate(cues, 1):
        hits = []
        for stems, head, rd, mean in words:
            at = min((ja.find(x) for x in stems if x and x in ja), default=-1)
            if at >= 0 and head not in [h[1] for h in hits]: hits.append((at, head, rd, mean))
        hits.sort()
        k, r = ko.get(i, ('', ''))
        out.append([s, e, ja, k, r, [[h, rd, mean] for _, h, rd, mean in hits[:6]]])
    return out


SHARP_HOMES = {'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#'}       # 이 조들은 G#m·D#m 처럼 샵 이름 그대로 쓴다


def fitted_bars(CH, end):
    bounds = np.array([s for s, e, c in CH][1:])
    best = None
    for h in np.arange(1.0, 2.6, 0.0005):
        for t0 in np.arange(0, h, 0.02):
            r = (bounds - t0) / h
            err = np.abs(r - np.round(r)).mean()
            if best is None or err < best[0]: best = (err, h, t0)
    _, h, t0 = best
    out, t = [], t0
    while t < end - h * .5: out.append(t); t += 2 * h
    return out


def build(app, title, artist, src, back, out, lyrics=True):
    S = os.path.join(ROOT, app, 'src')
    d = json.load(io.open(os.path.join(S, 'chords.json'), encoding='utf-8'))
    CH, END = d['chords'], d['chords'][-1][1]
    vid = re.search(r"VID\s*=\s*'([^']+)'", io.open(os.path.join(S, 'build.py'), encoding='utf-8').read()).group(1)
    bp = os.path.join(S, 'beats.json')
    how = ''
    if os.path.exists(bp):
        bj = json.load(io.open(bp, encoding='utf-8'))
        starts = [x for x in bj['bars'] if x < END]
        how = f'박자 격자 beats.json({bj["bpm"]:.0f} BPM)'
        if bj['bpm'] > 1.5 * d['bpm']:           # 격자가 두 배로 잡혔다 → 두 마디씩 묶는다
            ch_b = np.array([s for s, e, c in CH][1:])
            def score(off):
                st = np.array(starts[off::2]); return np.min(np.abs(ch_b[:, None] - st[None, :]), 1).mean()
            off = min((0, 1), key=score)
            starts = ([0.0] if off else []) + starts[off::2]
            how += ' 두 마디씩 묶음'
    else:
        starts = fitted_bars(CH, END); how = '코드 경계에 맞춘 격자'
    starts = sorted(set(round(x, 2) for x in starts))
    if starts[0] > .05: starts = [0.0] + starts if starts[0] > 1.5 else [0.0] + starts[1:]

    def at(t):
        for s, e, c in CH:
            if s <= t < e: return c
        return CH[-1][2] if t >= END else CH[0][2]

    bars = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else END
        if e - s < .3: continue
        a, b = at(s + (e - s) * .25), at(s + (e - s) * .75)
        bars.append([round(s, 2), round(e, 2), [a] if a == b else [a, b]])
    rows = [bars[i:i + 4] for i in range(0, len(bars), 4)]

    home = d.get('home', d['tonic'])
    capo, form = pick_capo(home)
    used = []
    for b in bars:
        for c in b[2]:
            if c not in used: used.append(c)
    sharp = NOTES[home] in SHARP_HOMES
    real = {c: (c if sharp else name(c, 0)) for c in used}
    shape = {c: name(c, capo) for c in used}

    DATA = {'vid': vid, 'title': title, 'artist': artist, 'key': real.get(d['key'], d['key']) if d['key'] in real else (d['key'] if sharp else name(d['key'], 0)),
            'mode': d['mode'], 'bpm': d['bpm'], 'fit': d['fit'], 'capo': capo, 'form': form, 'rows': rows,
            'real': real, 'order': used, 'fing': FING,   # 운지 그림·키 이동은 화면(tpl)이 한다 'store': app + '.blocks',
            'back': [back, '노래 앱으로'] if back else None, 'note': f'한 칸 = 1마디({how}).', 'src': src,
            'lines': app_lines(S) if lyrics else []}         # --no-lyrics: 가사는 노래 앱 본문에만 두고 여기엔 코드만
    tpl = io.open(os.path.join(ROOT, 'tools', 'block-practice', 'tpl.html'), encoding='utf-8').read()
    html = tpl.replace('/*__DATA__*/{}', json.dumps(DATA, ensure_ascii=False, separators=(',', ':'))) \
              .replace('/*__TITLE__*/', f'{title} 블록 연습')
    io.open(os.path.join(ROOT, app, out), 'w', encoding='utf-8').write(html)
    print(f'{app}/{out}: 조 {DATA["key"]} · {d["bpm"]} BPM · {how} · 블록 {len(bars)} · 줄 {len(rows)} · '
          f'카포 {capo} {form} 모양 · 가사 줄 {len(DATA["lines"])}(단어 {sum(len(x[5]) for x in DATA["lines"])}) · '
          + ' '.join(f'{real[c]}→{shape[c]}' for c in used))
    return DATA


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('app'); ap.add_argument('--title', required=True); ap.add_argument('--artist', required=True)
    ap.add_argument('--src', required=True); ap.add_argument('--back', default=''); ap.add_argument('--out', default='blocks.html'); ap.add_argument('--no-lyrics', action='store_true')
    a = ap.parse_args()
    back = a.back or next((os.path.basename(p) for p in glob.glob(os.path.join(ROOT, a.app.strip('/'), '*-Cards.html'))), '')
    build(a.app.strip('/'), a.title, a.artist, a.src, back, a.out, lyrics=not a.no_lyrics)
