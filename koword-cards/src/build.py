#!/usr/bin/env python3
"""한국어 영상 앱들에 흩어진 단어·표현을 모아 독립 암기앱을 만든다.

  ../*-cards/Korean-*.html 의 STUDY(표현 E / 단어 V) → 중복 제거 → 발음·예문·출처를 붙여 tpl.html 에 주입.
  한자 앱(kanji-cards)과 같은 구조. 유튜브 없이 돌고, 「▶ 장면」만 영상 앱을 연다.
"""
import io, json, os, re, glob, sys, datetime, collections
S    = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(S)                 # koword-cards/
SITE = os.path.dirname(ROOT)              # dokadoka-cards/
sys.path.insert(0, S)
from pron import pron

def load(path):
    """앱 HTML 에서 SERIES(다편) 또는 DATA/STUDY(단편) 를 꺼낸다"""
    h = io.open(path, encoding='utf-8').read()
    m = re.search(r'const SERIES = (\[.*?\]);', h, re.S)
    if m:
        return [(s['id'], s.get('title') or s.get('titleKo') or s['id'], s['data'], s['study'])
                for s in json.loads(m.group(1))]
    D = re.search(r'const DATA = (\[.*?\]);', h, re.S)
    T = re.search(r'const STUDY = (\[.*?\]);', h, re.S)
    if not (D and T): return []
    sid = (re.search(r"const SID = '([^']*)'", h) or [None, os.path.basename(os.path.dirname(path))])[1]
    ttl = (re.search(r'<title>([^<]*)</title>', h) or [None, sid])[1]
    return [(sid, ttl, json.loads(D.group(1)), json.loads(T.group(1)))]

APPS, ITEMS, seen = [], [], {}
for path in sorted(glob.glob(os.path.join(SITE, '*-cards', 'Korean-*.html'))):
    app  = os.path.basename(os.path.dirname(path))
    page = os.path.basename(path)
    if app == os.path.basename(ROOT): continue
    for sid, title, data, study in load(path):
        ai = len(APPS); APPS.append({'a': app, 'p': page, 's': sid, 'n': title})
        by = {c['id']: c for c in data}
        for r in study:
            if not r.get('ko') or not r.get('ja'): continue
            key = (r['t'], r['ko'])
            cids = r.get('cids') or []
            if key in seen:
                it = seen[key]
                it['src'].append({'i': ai, 'n': len(cids)})
                if r.get('note') and not it.get('note'): it['note'] = r['note']
                continue
            it = {'t': r['t'], 'ko': r['ko'], 'ja': r['ja'], 'src': [{'i': ai, 'n': len(cids)}]}
            if r.get('note'): it['note'] = r['note']
            p = pron(r['ko'])
            if p != r['ko']: it['pr'] = p          # 철자와 소리가 다를 때만
            c = by.get(r.get('ex'))
            if c: it['ex'] = {'ko': c['ko'], 'ja': c['ja'], 's': c['s'], 'id': c['id'], 'i': ai}
            seen[key] = it; ITEMS.append(it)

# 등장 횟수(빈도) 순으로 정렬 — 자주 나온 것부터 외우게
for it in ITEMS: it['n'] = sum(s['n'] for s in it['src'])
ITEMS.sort(key=lambda x: (-x['n'], -len(x['src']), x['ko']))
for i, it in enumerate(ITEMS): it['i'] = i

# 표현을 어미·문형으로 묶는다 (한자 앱의 「소리 가족」에 대응)
PAT = [('-거든(요)','거든'),('-잖아(요)','잖아'),('-더라(고)','더라'),('-네(요)','네'),('-ㄹ게(요)','ㄹ게'),
       ('-ㄹ까(요)','ㄹ까'),('-아/어야 되다','야 되'),('-아/어 보다',' 보'),('-아/어 주다',' 주'),
       ('-고 싶다','고 싶'),('-ㄹ 수 있다','ㄹ 수 있'),('-지 마','지 마'),('-아/어도 되다','도 되'),
       ('-는데(요)','는데'),('-니까','니까'),('-려고','려고'),('-면서','면서'),('-군(요)','구나')]
FAM = collections.defaultdict(list)
for it in ITEMS:
    if it['t'] != 'E': continue
    for name, needle in PAT:
        if needle in it['ko']: FAM[name].append(it['i'])
FAM = {k: v for k, v in sorted(FAM.items(), key=lambda kv: -len(kv[1])) if len(v) >= 2}

N  = len(ITEMS)
NE = sum(1 for x in ITEMS if x['t'] == 'E')
NP = sum(1 for x in ITEMS if 'pr' in x)
print(f'앱 {len(APPS)}편 · 항목 {N}개 (표현 {NE} · 단어 {N-NE}) · 발음 주의 {NP} · 문형 {len(FAM)}묶음')
for a in APPS: print(f"  {a['a']:<18} {a['s']:<12} {sum(1 for x in ITEMS for s in x['src'] if s['i']==APPS.index(a)):>4}개")

tpl = os.path.join(S, 'tpl.html')
if not os.path.exists(tpl):
    print('tpl.html 없음 → 데이터 검사만'); sys.exit(0)
out = os.path.join(ROOT, f'Korean-Words{N}-Cards.html')
html = (io.open(tpl, encoding='utf-8').read()
        .replace('/*__ITEMS__*/', json.dumps(ITEMS, ensure_ascii=False, separators=(',', ':')))
        .replace('/*__APPS__*/',  json.dumps(APPS,  ensure_ascii=False, separators=(',', ':')))
        .replace('/*__FAM__*/',   json.dumps(FAM,   ensure_ascii=False, separators=(',', ':')))
        .replace('__N__', str(N)).replace('__NE__', str(NE)).replace('__NP__', str(NP))
        .replace('__BUILD__', datetime.datetime.now().strftime('%Y-%m-%d %H:%M')))
for old in glob.glob(os.path.join(ROOT, 'Korean-Words*-Cards.html')): os.remove(old)
io.open(out, 'w', encoding='utf-8').write(html)
print('생성:', out, '(%.0f KB)' % (os.path.getsize(out)/1024))
