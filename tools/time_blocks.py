#!/usr/bin/env python3
"""글자 없는 시간 구간 블록 → <앱>/src/time_blocks.json — 대사 블록 연습의 「🎵 오프닝 · 🎵 엔딩 · 📺 마지막 구간」.

· 노래: 자막(subtitles.srt)의 ♪ 줄에서 시작·끝 시각만 가져온다. 가사 글자는 저장하지 않는다
  (가사는 작사가의 저작물 — 페이지에 싣지 않고, 보고 싶으면 영상 플레이어의 자막(CC)으로 본다).
  영상 앞 절반이면 오프닝, 뒤 절반이면 엔딩(오프닝 앞에 짧은 도입 대사가 있는 화가 있어 「첫 대사보다 앞」으로는 못 가른다).
· 자막이 끝난 뒤(영상 끝까지) 구간: 말소리 감지(faster-whisper 의 Silero VAD)로 말 구간 시각만 잡는다. 받아쓰지 않는다.
출력: [{"s": 초, "e": 초, "kind": "op"|"ed"|"ins"|"tail"}, ...]

사용: .venv/bin/python tools/time_blocks.py <앱> <음원.wav>
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 16000


def cues(path):
    out = []
    for b in re.split(r'\n\s*\n', io.open(path, encoding='utf-8-sig').read().strip()):
        L = b.split('\n')
        m = re.findall(r'(\d+):(\d+):(\d+),(\d+)', L[1]) if len(L) > 2 else []
        if len(m) < 2: continue
        f = lambda g: int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 1000
        out.append((f(m[0]), f(m[1]), '♪' in ' '.join(L[2:])))
    return out


def main():
    app, wav = sys.argv[1].strip('/'), sys.argv[2]
    S = os.path.join(ROOT, app, 'src')
    C = cues(os.path.join(S, 'subtitles.srt'))
    from faster_whisper.audio import decode_audio
    audio = decode_audio(wav); half = len(audio) / SR / 2
    blocks = []
    for s, e, song in C:
        if not song: continue
        kind = 'op' if s < half else 'ed'
        if blocks and blocks[-1]['kind'] == kind and s - blocks[-1]['e'] < .15 and e - blocks[-1]['s'] < 1.2:
            blocks[-1]['e'] = round(e, 2); continue                     # 겹쳐 쪼개진 짧은 큐는 잇는다
        blocks.append({'s': round(s, 2), 'e': round(e, 2), 'kind': kind})
    for a, b in zip(blocks, blocks[1:]):                                 # 겹치면 다음 시작에서 자른다
        if a['e'] > b['s']: a['e'] = b['s']
    # 자막이 끝난 뒤: 말소리 구간(시각만)
    from faster_whisper.vad import VadOptions, get_speech_timestamps
    end_sub = max(e for s, e, _ in C)
    tail = audio[int(end_sub * SR):]
    ts = get_speech_timestamps(tail, VadOptions(min_silence_duration_ms=350, speech_pad_ms=120))
    for t in ts:
        s, e = end_sub + t['start'] / SR, end_sub + t['end'] / SR
        if e - s < .6: continue
        blocks.append({'s': round(s, 2), 'e': round(e, 2), 'kind': 'tail'})
    json.dump(blocks, open(os.path.join(S, 'time_blocks.json'), 'w', encoding='utf-8'), indent=0)
    from collections import Counter
    print(f'{app}: 시간 블록 {len(blocks)} ' + str(dict(Counter(b["kind"] for b in blocks))) +
          f' · 자막 끝 {end_sub:.0f}초 · 영상 끝 {len(audio) / SR:.0f}초 → src/time_blocks.json')


if __name__ == '__main__':
    main()
