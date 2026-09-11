"""YouTube 자동생성 자막(큐당 한 줄, 시간이 겹치는 형식) → 카드 분할.
   각 줄의 실제 발화 구간 = 이 줄의 시작 ~ 다음 줄의 시작(단, 이 줄의 종료를 넘지 않게).
   화자 표기가 없으므로 화자·속마음은 ko.txt 의 5번째 칸에서 손으로 지정한다(build.py 가 붙임)."""
import re, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
raw = open(os.path.join(HERE, 'subtitles.srt'), encoding='utf-8-sig').read()

END_AT = 1290          # 21:30 부터 ED 곡. 자동자막이 가사를 못 알아들으므로 뺀다
cues = []
for b in re.split(r'\n\s*\n', raw.strip()):
    L = [l.strip() for l in b.strip().split('\n') if l.strip()]
    if len(L) < 3: continue
    m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', L[1])
    if not m: continue
    g = list(map(int, m.groups()))
    t = ' '.join(L[2:]).strip()
    if re.fullmatch(r'(\[[^\]]+\]\s*)+', t): continue                 # [音楽] [拍手] 만 있는 줄
    t = re.sub(r'\[[^\]]+\]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    if not t: continue
    st = g[0]*3600+g[1]*60+g[2]+g[3]/1000
    if st >= END_AT: continue                                        # ED 가사(오인식)는 제외
    cues.append({'s': st, 'e': g[4]*3600+g[5]*60+g[6]+g[7]/1000, 't': t})
for i, c in enumerate(cues):                                          # 겹치는 종료 시각을 다음 줄 시작으로 잘라 준다
    if i + 1 < len(cues): c['e'] = min(c['e'], cues[i+1]['s'])
    c['e'] = max(c['e'], c['s'] + 0.6)

# 병합: 간격 ≤ 1.0초, 합쳐서 ≤ 30자, 앞 줄이 문장 끝(よ/ね/か/だ/た/ない/ます 등)으로 끝나지 않을 때만 잇는다
GAP, MAXLEN = 1.0, 30
END = re.compile(r'(よ|ね|か|だ|た|ない|ます|です|う|ぞ|な|の|よね|だろ|じゃん|でしょ|って|さ|わ|よな)$')
segs = []
for c in cues:
    prev = segs[-1] if segs else None
    if (prev and c['s'] - prev['e'] <= GAP and len(prev['t']) + len(c['t']) + 1 <= MAXLEN
            and not END.search(prev['t'])):
        prev['t'] += ' ' + c['t']; prev['e'] = c['e']
    else:
        segs.append(dict(c))

out = [{'id': i, 's': round(g['s'], 2), 'e': round(g['e'], 2), 'ja': g['t']} for i, g in enumerate(segs, 1)]
json.dump(out, open(os.path.join(HERE, 'segs.json'), 'w'), ensure_ascii=False, indent=1)
if __name__ == '__main__':
    print('자막 줄:', len(cues), '→ 카드:', len(out))
    L = [len(o['ja']) for o in out]
    print('길이: 평균 %.1f 중앙 %d 최대 %d' % (sum(L)/len(L), sorted(L)[len(L)//2], max(L)))
