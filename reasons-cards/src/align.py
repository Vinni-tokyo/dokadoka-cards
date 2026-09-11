#!/usr/bin/env python3
"""가사 원문(lyrics.txt) 을 음성 인식 단어 시각(words.json, faster-whisper word_timestamps) 에 맞춰
   줄마다 시작·끝 시각을 구하고 subtitles.srt 로 쓴다.
   - 노래는 자막이 없으므로 이 절차로 타이밍을 만든다. 인식 결과의 단어 오류는 순서 정렬(부분 일치)로 흡수한다.
   - 매칭 실패한 줄은 앞뒤 줄 사이를 균등 보간하고 REPORT 에 표시한다. 그 줄은 fixes.txt(id|시작|끝) 로 손으로 고칠 수 있다.
   사용법: python3 src/align.py <words.json>"""
import sys, os, re, json
from difflib import SequenceMatcher
HERE = os.path.dirname(os.path.abspath(__file__))
words = json.load(open(sys.argv[1], encoding='utf-8'))
norm = lambda w: re.sub(r"[^a-z0-9]", '', w.lower().replace("'", ''))
W = [(norm(w['w']), w['s'], w['e']) for w in words if norm(w['w'])]

lines = []
for ln in open(os.path.join(HERE, 'lyrics.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if ln.startswith('#'): continue
    lines.append(ln.strip())          # 빈 줄도 유지(구간 경계)
cards = [(i + 1, t) for i, t in enumerate([l for l in lines if l])]

# 손 보정: id|시작|끝
fixes = {}
fp = os.path.join(HERE, 'fixes.txt')
if os.path.exists(fp):
    for ln in open(fp, encoding='utf-8'):
        ln = ln.strip()
        if not ln or ln.startswith('#'): continue
        i, s, e = ln.split('|')[:3]; fixes[int(i)] = (float(s), float(e))

def best_window(tokens, start, horizon_sec=28.0):
    """start 이후 horizon_sec 초 안에서 tokens 와 가장 비슷한 연속 구간을 찾는다(너무 멀리 건너뛰지 않게 시간으로 제한)"""
    n = len(tokens); best = (0.0, None, None)
    t0 = W[start][1] if start < len(W) else 1e9
    for a in range(start, len(W)):
        if W[a][1] - t0 > horizon_sec: break
        for L in range(max(1, n - 2), n + 3):
            b = a + L
            if b > len(W): break
            r = SequenceMatcher(None, tokens, [w[0] for w in W[a:b]]).ratio()
            if r > best[0]: best = (r, a, b)
    return best

out, ptr, report = [], 0, []
for cid, text in cards:
    toks = [norm(t) for t in text.split() if norm(t)]
    if cid in fixes:
        out.append([cid, text, fixes[cid][0], fixes[cid][1], 'FIX']); continue
    r, a, b = best_window(toks, ptr)
    if a is not None and r >= 0.45:
        out.append([cid, text, W[a][1], W[b - 1][2], 'ok %.2f' % r]); ptr = b
    else:
        out.append([cid, text, None, None, 'MISS %.2f' % r]); report.append(cid)   # 포인터는 그대로(다음 줄이 이어서 찾는다)

# 미매칭 줄: 앞뒤 사이 균등 보간
for k, row in enumerate(out):
    if row[2] is not None: continue
    prev_e = next((out[j][3] for j in range(k - 1, -1, -1) if out[j][3] is not None), 0.0)
    nxt = next((j for j in range(k + 1, len(out)) if out[j][2] is not None), None)
    nxt_s = out[nxt][2] if nxt is not None else prev_e + 3.0 * (nxt - k if nxt else 1)
    # 연속 미매칭 개수만큼 등분
    run = 1; j = k + 1
    while j < len(out) and out[j][2] is None: run += 1; j += 1
    pos = 0; jj = k
    while jj < k + run:
        seg = (nxt_s - prev_e) / run
        out[jj][2] = round(prev_e + seg * pos + 0.05, 2); out[jj][3] = round(prev_e + seg * (pos + 1) - 0.05, 2); pos += 1; jj += 1
# 끝 시각은 다음 줄 시작을 넘지 않게, 최소 길이 0.8초
for k in range(len(out)):
    if k + 1 < len(out): out[k][3] = min(out[k][3], out[k + 1][2])
    out[k][3] = max(out[k][3], out[k][2] + 0.8)

def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return '%02d:%02d:%06.3f' % (h, m, s)
with open(os.path.join(HERE, 'subtitles.srt'), 'w', encoding='utf-8') as f:
    for cid, text, s, e, st in out:
        f.write('%d\n%s --> %s\n%s\n\n' % (cid, ts(s).replace('.', ','), ts(e).replace('.', ','), text))
print('줄', len(out), '| 매칭', sum(1 for o in out if o[4].startswith('ok')), '| 손보정', sum(1 for o in out if o[4] == 'FIX'), '| 보간', len(report), (report or ''))
for cid, text, s, e, st in out:
    print('%2d %6.1f-%6.1f %-8s %s' % (cid, s, e, st, text))
