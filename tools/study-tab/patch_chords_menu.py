#!/usr/bin/env python3
"""노래 앱에 「🎸 기타 코드」 메뉴를 넣는다 — 장면 고르기 아래, 접었다 펴는 목록.

첫 줄은 도카도카 간이 코드 악보(chords.html), 다음 줄은 코드 사이트 검색(일본 노래 U-FRET,
영어 노래 Ultimate Guitar). 한국 노래는 맞는 사이트가 없어 악보만 둔다.
원곡 조·카포·템포는 src/chords_meta.json(make_chord_sheet.py 가 쓴다)에서 읽는다.
이미 메뉴가 있으면(class="chords") 건드리지 않는다 — utautai 는 손으로 고른 링크가 있다.

사용: python3 patch_chords_menu.py <앱폴더> --q "검색어" [--site ufret|ug|none]
"""
import argparse
import html
import io
import json
import os
import re
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CSS = '''.chords{margin-top:10px;font-size:13px}
.chords summary{cursor:pointer;display:inline-flex;align-items:baseline;gap:8px;flex-wrap:wrap;padding:7px 12px;border:1px solid var(--line-2);border-radius:9px;background:var(--surface);color:var(--ink);font-weight:600;list-style:none}
.chords summary::-webkit-details-marker{display:none}
.chords summary span{font-weight:400;font-size:11.5px;color:var(--ink-3)}
.chords[open] summary{border-color:var(--brand-line)}
.chords ul{list-style:none;margin:8px 0 0;padding:0;display:grid;gap:6px}
.chords a{display:block;padding:9px 12px;border:1px solid var(--line);border-radius:9px;background:var(--surface);color:var(--ink);text-decoration:none;font-weight:600}
.chords a:hover,.chords a:focus-visible{border-color:var(--brand-line);outline:none}
.chords a small{display:block;font-weight:400;font-size:11.5px;color:var(--ink-3);margin-top:2px}
.chords p{margin:8px 0 0;font-size:11.5px;line-height:1.6;color:var(--ink-3);max-width:520px}
'''

SITES = {'ufret': ('U-FRET 검색', '일본 노래 코드 사이트 · 정확한 원곡 악보', 'https://www.ufret.jp/search.php?key='),
         'ug': ('Ultimate Guitar 검색', '영어 노래 코드 사이트 · 정확한 원곡 악보',
                'https://www.ultimate-guitar.com/search.php?search_type=title&value=')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('app'); ap.add_argument('--q', default=''); ap.add_argument('--site', default='none')
    a = ap.parse_args()
    app = a.app.strip('/')
    p = os.path.join(ROOT, app, 'src', 'tpl.html')
    h = io.open(p, encoding='utf-8').read()
    if 'class="chords"' in h:
        print('  건너뜀(이미 있음):', app); return
    meta = json.load(io.open(os.path.join(ROOT, app, 'src', 'chords_meta.json'), encoding='utf-8'))
    capo = f"카포 {meta['capo']} + {meta['form']} 폼" if meta['capo'] else f"{meta['form']} 폼"
    items = ['      <li><a href="chords.html" target="_blank" rel="noopener">도카도카 간이 코드 악보 '
             '<small>가사 위에 코드 · 카포 폼 / 원래 키 · 운지 그림</small></a></li>']
    if a.site in SITES and a.q:
        t, sub, base = SITES[a.site]
        items.append(f'      <li><a href="{base}{urllib.parse.quote(a.q)}" target="_blank" rel="noopener noreferrer">'
                     f'{t} <small>{sub}</small></a></li>')
    menu = (f'''    <details class="chords">
     <summary>🎸 기타 코드<span>원곡 {html.escape(meta['key'])} · {capo} · {meta['bpm']} BPM</span></summary>
     <ul>
''' + '\n'.join(items) + '''
     </ul>
     <p>도카도카 악보는 음원에서 직접 딴 간이 코드입니다(경과 코드는 뺐습니다). 다른 사이트의 악보는 옮겨 싣지 않았습니다.</p>
    </details>
''')
    m = re.search(r'(    <select id="sceneSel" class="scene-sel"[^>]*></select>\n)', h)
    assert m, f'{app}: 장면 고르기를 못 찾았다'
    h = h[:m.end()] + menu + h[m.end():]
    anchor = '.scene-sel{display:none;'
    assert h.count(anchor) == 1, f'{app}: CSS 기준을 못 찾았다'
    h = h.replace(anchor, CSS + anchor, 1)
    io.open(p, 'w', encoding='utf-8').write(h)
    print('  메뉴 넣음:', app)


if __name__ == '__main__':
    main()
