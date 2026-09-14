#!/usr/bin/env python3
"""국립국어원 「국제 통용 한국어 표준 교육과정」 어휘·문법 등급 목록에서
이 앱에 쓰는 분량만 추려 src/levels.json 을 만든다.

  원본 xlsx(약 700KB)는 ~/.cache/dokadoka-koword/ 에만 두고 리포에 넣지 않는다(한자 앱 fetch.py 와 같은 방식).
  출처: 국립국어원 2017년 국제 통용 한국어 표준 교육과정 적용 연구(4단계) 어휘·문법 등급 목록
        https://www.korean.go.kr/front/reportData/reportDataView.do?mn_id=207&report_seq=932
        공공누리 제1유형 (출처표시)
"""
import io, json, os, re, sys, zipfile, collections, urllib.request
from xml.etree import ElementTree as ET

S     = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.expanduser('~/.cache/dokadoka-koword')
XLSX  = os.path.join(CACHE, 'nikl-levels.xlsx')
URL   = ('https://www.korean.go.kr/common/download.do?file_path=reportData'
         '&c_file_name=157339df-1904-443a-b1a9-d6d34578ba93.xlsx&o_file_name=levels.xlsx')
NS    = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
sys.path.insert(0, S)

def download():
    os.makedirs(CACHE, exist_ok=True)
    if os.path.exists(XLSX) and os.path.getsize(XLSX) > 100000:
        print(f'  캐시 사용: {XLSX} ({os.path.getsize(XLSX)//1024} KB)'); return
    print('  내려받는 중 …')
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as r, io.open(XLSX, 'wb') as f:
        f.write(r.read())
    print(f'  받음: {os.path.getsize(XLSX)//1024} KB')

def sheet_rows(z, path, shared):
    for row in ET.fromstring(z.read(path)).iter(NS + 'row'):
        cells = {}
        for c in row.iter(NS + 'c'):
            ref = re.match(r'([A-Z]+)', c.get('r') or 'A').group(1)
            v = c.find(NS + 'v')
            if v is None or v.text is None: continue
            cells[ref] = shared[int(v.text)] if c.get('t') == 's' and v.text.isdigit() else v.text
        yield cells

def lv(s):                                    # '3급' → 3
    d = re.sub(r'\D', '', s or '')
    return int(d) if d else 0

def load():
    z = zipfile.ZipFile(XLSX)
    shared = [''.join(t.text or '' for t in si.iter(NS + 't'))
              for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall(NS + 'si')]
    names = [s.get('name') for s in ET.fromstring(z.read('xl/workbook.xml')).iter(NS + 'sheet')]
    idx = {n: f'xl/worksheets/sheet{i+1}.xml' for i, n in enumerate(names)}

    words = {}                                # 표제어 → (급, 품사, 길잡이말)
    for r in list(sheet_rows(z, idx['어휘'], shared))[1:]:
        w = re.sub(r'\d+$', '', (r.get('D') or '').strip())   # 가격02 → 가격
        if not w: continue
        g = lv(r.get('C'))
        if g and (w not in words or g < words[w][0]):
            words[w] = (g, (r.get('E') or '').strip(), (r.get('F') or '').strip())

    gram = []                                 # [급, 분류, 대표형, [관련형…], 의미]
    for r in list(sheet_rows(z, idx['문법'], shared))[1:]:
        head = (r.get('E') or '').strip()
        if not head: continue
        rel = [x.strip() for x in re.split(r'[/,·]', (r.get('F') or '')) if x.strip()]
        gram.append([lv(r.get('C')), (r.get('D') or '').strip(), head, rel, (r.get('G') or '').strip()])
    return words, gram

def main():
    download()
    words, gram = load()
    print(f'  원본: 어휘 {len(words)} · 문법 {len(gram)}')

    from build import collect                 # 앱이 실제로 쓰는 455개를 그대로 가져온다
    items, _apps = collect()

    def variants(k):
        yield k
        if k.endswith('하다'): yield k[:-2]
        for s in ('요','아요','어요','었어','았어','어','아','다','한','은','는','이','가','을','를','도','만'):
            if k.endswith(s) and len(k) > len(s) + 1: yield k[:-len(s)]
        yield k + '하다'

    keep_w, keep_g, n_w, n_g = {}, {}, 0, 0
    for it in items:
        ko = it['ko']
        for v in variants(ko):
            if v in words:
                keep_w[v] = words[v]; n_w += 1; break
        else:                                 # 어휘에 없으면 문법에서 찾는다(표현은 대개 이쪽)
            best = None
            for g, kind, head, rel, mean in gram:
                for form in [head] + rel:
                    if len(form) >= 2 and form in ko and (best is None or len(form) > len(best[2])):
                        best = (g, kind, form, mean)
            if best:
                keep_g[best[2]] = [best[0], best[1], best[3]]; n_g += 1

    out = {'words': {k: list(v) for k, v in keep_w.items()}, 'gram': keep_g,
           'src': '국립국어원 국제 통용 한국어 표준 교육과정(2017) 어휘·문법 등급 목록 · 공공누리 제1유형'}
    p = os.path.join(S, 'levels.json')
    io.open(p, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n')
    dist = collections.Counter([v[0] for v in keep_w.values()] + [v[0] for v in keep_g.values()])
    print(f'  추림: 어휘 {len(keep_w)} · 문법 {len(keep_g)}  → {n_w + n_g}/{len(items)} 항목에 급수')
    print('  급수 분포:', ' · '.join(f'{g}급 {n}' for g, n in sorted(dist.items())))
    print(f'  생성: {p} ({os.path.getsize(p)//1024} KB)')

if __name__ == '__main__':
    main()
