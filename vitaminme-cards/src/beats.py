#!/usr/bin/env python3
"""公式MVの音声から BPM と小節(4/4)の頭を求めて beats.json に書く。
   音声はリポに入れない: yt-dlp -x --audio-format wav で scratch に落としたファイルのパスを引数で渡す。
   使い方: .venv/bin/python src/beats.py <wav> [--offset 秒]   (MV の音声と字幕は同じ動画なので時刻軸は共通)"""
import sys, json, os, numpy as np, librosa, re
wav = sys.argv[1]
y, sr = librosa.load(wav, sr=22050, mono=True)
onset = librosa.onset.onset_strength(y=y, sr=sr)
tempo, beats = librosa.beat.beat_track(onset_envelope=onset, sr=sr, units='frames', trim=False)
bt = librosa.frames_to_time(beats, sr=sr)
tempo = float(np.atleast_1d(tempo)[0])
# 拍の間隔から BPM を再推定(中央値)
ibi = np.median(np.diff(bt)); bpm = 60.0 / ibi
# 小節の頭 = 4拍ごと。位相(0..3)は「その拍のオンセット強度の平均が最大」かつ「歌詞行の開始と最も合う」ものを選ぶ
here = os.path.dirname(os.path.abspath(__file__))
line_starts = []
for b in re.split(r'\n\s*\n', open(os.path.join(here, 'subtitles.ko.srt'), encoding='utf-8-sig').read().strip()):
    L = [l for l in b.split('\n') if l.strip()]
    if len(L) >= 3:
        m = re.match(r'(\d+):(\d+):(\d+),(\d+)', L[1]); line_starts.append(int(m[1])*3600+int(m[2])*60+int(m[3])+int(m[4])/1000)
strength = onset[beats]
best = None
for ph in range(4):
    bars = bt[ph::4]
    s_mean = float(strength[ph::4].mean())
    # 各歌詞行の開始が最寄りの小節頭からどれだけ離れているか(拍の何割か)
    dist = np.array([min(abs(bars - t)) for t in line_starts]) / ibi
    near = float((dist < 0.35).mean())
    score = s_mean / strength.mean() + near
    print('phase %d: onset %.2f  行頭が小節頭に近い割合 %.0f%%  score %.2f' % (ph, s_mean, near*100, score))
    if best is None or score > best[0]: best = (score, ph, bars)
_, ph, bars = best
bars = [round(float(t), 3) for t in bars]
out = {'bpm': round(bpm, 2), 'beat_interval': round(float(ibi), 4), 'phase': ph, 'beats': [round(float(t), 3) for t in bt], 'bars': bars, 'source': os.path.basename(wav)}
json.dump(out, open(os.path.join(here, 'beats.json'), 'w'), indent=1)
print('BPM %.2f (librosa tempo %.1f) | 拍 %d | 小節 %d | 位相 %d | 最初の小節頭 %.2fs | 最後 %.2fs' % (bpm, tempo, len(bt), len(bars), ph, bars[0], bars[-1]))
print('歌詞行の開始と最寄り小節頭の差(秒):', ' '.join('%.2f' % min(abs(np.array(bars) - t)) for t in line_starts[:20]))
