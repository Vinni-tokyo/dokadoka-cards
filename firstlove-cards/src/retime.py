"""줄 시각 보정 — 영상에 새겨진 일본어 자막(노란색) 표시 구간 + 음성 인식 단어 시각.
입력
  video_cues.json : 프레임(10fps)에서 노란 자막 픽셀을 추적해 얻은 자막 큐 [{s,e,w}]  (scratch 의 sheet1/2.png 대조표로 확인)
  asr_words.json  : faster-whisper(medium, 가사 프롬프트) 단어 시각. 반주 구간에서 가사를 환각하므로 큐 창 안에서만 쓴다
  subtitles.srt   : 줄 텍스트(시각은 여기서 새로 쓴다)
규칙
  - 각 줄의 자막 큐 창 [cue_s-2, cue_e+2] 안에서 가사와 가장 비슷한 단어 구간을 찾아 음성 시작·끝(ws, we)을 얻는다.
  - 시작: 자막은 발성보다 조금 먼저 뜨므로 자막 시작(cue_s). 단 자막 검출이 늦게 잡힌 경우(ws < cue_s-0.8)는 음성 시작.
  - 끝:   자막은 반주 동안 남으므로 음성 끝(we)+0.4초(노래는 마지막 음을 끈다). 단 we 가 큐 밖(> cue_e+0.5)이거나 못 찾으면 자막 끝.
  - 앞 줄 끝과 다음 줄 시작이 겹치면: 다음 줄의 발성이 아직 시작 전이면 다음 줄 시작을 뒤로 미루고(자막이 먼저 뜬 것뿐),
    이미 발성 중이면 앞 줄 끝을 자른다.
"""
import json, re, os
from difflib import SequenceMatcher
S = os.path.dirname(os.path.abspath(__file__))
cues = json.load(open(os.path.join(S, 'video_cues.json')))
words = json.load(open(os.path.join(S, 'asr_words.json')))
MAP = {1:(0,0), 2:(1,2), 3:(3,4), 4:(5,5), 5:(6,6), 6:(7,7), 7:(8,8), 8:(9,9), 9:(10,10), 10:(11,11), 11:(12,12),
       12:(13,13), 13:(14,14), 14:(15,17), 15:(18,18), 16:(19,19), 17:(20,20), 18:(21,21), 19:(22,22), 20:(23,23),
       21:(24,24), 22:(25,25), 23:(26,26), 24:(27,27), 25:(28,28), 26:(29,29), 27:(30,31), 28:(32,32)}
CUE_END_OVERRIDE = {27: 218.0}        # 27번은 뒤에 노란 장면이 겹쳐 큐가 잘렸다
def norm(t): return re.sub(r'[^0-9a-z぀-ヿ一-鿿]', '', t.lower())
def tsec(t):
    h, m, s = t.replace(',', '.').split(':'); return int(h)*3600 + int(m)*60 + float(s)
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')
def asr_span(text, lo, hi):
    """창 안 단어열에서 가사와 가장 비슷한 연속 구간의 (시작, 끝, 유사도)"""
    W = [(norm(w['w']), w['s'], w['e']) for w in words if lo <= w['s'] <= hi and norm(w['w'])]
    q = norm(text); best = (0.0, None, None)
    for a in range(len(W)):
        acc = ''
        for b in range(a, len(W)):
            acc += W[b][0]
            if len(acc) > len(q) * 1.6 + 2: break
            r = SequenceMatcher(None, q, acc).ratio()
            if r > best[0]: best = (r, a, b)
    r, a, b = best
    return (W[a][1], W[b][2], r) if a is not None and r >= 0.5 else (None, None, r)
rows = []
for blk in open(os.path.join(S, 'subtitles.srt'), encoding='utf-8').read().strip().split('\n\n'):
    ln = blk.split('\n'); a, b = ln[1].split(' --> '); rows.append([int(ln[0]), tsec(a), tsec(b), '\n'.join(ln[2:])])
print(' id |  cue_s  cue_e |   ws     we   r  |  new_s  new_e')
for r in rows:
    i, os_, oe, text = r
    a, b = MAP[i]; cs, ce = cues[a]['s'], CUE_END_OVERRIDE.get(i, cues[b]['e'])
    ws, we, sim = asr_span(text, cs - 2, ce + 2)
    s = cs if (ws is None or ws >= cs - 0.8) else ws
    e = min(we + 0.4, ce + 0.5) if (we is not None and cs < we <= ce + 0.5) else ce
    r[1], r[2] = s, e; r.append(ws); r.append(we); r.append(cs)
    print('%3d | %6.2f %6.2f | %6s %6s %.2f | %6.2f %6.2f%s' % (i, cs, ce, '%.2f' % ws if ws else '—', '%.2f' % we if we else '—', sim, s, e, '' if abs(s - os_) < 0.3 and abs(e - oe) < 0.3 else '  (구 %.2f–%.2f)' % (os_, oe)))
for k in range(len(rows) - 1):
    a, b = rows[k], rows[k+1]
    pws, pwe, pcs = a[4], a[5], a[6]; nws, nwe, ncs = b[4], b[5], b[6]
    chained = nws is not None and pwe is not None and nws <= pwe + 0.05        # 음성 인식이 단어를 이어 붙인 경계(다음 줄 시작 시각은 못 믿는다)
    if chained and ncs < pwe:                                                 # 자막이 먼저 바뀐 채 노래가 이어짐: 경계는 음성 끝
        a[2] = pwe + 0.1
    elif b[1] < a[2] + 0.05:
        if chained: b[1] = max(ncs + 0.05, min(a[2] + 0.05, ncs + 0.25)); a[2] = b[1] - 0.05   # 자막이 늦게 바뀜 = 앞 줄이 끌린 것. 자막+0.25 까지만 미룬다
        elif nws is None or nws - 0.1 > a[2]: b[1] = a[2] + 0.05               # 다음 줄 발성 전(또는 불확실): 시작을 미룬다
        else: a[2] = max(a[1] + 0.6, min(b[1], nws) - 0.05)                  # 발성 중: 앞 줄을 자른다
    if a[2] > b[1] - 0.05 and b[1] > a[1] + 0.6: a[2] = b[1] - 0.05
    print('   경계 %d→%d: 끝 %.2f / 다음 시작 %.2f%s' % (a[0], b[0], a[2], b[1], ' (이어 부름)' if chained and ncs < pwe else ''))
with open(os.path.join(S, 'subtitles.srt'), 'w', encoding='utf-8') as f:
    for i, s, e, t, *_ in rows: f.write(f'{i}\n{ts(s)} --> {ts(e)}\n{t}\n\n')
