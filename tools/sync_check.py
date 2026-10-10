#!/usr/bin/env python3
"""노래 앱의 줄 시각(싱크)을 목소리 트랙으로 다시 재어 어긋난 줄을 골라낸다.

음성 인식으로 시각을 맞춘 앱은 반주와 섞인 소리를 받아썼다. 그래서 30초 창 경계·길게 끄는 감탄사·
라이브 잡음에 시작이 밀린 줄이 있다(歌うたいのバラッド 첫 줄 3.3초). 여기서는
 ① demucs 로 뗀 목소리 트랙의 받아쓰기(words.json)로 가사를 다시 정렬하고(align_dp 와 같은 방식)
 ② 지금 앱의 줄 시작과 비교해 기준(기본 0.7초)보다 다른 줄을 짚는다.
 ③ 짚은 줄마다 목소리가 실제로 나기 시작한 곳(목소리 구간 시작)도 함께 보여 준다.
고칠지는 짚은 줄을 짧게 잘라 다시 받아써서 사람이 정한다 — 목소리 구간 시작은 숨소리를 잡기도 한다.

사용: python3 tools/sync_check.py <앱폴더> <목소리 words.json> <vocals.wav> [--th 0.7]
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def srt(p):
    out = []
    for b in io.open(p, encoding='utf-8').read().strip().split('\n\n'):
        L = b.split('\n')
        m = re.findall(r'(\d+):(\d+):(\d+),(\d+)', L[1])
        f = lambda g: int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 1000
        out.append((f(m[0]), f(m[1]), L[2]))
    return out


def vocal_onsets(wav):
    import librosa
    import numpy as np
    y, sr = librosa.load(wav, sr=16000, mono=True)
    db = 20 * np.log10(librosa.feature.rms(y=y, frame_length=640, hop_length=160)[0] + 1e-9)
    on = db > db.max() - 35; t = np.arange(len(db)) * 0.01
    segs, s = [], None
    for i, v in enumerate(on):
        if v and s is None: s = t[i]
        if not v and s is not None: segs.append([s, t[i]]); s = None
    out = []
    for a, b in segs:
        if out and a - out[-1][1] < 0.35: out[-1][1] = b
        else: out.append([a, b])
    return [a for a, b in out if b - a > 0.25]


def main():
    args = sys.argv[1:]; th = 0.7
    if '--th' in args:
        i = args.index('--th'); th = float(args[i + 1]); del args[i:i + 2]
    app, words, wav = args
    src = os.path.join(ROOT, app.strip('/'), 'src')
    cur = srt(os.path.join(src, 'subtitles.srt'))
    tmp = os.path.join(tempfile.mkdtemp(), 'v.srt')
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'align_dp.py'), os.path.join(src, 'lyrics.txt'),
                    words, tmp], check=True, capture_output=True)
    vox = srt(tmp)
    assert len(cur) == len(vox), (len(cur), len(vox))
    on = vocal_onsets(wav)
    flags = []
    for i, ((a, _, t), (b, _, _)) in enumerate(zip(cur, vox), 1):
        if abs(a - b) > th:
            near = min(on, key=lambda o: abs(o - min(a, b))) if on else None
            flags.append((i, a, b, near, t))
    print(f'{app}: {len(cur)}줄 · 목소리 트랙과 {th}초 넘게 다른 줄 {len(flags)}')
    for i, a, b, near, t in flags:
        print(f'  {i:3d}  지금 {a:7.2f}  목소리 {b:7.2f} ({b - a:+5.2f})  가까운 목소리 시작 {near:7.2f}  {t[:24]}')
    json.dump([{'n': i, 'cur': a, 'vox': b, 'onset': near, 't': t} for i, a, b, near, t in flags],
              open(os.path.join(tempfile.gettempdir(), f'sync_{app.strip("/")}.json'), 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    main()
