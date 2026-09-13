#!/usr/bin/env python3
"""학습 음원(mp3)의 음량을 통일한다. edge-tts 출력은 -16 LUFS 안팎으로 유튜브 음악보다 훨씬 크게 들리므로
EBU R128 loudnorm 으로 I=-22 LUFS, TP=-3 dBFS 로 낮춘다(파일 자체를 바꿔 iOS 처럼 audio.volume 을 무시하는 환경에도 적용).
정규화한 파일은 <audio>/norm.json 에 기록해 두 번 하지 않는다.

  사용: python3 tools/normalize_audio.py [<앱폴더> ...]      (없으면 전 앱)
        make_study_audio.py 가 새 파일을 만든 뒤에도 같은 함수를 부른다."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = 'loudnorm=I=-22:TP=-3:LRA=11'

def normalize_dir(adir, workers=8):
    if not os.path.isdir(adir): return 0
    mark = os.path.join(adir, 'norm.json')
    done = set(json.load(open(mark, encoding='utf-8'))) if os.path.exists(mark) else set()
    todo = [f for f in os.listdir(adir) if f.endswith('.mp3') and f not in done]
    def one(fn):
        src = os.path.join(adir, fn); tmp = src + '.tmp.mp3'
        r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', TARGET, '-ar', '24000', '-codec:a', 'libmp3lame', '-q:a', '4', tmp], capture_output=True)
        if r.returncode == 0 and os.path.getsize(tmp) > 0: os.replace(tmp, src); return fn
        if os.path.exists(tmp): os.remove(tmp)
        return None
    ok = []
    with ThreadPoolExecutor(workers) as ex:
        for fn in ex.map(one, todo):
            if fn: ok.append(fn)
    done.update(ok)
    json.dump(sorted(done), open(mark, 'w', encoding='utf-8'))
    return len(ok)

if __name__ == '__main__':
    apps = [a.strip('/') for a in sys.argv[1:]] or sorted(d for d in os.listdir(ROOT) if d.endswith('-cards') and os.path.isdir(os.path.join(ROOT, d, 'src', 'audio')))
    for app in apps:
        n = normalize_dir(os.path.join(ROOT, app, 'src', 'audio'))
        print(f'{app}: {n}개 정규화')
