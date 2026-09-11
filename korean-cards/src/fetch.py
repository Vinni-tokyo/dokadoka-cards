#!/usr/bin/env python3
"""YouTube 動画 → src/series/<id>/ の下ごしらえ。字幕(SRT)と meta.json(公式チャプター入り)を用意し、
カード一覧(cards.txt)を出す。訳(ja.txt)・表現(study.txt)・手直し(fixes.txt)は人が書く。

  python3 src/fetch.py <URL または 動画ID> <series_id> [--auto]
    --auto : 手動字幕があっても自動生成字幕を使う
"""
import io, json, os, re, shutil, subprocess, sys, tempfile

S    = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(S))            # dokadoka-cards/
sys.path.insert(0, S)
from build import read_cues, segment, segment_manual                  # build.py は __main__ 保護済み

def ytdlp():
    cand = os.path.join(ROOT, '.venv', 'bin', 'yt-dlp')
    return cand if os.path.exists(cand) else shutil.which('yt-dlp') or sys.exit('yt-dlp が見つかりません')

def vid_of(s):
    m = re.search(r'(?:v=|youtu\.be/|shorts/|embed/)([A-Za-z0-9_-]{11})', s)
    return m.group(1) if m else (s if re.fullmatch(r'[A-Za-z0-9_-]{11}', s) else sys.exit('動画IDを読めません'))

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 2: sys.exit(__doc__)
    prefer_auto = '--auto' in sys.argv
    vid, sid = vid_of(args[0]), args[1]
    out = os.path.join(S, 'series', sid)
    if os.path.exists(os.path.join(out, 'subtitles.srt')):
        sys.exit(f'{out}/subtitles.srt が既にあります。上書きしたければ先に消してください')
    Y = ytdlp(); url = f'https://www.youtube.com/watch?v={vid}'
    base = [Y, '--js-runtimes', 'node', '--skip-download']

    meta = json.loads(subprocess.run(base + ['--dump-json', '--', url], capture_output=True, text=True, check=True).stdout)
    has_manual = 'ko' in (meta.get('subtitles') or {})
    has_auto   = 'ko' in (meta.get('automatic_captions') or {})
    use_manual = has_manual and not prefer_auto
    if not (use_manual or has_auto): sys.exit('韓国語字幕がありません')

    tmp = tempfile.mkdtemp()
    flag = '--write-subs' if use_manual else '--write-auto-subs'
    subprocess.run(base + [flag, '--sub-lang', 'ko', '--sub-format', 'srt', '--convert-subs', 'srt',
                           '-o', os.path.join(tmp, '%(id)s.%(ext)s'), '--', url],
                   capture_output=True, text=True, check=True)
    srt = next((os.path.join(tmp, f) for f in os.listdir(tmp) if f.endswith('.srt')), None) or sys.exit('SRT を取得できませんでした')
    os.makedirs(out, exist_ok=True)
    shutil.copy(srt, os.path.join(out, 'subtitles.srt')); shutil.rmtree(tmp)

    cues = read_cues(os.path.join(out, 'subtitles.srt'))
    cards = segment_manual(cues) if use_manual else segment(cues)
    with io.open(os.path.join(out, 'cards.txt'), 'w', encoding='utf-8') as f:
        f.write('# 訳を書くための一覧。build には使われない\n')
        for c in cards: f.write(f"{c['id']}|{c['ko']}\n")

    ch = meta.get('chapters') or []
    chapters = ([[f'c{i+1:02d}', int(c['start_time']), c['title'], c['title'], 1 if '인터뷰' in c['title'] else 0]
                 for i, c in enumerate(ch)] if ch else [['all', 0, '全編', '전체', 0]])
    title = meta.get('title', '')
    m = {'id': sid, **({'source': 'manual'} if use_manual else {}), 'videoId': vid,
         'title': title, 'titleKo': title,            # title(日本語) は後で人が直す
         'subtitle': '', 'subtitleKo': '', 'seal': '韓',
         'chapters': chapters, 'merges': [],
         '_source': {'channel': meta.get('channel'), 'upload': meta.get('upload_date'),
                     'duration': meta.get('duration'), 'subs': 'manual' if use_manual else 'auto',
                     'todo': ['title(ja)', 'subtitle/subtitleKo', 'chapters の ja ラベル', 'ja.txt', 'study.txt', 'fixes.txt']}}
    io.open(os.path.join(out, 'meta.json'), 'w', encoding='utf-8').write(json.dumps(m, ensure_ascii=False, indent=2) + '\n')

    print(f"series/{sid}  ←  {vid}  「{title}」")
    print(f"  字幕: {'手動(公式)' if use_manual else '自動生成'}  · カード {len(cards)} 枚  · チャプター {len(ch)} 個  · {meta.get('duration',0)//60}分")
    print(f"  次: ja.txt / study.txt / fixes.txt を書き、meta.json の日本語ラベルを直してから  python3 src/build.py")

if __name__ == '__main__':
    main()
