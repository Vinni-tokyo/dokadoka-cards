#!/usr/bin/env python3
"""노래 앱의 간이 코드 악보(<앱>/chords.html)를 만든다 — 가사 위에 코드, 카포 폼 / 원래 키 전환, 운지 그림.

재료: <앱>/src/chords.json(tools/chord_simple.py) · subtitles.srt(줄 시각) · lyrics.txt · build.py 의 SECTIONS.
코드는 줄 안에서 「그 코드가 시작한 시각」의 비율 자리에 얹는다(글자 단위 박자 정보가 없어 대략이다).
카포: C → G → D → A → E 폼 순으로, 카포 5프렛 이내에서 먼저 되는 폼을 고른다(개방현 코드로 치게).

사용: python3 tools/make_chord_sheet.py <앱폴더> --title 曲名 --artist 歌手 [--sub 한국어 제목] [--lang ja|ko|en]
"""
import html
import io
import json
import os
import re

import argparse
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = OUT = None

NOTES = 'C C# D D# E F F# G G# A A# B'.split()
SHOW = {'A#': 'B♭', 'G#': 'A♭', 'D#': 'E♭', 'C#': 'C#', 'F#': 'F#'}

# 운지(6번 줄 → 1번 줄). 간단하게: F 는 작은 F. 장·단 3화음 24개.
FING = {'C': 'x32010', 'C#': 'x46664', 'D': 'xx0232', 'E♭': 'x68886', 'E': '022100', 'F': 'xx3211',
        'F#': '244322', 'G': '320003', 'A♭': '466544', 'A': 'x02220', 'B♭': 'x13331', 'B': 'x24442',
        'Cm': 'x35543', 'C#m': 'x46654', 'Dm': 'xx0231', 'E♭m': 'x68876', 'Em': '022000', 'Fm': '133111',
        'F#m': '244222', 'Gm': '355333', 'A♭m': '466444', 'Am': 'x02210', 'B♭m': 'x13321', 'Bm': 'x24432'}


def pick_capo(home):
    for form in ('C', 'G', 'D', 'A', 'E'):
        capo = (home - NOTES.index(form)) % 12
        if capo <= 5: return capo, form
    return 0, NOTES[home]


def name(label, shift):
    m = re.match(r'([A-G]#?)(.*)', label)
    r, q = m.groups()
    n = NOTES[(NOTES.index(r) - shift) % 12]
    return SHOW.get(n, n) + q


def srt():
    out = []
    f0 = next(f for f in ('subtitles.srt', 'subtitles.ko.srt') if os.path.exists(os.path.join(S, f)))
    for b in io.open(os.path.join(S, f0), encoding='utf-8').read().strip().split('\n\n'):
        L = b.split('\n')
        m = re.findall(r'(\d+):(\d+):(\d+),(\d+)', L[1])
        f = lambda g: int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 1000
        out.append((f(m[0]), f(m[1]), L[2]))
    return out


def sections():
    s = io.open(os.path.join(S, 'build.py'), encoding='utf-8').read()
    m = re.search(r"SECTIONS = \[\n(.*?)\n\]", s, re.S)
    if not m or not os.path.exists(os.path.join(S, 'lyrics.txt')): return {}     # 구간 정보가 없는 앱
    names = []
    for ln in m.group(1).split('\n'):
        f = re.findall(r"'([^']*)'", ln)
        if len(f) < 2: continue
        ko = [x for x in f[1:] if re.search('[가-힣]', x)]                  # 한국어 표기가 있으면 그쪽
        names.append(ko[0] if ko else f[1])
    blocks = [b for b in re.split(r'\n\s*\n', io.open(os.path.join(S, 'lyrics.txt'), encoding='utf-8').read().strip()) if b.strip()]
    starts, n = [], 0
    for b in blocks:
        starts.append(n); n += len([x for x in b.split('\n') if x.strip()])
    return dict(zip(starts, names))


