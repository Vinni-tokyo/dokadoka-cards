#!/usr/bin/env python3
"""スピッツ 「楓」 블록 연습 페이지(../index.html) — 공용 도구 tools/make_block_practice.py 로 만든다.

영상(공식 MV)에 자막이 없어 가사는 싣지 않는다(정식 발매곡 가사를 받아써 옮기지 않는다). 코드·마디·버스킹(코드)만.
코드: 음원을 demucs 로 목소리와 반주로 나누고, 반주(no_vocals)를 tools/chord_simple.py 로 자동 채보 → chords.json.
beats.json 이 없어서 코드 경계에 가장 잘 맞는 반 마디 격자를 잰다.
사용: python3 build.py
"""
import os
import subprocess
import sys

VID = 'YapsFDcGe_s'                       # make_block_practice.py 가 이 줄에서 영상 ID 를 읽는다
S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(S))
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'make_block_practice.py'), 'kaede-guitar',
                '--title', '楓', '--artist', 'スピッツ', '--out', 'index.html',
                '--src', '가사는 싣지 않았습니다. 영상·음원: YouTube スピッツ 「楓」 공식 MV(spitzclips).'], check=True)
