#!/usr/bin/env python3
"""뒤에서부터 쌓는 섀도잉(백 빌드업)용 덩어리 시각 → <앱>/src/shadow.json

대사 하나를 「끝 덩어리 → 끝 두 덩어리 → … → 전체」로 끊어 들려주려면 대사 안 덩어리의 시작 시각이 필요하다.
· 덩어리: 앱의 읽기(ko.txt 셋째 칸)는 어절마다 띄어 써 있다 — 그 띄어쓰기가 경계. 원문 글자 위치는
  wordtap/src/furigana.py 의 ruby()(원문 한자 ↔ 읽기 맞추기)로 찾는다. 덩어리가 많으면 최대 MAX 단계로 묶는다(모라 수 고르게).
· 시각: 대사 구간 소리를 faster-whisper(단어 시각)로 다시 듣고, 인식 글자(가나)와 내 읽기를 맞대어(difflib)
  경계 글자가 들린 시각을 찾는다. 잘 안 맞으면(일치 < MIN_RATIO) 모라 수 비례로 추정한다.
출력: {"<id>": {"t": [덩어리 시작 초 ...], "x": [원문 글자 위치 ...], "how": "asr"|"ratio"}} — 첫 덩어리는 대사 시작.
음원은 리포에 넣지 않는다(yt-dlp 로 받아 경로를 준다).

사용: .venv/bin/python tools/shadow_chunks.py <앱> <음원.wav> [--model medium]
"""
import argparse
import difflib
import importlib.util
import io
import json
import os
import re

import jaconv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX, MIN_RATIO, SR = 4, .55, 16000
spec = importlib.util.spec_from_file_location('furigana', os.path.join(ROOT, 'wordtap', 'src', 'furigana.py'))
furigana = importlib.util.module_from_spec(spec); spec.loader.exec_module(furigana)
KANA = lambda s: re.sub(r'[^ぁ-ゖー]', '', jaconv.kata2hira(s or ''))
_TG = None


def kana_of(w):
    """인식된 단어(한자 섞임) → 가나. 형태소 분석의 읽기"""
    global _TG
    if _TG is None:
        import fugashi; _TG = fugashi.Tagger()
    return KANA(''.join(jaconv.kata2hira(t.feature.kana or t.surface) for t in _TG(w)))


def rows_of(path, n):
    if not os.path.exists(path): return []
    return [[x.strip() for x in ln.rstrip('\n').split('|')] for ln in io.open(path, encoding='utf-8')
            if not ln.startswith('#') and ln.count('|') >= n - 1]


def text_index_of_reading(ja, rd):
    """읽기(띄어쓰기 없는) 글자 위치 → 원문 글자 위치 표. 못 맞추면 None"""
    r = furigana.ruby(ja, rd)
    if not r: return None
    out, ti = [], 0
    for base, rdg in r:
        piece = rdg if rdg else KANA(base)
        for j in range(len(piece)): out.append(ti + (0 if rdg else min(j, len(base) - 1)))
        ti += len(base)
    return out


def merge(chunks, maxn):
    """덩어리(모라 수 목록)를 maxn 개 이하로 — 뒤에서부터 쌓으니 끝쪽을 잘게 둔다"""
    groups = [[c] for c in range(len(chunks))]
    while len(groups) > maxn:
        best = min(range(len(groups) - 1), key=lambda g: sum(chunks[i] for i in groups[g] + groups[g + 1]))
        groups[best:best + 2] = [groups[best] + groups[best + 1]]
    return [g[0] for g in groups]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('app'); ap.add_argument('wav'); ap.add_argument('--model', default='medium')
    a = ap.parse_args()
    from faster_whisper import WhisperModel
    from faster_whisper.audio import decode_audio
    S = os.path.join(ROOT, a.app, 'src')
    segs = json.load(io.open(os.path.join(S, 'segs.json'), encoding='utf-8'))
    ko = {int(q[0]): q for q in rows_of(os.path.join(S, 'ko.txt'), 3) if q[0].isdigit()}
    fixes = {int(q[0]): q[1] for q in rows_of(os.path.join(S, 'fixes.txt'), 2) if q[0].isdigit()}
    audio = decode_audio(a.wav); m = WhisperModel(a.model, device='cpu', compute_type='int8')
    out, n_asr, n_ratio, n_one = {}, 0, 0, 0
    for x in sorted(segs, key=lambda x: x['s']):
        i, s, e = x['id'], x['s'], x['e']
        ja, rd = fixes.get(i, x['ja']), (ko.get(i) or ['', '', ''])[2]
        parts = [KANA(p) for p in rd.split() if KANA(p)]
        if len(parts) < 2: n_one += 1; continue
        starts = merge([len(p) for p in parts], MAX)                       # 덩어리 번호(읽기 어절 기준)
        cum = [0]
        for p in parts: cum.append(cum[-1] + len(p))
        rpos = [cum[k] for k in starts]                                    # 덩어리 시작의 읽기 글자 위치
        full = ''.join(parts)
        tmap = text_index_of_reading(ja, rd)
        xs = [tmap[min(p, len(tmap) - 1)] if tmap else round(p / max(1, len(full)) * len(ja)) for p in rpos]
        # 소리: 인식 가나 + 글자별 시각
        off = max(0, s - .15); clip = audio[int(off * SR):int((e + .15) * SR)]
        r, _ = m.transcribe(clip, language='ja', beam_size=5, word_timestamps=True, condition_on_previous_text=False,
                            initial_prompt=ja[:60])
        ak, at = '', []
        for seg in r:
            for w in seg.words or []:
                k = kana_of(w.word)
                if not k: continue
                for j in range(len(k)): at.append(off + w.start + (w.end - w.start) * j / len(k))
                ak += k
        sm = difflib.SequenceMatcher(None, full, ak, autojunk=False)
        ts = None
        if ak and sm.ratio() >= MIN_RATIO:
            pos = {}
            for blk in sm.get_matching_blocks():
                for j in range(blk.size): pos[blk.a + j] = blk.b + j
            ts = []
            for p in rpos:
                q = next((pos[p2] for p2 in range(p, min(len(full), p + 4)) if p2 in pos), None)
                ts.append(at[q] if q is not None else None)
        if ts and all(t is not None for t in ts[1:]) and all(b > a2 + .08 for a2, b in zip([s] + ts[1:], ts[1:])):
            ts[0] = s; how = 'asr'; n_asr += 1
        else:
            ts = [s + (e - s) * p / len(full) for p in rpos]; how = 'ratio'; n_ratio += 1
        out[str(i)] = {'t': [round(t, 2) for t in ts], 'x': xs, 'how': how}
    json.dump(out, open(os.path.join(S, 'shadow.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f'{a.app}: 덩어리 대사 {len(out)} (음성 인식 {n_asr} · 비율 추정 {n_ratio}) · 한 덩어리라 제외 {n_one} → src/shadow.json')


if __name__ == '__main__':
    main()
