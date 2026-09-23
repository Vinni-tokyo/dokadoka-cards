#!/usr/bin/env python3
"""읽어주기 음성이 한자를 어떻게 읽는지 가려낸다.

받아 적기(음성 인식)는 한자로 돌려주기 때문에 읽는 소리를 알 수 없다. 그래서
소리끼리 맞대 본다 — 한자가 든 말을 한 번 읽히고, 후보 가나들을 각각 읽힌 뒤
소리 모양(MFCC)을 재어 가장 가까운 후보를 고른다. 같은 목소리·같은 속도라
읽는 소리가 같으면 거의 겹친다.

사용: .venv/bin/python tools/hear_tts.py 落葉 おちば らくよう
      (첫 인자 = 한자가 든 말, 나머지 = 후보들)
"""
import asyncio
import os
import sys
import tempfile

import edge_tts
import librosa
import numpy as np

VOICE = 'ja-JP-NanamiNeural'
RATE = '-10%'


async def say(text, path):
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(path)


def mfcc(path):
    y, sr = librosa.load(path, sr=16000, mono=True)
    y, _ = librosa.effects.trim(y, top_db=35)
    return librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13), len(y) / sr


def dist(a, b):
    d, _ = librosa.sequence.dtw(X=a, Y=b, metric='cosine')
    return float(d[-1, -1]) / (a.shape[1] + b.shape[1])


def main(word, cands):
    d = tempfile.mkdtemp()
    paths = {}
    for i, t in enumerate([word] + cands):
        p = os.path.join(d, f'{i}.mp3')
        asyncio.run(say(t, p))
        paths[t] = p
    base, bdur = mfcc(paths[word])
    print(f'  「{word}」 {bdur:.2f}초')
    rows = []
    for c in cands:
        m, dur = mfcc(paths[c])
        rows.append((dist(base, m), c, dur))
    rows.sort()
    for i, (s, c, dur) in enumerate(rows):
        print(f'   {"←" if i == 0 else " "} {c:<12} 거리 {s:.4f} · {dur:.2f}초')
    print(f'  → 「{word}」은 「{rows[0][1]}」로 읽는다')
    return rows[0][1]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2:])
