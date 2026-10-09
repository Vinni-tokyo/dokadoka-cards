#!/usr/bin/env python3
"""公式MVの音声から BPM と小節(4/4)の頭を求めて beats.json に書く。
   K-POP のようにテンポが一定な曲では、拍追跡(beat_track)より「等間隔グリッド」を全曲のオンセットに合わせる方が正確
   (beat_track は途中で1拍ずれることがあり、実際にこの曲で 55〜110秒の間に1拍ずれた)。
   手順: 1) beat_track でおおよその周期  2) 周期と位相を細かく振って、オンセット強度の合計が最大の等間隔グリッドを選ぶ
         3) 4拍のうち小節の頭を、拍の強さ + 「繰り返し歌詞が同じ拍位置に来るか」で選ぶ
   使い方: .venv/bin/python src/beats.py <wav>   (音声はリポに入れない)"""
import sys, json, os, re, bisect, numpy as np, librosa
wav = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
y, sr = librosa.load(wav, sr=22050, mono=True)
HOP = 512
onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
t_frames = librosa.frames_to_time(np.arange(len(onset)), sr=sr, hop_length=HOP)
tempo0, bt0 = librosa.beat.beat_track(onset_envelope=onset, sr=sr, hop_length=HOP, units='time', trim=False)
T0 = float(np.median(np.diff(bt0)))
dur = float(len(y)) / sr

def grid_score(T, ph):
    grid = np.arange(ph, dur, T)
    v = np.interp(grid, t_frames, onset)
    return float(v.sum())

# 2) 周期 T を ±2% の範囲で 0.0002 秒刻み、位相を 0.01 秒刻みで探索(粗→細)
best = (-1, T0, 0.0)
for T in np.arange(T0 * 0.98, T0 * 1.02, 0.0004):
    for ph in np.arange(0, T, 0.02):
        s = grid_score(T, ph)
        if s > best[0]: best = (s, T, ph)
_, T, ph = best
for T2 in np.arange(T - 0.0005, T + 0.0005, 0.00005):
    for ph2 in np.arange(max(0, ph - 0.03), ph + 0.03, 0.004):
        s = grid_score(T2, ph2)
        if s > best[0]: best = (s, T2, ph2)
_, T, ph = best
beats = np.arange(ph, dur, T)
bpm = 60.0 / T
# --track BPM: 終盤のリタルダンドなどテンポが動く曲は、等間隔ではなく beat_track の拍列をそのまま使う(拍の抜け・重複だけ補正)
if '--track' in sys.argv:
    sb = float(sys.argv[sys.argv.index('--track') + 1])
    _, bt = librosa.beat.beat_track(onset_envelope=onset, sr=sr, hop_length=HOP, start_bpm=sb, units='time', trim=False)
    bt = list(bt); Tm = float(np.median(np.diff(bt))); fixed = [bt[0]]
    for t in bt[1:]:
        gap = t - fixed[-1]
        if gap > 1.6 * Tm: fixed.append(fixed[-1] + gap / 2)          # 抜けた拍を補う
        if gap < 0.6 * Tm: continue                                   # 二重の拍を捨てる
        fixed.append(t)
    beats = np.array(fixed); T = Tm; bpm = 60.0 / T
    print('track mode: start_bpm %.0f → 拍 %d, 中央間隔 %.3f (範囲 %.3f〜%.3f)' % (sb, len(beats), T, np.diff(beats).min(), np.diff(beats).max()))

# 3) 小節の頭(位相 0..3): 拍の強さ + 繰り返し歌詞の一貫性(同じ歌詞行は同じ拍位置に来るはず)
lines = []
srt = sys.argv[2] if len(sys.argv) > 2 else next(p for p in (os.path.join(here, 'subtitles.srt'), os.path.join(here, 'subtitles.ko.srt')) if os.path.exists(p))
for b in re.split(r'\n\s*\n', open(srt, encoding='utf-8-sig').read().strip()):
    L = [l for l in b.split('\n') if l.strip()]
    if len(L) >= 3:
        m = re.match(r'(\d+):(\d+):(\d+),(\d+)', L[1])
        lines.append((int(m[1])*3600+int(m[2])*60+int(m[3])+int(m[4])/1000, ' '.join(L[2:])))
strength = np.interp(beats, t_frames, onset)
def bar_pos(t, k):
    i = bisect.bisect_right(beats, t) - 1; i = max(0, min(i, len(beats) - 2))
    return ((i - k) % 4) + (t - beats[i]) / T
best_k = None
for k in range(4):
    on = float(strength[k::4].mean()) / float(strength.mean())
    # 歌詞行の開始が小節頭(0拍)またはその直前(3.5拍以降)に来る割合
    pos = np.array([bar_pos(t, k) for t, _ in lines])
    head = float(((pos < 0.6) | (pos > 3.4)).mean())
    score = on + head
    print('phase %d: 拍の強さ %.2f  行頭が小節頭付近 %.0f%%  score %.2f' % (k, on, head * 100, score))
    if best_k is None or score > best_k[0]: best_k = (score, k)
k = best_k[1]
bars = [round(float(t), 3) for t in beats[k::4]]
# 繰り返し歌詞の一貫性チェック(同じ本文の行が同じ拍位置に来るか)
by = {}
for t, txt in lines:
    by.setdefault(txt, []).append(round(bar_pos(t, k), 2))
spread = [max(v) - min(v) for v in by.values() if len(v) > 1]
out = {'bpm': round(bpm, 3), 'beat_interval': round(T, 5), 'offset': round(float(ph), 4), 'phase': k, 'method': ('beat_track' if '--track' in sys.argv else 'constant-tempo grid fit'),
       'beats': [round(float(t), 3) for t in beats], 'bars': bars, 'source': os.path.basename(wav)}
json.dump(out, open(os.path.join(here, 'beats.json'), 'w'), indent=1)
print('BPM %.3f (beat_track %.1f → 等間隔) | 拍 %d | 小節 %d | 位相 %d | 最初の小節頭 %.2fs' % (bpm, tempo0 if np.isscalar(tempo0) else tempo0[0], len(beats), len(bars), k, bars[0]))
if spread: print('繰り返し歌詞の拍位置のばらつき(拍): 最大 %.2f, 平均 %.2f  (0.25以下なら一貫)' % (max(spread), sum(spread)/len(spread)))
for txt, v in by.items():
    if len(v) > 1: print('  %-22s %s' % (txt[:22], v))
