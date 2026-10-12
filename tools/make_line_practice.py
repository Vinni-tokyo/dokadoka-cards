#!/usr/bin/env python3
"""「대사 블록 연습」 페이지(<앱>/blocks.html)를 만든다 — 애니·영상 앱용 블록 연습. 블록 = 대사 한 줄.

노래용(make_block_practice.py)은 블록이 마디·코드였다. 여기서는 대사 한 줄이 블록이고, 4줄을 한 묶음(주고받는 대화)으로 둔다.
영상에 맞춰 지금 대사가 켜지고, 블록을 눌러 듣기·다시 눌러 멈추기, 🔁 이 줄 / 🔁 4줄 반복, 0.75×·0.5×,
🗣 따라 말하기(대사가 끝나면 멈추고 그 길이 + 0.6초 쉰 뒤 다음으로). 아래 막대에 지금 대사·뜻·단어.

재료는 앱에 이미 있는 데이터를 그대로 쓴다(새로 받아쓰지 않는다):
  src/segs.json(대사·시각·화자) · src/ko.txt(id|뜻|읽기|주석[|화자]) · src/fixes.txt(id|교정문, 있으면 원문 대신)
  · src/words.txt(단어 칩) · src/build.py 의 VID.
화면: tools/block-practice/lines.html.

사용: python3 tools/make_line_practice.py <앱폴더> --title 제목 --src "출처 문구" [--back 앱.html]
"""
import argparse
import asyncio
import hashlib
import glob
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rows_of(path, n):
    out = []
    if not os.path.exists(path): return out
    for ln in io.open(path, encoding='utf-8'):
        if ln.startswith('#') or '|' not in ln: continue
        q = [x.strip() for x in ln.rstrip('\n').split('|')]
        if len(q) >= n: out.append(q)
    return out


KO_VOICE, KO_RATE = 'ko-KR-SunHiNeural', '-5%'


