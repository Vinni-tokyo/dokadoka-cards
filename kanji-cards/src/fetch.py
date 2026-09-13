#!/usr/bin/env python3
"""외부 사전 2종을 받아 이 사이트의 한자 분만 src/dict.json 으로 추린다.

   Unihan  (Unicode)      https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip   — 부수·획수·한국음·음독/훈독
   KanjiVG (CC BY-SA 3.0) https://github.com/KanjiVG/kanjivg/releases                — 구성 트리·부수 표시·획순

   원본은 ~/.cache/dokadoka-kanji/ 에 두고 리포에는 추린 dict.json 만 넣는다.
   대상 한자 목록은 build.py 가 만든 src/kanji_list.txt (한 줄 한 자). 없으면 build.py 를 먼저 돌린다.
"""
import gzip, io, json, os, re, sys, urllib.request, zipfile
import xml.etree.ElementTree as ET

S = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.expanduser('~/.cache/dokadoka-kanji'); os.makedirs(CACHE, exist_ok=True)
UNIHAN = 'https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip'
KVG_API = 'https://api.github.com/repos/KanjiVG/kanjivg/releases/latest'

def get(url, fn):
    p = os.path.join(CACHE, fn)
    if not os.path.exists(p):
        print('받는 중:', url); urllib.request.urlretrieve(url, p)
    return p

lst = os.path.join(S, 'kanji_list.txt')
if not os.path.exists(lst):
    sys.exit('kanji_list.txt 가 없습니다. 먼저 python3 src/build.py 를 실행하세요')
K = [l.strip() for l in io.open(lst, encoding='utf-8') if l.strip()]
# 정자체도 같이 뽑는다(한국음을 정자체에서 가져오기 위해)
ky = {}
for ln in io.open(os.path.join(S, 'kyujitai.txt'), encoding='utf-8'):
    if ln.startswith('#') or '|' not in ln: continue
    a, b = ln.strip().split('|'); ky[a] = b
want = set(K) | set(ky.values())
cps = {'U+%04X' % ord(c): c for c in want}

# --- Unihan ---
FIELDS = ('kHangul', 'kRSUnicode', 'kTotalStrokes', 'kJapanese', 'kDefinition')
U = {c: {} for c in want}
with zipfile.ZipFile(get(UNIHAN, 'Unihan.zip')) as z:
    for name in z.namelist():
        if not name.endswith('.txt'): continue
        for ln in io.TextIOWrapper(z.open(name), encoding='utf-8'):
            if ln.startswith('#') or '\t' not in ln: continue
            cp, f, v = ln.rstrip('\n').split('\t', 2)
            if cp in cps and f in FIELDS: U[cps[cp]][f] = v

# --- KanjiVG ---
kvg_zip = os.path.join(CACHE, 'kanjivg.xml.gz')
if not os.path.exists(kvg_zip):
    rel = json.load(urllib.request.urlopen(KVG_API))
    url = next(a['browser_download_url'] for a in rel['assets'] if a['name'].endswith('.xml.gz'))
    get(url, 'kanjivg.xml.gz')
NS = '{http://kanjivg.tagaini.net}'
root = ET.parse(gzip.open(kvg_zip)).getroot()
V = {}
def tree(g):
    out = []
    for c in g.findall('g'):
        e = c.get(NS + 'element')
        if e:
            node = {'e': e}
            if c.get(NS + 'radical'): node['r'] = 1
            if c.get(NS + 'position'): node['p'] = c.get(NS + 'position')
            sub = tree(c)
            if sub: node['c'] = sub
            out.append(node)
        else:
            out += tree(c)
    return out
def rnd(d):   # 좌표 소수 1자리
    return re.sub(r'(\d+\.\d\d+)', lambda m: ('%.1f' % float(m.group(1))).rstrip('0').rstrip('.'), d)
for kj in root.iter('kanji'):
    g = kj.find('g')
    if g is None: continue
    ch = g.get(NS + 'element')
    if ch in want and ch not in V:
        V[ch] = {'tree': tree(g), 'paths': [rnd(p.get('d')) for p in g.iter('path')]}

out = {}
for c in K:
    u = U.get(c, {}); v = V.get(c, {})
    row = {}
    if 'kRSUnicode' in u:
        rs = u['kRSUnicode'].split()[0]; n = int(rs.split('.')[0].rstrip("'"))
        row['rad'] = chr(0x2F00 + n - 1); row['radn'] = n
    if 'kTotalStrokes' in u: row['strokes'] = int(u['kTotalStrokes'].split()[0])
    hg = u.get('kHangul')
    if c in ky and U.get(ky[c], {}).get('kHangul'):     # 신자체는 정자체의 한국음을 우선 (体→體 체, 円→圓 원)
        hg = U[ky[c]]['kHangul']
    if hg: row['ko'] = [x.split(':')[0] for x in hg.split()]
    if c in ky: row['trad'] = ky[c]
    if 'kJapanese' in u: row['ja'] = u['kJapanese'].split()
    if 'kDefinition' in u: row['en'] = u['kDefinition']
    if v: row['tree'] = v['tree']; row['paths'] = v['paths']
    out[c] = row
json.dump(out, io.open(os.path.join(S, 'dict.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('dict.json:', len(out), '자 · 부수', sum(1 for r in out.values() if 'rad' in r), '· 한국음', sum(1 for r in out.values() if 'ko' in r),
      '· 구성', sum(1 for r in out.values() if 'tree' in r), '· 획순', sum(1 for r in out.values() if 'paths' in r),
      '· 크기 %.0f KB' % (os.path.getsize(os.path.join(S, 'dict.json')) / 1024))
print('한국음 없음:', ''.join(c for c, r in out.items() if 'ko' not in r) or '없음')
