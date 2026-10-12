#!/usr/bin/env python3
"""한국어·일본어(등)가 섞인 말 영상을 받아쓴다 — 말 구간마다 언어를 판별해 그 언어로 받아쓴다.

자막이 없는 「한국어 설명 + 일본어 문장」 영상(haenali-cards)에서 일본어로 말한 곳만 찾을 때 쓴다.
한 언어로 통째 받아쓰면 다른 언어 구간이 엉뚱하게 나온다:
  · 한국어로 고정하면 일본어 문장이 한글 소리로 적힌다(なるほど → 나루호도).
  · large-v3 에 일본어를 강제하면 한국어 설명을 일본어로 「번역」해 버린다.
그래서 (1) 말 구간(VAD)을 잡고 (2) 구간마다 언어를 판별해 (3) 그 언어로 단어 시각까지 받아쓴다.
판별이 애매한 구간(둘째 언어 확률 > --both)은 두 언어로 다 받아써 사람이 고르게 한다.

출력: <out>/mixed.json  [{s, e, p: {언어: 확률}, res: {언어: {text, words:[{w,s,e}]}}}]
      <out>/mixed.txt   사람이 읽는 목록(시각 · 판별 언어 · 받아쓰기)
--recheck 언어 모델 : 그 언어로 판별된 구간만 더 큰 모델로 짧게 다시 받아써 res[언어+'+'] 에 넣는다
                      (haenali: 일본어 구간만 large-v3 로 — 앞부분을 건너뛰지 않게 힌트 문장 없이, 짧은 창으로).

사용: .venv/bin/python tools/asr_mixed.py <wav> <출력 폴더> [--langs ko,ja] [--model medium] [--both 0.15]
                                          [--recheck ja large-v3]
"""
import argparse
import json
import os

from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio

SR = 16000


def words_of(segs, off):
    return [{'w': w.word, 's': round(off + w.start, 2), 'e': round(off + w.end, 2)} for x in segs for w in (x.words or [])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('wav'); ap.add_argument('out')
    ap.add_argument('--langs', default='ko,ja'); ap.add_argument('--model', default='medium')
    ap.add_argument('--both', type=float, default=.15)
    ap.add_argument('--recheck', nargs=2, metavar=('LANG', 'MODEL'))
    a = ap.parse_args()
    langs = a.langs.split(',')
    os.makedirs(a.out, exist_ok=True)
    m = WhisperModel(a.model, device='cpu', compute_type='int8')
    audio = decode_audio(a.wav)
    # 1) 말 구간 — 첫 언어로 한 번 훑어 경계만 얻는다(vad: 말 영상이라 켜도 된다. 노래에는 쓰지 말 것)
    segs, _ = m.transcribe(audio, language=langs[0], beam_size=1, vad_filter=True, condition_on_previous_text=False)
    spans = [(s.start, s.end) for s in segs]
    print('말 구간', len(spans), flush=True)
    out = []
    for i, (s, e) in enumerate(spans):
        off = max(0, s - .2); clip = audio[int(off * SR):int((e + .2) * SR)]
        _, _, allp = m.detect_language(clip)
        p = {l: round(dict(allp).get(l, 0), 3) for l in langs}
        top = max(p, key=p.get)
        res = {}
        for L in [top] + [l for l in langs if l != top and p[l] > a.both]:
            r, _ = m.transcribe(clip, language=L, beam_size=5, word_timestamps=True, condition_on_previous_text=False)
            r = list(r)
            res[L] = {'text': ''.join(x.text for x in r).strip(), 'words': words_of(r, off)}
        out.append({'s': round(s, 2), 'e': round(e, 2), 'p': p, 'top': top, 'res': res})
        if i % 20 == 0: print(f'{i}/{len(spans)} {s:7.1f} {top} {res[top]["text"][:40]}', flush=True)
    if a.recheck:
        L, big = a.recheck
        bm = WhisperModel(big, device='cpu', compute_type='int8')
        for x in out:
            if x['top'] != L: continue
            off = max(0, x['s'] - .3); clip = audio[int(off * SR):int((x['e'] + .3) * SR)]
            r, _ = bm.transcribe(clip, language=L, beam_size=5, word_timestamps=True, condition_on_previous_text=False)
            r = list(r)
            x['res'][L + '+'] = {'text': ''.join(y.text for y in r).strip(), 'words': words_of(r, off)}
        print('다시 받아씀:', sum(1 for x in out if L + '+' in x['res']), '구간', flush=True)
    json.dump(out, open(os.path.join(a.out, 'mixed.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    with open(os.path.join(a.out, 'mixed.txt'), 'w', encoding='utf-8') as f:
        for x in out:
            t = x['res'].get(x['top'] + '+', x['res'][x['top']])['text']
            f.write(f"{int(x['s'] // 60):02d}:{x['s'] % 60:05.2f} {x['top']} {max(x['p'].values()):.2f} | {t}\n")
    print(f'{a.wav}: 구간 {len(out)} · ' + ' · '.join(f'{l} {sum(1 for x in out if x["top"] == l)}' for l in langs) + f' → {a.out}')


if __name__ == '__main__':
    main()
