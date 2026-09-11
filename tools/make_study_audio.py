#!/usr/bin/env python3
"""학습 탭(표현·단어)의 로컬 음원을 만든다.  Microsoft 신경망 음성(edge-tts)으로 mp3 를 생성해
<앱>/src/audio/ 에 저장하고 index.json(원문 → 파일명)을 쓴다. build.py 가 이 파일들을 data URI 로 HTML 에 심는다.

  사용법:  .venv/bin/python tools/make_study_audio.py <앱폴더> [<앱폴더> ...]     (예: yubisaki-cards)
           .venv/bin/python tools/make_study_audio.py --all
  옵션:    --voice ja-JP-KeitaNeural   --rate -10%   --force(기존 파일도 다시 생성)

  항목은 빌드된 HTML 의 STUDY(또는 SERIES[].study) 에서 읽으므로 먼저 build.py 를 한 번 돌려 둔다.
  키 = 원문에서 「〜」와 괄호 주석을 뗀 문자열. 앱의 JS(aKey) 와 같은 규칙이어야 한다.
  뜻 음원도 함께 만든다(키 'm:' + 뜻). 「뜻과 함께 듣기」가 쓴다.
  edge-tts 는 온라인 서비스라 인터넷이 필요하다. 이미 있는 파일은 건너뛴다(증분).
"""
import asyncio, glob, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAMILY = {   # 앱 → (원문 필드, 원문 음성, 뜻 필드, 뜻 음성)
    'japanese-cards': ('ja', 'ja-JP-NanamiNeural', 'ko', 'ko-KR-SunHiNeural'),
    'yubisaki-cards': ('ja', 'ja-JP-NanamiNeural', 'ko', 'ko-KR-SunHiNeural'),
    'bokuyaba-cards': ('ja', 'ja-JP-NanamiNeural', 'ko', 'ko-KR-SunHiNeural'),
    'english-cards':  ('en', 'en-US-AvaNeural',    'ko', 'ko-KR-SunHiNeural'),
    'altman-cards':   ('en', 'en-US-AndrewNeural', 'ko', 'ko-KR-SunHiNeural'),
    'feifei-cards':   ('en', 'en-US-AvaNeural',    'ko', 'ko-KR-SunHiNeural'),
    'korean-cards':   ('ko', 'ko-KR-SunHiNeural',  'ja', 'ja-JP-NanamiNeural'),
    'firstlove-cards': ('ja', 'ja-JP-NanamiNeural', 'ko', 'ko-KR-SunHiNeural'),
}
MEAN_PREFIX = 'm:'   # 뜻 음원의 index 키 접두어 (앱 JS 의 aPlay(..., which=1) 와 같은 규칙)

def akey(t):
    t = re.sub(r'[〜～]', '', t or '')
    t = re.sub(r'[（(][^）)]*[）)]', '', t)
    return re.sub(r'\s+', ' ', t).strip()

def mean_text(t):
    """뜻 문자열을 읽기 좋게: '·' '/' 로 나열된 뜻은 쉼표로, 괄호 주석은 뗀다"""
    t = re.sub(r'[（(][^）)]*[）)]', '', t or '')
    t = re.sub(r'\s*[·・/]\s*', ', ', t)
    return re.sub(r'\s+', ' ', t).strip(' ,')

def items_of(app, field):
    htmls = [f for f in glob.glob(os.path.join(ROOT, app, '*.html'))]
    assert htmls, f'{app}: 빌드된 HTML 이 없다. 먼저 build.py 를 돌려라'
    h = open(htmls[0], encoding='utf-8').read()
    out = []
    m = re.search(r'const STUDY = (\[.*?\]);\s*(?:/\*|\n)', h, re.S)
    if m: out += json.loads(m.group(1))
    m = re.search(r'const SERIES = (\[.*?\]);\n', h, re.S)
    if m:
        for s in json.loads(m.group(1)): out += s.get('study', [])
    keys = []
    for it in out:
        k = akey(it.get(field, ''))
        if k and k not in keys: keys.append(k)
    return keys

async def gen(app, field, voice, rate, force, mfield=None, mvoice=None):
    import edge_tts
    adir = os.path.join(ROOT, app, 'src', 'audio'); os.makedirs(adir, exist_ok=True)
    ipath = os.path.join(adir, 'index.json')
    index = json.load(open(ipath, encoding='utf-8')) if os.path.exists(ipath) else {}
    keys = items_of(app, field)
    # 뜻 음원: 키는 'm:' + 뜻 문자열(akey), 읽는 텍스트는 mean_text()
    mkeys = {}
    if mfield:
        for m in items_of(app, mfield):
            mkeys[MEAN_PREFIX + m] = mean_text(m)
    allkeys = list(keys) + list(mkeys)
    todo = []
    for k in allkeys:
        fn = index.get(k) or (hashlib.sha1(k.encode('utf-8')).hexdigest()[:16] + '.mp3')
        index[k] = fn
        if force or not os.path.exists(os.path.join(adir, fn)): todo.append((k, fn))
    print(f'{app}: 원문 {len(keys)} · 뜻 {len(mkeys)} · 새로 만들 것 {len(todo)} · 음성 {voice} / {mvoice}')
    sem = asyncio.Semaphore(4)
    async def one(k, fn):
        async with sem:
            text, v = (mkeys[k], mvoice) if k in mkeys else (k, voice)
            for attempt in range(3):
                try:
                    await edge_tts.Communicate(text, v, rate=rate).save(os.path.join(adir, fn)); return True
                except Exception as e:
                    err = e; await asyncio.sleep(1.5 * (attempt + 1))
            print('  실패:', k, err); return False
    res = await asyncio.gather(*[one(k, fn) for k, fn in todo])
    # 실패한 것은 index 에서 빼서 앱이 TTS 로 폴백하게 한다
    for (k, fn), ok in zip(todo, res):
        if not ok: index.pop(k, None)
    # 더 이상 쓰이지 않는 키 정리
    for k in list(index):
        if k not in allkeys: index.pop(k)
    json.dump(index, open(ipath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    size = sum(os.path.getsize(os.path.join(adir, fn)) for fn in index.values() if os.path.exists(os.path.join(adir, fn)))
    print(f'  완료 {sum(1 for r in res if r)}/{len(todo)} · 보유 {len(index)} 파일 · {size/1024:.0f} KB')

def main():
    args = sys.argv[1:]
    voice = rate = None; force = False
    if '--voice' in args: i = args.index('--voice'); voice = args[i+1]; del args[i:i+2]
    if '--rate' in args: i = args.index('--rate'); rate = args[i+1]; del args[i:i+2]
    if '--force' in args: force = True; args.remove('--force')
    apps = list(FAMILY) if '--all' in args else [a.strip('/') for a in args]
    if not apps: print(__doc__); sys.exit(1)
    for app in apps:
        field, dv, mfield, mv = FAMILY[app]
        asyncio.run(gen(app, field, voice or dv, rate or '-10%', force, mfield, mv))

if __name__ == '__main__':
    main()
