"""공식 일본어 자막(화자명 포함) → 카드 분할.
   자막 형식:  'Iwamoto: 대사'  /  '-대사' (화자 미상, 한 큐에 여럿)  /  '［화면 자막］' (대사 아님)
   같은 큐 안에서 화자 표시 없이 이어지는 줄은 앞 대사의 연속이다."""
import re, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
raw = open(os.path.join(HERE, 'subtitles.srt'), encoding='utf-8-sig').read()

cues = []
for b in re.split(r'\n\s*\n', raw.strip()):
    L = [l.rstrip() for l in b.strip().split('\n') if l.strip()]
    if len(L) < 3: continue
    m = re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)', L[1])
    if not m: continue
    g = list(map(int, m.groups()))
    cues.append({'s': g[0]*3600+g[1]*60+g[2]+g[3]/1000,
                 'e': g[4]*3600+g[5]*60+g[6]+g[7]/1000, 'lines': L[2:]})

# 화자 표시가 없는 줄 가운데, 문맥상 화자가 분명한 것만 손으로 지정한다
SPK_FIX = {'いや なんか5年間': 'Watanabe'}

pieces, caps = [], []          # pieces = 대사 조각, caps = 화면 자막(연도·행사 설명)
for c in cues:
    incap, cur = False, None
    for ln in c['lines']:
        t = ln.strip()
        if incap or t.startswith('［'):
            incap = not t.endswith('］')
            body = t.strip('［］').strip()
            if caps and caps[-1]['open']: caps[-1]['t'] += ' ' + body   # 두 줄짜리 화면 자막
            else: caps.append({'s': c['s'], 'e': c['e'], 't': body, 'open': True})
            caps[-1]['open'] = incap
            if not incap: pass
            continue
        m = re.match(r'^([A-Za-z]+):\s*(.*)$', t)
        if m:
            cur = {'s': c['s'], 'e': c['e'], 'spk': m.group(1), 't': m.group(2).strip()}
            pieces.append(cur); continue
        if t.startswith('-'):
            cur = {'s': c['s'], 'e': c['e'], 'spk': '', 't': t[1:].strip()}
            pieces.append(cur); continue
        if cur is not None:                       # 같은 큐 안의 이어지는 줄
            cur['t'] = (cur['t'] + ' ' + t).strip(); continue
        cur = {'s': c['s'], 'e': c['e'], 'spk': SPK_FIX.get(t, ''), 't': t}
        pieces.append(cur)

# 같은 화자가 바로 이어 말한 짧은 조각은 한 장으로 합친다 (문장 끝이면 끊는다)
GAP, MAXLEN = 0.35, 34
segs = []
for p in pieces:
    prev = segs[-1] if segs else None
    if (prev and prev['spk'] and prev['spk'] == p['spk']
            and p['s'] - prev['e'] <= GAP
            and len(prev['t']) + len(p['t']) + 1 <= MAXLEN
            and not re.search(r'[。！？!?]\s*$', prev['t'])):
        prev['t'] = prev['t'] + ' ' + p['t']; prev['e'] = p['e']
    else:
        segs.append(dict(p))

out = [{'s': round(g['s'], 2), 'e': round(g['e'], 2), 'ja': g['t'], 'spk': g['spk']} for g in segs]
# 같은 화면 자막이 여러 큐에 걸쳐 반복되면 하나로 (표시 구간은 이어 붙인다)
merged = []
for cp in caps:
    if merged and merged[-1]['t'] == cp['t'] and cp['s'] - merged[-1]['e'] < 0.5: merged[-1]['e'] = cp['e']
    else: merged.append({'s': round(cp['s'], 2), 'e': round(cp['e'], 2), 't': cp['t']})

# 화면 자막도 읽기 재료이므로 카드에 넣는다 (spk='Cap'). 시각순으로 섞고 id 를 매긴다
out += [{'s': cp['s'], 'e': cp['e'], 'ja': cp['t'], 'spk': 'Cap'} for cp in merged]
out.sort(key=lambda x: (x['s'], x['spk'] != 'Cap'))
for i, o in enumerate(out, 1): o['id'] = i

json.dump(out, open(os.path.join(HERE, 'segs.json'), 'w'), ensure_ascii=False, indent=1)
if __name__ == '__main__':
    print('대사 조각:', len(pieces), '→ 대사 카드:', len(segs), '+ 화면 자막:', len(merged), '= 카드', len(out))
    L = [len(o['ja']) for o in out]
    print('길이: 평균 %.1f 중앙 %d 최대 %d' % (sum(L)/len(L), sorted(L)[len(L)//2], max(L)))
    from collections import Counter
    print('화자:', dict(Counter(o['spk'] or '?' for o in out)))
