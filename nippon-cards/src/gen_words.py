# -*- coding: utf-8 -*-
import json, os, re, sys
import fugashi
from lemma_meanings import MEANINGS

tagger = fugashi.Tagger()
KANJI = re.compile(r'[一-鿿々]')

KJ = {}
for ln in open('kanji.txt', encoding='utf-8'):
    ln = ln.strip()
    if not ln or ln.startswith('#'):
        continue
    ch, hun = ln.split('|', 1)
    KJ[ch.strip()] = hun.strip().split()[-1]

by_lemma = {}
lemma_order = []
in_ctx = {}          # 표제어 → {본문 표기: [(접사 여부, 읽힌 가나)]}
for s in json.load(open('segs.json', encoding='utf-8')):
    if True:
        for w in tagger(s['ja']):
            surf = w.surface
            if not KANJI.search(surf):
                continue
            pos1 = w.feature.pos1
            if pos1 in ('助詞', '助動詞', '記号', '補助記号'):
                continue
            lemma = w.feature.lemma or surf
            if lemma not in by_lemma:
                by_lemma[lemma] = []
                lemma_order.append(lemma)
            if surf not in by_lemma[lemma]:
                by_lemma[lemma].append(surf)
            _kana = w.feature.kana or w.feature.pron          # 문맥에서 실제로 읽힌 소리
            if _kana:                                          # 접사 용례는 뒤로 미룬다(世界中의 中=チュウ 따위)
                _affix = pos1 in ('接尾辞', '接頭辞')
                in_ctx.setdefault(lemma, {}).setdefault(surf, []).append((_affix, _kana))


def headword_of(lemma):
    return lemma.split('-')[0]


import jaconv


READING_OVERRIDE = {'離す': 'はなす', '1人': 'ひとり', '行う': 'いく', '抱く': 'だく', '描く': 'かく', '君': 'きみ', '私': 'わたし', '御前': 'おまえ', '御飯': 'ごはん', '御腹': 'おなか', '何': 'なに', '人陰': 'かげ', '瞬間': 'とき', '時々': 'ときどき', '主': 'しゅ', '民': 'たみ'}


def reading_of(headword, lemma=None):
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
    return ''.join(jaconv.kata2hira(t.feature.kana or t.feature.pron or t.surface) for t in toks)


EXTRA = []  # 형태소 분석이 못 잡는 고유명사
missing_meaning = []
lines = []
for lemma in lemma_order:
    stems = by_lemma[lemma]
    headword = headword_of(lemma)
    if lemma not in MEANINGS:
        missing_meaning.append(lemma)
        continue
    meaning = MEANINGS[lemma]
    reading = reading_of(headword, lemma)
    hanja = ''.join(KJ.get(c, '?') for c in headword if KANJI.match(c))
    stem_field = ','.join(stems)
    lines.append(f'{stem_field}|{headword}|{reading}|{meaning}|{hanja}')

if missing_meaning:
    print('MEANINGS 누락:', missing_meaning, file=sys.stderr)

for stem, head, rd, mean in EXTRA:
    hanja = ''.join(KJ.get(c, '?') for c in head if KANJI.match(c))
    lines.append(f'{stem}|{head}|{rd}|{mean}|{hanja}')

print('# 한자어 사전. 형식: 어간(쉼표로 여럿)|표제(사전형)|일본어 독음|뜻|한국 한자음  (자동생성)')
for ln in lines:
    print(ln)
