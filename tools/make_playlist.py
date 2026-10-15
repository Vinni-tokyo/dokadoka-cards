#!/usr/bin/env python3
"""🎵 전곡 듣기(playlist/index.html) — 노래·찬양 앱을 한 플레이어로 이어 듣는 페이지를 만든다.

곡 목록은 관문 페이지(index.html)의 APPS 에서 kind 가 「노래」·「찬양」인 일본어 앱을 관문 차례대로 가져온다.
곡이 끝나면 같은 YouTube 플레이어에 다음 영상을 싣는다(페이지를 옮기면 폰이 자동 재생을 막는다).
반복: 🔁 전곡 반복 / 🔂 한 곡 반복 / ➡ 반복 없음 · 🔀 섞기 · 묶음(전체·노래·찬양). 가사는 싣지 않는다(각 노래 앱에 있다).
화면: tools/block-practice/playlist.html.

사용: python3 tools/make_playlist.py
"""
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
songs = []
for m in re.finditer(r"\{vid:'([^']*)', href:'([a-z0-9-]+)/([^']*)', learn:'ja', kind:'([^']*)',\s*title:(['\"])(.*?)\5", HUB, re.S):
    vid, app, page, kind, _, title = m.groups()
    if not (kind.startswith('노래') or kind.startswith('찬양')) or not vid: continue
    title = re.sub(r'\s*[(（][^)）]*[)）]\s*$', '', title).replace(' — 가사로 배우기', '').strip()
    songs.append({'k': app, 'app': page, 'vid': vid, 't': title, 'g': '노래' if kind.startswith('노래') else '찬양'})
tpl = io.open(os.path.join(ROOT, 'tools', 'block-practice', 'playlist.html'), encoding='utf-8').read()
os.makedirs(os.path.join(ROOT, 'playlist'), exist_ok=True)
io.open(os.path.join(ROOT, 'playlist', 'index.html'), 'w', encoding='utf-8').write(
    tpl.replace('/*__SONGS__*/[]', json.dumps(songs, ensure_ascii=False, separators=(',', ':'))))
print(f'playlist/index.html: {len(songs)}곡 (노래 {sum(s["g"] == "노래" for s in songs)} · 찬양 {sum(s["g"] == "찬양" for s in songs)})')
