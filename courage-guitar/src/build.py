#!/usr/bin/env python3
"""Lofi Brew 「Courage Within」 블록 연습 페이지(../index.html) — 공용 도구 tools/make_block_practice.py 로 만든다.

이 곡은 가사가 없어(정식 발매곡이라 가사를 싣지 않는다) 노래 앱 없이 블록 연습 페이지만 있다.
beats.json 이 없어서 코드 경계에 가장 잘 맞는 반 마디 격자를 잰다.
사용: python3 build.py
"""
import os
import subprocess
import sys

VID = '9cbcKa3gE9Y'                       # make_block_practice.py 가 이 줄에서 영상 ID 를 읽는다
S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(S))
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'make_block_practice.py'), 'courage-guitar',
                '--title', 'Courage Within', '--artist', 'Lofi Brew (로파이 브루)', '--out', 'index.html',
                '--src', '가사는 싣지 않았습니다. 영상·음원: YouTube Lofi Brew 「Courage Within」(mixtape.so 제공).'], check=True)