def place(line, a, b, seq):
    """줄 안 글자 자리에 코드를 얹는다 → [(글자, 코드|None)]"""
    chars = list(line)
    idx = [i for i, c in enumerate(chars) if c not in '　 「」…？']
    marks = {}
    sounding = [n for s, e, n in seq if s <= a + 0.25 < e]
    if sounding: marks[idx[0]] = sounding[0]
    for s, e, n in seq:
        if a + 0.25 < s < b - 0.3:
            k = idx[min(len(idx) - 1, int(round((s - a) / (b - a) * len(idx))))]
            prev = max([j for j in marks if j <= k], default=None)
            if prev is not None and k - prev < 2: k = prev + 2      # 코드 이름이 겹치지 않게 두 글자 띄운다
            if k >= len(chars): continue
            marks[k] = n
    # 같은 코드가 이어 얹히면 뒤를 지운다
    last = None
    for k in sorted(marks):
        if marks[k] == last: del marks[k]
        else: last = marks[k]
    return [(c, marks.get(i)) for i, c in enumerate(chars)]


def bars(seq, a, b):
    out = []
    for s, e, n in seq:
        if e > a + 0.3 and s < b - 0.3 and (not out or out[-1] != n): out.append(n)
    return out


def diagram(nm):
    f = FING.get(nm)
    if not f: return ''
    frets = [None if c == 'x' else int(c) for c in f]
    used = [x for x in frets if x]
    base = 1 if not used or max(used) <= 4 else min(used)
    W, H, x0, y0, dx, dy = 70, 84, 12, 18, 9.2, 12
    g = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{nm} 운지"><title>{nm}</title>']
    g.append(f'<line x1="{x0}" y1="{y0}" x2="{x0 + 5 * dx}" y2="{y0}" class="nut" stroke-width="{3 if base == 1 else 1}"/>')
    for i in range(6): g.append(f'<line x1="{x0 + i * dx}" y1="{y0}" x2="{x0 + i * dx}" y2="{y0 + 5 * dy}" class="ln"/>')
    for j in range(6): g.append(f'<line x1="{x0}" y1="{y0 + j * dy}" x2="{x0 + 5 * dx}" y2="{y0 + j * dy}" class="ln"/>')
    if base > 1: g.append(f'<text x="{x0 + 5 * dx + 4}" y="{y0 + dy * .75}" class="fr">{base}</text>')
    for i, fr in enumerate(frets):
        x = x0 + i * dx
        if fr is None: g.append(f'<text x="{x}" y="{y0 - 5}" class="mk">×</text>')
        elif fr == 0: g.append(f'<circle cx="{x}" cy="{y0 - 8}" r="2.6" class="open"/>')
        else: g.append(f'<circle cx="{x}" cy="{y0 + (fr - base + .5) * dy}" r="3.6" class="dot"/>')
    g.append('</svg>')
    return ''.join(g)


