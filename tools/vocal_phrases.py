#!/usr/bin/env python3
"""노래가 불리는 구간(프레이즈)의 시각만 → <앱>/src/phrases.json — 「📝 내 가사」의 자동 줄 맞추기용.

자막이 없는 곡에서 사용자가 정식 가사 사이트에서 복사해 붙여 넣은 가사(그 브라우저에만 저장)를
노래 구간에 자동으로 배정할 때 쓴다. 가사 글자는 다루지 않는다 — 목소리 트랙(demucs vocals)의
말소리 감지(Silero VAD) 구간 [시작, 끝] 만 저장한다.

사용: .venv/bin/python tools/vocal_phrases.py <앱> <vocals.wav> [--silence-ms 300]
"""
import argparse
import json
import os

from faster_whisper.audio import decode_audio
from faster_whisper.vad import VadOptions, get_speech_timestamps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 16000
ap = argparse.ArgumentParser()
ap.add_argument('app'); ap.add_argument('wav'); ap.add_argument('--silence-ms', type=int, default=300)
a = ap.parse_args()
audio = decode_audio(a.wav)
ts = get_speech_timestamps(audio, VadOptions(min_silence_duration_ms=a.silence_ms, speech_pad_ms=100, threshold=.4))
ph = [[round(t['start'] / SR, 2), round(t['end'] / SR, 2)] for t in ts if (t['end'] - t['start']) / SR >= .8]
json.dump(ph, open(os.path.join(ROOT, a.app.strip('/'), 'src', 'phrases.json'), 'w'), indent=0)
print(f'{a.app}: 노래 구간 {len(ph)} ({ph[0][0]}~{ph[-1][1]}초) → src/phrases.json')
