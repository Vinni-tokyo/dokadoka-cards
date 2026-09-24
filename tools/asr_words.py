#!/usr/bin/env python3
"""음원에서 단어 시각(words.json)과 구간별 받아쓰기(transcript.txt)를 뽑는다.

자막 트랙이 없는 곡의 줄 시각을 맞출 때 쓴다. words.json 은 <앱>/src/align.py 가 읽고,
transcript.txt 는 가사가 실제로 어떤 차례로 불렸는지(반복·생략) 사람이 확인하는 데 쓴다.

사용: .venv/bin/python tools/asr_words.py <wav> <출력 폴더> [--model medium]
"""
import argparse
import json
import os

from faster_whisper import WhisperModel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('wav'); ap.add_argument('out'); ap.add_argument('--model', default='medium')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    model = WhisperModel(a.model, device='cpu', compute_type='int8')
    # vad_filter 는 쓰지 않는다 — 반주 위의 노래를 「말이 아니다」로 보고 통째로 버린다(다섯 곡 중 둘이 0단어).
    segs, info = model.transcribe(a.wav, language='ja', beam_size=5, word_timestamps=True,
                                  condition_on_previous_text=False)
    words, lines = [], []
    for s in segs:
        lines.append(f'{s.start:7.2f} {s.end:7.2f}  {s.text.strip()}')
        for w in (s.words or []):
            words.append({'w': w.word.strip(), 's': round(w.start, 3), 'e': round(w.end, 3)})
    json.dump(words, open(os.path.join(a.out, 'words.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    open(os.path.join(a.out, 'transcript.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(f'{a.wav}: 단어 {len(words)} · 구간 {len(lines)} → {a.out}')


if __name__ == '__main__':
    main()
