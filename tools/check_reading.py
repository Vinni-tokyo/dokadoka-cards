#!/usr/bin/env python3
"""가사 줄의 「내가 적은 읽기」와 「기계가 읽는 소리」를 맞대 본다.

읽어주기 음원은 한자가 섞인 원문을 그대로 합성한다. 그래서 落葉(おちば)처럼
기계가 다르게 읽는 한자가 있으면, 화면의 읽기와 실제 소리가 어긋난다.
이 도구는 어긋나는 낱말만 뽑아 준다 — 고칠 것은 <앱>/src/tts_fix.txt 에 적는다.

기계 읽기는 형태소 분석기(unidic)로 구한다. 음성 합성기와 같은 물건은 아니지만
「한자를 사전대로 읽는다」는 점이 같아서, 어긋나는 자리를 거의 그대로 짚어 준다.

사용: .venv/bin/python tools/check_reading.py <앱폴더> [...]
"""
import io
import os
import re
import sys

import fugashi
import jaconv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tagger = fugashi.Tagger()
KANA = re.compile(r'[ぁ-ゖ]')


def norm(s):
    """견줄 수 있게: 가타카나→히라가나, 라틴 글자·공백·기호를 뗀다"""
    s = jaconv.kata2hira(s or '')
    return re.sub(r'[^ぁ-ゖー]', '', s)


def line_kana(ja):
    return ''.join(jaconv.kata2hira(t.feature.kana or t.feature.pron or t.surface) for t in tagger(ja))


def check(app):
    src = os.path.join(ROOT, app, 'src')
    lines = [x for x in io.open(os.path.join(src, 'lyrics.txt'), encoding='utf-8').read().split('\n')
             if x.strip() and not x.startswith('#')]
    mine = {}
    for ln in io.open(os.path.join(src, 'ko.txt'), encoding='utf-8'):
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        p = ln.split('|')
        mine[int(p[0])] = p[2]

    fix = set()
    fixp = os.path.join(src, 'tts_fix.txt')
    if os.path.exists(fixp):
        for ln in io.open(fixp, encoding='utf-8'):
            ln = ln.strip()
            if ln and not ln.startswith('#'):
                fix.add(ln.split('|')[0])

    bad = 0
    for i, ja in enumerate(lines, 1):
        if norm(line_kana(ja)) == norm(mine.get(i, '')):
            continue
        # 어긋난 낱말만 짚는다
        hits = []
        for t in tagger(ja):
            surf = t.surface
            if not re.search(r'[一-鿿々]', surf):
                continue
            k = jaconv.kata2hira(t.feature.kana or t.feature.pron or surf)
            if norm(k) and norm(k) not in norm(mine.get(i, '')):
                hits.append(f'{surf}→기계 {k}' + ('  (tts_fix 있음)' if surf in fix else ''))
        if hits:
            bad += 1
            print(f'  {i:>3} {ja}')
            print(f'      내 읽기: {mine.get(i, "—")}')
            print(f'      어긋남 : {" · ".join(hits)}')
    print(f'{app}: {len(lines)}줄 중 {bad}줄 어긋남')
    return bad


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    n = 0
    for a in sys.argv[1:]:
        n += check(a.strip('/'))
    sys.exit(1 if n else 0)
