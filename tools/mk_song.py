#!/usr/bin/env python3
"""공식 자막(ja, 있으면 ko)으로 노래 앱의 뼈대를 만든다.

    .venv/bin/python tools/mk_song.py <앱폴더> <영상id> <포트> <출력 HTML 이름> \
        --ja <ja.srt> [--ko <ko.srt>] --title-ja 曲名 --title-ko 곡명 --artist-ja 歌手 --artist-ko 가수 [--gap 3.0]

만드는 것: <앱>/src/{lyrics.txt, subtitles.srt, _ko_official.txt, segs.json} 와
          빌드 도구·템플릿(forgetmenot-cards 계열 복사) · start.sh / start.bat · build.py 의 VID·OUT.
남는 손일: ko.txt(뜻·읽기·주석) · kanji.txt · words.txt · study.txt · build.py 의 SECTIONS.

줄과 시각은 이렇게 정한다.
 · 일본어 큐 한 개 = 줄 한 개. 큐 안에 줄바꿈이 있으면 그 수만큼 줄이 되고, 시각은 글자 수 비율로 나눈다.
 · 한국어 자막이 있으면 「시간이 가장 많이 겹치는」 한국어 큐를 짝으로 삼는다(순서대로 짝지으면
   자막 두 벌이 나누는 지점이 달라 어긋난다 — mahou 에서 최대 16초).
 · 한국어 큐 하나가 일본어 큐 여럿을 덮으면(無条件の愛: 84큐 ↔ 64큐) 그 일본어 큐들을 한 줄로 합친다.
   자막이 너무 잘게 쪼개져 있을 때 카드 한 장이 너무 짧아지는 것을 막는다.
 · 앞 줄 끝과 다음 줄 시작이 gap 초 넘게 비면 구간(빈 줄)을 나눈다.
"""
import argparse
import io
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'forgetmenot-cards'          # 가장 최근 계열(패치가 다 들어간 템플릿)


def load(p):
    out = []
    for blk in re.split(r'\n\s*\n', io.open(p, encoding='utf-8').read().strip()):
        L = [x for x in blk.strip().split('\n') if x.strip()]
        if len(L) < 3:
            continue
        m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', L[1])
        g = list(map(int, m.groups()))
        out.append({'s': g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000,
                    'e': g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000,
                    't': [x.strip() for x in L[2:] if x.strip()]})
    return out


def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')


def overlap(a, b):
    return max(0.0, min(a['e'], b['e']) - max(a['s'], b['s']))


