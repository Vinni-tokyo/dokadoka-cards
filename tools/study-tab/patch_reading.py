#!/usr/bin/env python3
"""한자어 사전의 일본어 독음을 문맥에서 가져오도록 gen_words.py 를 고친다.

버그: 독음을 낱말 하나만 떼어 형태소 분석기에 다시 넣어 구했다. 그러면 음독이 나온다
(時=じ, 的=まと, 室=むろ, 大=おお). 읽어주기 버튼이 그 가나로 소리를 내므로 잘못 읽어 준다.
고침: 본문에 사전형 그대로 나온 적이 있으면 그때 읽힌 소리를 쓴다. 접사로 쓰인 용례
(世界中의 中=チュウ)보다 자립어 용례를 우선한다.

사용: python3 patch_reading.py <앱폴더>/src/gen_words.py [...]
"""
import io, sys

A_OLD = """            if surf not in by_lemma[lemma]:
                by_lemma[lemma].append(surf)
"""
A_NEW = """            if surf not in by_lemma[lemma]:
                by_lemma[lemma].append(surf)
            _kana = w.feature.kana or w.feature.pron          # 문맥에서 실제로 읽힌 소리
            if _kana:                                          # 접사 용례는 뒤로 미룬다(世界中의 中=チュウ 따위)
                _affix = pos1 in ('接尾辞', '接頭辞')
                in_ctx.setdefault(lemma, {}).setdefault(surf, []).append((_affix, _kana))
"""

B_OLD = """def reading_of(headword):
    if headword in READING_OVERRIDE:
        return READING_OVERRIDE[headword]
    toks = list(tagger(headword))
"""
B_NEW = """def reading_of(headword, lemma=None):
    if headword in READING_OVERRIDE:
        return READING_OVERRIDE[headword]
    # 본문에 사전형 그대로 나온 적이 있으면 그때 읽힌 소리를 쓴다.
    # 낱글자를 떼어 다시 분석하면 음독이 나온다(時=じ, 的=まと 따위).
    cand = (in_ctx.get(lemma) or {}).get(headword)
    if cand:
        from collections import Counter
        free = [k for af, k in cand if not af]                  # 자립어로 쓰인 용례를 우선
        pool = free or [k for _af, k in cand]
        return jaconv.kata2hira(Counter(pool).most_common(1)[0][0])
    toks = list(tagger(headword))
"""


def patch(path):
    s = io.open(path, encoding='utf-8').read()
    if 'in_ctx' in s:
        print(f'skip (이미 적용) {path}')
        return
    for old, new in ((A_OLD, A_NEW), (B_OLD, B_NEW)):
        assert s.count(old) == 1, f'{path}: 앵커 {s.count(old)}개'
        s = s.replace(old, new)
    s = s.replace("by_lemma = {}\nlemma_order = []\n",
                  "by_lemma = {}\nlemma_order = []\nin_ctx = {}          # 표제어 → {본문 표기: [(접사 여부, 읽힌 가나)]}\n")
    s = s.replace("reading = reading_of(headword)", "reading = reading_of(headword, lemma)")
    if "'私': 'わたし'" not in s:                                   # UniDic 기본값 わたくし → 현대 표준
        s = s.replace("READING_OVERRIDE = {", "READING_OVERRIDE = {'私': 'わたし', ", 1)
    io.open(path, 'w', encoding='utf-8').write(s)
    print(f'ok   {path}')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        patch(p)
