#!/usr/bin/env python3
"""「듣고 탭」 단어 게임 — 일본어 앱들의 단어를 모아 wordtap/index.html 과 단어 음원을 만든다.

재료: */src/words.txt (어간|표제|읽기|뜻|한자음) — 일본어 앱이 만든 한자어 사전.
      노래 앱의 src/subtitles.srt + build.py 의 VID — 예문 줄과 원곡 시각.
순서: 여러 앱에 나온 단어일수록 먼저(자주 나오는 단어부터 익힌다).
음원: 화면에 보이는 히라가나 읽기를 edge-tts 로 읽힌다(한자를 읽히면 主→ぬし 처럼 틀린다).
      audio/<sha1>.mp3 — 이미 있으면 건너뛴다. 음량은 tools/normalize_audio 로 맞춘다.

사용: ../../.venv/bin/python build.py            (음원까지)
      ../../.venv/bin/python build.py --no-audio  (데이터·페이지만)
"""
import asyncio
import collections
import glob
import hashlib
import io
import json
import os
import re
import sys

S = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(S)
ROOT = os.path.dirname(APP)
ADIR = os.path.join(APP, 'audio')
VOICE, RATE = 'ja-JP-NanamiNeural', '-10%'
BAD_MEANING = re.compile(r'불명|^\s*$|\?')


def srt(p):
    out = []
    for b in io.open(p, encoding='utf-8').read().strip().split('\n\n'):
        L = b.split('\n')
        if len(L) < 3: continue
        m = re.findall(r'(\d+):(\d+):(\d+),(\d+)', L[1])
        if len(m) < 2: continue
        f = lambda g: int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 1000
        out.append((round(f(m[0]), 2), round(f(m[1]), 2), ' '.join(L[2:]).strip()))
    return out


HUB = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()


def title_of(app):
    """관문 페이지의 제목 — 「秦基博 「ひまわりの約束」」 같은 꼴"""
    m = re.search(r"href:'" + re.escape(app) + r"/[^']*'.*?title:(['\"])(.*?)\1", HUB, re.S)
    t = m.group(2) if m else app.replace('-cards', '')
    return re.sub(r'\s*[(（][^)）]*[)）]\s*$', '', t).replace(' — 가사로 배우기', '').strip()


KAN = re.compile(r'[一-鿿々]')


def found(stem, text):
    """stem 이 text 안에 「따로 선 단어」로 있는가 — 한자 한두 글자 단어가 더 긴 한자어 속에서 걸리지 않게"""
    i = text.find(stem)
    while i >= 0:
        before = text[i - 1] if i else ''
        after = text[i + len(stem)] if i + len(stem) < len(text) else ''
        if not (KAN.match(stem[0]) and KAN.match(before)) and not (KAN.match(stem[-1]) and KAN.match(after)):
            return True
        i = text.find(stem, i + 1)
    return False


def collect():
    words = collections.OrderedDict()            # 표제 → 단어
    for f in sorted(glob.glob(os.path.join(ROOT, '*-cards', 'src', 'words.txt'))):
        app = f.split(os.sep)[-3]
        src = os.path.dirname(f)
        lines, vid = [], ''
        if os.path.exists(os.path.join(src, 'subtitles.srt')):
            b = io.open(os.path.join(src, 'build.py'), encoding='utf-8').read()
            m = re.search(r"VID\s*=\s*'([^']+)'", b)
            if m: vid, lines = m.group(1), srt(os.path.join(src, 'subtitles.srt'))
        song = title_of(app) if vid else ''
        for ln in io.open(f, encoding='utf-8'):
            if ln.startswith('#') or '|' not in ln: continue
            p = ln.rstrip('\n').split('|')
            if len(p) < 4: continue
            stems, head, rd, mean = p[0].split(','), p[1], p[2], p[3]
            if BAD_MEANING.search(mean) or not rd or not re.search(r'[ぁ-ゖ]', rd): continue
            w = words.setdefault(head, {'w': head, 'r': rd, 'm': mean, 'apps': [], 'ex': None})
            if app not in w['apps']: w['apps'].append(app)
            if w['ex'] is None and lines:
                for s, e, t in lines:
                    if any(st and found(st, t) for st in stems):
                        w['ex'] = {'t': t, 'v': vid, 's': s, 'e': e, 'song': song}
                        break
    # 뜻이 똑같은 단어끼리는 보기가 헷갈리지 않게 그대로 둔다(보기 고를 때 같은 뜻은 뺀다)
    ws = sorted(words.values(), key=lambda w: (-len(w['apps']), w['ex'] is None))
    for i, w in enumerate(ws):
        w['id'] = i; w['n'] = len(w['apps']); del w['apps']
        w['a'] = hashlib.sha1(('r:' + w['r']).encode('utf-8')).hexdigest()[:14] + '.mp3'
    return ws


async def make_audio(ws):
    import edge_tts
    os.makedirs(ADIR, exist_ok=True)
    todo = [w for w in ws if not os.path.exists(os.path.join(ADIR, w['a']))]
    print(f'음원 새로 만들 것 {len(todo)} / {len(ws)}')
    sem = asyncio.Semaphore(6)

    async def one(w):
        async with sem:
            for k in range(3):
                try:
                    await edge_tts.Communicate(w['r'], VOICE, rate=RATE).save(os.path.join(ADIR, w['a'])); return True
                except Exception:
                    await asyncio.sleep(1.5 * (k + 1))
            print('  실패:', w['w']); return False
    res = await asyncio.gather(*[one(w) for w in todo])
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from normalize_audio import normalize_dir
    print('음량 정규화:', normalize_dir(ADIR), '개 · 실패', res.count(False))


def main():
    ws = collect()
    if '--no-audio' not in sys.argv:
        asyncio.run(make_audio(ws))
    for w in ws:
        if not os.path.exists(os.path.join(ADIR, w['a'])): w['a'] = ''
    data = [{k: w[k] for k in ('id', 'w', 'r', 'm', 'n', 'a', 'ex')} for w in ws]
    tpl = io.open(os.path.join(S, 'tpl.html'), encoding='utf-8').read()
    html = tpl.replace('/*__WORDS__*/[]', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    io.open(os.path.join(APP, 'index.html'), 'w', encoding='utf-8').write(html)
    ex = sum(1 for w in ws if w['ex'])
    print(f'단어 {len(ws)} · 여러 곡(3+) {sum(1 for w in ws if w["n"] >= 3)} · 원곡 예문 {ex} · '
          f'음원 {sum(1 for w in ws if w["a"])} · index.html {os.path.getsize(os.path.join(APP, "index.html")) / 1024:.0f} KB')


if __name__ == '__main__':
    main()