def rows_from(ja, ko):
    """줄 목록 [{ja, ko, s, e}] 를 만든다."""
    if not ko:
        rows = []
        for c in ja:
            n = len(c['t']); tot = sum(len(x) for x in c['t']) or 1; t = c['s']
            for x in c['t']:
                d = (c['e'] - c['s']) * len(x) / tot if n > 1 else c['e'] - c['s']
                rows.append({'ja': x, 'ko': '', 's': t, 'e': t + d}); t += d
        return rows, 'ko 없음'
    # 일본어 큐마다 가장 많이 겹치는 한국어 큐
    pair = []
    for c in ja:
        best = max(range(len(ko)), key=lambda i: overlap(c, ko[i]))
        pair.append(best if overlap(c, ko[best]) > 0 else None)
    # 같은 한국어 큐에 붙은 일본어 큐들을 한 줄로
    groups = []
    for i, c in enumerate(ja):
        k = pair[i]
        # 겹치는 한국어 큐가 없는 일본어 큐는 앞 줄에 붙인다 — 한국어 자막이 두 조각을 한 큐로
        # 묶고 뒷조각의 시간엔 아무것도 띄우지 않는 꼴(無条件の愛: その愛が / 私を支え)
        if groups and (k is None or groups[-1]['k'] == k):
            groups[-1]['cues'].append(c)
        else:
            groups.append({'k': k, 'cues': [c]})
    rows = []
    for g in groups:
        cues = g['cues']
        if len(cues) == 1 and len(cues[0]['t']) > 1:   # 한 큐에 여러 줄: 글자 수 비율로 나눈다
            c = cues[0]; tot = sum(len(x) for x in c['t']) or 1; t = c['s']
            kt = ' '.join(ko[g['k']]['t']) if g['k'] is not None else ''
            for j, x in enumerate(c['t']):
                d = (c['e'] - c['s']) * len(x) / tot
                rows.append({'ja': x, 'ko': kt if j == 0 else '', 's': t, 'e': t + d}); t += d
        else:
            rows.append({'ja': ' '.join(' '.join(c['t']) for c in cues),
                         'ko': ' '.join(ko[g['k']]['t']) if g['k'] is not None else '',
                         's': cues[0]['s'], 'e': cues[-1]['e']})
    merged = sum(1 for g in groups if len(g['cues']) > 1)
    return rows, f'ko {len(ko)}큐 · 합친 줄 {merged}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('app'); ap.add_argument('vid'); ap.add_argument('port', type=int); ap.add_argument('outname')
    ap.add_argument('--ja', required=True); ap.add_argument('--ko')
    ap.add_argument('--title-ja', required=True); ap.add_argument('--title-ko', required=True)
    ap.add_argument('--artist-ja', required=True); ap.add_argument('--artist-ko', required=True)
    ap.add_argument('--gap', type=float, default=3.0)
    a = ap.parse_args()

    src = os.path.join(ROOT, a.app, 'src'); os.makedirs(os.path.join(src, 'audio'), exist_ok=True)
    for f in ('align.py', 'beats.py', 'build.py', 'gen_words.py', 'lemma_base.py', 'lemma_meanings.py',
              'check_cov.py', 'tpl.html'):
        shutil.copy(os.path.join(ROOT, BASE, 'src', f), src)
    for f in ('start.sh', 'start.bat'):
        shutil.copy(os.path.join(ROOT, BASE, f), os.path.join(ROOT, a.app))

    ja = load(a.ja); ko = load(a.ko) if a.ko else None
    rows, how = rows_from(ja, ko)
    secs = [0] + [i + 1 for i in range(len(rows) - 1) if rows[i + 1]['s'] - rows[i]['e'] > a.gap]
    with io.open(os.path.join(src, 'lyrics.txt'), 'w', encoding='utf-8') as f:
        for i, r in enumerate(rows):
            if i in secs and i > 0:
                f.write('\n')
            f.write(r['ja'] + '\n')
    with io.open(os.path.join(src, 'subtitles.srt'), 'w', encoding='utf-8') as f:
        for i, r in enumerate(rows, 1):
            f.write(f"{i}\n{ts(r['s'])} --> {ts(r['e'])}\n{r['ja']}\n\n")
    io.open(os.path.join(src, '_ko_official.txt'), 'w', encoding='utf-8').write(
        '\n'.join(f"{i}|{r['ko']}" for i, r in enumerate(rows, 1)) + '\n')
    json.dump([{'id': i, 'ja': r['ja']} for i, r in enumerate(rows, 1)],
              io.open(os.path.join(src, 'segs.json'), 'w', encoding='utf-8'), ensure_ascii=False)

    base_html = [x for x in os.listdir(os.path.join(ROOT, BASE)) if x.endswith('-Cards.html')][0]
    bp = os.path.join(src, 'build.py'); s = io.open(bp, encoding='utf-8').read()
    s = re.sub(r"VID = '[^']*'", f"VID = '{a.vid}'", s, count=1)
    s = s.replace(f"'{base_html}'", f"'{a.outname}'")
    io.open(bp, 'w', encoding='utf-8').write(s)
    for p in ('start.sh', 'start.bat'):
        q = os.path.join(ROOT, a.app, p)
        x = io.open(q, encoding='utf-8').read()
        x = re.sub(r'PORT:-\d+', f'PORT:-{a.port}', x); x = re.sub(r'set PORT=\d+', f'set PORT={a.port}', x)
        io.open(q, 'w', encoding='utf-8').write(x.replace(base_html, a.outname))
    tp = os.path.join(src, 'tpl.html'); t = io.open(tp, encoding='utf-8').read()
    t = re.sub(r'<title>도카도카 일본어 공부 · [^<]*</title>',
               f'<title>도카도카 일본어 공부 · {a.title_ja} · {a.artist_ja}</title>', t, count=1)
    t = re.sub(r'<small>[^<]*<span class="n">—</span>줄<br><span lang="ja">[^<]*<span class="n">—</span>行</span></small>',
               f'<small>{a.title_ko} · {a.artist_ko} · <span class="n">—</span>줄<br>'
               f'<span lang="ja">{a.title_ja} · {a.artist_ja} · <span class="n">—</span>行</span></small>', t, count=1)
    io.open(tp, 'w', encoding='utf-8').write(t)
    print(f'{a.app}: {len(rows)}줄 · {len(secs)}구간 · 포트 {a.port} · {how}')
    print('  남은 손일: ko.txt · kanji.txt · words.txt · study.txt · build.py 의 SECTIONS')


if __name__ == '__main__':
    main()
