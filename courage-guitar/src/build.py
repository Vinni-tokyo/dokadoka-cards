#!/usr/bin/env python3
"""Lofi Brew 「Courage Within」 기타 연습 페이지(../index.html)를 만든다 — 가사 없이 코드만.

재료: chords.json — tools/chord_simple.py 로 반주 트랙(demucs no_vocals)에서 딴 코드.
마디: 코드는 반 마디(2박) 단위로 바뀐다. 코드 경계에 가장 잘 맞는 반 마디 길이·시작점을 재서(HALF, T0)
     4박 = 1마디, 한 줄 = 4마디로 묶는다. 반 마디마다 그 가운데 시각에 울리는 코드를 쓴다.
카포: tools/make_chord_sheet.py 와 같은 규칙(C → G → D → A → E 모양, 5프렛 이내)과 운지 그림을 쓴다.

사용: python3 build.py
"""
import io
import json
import os
import sys

import numpy as np

S = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(S)
ROOT = os.path.dirname(APP)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from make_chord_sheet import FING, NOTES, SHOW, diagram, name, pick_capo   # noqa: E402

VID = '9cbcKa3gE9Y'
TITLE, ARTIST = 'Courage Within', 'Lofi Brew (로파이 브루)'

d = json.load(io.open(os.path.join(S, 'chords.json'), encoding='utf-8'))
CH = d['chords']
END = CH[-1][1]

# 반 마디 길이·시작점: 코드 경계들이 격자에 가장 잘 맞는 값
bounds = np.array([s for s, e, c in CH][1:])
best = None
for h in np.arange(1.70, 1.83, 0.0005):
    for t0 in np.arange(0, h, 0.02):
        r = (bounds - t0) / h
        err = np.abs(r - np.round(r)).mean()
        if best is None or err < best[0]: best = (err, h, t0)
ERR, HALF, T0 = best
HALF, T0 = round(float(HALF), 4), round(float(T0), 2)


def at(t):
    for s, e, c in CH:
        if s <= t < e: return c
    return CH[-1][2] if t >= END else CH[0][2]


bars = []                                   # [시작, 끝, [앞 반 코드, 뒤 반 코드]]
t = T0
while t < END - HALF * .5:
    a, b = at(t + HALF * .5), at(t + HALF * 1.5)
    bars.append([round(t, 2), round(t + 2 * HALF, 2), [a] if a == b else [a, b]])
    t += 2 * HALF
if T0 > .05: bars[0][0] = 0.0               # 첫 마디는 곡 처음부터

rows = [bars[i:i + 4] for i in range(0, len(bars), 4)]
# 줄 이름: 브리지 코드(D#m · C#m)가 들어 있으면 B, 아니면 A — 소리로 확인한 구분이 아니라 코드로 가른 것
labels = []
for r in rows:
    cs = {c for b in r for c in b[2]}
    labels.append('B' if cs & {'D#m', 'C#m'} else 'A')

capo, form = pick_capo(d['home'])
shift = capo
used = []
for b in bars:
    for c in b[2]:
        if c not in used: used.append(c)
real = {c: c for c in used}                 # 원래 코드 — B장조는 샵 조라 G#m·D#m 그대로(♭ 로 바꾸지 않는다)
shape = {c: name(c, shift) for c in used}   # 카포에서 잡는 모양
diag = {c: diagram(name(c, 0)) for c in used}                   # 운지 표는 ♭ 이름으로 적혀 있다
diag.update({nm: diagram(nm) for nm in shape.values()})

DATA = {'vid': VID, 'title': TITLE, 'artist': ARTIST, 'key': d['key'], 'mode': d['mode'], 'bpm': d['bpm'],
        'fit': d['fit'], 'capo': capo, 'form': form, 'half': HALF, 'rows': rows, 'labels': labels,
        'real': real, 'shape': shape, 'order': used, 'diag': diag}
tpl = io.open(os.path.join(S, 'tpl.html'), encoding='utf-8').read()
html = tpl.replace('/*__DATA__*/{}', json.dumps(DATA, ensure_ascii=False, separators=(',', ':')))
io.open(os.path.join(APP, 'index.html'), 'w', encoding='utf-8').write(html)
print(f'조 {DATA["key"]} {d["mode"]} · {d["bpm"]} BPM · 반 마디 {HALF}초(시작 {T0}, 격자 오차 {ERR:.3f}) · '
      f'마디 {len(bars)} · 줄 {len(rows)}(A {labels.count("A")} · B {labels.count("B")}) · 카포 {capo} · {form} 모양 · '
      f'코드 {" ".join(real[c] + "→" + shape[c] for c in used)}')
