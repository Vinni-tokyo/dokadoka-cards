#!/usr/bin/env python3
"""가사 줄 ↔ 음성 인식 단어 시각을 앞뒤를 다 보고 맞춘다(동적 계획법).

<앱>/src/align.py 는 줄마다 「지금 자리에서 가장 비슷한 구간」을 고르고 앞으로만 간다.
한 줄이 못 맞으면(인식이 뭉개진 줄) 커서가 엉뚱한 곳으로 튀어 그 뒤 줄이 줄줄이 틀린다 —
후렴이 여러 번 도는 찬양에서 실제로 그랬다(38줄 중 21줄 보간).

여기서는 모든 줄의 자리를 한꺼번에 정한다. 줄은 순서대로(앞 줄의 끝 ≤ 다음 줄의 시작),
전체 비용(1−유사도 의 합)이 가장 작은 배치를 고른다. 못 맞는 줄은 「건너뜀」 비용을 물고
앞뒤 줄 사이로 보간한다. 한 줄이 뭉개져도 나머지 줄은 제자리를 찾는다.

사용: python3 tools/align_dp.py <lyrics.txt> <words.json> <subtitles.srt 출력>
      (lyrics.txt 의 빈 줄은 구간 경계라 무시한다)
"""
import json
import re
import sys
from difflib import SequenceMatcher

SKIP = 0.72          # 못 맞는 줄을 건너뛰는 비용 (1−유사도 가 이보다 크면 건너뛴다)


def norm(t):
    return re.sub(r'[^0-9a-z぀-ヿ一-鿿]', '', t.lower())


def main(lyr, wj, out):
    words = json.load(open(wj, encoding='utf-8'))
    W = [(norm(w['w']), w['s'], w['e']) for w in words if norm(w['w'])]
    chars, cidx = [], []
    for i, (t, s, e) in enumerate(W):
        for ch in t:
            chars.append(ch); cidx.append(i)
    S = ''.join(chars); N = len(S)
    lines = [l.strip() for l in open(lyr, encoding='utf-8') if l.strip() and not l.startswith('#')]
    Q = [norm(l) for l in lines]
    M = len(lines)

    # 줄마다: 시작 위치 a → (가장 좋은 유사도, 그때 길이)
    best = []
    for q in Q:
        n = len(q); row = [(0.0, 0)] * (N + 1)
        if n:
            Ls = range(max(2, int(n * 0.6)), int(n * 1.5) + 2)
            for a in range(N):
                br, bL = 0.0, 0
                for L in Ls:
                    if a + L > N: break
                    r = SequenceMatcher(None, q, S[a:a + L]).ratio()
                    if r > br: br, bL = r, L
                row[a] = (br, bL)
        best.append(row)

    INF = 1e9
    # dp[i][a]: 0..i 줄을 놓고 i 줄이 a 에서 시작할 때의 최소 비용. 건너뛴 줄은 길이 0 으로 a 에 둔다.
    dp = [[INF] * (N + 1) for _ in range(M)]
    back = [[None] * (N + 1) for _ in range(M)]
    for i in range(M):
        # 이전 줄의 「끝 위치 ≤ a」인 것 중 최소 — 끝 위치별 접두 최소로 O(N)
        if i == 0:
            prevmin = [(0.0, None)] * (N + 1)
        else:
            endmin = [(INF, None)] * (N + 2)
            for b in range(N + 1):
                if dp[i - 1][b] < INF:
                    e = b + (back[i - 1][b][1] if back[i - 1][b] else 0)
                    e = min(e, N)
                    if dp[i - 1][b] < endmin[e][0]: endmin[e] = (dp[i - 1][b], b)
            prevmin = [(INF, None)] * (N + 1); cur = (INF, None)
            for a in range(N + 1):
                if endmin[a][0] < cur[0]: cur = endmin[a]
                prevmin[a] = cur
        for a in range(N + 1):
            pm, pb = prevmin[a]
            if pm >= INF: continue
            r, L = best[i][a] if a < N else (0.0, 0)
            c = 1.0 - r
            if c < SKIP and L > 0:
                dp[i][a] = pm + c; back[i][a] = (pb, L, r)
            else:
                dp[i][a] = pm + SKIP; back[i][a] = (pb, 0, 0.0)
    # 되짚기
    a = min(range(N + 1), key=lambda x: dp[M - 1][x]); place = [None] * M
    for i in range(M - 1, -1, -1):
        pb, L, r = back[i][a]; place[i] = (a, L, r); a = pb if pb is not None else 0
    # 시각
    res = []
    for i, (a, L, r) in enumerate(place):
        if L > 0:
            res.append([W[cidx[a]][1], W[cidx[min(a + L - 1, N - 1)]][2], r])
        else:
            res.append([None, None, 0.0])
    # 못 맞은 줄: 앞뒤 사이를 글자 수 비율로 보간
    i = 0
    while i < M:
        if res[i][0] is None:
            j = i
            while j < M and res[j][0] is None: j += 1
            s = res[i - 1][1] if i > 0 else (res[j][0] - 3.0 * (j - i) if j < M else 0.0)
            e = res[j][0] if j < M else s + 3.0 * (j - i)
            tot = sum(len(Q[k]) for k in range(i, j)) or 1; t = s
            for k in range(i, j):
                d = (e - s) * len(Q[k]) / tot; res[k] = [t, t + d, 0.0]; t += d
            i = j
        else:
            i += 1
    # 겹침 정리(앞 줄 끝이 다음 줄 시작을 넘지 않게)
    for i in range(1, M):
        if res[i][0] < res[i - 1][1]: res[i - 1][1] = res[i][0]

    def ts(x):
        h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
        return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')
    with open(out, 'w', encoding='utf-8') as f:
        for i, (s, e, r) in enumerate(res, 1):
            f.write(f'{i}\n{ts(s)} --> {ts(e)}\n{lines[i - 1]}\n\n')
    hit = sum(1 for x in res if x[2] > 0)
    print(f'줄 {M} | 매칭 {hit} | 보간 {M - hit} | 유사도 평균 {sum(x[2] for x in res if x[2] > 0) / max(1, hit):.2f}')
    for i, (s, e, r) in enumerate(res, 1):
        print(f'{i:3d} {s:7.2f}-{e:7.2f} ({e - s:4.1f}s) r={r:.2f}{"  ← 보간" if r == 0 else ""}  {lines[i - 1]}')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(__doc__); sys.exit(1)
    main(*sys.argv[1:])
