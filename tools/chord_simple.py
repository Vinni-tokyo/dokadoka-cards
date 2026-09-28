#!/usr/bin/env python3
"""반주 트랙에서 간이 코드를 딴다(자동 채보). 조를 스스로 재고, 그 조에 맞는 코드 후보만 쓴다.

· 조: 크로마 분포를 Krumhansl 장·단조 틀과 맞대어 고른다. 단조면 나란한조(장조)의 코드 표를 쓴다.
· 후보: 장조 으뜸음 기준 I ii iii IV V vi 에, 가요·찬양에서 자주 빌리는 III VI II iv ♭VII ♭VI.
  경과 코드(dim·m7-5 등)는 넣지 않는다 — 넣었더니 엉뚱한 코드가 튀었다(歌うたいのバラッド 1절).
· 박마다 크로마를 코드 틀과 맞대고(베이스 음이 근음이면 가산), 바꿀 때 벌점을 줘 비터비로 다듬는다.

반주 트랙은 demucs 로 목소리를 뗀 no_vocals.wav 를 쓴다(목소리 선율이 코드 판별을 흐린다).

사용: .venv/bin/python tools/chord_simple.py <no_vocals.wav> <출력 json>
출력: {"key":"D","mode":"major","tonic":2,"bpm":76,"chords":[[시작,끝,"D"],...]}
"""
import json
import sys

import librosa
import numpy as np

N = 'C C# D D# E F F# G G# A A# B'.split()
MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
# (장조 으뜸음에서의 반음 거리, 장/단, 사전 가산점)
DEG = [(0, 'M', .06), (2, 'm', .03), (4, 'm', .02), (5, 'M', .06), (7, 'M', .06), (9, 'm', .04),
       (4, 'M', 0), (9, 'M', 0), (2, 'M', 0), (5, 'm', 0), (10, 'M', 0), (8, 'M', 0)]


def main(wav, out):
    y, sr = librosa.load(wav, sr=22050, mono=True)
    tun = librosa.estimate_tuning(y=y, sr=sr)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time', start_bpm=90)
    H = librosa.effects.harmonic(y, margin=3); hop = 512
    C = librosa.feature.chroma_cqt(y=H, sr=sr, tuning=tun, hop_length=hop, bins_per_octave=36)
    B = librosa.feature.chroma_cqt(y=H, sr=sr, tuning=tun, hop_length=hop, fmin=librosa.note_to_hz('E1'),
                                   n_octaves=2, bins_per_octave=36)
    t = librosa.frames_to_time(np.arange(C.shape[1]), sr=sr, hop_length=hop)

    prof = C.mean(1)
    sc = [(np.corrcoef(np.roll(MAJ, k), prof)[0, 1], k, 'major') for k in range(12)] + \
         [(np.corrcoef(np.roll(MIN, k), prof)[0, 1], k, 'minor') for k in range(12)]
    fit, tonic, mode = max(sc)
    home = tonic if mode == 'major' else (tonic + 3) % 12        # 코드 표는 장조 기준

    labels, T, prior = [], [], []
    for d, q, p in DEG:
        r = (home + d) % 12
        v = np.zeros(12); v[r] = 1.5; v[(r + (4 if q == 'M' else 3)) % 12] = 1; v[(r + 7) % 12] = 1
        labels.append((r, '' if q == 'M' else 'm')); T.append(v / np.linalg.norm(v)); prior.append(p)
    T = np.array(T); prior = np.array(prior)

    edges = list(beats) + [t[-1]]; X, Bx, span = [], [], []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (t >= a) & (t < b)
        if not m.any(): continue
        X.append(C[:, m].mean(1)); Bx.append(B[:, m].mean(1)); span.append((float(a), float(b)))
    X = np.array(X); Bx = np.array(Bx)
    S = (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)) @ T.T
    bass = Bx / (Bx.max(1, keepdims=True) + 1e-9)
    for j, (r, q) in enumerate(labels): S[:, j] += 0.3 * bass[:, r] + prior[j]

    K = len(labels); sw = 0.55
    D = S[0].copy(); P = []
    for i in range(1, len(S)):
        bj = int(D.argmax()); change = D[bj] - sw
        P.append(np.where(D >= change, np.arange(K), bj)); D = np.maximum(D, change) + S[i]
    path = [int(D.argmax())]
    for ch in reversed(P): path.append(int(ch[path[-1]]))
    path = path[::-1]
    seq = []
    for i, j in enumerate(path):
        r, q = labels[j]; n = N[r] + q
        if seq and seq[-1][2] == n: seq[-1][1] = span[i][1]
        else: seq.append([span[i][0], span[i][1], n])

    res = {'key': N[tonic] + ('' if mode == 'major' else 'm'), 'mode': mode, 'tonic': int(tonic), 'home': int(home),
           'fit': round(float(fit), 3), 'bpm': int(round(float(np.atleast_1d(tempo)[0]))),
           'chords': [[round(a, 2), round(b, 2), n] for a, b, n in seq]}
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'{wav}: 조 {res["key"]}(일치도 {res["fit"]}) · {res["bpm"]} BPM · 코드 구간 {len(seq)} → {out}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(1)
    main(*sys.argv[1:])
