#!/usr/bin/env python3
"""Lofi Brew 「Courage Within」 블록 연습 페이지(../index.html) — 공용 도구 tools/make_block_practice.py 로 만든다.

가사(lyrics.txt)와 줄 시각(subtitles.srt)이 생겨 간이 코드 악보(chords.html)도 함께 만든다.
beats.json 이 없어서 코드 경계에 가장 잘 맞는 반 마디 격자를 잰다.
사용: python3 build.py
"""
import os
import subprocess
import sys

SECTIONS = [
 ('v1',     '1절 · 폭풍의 밤',      'Verse 1 · The storm is wild'),
 ('v2',     '2절 · 끝없는 산',      'Verse 2 · The mountain looms'),
 ('cho1',   '후렴 1',             'Chorus 1'),
 ('bridge', '브릿지 · 길이 가파를 때', 'Bridge · When the road feels steep'),
 ('v3',     '3절 · 천 개의 목소리',   'Verse 3 · A thousand voices'),
 ('cho2',   '후렴 2',             'Chorus 2'),
]

VID = '9cbcKa3gE9Y'                       # make_block_practice.py 가 이 줄에서 영상 ID 를 읽는다
S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(S))
TITLE, ARTIST = 'Courage Within', 'Lofi Brew (로파이 브루)'
SRC = '영상·음원: YouTube Lofi Brew 「Courage Within」(mixtape.so 제공). 가사는 코드 악보에만 싣습니다.'

# 1) 블록 연습(index.html) — 코드만. 2) 간이 코드 악보(chords.html) — 가사 위에 코드.
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'make_block_practice.py'), 'courage-guitar',
                '--title', TITLE, '--artist', ARTIST, '--out', 'index.html',
                '--back', 'chords.html', '--back-label', '코드 악보(가사)로', '--no-lyrics',
                '--src', SRC], check=True)
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'make_chord_sheet.py'), 'courage-guitar',
                '--title', TITLE, '--artist', ARTIST, '--sub', '용기는 안에', '--lang', 'en'], check=True)
