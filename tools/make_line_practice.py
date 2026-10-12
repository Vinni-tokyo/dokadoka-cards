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


def build(app, title, src, back):
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
    DATA = {'vid': vid, 'title': title, 'src': src, 'store': app + '.lines',
            'back': [back, '앱으로'] if back else None, 'lines': lines, 'spk': spk_order}
    tpl = io.open(os.path.join(ROOT, 'tools', 'block-practice', 'lines.html'), encoding='utf-8').read()
    html = tpl.replace('/*__DATA__*/{}', json.dumps(DATA, ensure_ascii=False, separators=(',', ':'))) \
              .replace('/*__TITLE__*/', f'{title} 대사 블록 연습')
    io.open(os.path.join(ROOT, app, 'blocks.html'), 'w', encoding='utf-8').write(html)
    print(f'{app}/blocks.html: 대사 {len(lines)} · 묶음 {(len(lines) + 3) // 4} · 화자 {len(spk_order)} · '
          f'교정문 {sum(1 for x in segs if x["id"] in fixes)} · 단어 칩 {sum(len(l[6]) for l in lines)} · '
          f'뒤에서 쌓기 대사 {sum(1 for l in lines if l[7])}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('app'); ap.add_argument('--title', required=True); ap.add_argument('--src', required=True)
    ap.add_argument('--back', default='')
    a = ap.parse_args()
    app = a.app.strip('/')
    back = a.back or next((os.path.basename(p) for p in glob.glob(os.path.join(ROOT, app, '*-Cards.html'))), '')
    build(app, a.title, a.src, back)
