#!/usr/bin/env python3
"""frieren-cards 전용 학습 음원 생성기. 사용: ../../.venv/bin/python make_audio.py [ep번호 ...]"""
import asyncio, hashlib, json, os, re, sys
S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(S)

VOICE, MVOICE, RATE = 'ja-JP-NanamiNeural', 'ko-KR-SunHiNeural', '-10%'
MEAN_PREFIX = 'm:'


def akey(t):
    t = re.sub(r'[〜～]', '', t or '')
    t = re.sub(r'[（(][^）)]*[）)]', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def mean_text(t):
    t = re.sub(r'[（(][^）)]*[）)]', '', t or '')
    t = re.sub(r'\s*[·・/]\s*', ', ', t)
    return re.sub(r'\s+', ' ', t).strip(' ,')


def study_of(ep):
    path = os.path.join(ROOT, f'Japanese-Frieren{ep}-Cards.html')
    h = open(path, encoding='utf-8').read()
    m = re.search(r'const STUDY = (\[.*?\]);\s*(?:/\*|\n)', h, re.S)
    return json.loads(m.group(1)) if m else []


async def gen(ep, force):
    import edge_tts
    study = study_of(ep)
    keys = []
    for it in study:
        k = akey(it.get('ja', ''))
        if k and k not in keys:
            keys.append(k)
    mkeys = {}
    for it in study:
        m = akey(it.get('ko', ''))
        if m:
            mkeys[MEAN_PREFIX + m] = mean_text(it.get('ko', ''))
    adir = os.path.join(S, f'ep{ep}', 'audio')
    os.makedirs(adir, exist_ok=True)
    ipath = os.path.join(adir, 'index.json')
    index = json.load(open(ipath, encoding='utf-8')) if os.path.exists(ipath) else {}
    allkeys = list(keys) + list(mkeys)
    todo = []
    for k in allkeys:
        fn = index.get(k) or (hashlib.sha1(k.encode('utf-8')).hexdigest()[:16] + '.mp3')
        index[k] = fn
        if force or not os.path.exists(os.path.join(adir, fn)):
            todo.append((k, fn))
    print(f'ep{ep}: 원문 {len(keys)} · 뜻 {len(mkeys)} · 새로 만들 것 {len(todo)}')
    sem = asyncio.Semaphore(4)

    async def one(k, fn):
        async with sem:
            text, v = (mkeys[k], MVOICE) if k in mkeys else (k, VOICE)
            err = None
            for attempt in range(3):
                try:
                    await edge_tts.Communicate(text, v, rate=RATE).save(os.path.join(adir, fn))
                    return True
                except Exception as e:
                    err = e
                    await asyncio.sleep(1.5 * (attempt + 1))
            print('  실패:', k, err)
            return False

    res = await asyncio.gather(*[one(k, fn) for k, fn in todo])
    for (k, fn), ok in zip(todo, res):
        if not ok:
            index.pop(k, None)
    for k in list(index):
        if k not in allkeys:
            index.pop(k)
    json.dump(index, open(ipath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    size = sum(os.path.getsize(os.path.join(adir, fn)) for fn in index.values() if os.path.exists(os.path.join(adir, fn)))
    print(f'  완료 {sum(1 for r in res if r)}/{len(todo)} · 보유 {len(index)} 파일 · {size/1024:.0f} KB')


if __name__ == '__main__':
    force = '--force' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--force']
    eps = [int(a) for a in args] or [20, 21, 22]
    for ep in eps:
        asyncio.run(gen(ep, force))
