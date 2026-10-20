#!/usr/bin/env python3
"""목소리 조각(숨·끊김 사이)의 시각만 → <앱>/src/vsegs.json — 「📝 내 가사」 자동 줄 맞추기·탭 보정용.

vocal_phrases.py(Silero VAD)는 말소리용이라 노래를 많이 놓쳤다(楓: 22~223초만 잡고 마지막 후렴 등 1/3 누락).
여기서는 demucs 목소리 트랙의 음량에서 「깊은 골」(좌우 0.6초 안 최대보다 10dB 이상 낮은 곳)과 무음을 경계로 자른다.
가사 글자는 다루지 않는다 — [시작, 끝] 초만 저장한다.

사용: .venv/bin/python tools/vocal_segments.py <앱> <vocals.wav> [--depth 10]
"""
import argparse
import json
import os

import librosa
import numpy as np
from scipy.ndimage import uniform_filter1d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def segments(path, depth=10, minlen=0.6, rel=-30):
    y, sr = librosa.load(path, sr=16000, mono=True)
    hop = 160; fps = sr / hop
    db = 20 * np.log10(librosa.feature.rms(y=y, frame_length=640, hop_length=hop)[0] + 1e-9)
    ref = np.percentile(db[db > -80], 95); db = np.maximum(db, ref - 50)
    sm = uniform_filter1d(db, int(0.08 * fps))
    loud = sm > ref + rel
    w = int(0.6 * fps)
    cut = ~loud
    for i in range(1, len(sm) - 1):
        if sm[i] <= sm[i - 1] and sm[i] <= sm[i + 1] and min(sm[max(0, i - w):i].max(), sm[i + 1:i + 1 + w].max()) - sm[i] >= depth:
            cut[i] = True
    out, i, n = [], 0, len(sm)
    while i < n:
        if cut[i]: i += 1; continue
        j = i
        while j < n and not cut[j]: j += 1
        if (j - i) / fps >= minlen and loud[i:j].mean() > .5: out.append([round(i / fps, 2), round(j / fps, 2)])
        i = j
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('app'); ap.add_argument('wav'); ap.add_argument('--depth', type=float, default=10)
    a = ap.parse_args()
    seg = segments(a.wav, a.depth)
    json.dump(seg, open(os.path.join(ROOT, a.app.strip('/'), 'src', 'vsegs.json'), 'w'), separators=(',', ':'))
    print(f'{a.app}: 목소리 조각 {len(seg)} ({seg[0][0]}~{seg[-1][1]}초) → src/vsegs.json')