def ko_text(t):
    """뜻을 읽기 좋게: 괄호 주석·〜 를 뗀다"""
    t = re.sub(r'[（(][^）)]*[）)]', '', t or ''); t = re.sub(r'[~〜～]', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def ko_audio(app, lines):
    """🇰🇷 뜻 듣기용 음원: 대사마다 한국어 뜻을 edge-tts 로 → <앱>/lines_ko/<해시>.mp3 (있으면 건너뜀)"""
    import edge_tts, sys
    d = os.path.join(ROOT, app, 'lines_ko'); os.makedirs(d, exist_ok=True)
    jobs = {}
    for ln in lines:
        k = ko_text(ln[3])
        if not k: ln.append(''); continue
        fn = hashlib.sha1(('ko:' + k).encode('utf-8')).hexdigest()[:14] + '.mp3'
        ln.append(fn); jobs.setdefault(fn, k)
    todo = [(fn, k) for fn, k in jobs.items() if not os.path.exists(os.path.join(d, fn))]
    async def run():
        sem = asyncio.Semaphore(6)
        async def one(fn, k):
            async with sem:
                fp = os.path.join(d, fn)
                for n in range(3):
                    try:
                        await edge_tts.Communicate(k, KO_VOICE, rate=KO_RATE).save(fp)
                        if os.path.getsize(fp) > 0: return
                    except Exception: await asyncio.sleep(1.5 * (n + 1))
                if os.path.exists(fp) and os.path.getsize(fp) == 0: os.remove(fp)   # 실패하면 빈 파일을 남기지 않는다
        await asyncio.gather(*[one(fn, k) for fn, k in todo])
    if todo:
        try: asyncio.run(run())
        except Exception as e: print('  뜻 음원 생성 실패(내장 음성으로 읽는다):', str(e)[:80])
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        from normalize_audio import normalize_dir
        normalize_dir(d)
    keep = set(jobs)
    for f in os.listdir(d):                              # 대사가 바뀌어 안 쓰는 파일은 지운다
        if f.endswith('.mp3') and f not in keep: os.remove(os.path.join(d, f))
    for ln in lines:                                     # 없거나 빈 파일이면 화면이 브라우저 내장 음성으로 읽는다
        fp = os.path.join(d, ln[8]) if ln[8] else ''
        if ln[8] and (not os.path.exists(fp) or os.path.getsize(fp) == 0): ln[8] = ''
    if not os.listdir(d): os.rmdir(d)
    return sum(1 for fn in jobs if os.path.exists(os.path.join(d, fn)))


def build(app, title, src, back, audio=True):
    S = os.path.join(ROOT, app, 'src')
    segs = json.load(io.open(os.path.join(S, 'segs.json'), encoding='utf-8'))
    ko = {int(q[0]): q for q in rows_of(os.path.join(S, 'ko.txt'), 3) if q[0].isdigit()}
    fixes = {int(q[0]): q[1] for q in rows_of(os.path.join(S, 'fixes.txt'), 2) if q[0].isdigit()}
    words = [(q[0].split(','), q[1], q[2], q[3]) for q in rows_of(os.path.join(S, 'words.txt'), 4)]
    shp = os.path.join(S, 'shadow.json')                # 🪜 뒤에서부터 쌓기용 덩어리 시각(tools/shadow_chunks.py)
    shadow = json.load(io.open(shp, encoding='utf-8')) if os.path.exists(shp) else {}
    vid = re.search(r"VID\s*=\s*'([^']+)'", io.open(os.path.join(S, 'build.py'), encoding='utf-8').read()).group(1)
    lines, spk_order = [], []
    for x in sorted(segs, key=lambda x: x['s']):
        i = x['id']; q = ko.get(i, [str(i), '', ''])
        ja = fixes.get(i, x['ja'])
        spk = (x.get('spk') or (q[4] if len(q) > 4 else '') or '').strip()
        spk = re.sub(r'〈〉$', ' (속마음)', spk)
        if spk and spk not in spk_order: spk_order.append(spk)
        hits = []
        for stems, head, rd, mean in words:
            at = min((ja.find(s) for s in stems if s and s in ja), default=-1)
            if at >= 0 and head not in [h[1] for h in hits]: hits.append((at, head, rd, mean))
        hits.sort()
        sh = shadow.get(str(i))
        lines.append([round(x['s'], 2), round(x['e'], 2), ja, q[1], q[2], spk, [[h, r, m] for _, h, r, m in hits[:6]],
                      [sh['t'], sh['x']] if sh else None])
    for a, b in zip(lines, lines[1:]):                  # 자막이 겹치면 다음 대사 시작에서 자른다(블록이 겹치지 않게)
        if a[1] > b[0]: a[1] = b[0]
    new = ko_audio(app, lines) if audio else [ln.append('') for ln in lines] and 0   # [8] = 한국어 뜻 음원 파일
    for ln in lines: ln.append('')                      # [9] = 시간 블록 종류('' = 대사)
    # 🎵 오프닝·엔딩 · 📺 자막 없는 마지막 구간: 글자 없는 시간 블록(tools/time_blocks.py — 시각만, 가사·대사 글자는 없다)
    tbp = os.path.join(S, 'time_blocks.json')
    tb = json.load(io.open(tbp, encoding='utf-8')) if os.path.exists(tbp) else []
    for b in tb: lines.append([b['s'], b['e'], '', '', '', '', [], None, '', b['kind']])
    lines.sort(key=lambda l: l[0])
    DATA = {'vid': vid, 'title': title, 'src': src, 'store': app + '.lines',
            'back': [back, '앱으로'] if back else None, 'lines': lines, 'spk': spk_order}
    tpl = io.open(os.path.join(ROOT, 'tools', 'block-practice', 'lines.html'), encoding='utf-8').read()
    html = tpl.replace('/*__DATA__*/{}', json.dumps(DATA, ensure_ascii=False, separators=(',', ':'))) \
              .replace('/*__TITLE__*/', f'{title} 대사 블록 연습')
    io.open(os.path.join(ROOT, app, 'blocks.html'), 'w', encoding='utf-8').write(html)
    print(f'{app}/blocks.html: 대사 {len(lines) - len(tb)} · 화자 {len(spk_order)} · '
          f'교정문 {sum(1 for x in segs if x["id"] in fixes)} · 단어 칩 {sum(len(l[6]) for l in lines)} · '
          f'시간 블록 {len(tb)} · 뒤에서 쌓기 대사 {sum(1 for l in lines if l[7])} · 뜻 음원 파일 {sum(1 for l in lines if l[8])}/{len(lines)}(없는 대사는 내장 음성)')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('app'); ap.add_argument('--title', required=True); ap.add_argument('--src', required=True)
    ap.add_argument('--back', default=''); ap.add_argument('--no-audio', action='store_true')
    a = ap.parse_args()
    app = a.app.strip('/')
    back = a.back or next((os.path.basename(p) for p in glob.glob(os.path.join(ROOT, app, '*-Cards.html'))), '')
    build(app, a.title, a.src, back, audio=not a.no_audio)