def main():
    global S, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument('app'); ap.add_argument('--title', required=True); ap.add_argument('--artist', required=True)
    ap.add_argument('--sub', default=''); ap.add_argument('--lang', default='ja')
    a_ = ap.parse_args()
    S = os.path.join(ROOT, a_.app.strip('/'), 'src'); OUT = os.path.join(ROOT, a_.app.strip('/'), 'chords.html')
    data = json.load(io.open(os.path.join(S, 'chords.json'), encoding='utf-8'))
    seq = data['chords']; KEY = data['key']; BPM = data['bpm']
    CAPO, FORM = pick_capo(data['home'])
    fit = data.get('fit', 1.0)
    WARN = (f' <b>이 곡은 조 판별 확신이 낮습니다(일치도 {fit:.2f}).</b> 전자음·효과음이 많아 코드가 크게 틀렸을 수 있습니다.'
            if fit < 0.7 else '')
    L = srt(); sec = sections()
    LANG = a_.lang
    rows = []                                   # ('sec', 이름) | ('bars', [코드]) | ('line', [(글자,코드)])
    prev_end = 0.0
    for i, (a, b, t) in enumerate(L):
        if a - prev_end > 4.0:
            label = '전주' if i == 0 else '간주'
            rows.append(('bars', label, bars(seq, prev_end, a)))
        if i in sec: rows.append(('sec', sec[i], None))
        rows.append(('line', None, place(t, a, b, seq)))
        prev_end = b
    rows.append(('bars', '후주', bars(seq, prev_end, seq[-1][1])))

    used = []
    for s, e, n in seq:
        if n not in used and any(n == c for r in rows if r[0] != 'sec' for c in (r[2] if r[0] == 'bars' else [x[1] for x in r[2]])):
            used.append(n)

    def chord_span(n):
        return (f'<b class="ch" data-c="{html.escape(name(n, CAPO))}" data-o="{html.escape(name(n, 0))}">'
                f'{html.escape(name(n, CAPO))}</b>')

    body = []
    for kind, label, val in rows:
        if kind == 'sec':
            body.append(f'<h2>{html.escape(label)}</h2>')
        elif kind == 'bars':
            if val:
                body.append(f'<p class="bars"><span class="lb">{label}</span>' +
                            '<span class="sep">|</span>'.join(chord_span(n) for n in val) + '</p>')
        else:
            out = []
            for c, n in val:
                if n: out.append(f'<span class="w">{chord_span(n)}{html.escape(c)}</span>')
                else: out.append(html.escape(c))
            body.append(f'<p class="ly" lang="{LANG}">{"".join(out)}</p>')

    diags_c = ''.join(f'<figure>{diagram(name(n, CAPO))}<figcaption>{html.escape(name(n, CAPO))}</figcaption></figure>' for n in used)
    diags_o = ''.join(f'<figure>{diagram(name(n, 0))}<figcaption>{html.escape(name(n, 0))}</figcaption></figure>' for n in used)

    keyname = name(KEY.rstrip('m'), 0) + ('m' if KEY.endswith('m') else '')
    capo_lbl = f'카포 {CAPO} · {FORM} 폼' if CAPO else f'{FORM} 폼 (카포 없음)'
    page = TEMPLATE.format(title=f'{a_.title} 간이 코드', title_ja=html.escape(a_.title), artist=html.escape(a_.artist),
                           title_ko=html.escape(a_.sub or a_.title), key=keyname, capo_lbl=capo_lbl, bpm=BPM,
                           warn=WARN, lang=a_.lang, body='\n'.join(body), diags_c=diags_c, diags_o=diags_o)
    json.dump({'key': keyname, 'capo': CAPO, 'form': FORM, 'bpm': BPM},
              io.open(os.path.join(S, 'chords_meta.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    io.open(OUT, 'w', encoding='utf-8').write(page)
    print(f'{a_.app}: 조 {keyname} · {capo_lbl} · {BPM} BPM · 줄 {len(L)} · 코드 {len(used)}종 ({", ".join(name(n, CAPO) for n in used)})')


TEMPLATE = '''<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>{title}</title>
<style>
:root{{--bg:#f6f7fb;--surface:#fff;--ink:#1d2230;--ink-2:#4a5266;--ink-3:#7a8296;--line:#e3e6ee;--brand:#3b4a7a;--brand-soft:#eceffa;--ch:#b4432b}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#12151d;--surface:#1a1e29;--ink:#e8ebf3;--ink-2:#b6bdcf;--ink-3:#8c94a8;--line:#2b3142;--brand:#9fb0ea;--brand-soft:#232a3d;--ch:#ff9a7d}}}}
:root[data-theme="dark"]{{--bg:#12151d;--surface:#1a1e29;--ink:#e8ebf3;--ink-2:#b6bdcf;--ink-3:#8c94a8;--line:#2b3142;--brand:#9fb0ea;--brand-soft:#232a3d;--ch:#ff9a7d}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI","Hiragino Sans","Noto Sans JP","Noto Sans KR",sans-serif}}
.wrap{{max-width:760px;margin:0 auto;padding:22px 16px 60px}}
header h1{{margin:0;font-size:24px;letter-spacing:-.01em}} header h1 small{{font-size:14px;font-weight:500;color:var(--ink-2);margin-left:6px}}
.meta{{margin:6px 0 0;color:var(--ink-2);font-size:13.5px}}
.bar{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:16px 0 8px}}
.seg{{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden;background:var(--surface)}}
.seg button{{border:0;background:none;color:var(--ink-2);font:inherit;font-size:13px;padding:8px 12px;cursor:pointer}}
.seg button[aria-pressed="true"]{{background:var(--brand-soft);color:var(--brand);font-weight:700}}
.seg button:focus-visible{{outline:2px solid var(--brand);outline-offset:-2px}}
.note{{font-size:12px;line-height:1.7;color:var(--ink-3);margin:6px 0 16px}}
.diags{{display:flex;flex-wrap:wrap;gap:6px 10px;margin:4px 0 18px;padding:12px;background:var(--surface);border:1px solid var(--line);border-radius:12px}}
.diags figure{{margin:0;width:64px;text-align:center}} .diags svg{{width:64px;height:auto;display:block}}
.diags figcaption{{font-size:13px;font-weight:700;color:var(--ch)}}
.diags .ln{{stroke:var(--ink-3);stroke-width:1}} .diags .nut{{stroke:var(--ink)}} .diags .dot{{fill:var(--ink)}}
.diags .open{{fill:none;stroke:var(--ink);stroke-width:1.2}} .diags .mk,.diags .fr{{fill:var(--ink-3);font-size:9px;text-anchor:middle}} .diags .fr{{text-anchor:start}}
.sheet{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:6px 16px 18px}}
h2{{font-size:12px;font-weight:700;letter-spacing:.04em;color:var(--brand);margin:20px 0 2px;padding-top:10px;border-top:1px dashed var(--line)}}
h2:first-child{{border-top:0;margin-top:8px}}
.ly{{font-size:19px;line-height:1;margin:0;padding:26px 0 8px;overflow-wrap:anywhere}}
.w{{position:relative;display:inline-block}}
.ch{{font-size:13px;font-weight:800;color:var(--ch);font-family:ui-monospace,Menlo,Consolas,monospace}}
.ly .ch{{position:absolute;left:0;bottom:1.25em;white-space:nowrap}}
.bars{{margin:10px 0 2px;font-size:14px;display:flex;flex-wrap:wrap;gap:6px;align-items:baseline}}
.bars .lb{{font-size:11.5px;color:var(--ink-3);margin-right:4px}} .bars .sep{{color:var(--line)}}
.o{{display:none}} body.orig .o{{display:flex}} body.orig .c{{display:none}}
footer{{margin-top:22px;font-size:12px;color:var(--ink-3);line-height:1.7}}
footer a{{color:var(--brand)}}
@media (max-width:420px){{.ly{{font-size:17px}}}}
</style></head>
<body><div class="wrap">
<header>
 <h1 lang="{lang}">{title_ja}<small>{artist}</small></h1>
 <p class="meta">{title_ko} · 간이 코드 악보 · ♩≒{bpm}</p>
</header>
<div class="bar">
 <div class="seg" role="group" aria-label="코드 표기">
  <button type="button" id="bC" aria-pressed="true">{capo_lbl}</button>
  <button type="button" id="bO" aria-pressed="false">원래 키 {key}</button>
 </div>
</div>
<p class="note">음원에서 반주만 떼어 내 직접 딴 <b>간이 코드</b>입니다. 원곡의 경과 코드(dim·m7-5 등)는 빼고 기본 코드로 줄였고,
코드를 얹은 글자 자리는 대략입니다. 원곡과 다를 수 있습니다. 원곡의 조는 {key} 입니다.{warn}</p>
<div class="diags c">{diags_c}</div>
<div class="diags o">{diags_o}</div>
<main class="sheet">
{body}
</main>
<footer>가사: 앱과 같은 출처(앱 폴더 README) · 코드: 도카도카가 음원 분석(tools/chord_simple.py)으로 직접 채보 · 학습용 개인 이용</footer>
</div>
<script>
(function(){{
  var bC=document.getElementById('bC'), bO=document.getElementById('bO');
  function set(orig){{
    document.body.classList.toggle('orig', orig);
    bC.setAttribute('aria-pressed', String(!orig)); bO.setAttribute('aria-pressed', String(orig));
    document.querySelectorAll('.ch[data-c]').forEach(function(e){{ e.textContent = orig ? e.dataset.o : e.dataset.c; }});
    try{{ localStorage.setItem('chordKey', orig ? 'o' : 'c'); }}catch(_){{}}
  }}
  bC.onclick=function(){{ set(false); }}; bO.onclick=function(){{ set(true); }};
  try{{ if(localStorage.getItem('chordKey')==='o') set(true); }}catch(_){{}}
}})();
</script>
</body></html>
'''

if __name__ == '__main__':
    main()
