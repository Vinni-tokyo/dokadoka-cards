#!/usr/bin/env python3
"""가사(lyrics.txt) 줄 ↔ faster-whisper 단어 시각(words.json) 정렬 → subtitles.srt  (일본어·영어 혼용 가사용)
   - 단어를 이어 붙인 문자열에서 각 줄과 가장 비슷한 구간을 순서대로 찾는다(문자 단위 유사도, 앞으로만 진행).
   - 유사도가 낮은 줄은 앞뒤 줄 사이를 균등 보간하고 REPORT 에 표시한다. fixes.txt(id|시작|끝) 로 손 보정 가능.
   사용법: python3 src/align.py <words.json>"""
import sys, os, re, json
from difflib import SequenceMatcher
HERE = os.path.dirname(os.path.abspath(__file__))
words = json.load(open(sys.argv[1], encoding='utf-8'))
def norm(t):
    t = t.lower()
    return re.sub(r'[^0-9a-z぀-ヿ一-鿿가-힣]', '', t)   # 한자·가나·한글·영숫자만
W = [(norm(w['w']), w['s'], w['e']) for w in words if norm(w['w'])]
chars, cidx = [], []                                                # 이어 붙인 문자열과 각 문자의 단어 번호
for i, (t, s, e) in enumerate(W):
    for ch in t: chars.append(ch); cidx.append(i)
S = ''.join(chars)

lines = [ln.rstrip('\n') for ln in open(os.path.join(HERE, 'lyrics.txt'), encoding='utf-8') if not ln.startswith('#')]
cards = [(i + 1, t.strip()) for i, t in enumerate([l for l in lines if l.strip()])]
fixes = {}
fp = os.path.join(HERE, 'fixes.txt')
if os.path.exists(fp):
    for ln in open(fp, encoding='utf-8'):
        ln = ln.strip()
        if not ln or ln.startswith('#'): continue
        i, s, e = ln.split('|')[:3]; fixes[int(i)] = (float(s), float(e))

res, cursor, report = {}, 0, []
for cid, text in cards:
    q = norm(text); n = len(q)
    if not n: continue
    best = (0.0, None, None)
    # 시간 제한: 앞 줄의 끝에서 60초 이상 뒤로는 건너뛰지 않는다(반복 후렴을 뒤쪽에 잘못 맞추는 것을 막는다)
    t_prev = W[cidx[cursor - 1]][2] if cursor > 0 else 0.0
    hi = cursor
    while hi < len(S) and W[cidx[hi]][1] <= t_prev + 60.0: hi += 1
    GOOD = 0.85 if n <= 4 else 0.72                                 # 이만큼 비슷하면 더 뒤를 보지 않는다
    for a in range(cursor, hi):
        for L in range(max(2, int(n * 0.6)), int(n * 1.5) + 2):
            b = a + L
            if b > len(S): break
            r = SequenceMatcher(None, q, S[a:b]).ratio()
            if r > best[0]: best = (r, a, b)
        if best[0] >= GOOD and best[1] is not None and best[1] <= a: break
    r, a, b = best
    if a is not None and r >= 0.45:
        wi, wj = cidx[a], cidx[b - 1]
        res[cid] = (W[wi][1], W[wj][2], r); cursor = b
    else:
        res[cid] = None; report.append((cid, text, round(r, 2)))

ids = [c for c, _ in cards]
for k, cid in enumerate(ids):                                       # 못 찾은 줄: 앞뒤 사이 보간
    if res.get(cid) is None:
        prev = next((res[ids[j]] for j in range(k - 1, -1, -1) if res.get(ids[j])), None)
        nxt = next((res[ids[j]] for j in range(k + 1, len(ids)) if res.get(ids[j])), None)
        s = prev[1] + 0.3 if prev else 0.0; e = nxt[0] - 0.3 if nxt else s + 4.0
        res[cid] = (s, max(s + 1.0, e), 0.0)
for cid, (s, e) in fixes.items(): res[cid] = (s, e, 1.0)
# 겹침 정리: 다음 줄 시작보다 늦게 끝나지 않게
for k in range(len(ids) - 1):
    s, e, r = res[ids[k]]; s2 = res[ids[k + 1]][0]
    if e > s2 - 0.05: res[ids[k]] = (s, max(s + 0.6, s2 - 0.05), r)

def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')
with open(os.path.join(HERE, 'subtitles.srt'), 'w', encoding='utf-8') as f:
    for cid, text in cards:
        s, e, r = res[cid]; f.write(f'{cid}\n{ts(s)} --> {ts(e)}\n{text}\n\n')
print('줄', len(cards), '| 매칭', sum(1 for c in ids if res[c][2] > 0), '| 보간', len(report), '| 손보정', len(fixes))
for cid, text in cards:
    s, e, r = res[cid]; print(f'{cid:3d} {s:7.2f}-{e:7.2f} ({e-s:4.1f}s) r={r:.2f}  {text}')
if report: print('REPORT 보간된 줄:', report)
