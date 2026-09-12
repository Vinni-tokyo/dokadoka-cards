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
for ep in sorted(int(d[2:]) for d in os.listdir('.') if d.startswith('ep') and d[2:].isdigit()):
    segs = json.load(open(f'ep{ep}/segs.json', encoding='utf-8'))
    for s in segs:
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


def headword_of(lemma):
    return lemma.split('-')[0]


import jaconv


READING_OVERRIDE = {'御前': 'おまえ'}


def reading_of(headword):
    if headword in READING_OVERRIDE:
        return READING_OVERRIDE[headword]
    toks = list(tagger(headword))
    return ''.join(jaconv.kata2hira(t.feature.kana or t.feature.pron or t.surface) for t in toks)


missing_meaning = []
lines = []
for lemma in lemma_order:
    stems = by_lemma[lemma]
    headword = headword_of(lemma)
    if lemma not in MEANINGS:
        missing_meaning.append(lemma)
        continue
    meaning = MEANINGS[lemma]
    reading = reading_of(headword)
    hanja = ''.join(KJ.get(c, '?') for c in headword if KANJI.match(c))
    stem_field = ','.join(stems)
    lines.append(f'{stem_field}|{headword}|{reading}|{meaning}|{hanja}')

if missing_meaning:
    print('MEANINGS 누락:', missing_meaning, file=sys.stderr)

print('# 한자어 사전. 형식: 어간(쉼표로 여럿)|표제(사전형)|일본어 독음|뜻|한국 한자음  (자동생성)')
for ln in lines:
    print(ln)
