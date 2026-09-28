#!/usr/bin/env python3
"""간이 코드 악보(chords.html)를 만든다 — 가사 위에 코드, 카포 2 C 폼 / 원래 키 D 전환, 운지 그림.

재료: chords.json(tools/chord_simple.py 의 자동 채보) · subtitles.srt(줄 시각) · lyrics.txt · build.py 의 SECTIONS.
코드는 줄 안에서 「그 코드가 시작한 시각」의 비율 자리에 얹는다(글자 단위 박자 정보가 없어 대략이다).

사용: python3 make_chords.py   → ../chords.html
"""
import html
import io
import json
import os
import re

S = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(S), 'chords.html')

TITLE_JA, ARTIST_JA, TITLE_KO = '歌うたいのバラッド', '斉藤和義', '노래하는 이의 발라드'
KEY, CAPO, BPM = 'D', 2, 76

NOTES = 'C C# D D# E F F# G G# A A# B'.split()
SHOW = {'A#': 'B♭', 'G#': 'A♭', 'D#': 'E♭', 'C#': 'C#', 'F#': 'F#'}

# 운지(6번 줄 → 1번 줄). 간단하게: F 는 작은 F.
FING = {'C': 'x32010', 'D': 'xx0232', 'Dm': 'xx0231', 'E': '022100', 'Em': '022000', 'F': 'xx3211',
        'Fm': '133111', 'G': '320003', 'A': 'x02220', 'Am': 'x02210', 'B♭': 'x13331', 'A♭': '466544',
        'B': 'x24442', 'Bm': 'x24432', 'F#': '244322', 'F#m': '244222', 'Gm': '355333', 'E♭': 'x68886'}


def name(label, shift):
    m = re.match(r'([A-G]#?)(.*)', label)
    r, q = m.groups()
    n = NOTES[(NOTES.index(r) - shift) % 12]
    return SHOW.get(n, n) + q


def srt():
    out = []
    for b in io.open(os.path.join(S, 'subtitles.srt'), encoding='utf-8').read().strip().split('\n\n'):
        L = b.split('\n')
        m = re.findall(r'(\d+):(\d+):(\d+),(\d+)', L[1])
        f = lambda g: int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 1000
        out.append((f(m[0]), f(m[1]), L[2]))
    return out


def sections():
    s = io.open(os.path.join(S, 'build.py'), encoding='utf-8').read()
    body = re.search(r"SECTIONS = \[\n(.*?)\n\]", s, re.S).group(1)
    names = [re.findall(r"'([^']*)'", ln)[1] for ln in body.split('\n') if ln.strip()]
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
    seq = json.load(io.open(os.path.join(S, 'chords.json'), encoding='utf-8'))
    L = srt(); sec = sections()
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
            body.append(f'<p class="ly" lang="ja">{"".join(out)}</p>')

    diags_c = ''.join(f'<figure>{diagram(name(n, CAPO))}<figcaption>{html.escape(name(n, CAPO))}</figcaption></figure>' for n in used)
    diags_o = ''.join(f'<figure>{diagram(name(n, 0))}<figcaption>{html.escape(name(n, 0))}</figcaption></figure>' for n in used)

    page = TEMPLATE.format(title=f'{TITLE_JA} 간이 코드', title_ja=TITLE_JA, artist=ARTIST_JA, title_ko=TITLE_KO,
                           key=KEY, capo=CAPO, bpm=BPM, ckey=name(KEY, CAPO), body='\n'.join(body),
                           diags_c=diags_c, diags_o=diags_o)
    io.open(OUT, 'w', encoding='utf-8').write(page)
    print(f'생성: {OUT} · 줄 {len(L)} · 코드 종류 {len(used)} ({", ".join(name(n, CAPO) for n in used)})')


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
 <h1 lang="ja">{title_ja}<small>{artist}</small></h1>
 <p class="meta">{title_ko} · 간이 코드 악보 · ♩≒{bpm}</p>
</header>
<div class="bar">
 <div class="seg" role="group" aria-label="코드 표기">
  <button type="button" id="bC" aria-pressed="true">카포 {capo} · {ckey} 폼</button>
  <button type="button" id="bO" aria-pressed="false">원래 키 {key}</button>
 </div>
</div>
<p class="note">음원에서 반주만 떼어 내 직접 딴 <b>간이 코드</b>입니다. 원곡의 경과 코드(dim·m7-5 등)는 빼고 기본 코드로 줄였고,
코드를 얹은 글자 자리는 대략입니다. 원곡과 다를 수 있으니 정확한 악보는 앱의 「🎸 기타 코드」 링크를 보세요.</p>
<div class="diags c">{diags_c}</div>
<div class="diags o">{diags_o}</div>
<main class="sheet">
{body}
</main>
<footer>가사: 斉藤和義 공식 채널 설명란 · 코드: 도카도카가 음원 분석(tools/chord_simple.py)으로 직접 채보 · 학습용 개인 이용</footer>
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
