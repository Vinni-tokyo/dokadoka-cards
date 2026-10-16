#!/usr/bin/env python3
"""スピッツ 「楓」 블록 연습 페이지(../index.html) — 공용 도구 tools/make_block_practice.py 로 만든다.

영상(공식 MV)에 자막이 없어 가사는 싣지 않는다(정식 발매곡 가사를 받아써 옮기지 않는다). 코드·마디·버스킹(코드)만.
📝 내 가사: 사용자가 가사 사이트에서 붙여 넣은 가사(그 브라우저에만 저장)를 노래 구간(src/phrases.json — 시각만, tools/vocal_phrases.py)에 맞춘다.
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
                '--title', '楓', '--artist', 'スピッツ', '--out', 'index.html', '--my-lyrics',
                '--src', '가사는 싣지 않았습니다(아래 가사 사이트 링크로 봅니다). 영상·음원: YouTube スピッツ 「楓」 공식 MV(spitzclips).',
                # 정식 가사 사이트 링크만 단다(가사 본문은 싣지 않는다)
                '--link', '📖 가사 · 歌ネット|https://www.uta-net.com/song/10397/|작사·작곡 草野正宗 · 새 탭',
                '--link', '📖 가사 · うたてん|https://utaten.com/lyric/ja00006655/|후리가나 포함 · 새 탭',
                '--link', '📖 가사 · J-Lyric|https://j-lyric.net/artist/a000603/l0001b8.html|새 탭',
                '--link', '🎸 歌ネット 코드 악보|https://www.uta-net.com/chord/10397/|카포·간단 코드 · 새 탭'], check=True)
