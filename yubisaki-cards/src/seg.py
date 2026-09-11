"""방송용 일본어 CC 자막 → 카드 분할.
   자막 형식:  （화자）대사  /  〈속마음〉 (화자 태그 없으면 주인공 雪)  /  （효과음）  /  ♪ 가사
   화자 태그는 화자가 바뀔 때만 붙으므로, 태그 없는 발화는 '직전에 태그가 붙은 발화 화자'로 추정한다(inf=1).
   추정이 틀린 곳은 SPK_FIX 로 고친다(키 = 큐 번호)."""
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
    cues.append({'n': int(L[0]), 's': g[0]*3600+g[1]*60+g[2]+g[3]/1000,
                 'e': g[4]*3600+g[5]*60+g[6]+g[7]/1000, 't': ' '.join(L[2:])})

SFX = re.compile(r'音|鼓動|チャイム|メロディー|英語|振動|足音')     # （…）안에 이 말이 있으면 효과음
HERO = '雪'                                                      # 〈속마음〉의 주인
SPK_FIX = {35: '外国人', 41: '外国人', 136: 'りん', 138: '逸臣', 141: 'りん', 150: '逸臣', 160: '逸臣',
           179: '逸臣', 190: '逸臣', 191: 'りん', 200: '雪', 202: '逸臣', 229: '桜志', 46: '逸臣', 161: 'りん'}   # {큐번호: 화자} 검토 결과
tag_re = re.compile(r'（([^（）]+?)）')

def clean(t):
    t = re.sub(r'([一-龥々]+)\([ぁ-ゖー]+\)', r'\1', t)             # 본문 후리가나 橋元(はしもと) → 橋元
    return re.sub(r'\s+', ' ', t).strip()

pieces, last_spoken, n_lyric, n_sfx = [], '', 0, 0
for c in cues:
    t = c['t']
    if t.startswith('♪') or t.endswith('♪'): n_lyric += 1; continue
    # 화자 태그 위치로 조각을 나눈다
    parts, pos, cur_spk = [], 0, None
    for m in tag_re.finditer(t):
        name = m.group(1)
        if SFX.search(name): continue                                # 효과음 태그
        if pos < m.start() and t[pos:m.start()].strip(): parts.append((cur_spk, t[pos:m.start()]))
        cur_spk = re.sub(r'\(.*?\)', '', name).strip(); pos = m.end()
    if t[pos:].strip(): parts.append((cur_spk, t[pos:]))
    parts = [(s, tag_re.sub(' ', x)) for s, x in parts]               # 남은 효과음 괄호 제거
    parts = [(s, x) for s, x in parts if x.strip()]
    if not parts: n_sfx += 1; continue
    for spk, body in parts:
        body = clean(body)
        th = body.startswith('〈') or body.endswith('〉')
        body = clean(body.strip('〈〉'))
        if not body: continue
        inf = 0
        if spk is None:
            if c['n'] in SPK_FIX: spk = SPK_FIX[c['n']]
            elif th: spk = HERO
            else: spk, inf = last_spoken, 1
        elif c['n'] in SPK_FIX: spk = SPK_FIX[c['n']]
        if not th: last_spoken = spk
        pieces.append({'n': c['n'], 's': c['s'], 'e': c['e'], 'spk': spk, 'th': int(th), 'inf': inf, 't': body})

# 같은 화자·같은 종류(대사/속마음)의 짧은 조각을 잇는다
GAP, MAXLEN = 0.6, 26
segs = []
for p in pieces:
    prev = segs[-1] if segs else None
    if (prev and prev['spk'] == p['spk'] and prev['th'] == p['th'] and p['s'] - prev['e'] <= GAP
            and len(prev['t']) + len(p['t']) + 1 <= MAXLEN
            and not re.search(r'[。！？!?…―]\s*$', prev['t'])):
        prev['t'] += ' ' + p['t']; prev['e'] = p['e']
    else:
        segs.append(dict(p))

out = []
for i, g in enumerate(segs, 1):
    row = {'id': i, 's': round(g['s'], 2), 'e': round(g['e'], 2), 'ja': g['t'], 'spk': g['spk'], 'cue': g['n']}
    if g['th']: row['th'] = 1
    if g['inf']: row['inf'] = 1
    out.append(row)
json.dump(out, open(os.path.join(HERE, 'segs.json'), 'w'), ensure_ascii=False, indent=1)
if __name__ == '__main__':
    print('큐:', len(cues), '| 가사 제외:', n_lyric, '| 효과음만 제외:', n_sfx, '| 조각:', len(pieces), '→ 카드:', len(out))
    L = [len(o['ja']) for o in out]
    print('길이: 평균 %.1f 중앙 %d 최대 %d | 속마음 %d | 화자 추정 %d' % (sum(L)/len(L), sorted(L)[len(L)//2], max(L), sum(1 for o in out if o.get('th')), sum(1 for o in out if o.get('inf'))))
    from collections import Counter
    print('화자:', dict(Counter(o['spk'] for o in out)))
