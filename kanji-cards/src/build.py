#!/usr/bin/env python3
"""한자 카드 빌드. 일본어 앱들의 산출물(../../*/Japanese-*Cards.html)에서 DATA[].kj 를 전부 읽어
   한자·한자어 표를 만들고, dict.json(Unihan+KanjiVG 추림)과 직접 쓴 표(hun/parts/hanja_ko/kyujitai)를 붙여 앱을 만든다.

   순서:  python3 src/build.py  →  (처음 한 번) python3 src/fetch.py  →  python3 src/build.py
"""
import io, json, os, re, glob, collections

S = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(S); SITE = os.path.dirname(ROOT)
APPS = collections.OrderedDict([   # 폴더 → (표시 이름, 정렬)  ※ SnowMan(japanese-cards)은 kj 가 없어 제외
    ('yubisaki-cards', 'ゆびさきと恋々'), ('bokuyaba-cards', '僕やば'), ('frieren-cards', '프리렌'),
    ('milky-cards', '밀키☆서브웨이'), ('hatsukoi-cards', 'First Love 메이킹'), ('firstlove-cards', 'First Love'), ('mika-cards', '나카시마 미카'),
])
KANJI_RE = re.compile(r'[一-鿿]')

def table(fn, n=2):
    out = {}
    p = os.path.join(S, fn)
    if not os.path.exists(p): return out
    for ln in io.open(p, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln.strip() or ln.startswith('#'): continue
        parts = ln.split('|')
        if len(parts) < 2: continue
        out[parts[0].strip()] = [x.strip() for x in parts[1:]] if n > 2 else parts[1].strip()
    return out

HUN = table('hun.txt'); PARTS = table('parts.txt'); KYU = table('kyujitai.txt')
HANJA = {k: [x for x in v if x and '없음' not in x] for k, v in table('hanja_ko.txt', 3).items()}

# --- 1. 앱 산출물에서 모으기 ---
words = collections.OrderedDict(); kanji = collections.OrderedDict(); hun_seen = collections.defaultdict(collections.Counter)
for app in APPS:
    for f in sorted(glob.glob(os.path.join(SITE, app, 'Japanese-*Cards.html'))):
        page = os.path.basename(f)
        D = json.loads(re.search(r'const DATA = (\[.*?\]);\n', io.open(f, encoding='utf-8').read(), re.S).group(1))
        for c in D:
            for w in c.get('kj') or []:
                head, rd, mean, kr, parts = w[:5]
                W = words.setdefault(head, {'w': head, 'rd': rd, 'ko': mean, 'kr': kr, 'k': [p[0] for p in parts if KANJI_RE.match(p[0])],
                                            'n': 0, 'apps': collections.Counter(), 'ex': None})
                W['n'] += 1; W['apps'][app] += 1
                ex = {'ja': c['ja'], 'ko': c['ko'], 'app': app, 'page': page, 'id': c['id'], 's': c['s']}
                if W['ex'] is None or (8 <= len(c['ja']) < len(W['ex']['ja'])) or (len(W['ex']['ja']) < 8 < len(c['ja'])): W['ex'] = ex
                for k, h in parts:
                    if not KANJI_RE.match(k): continue           # 々 같은 부호 제외
                    K = kanji.setdefault(k, {'k': k, 'n': 0, 'words': collections.Counter(), 'apps': collections.Counter()})
                    K['n'] += 1; K['words'][head] += 1; K['apps'][app] += 1; hun_seen[k][h] += 1

# --- 2. 훈음 통일 ---
conflict = []
for k, K in kanji.items():
    if k in HUN: K['hun'] = HUN[k]
    else:
        c = hun_seen[k]
        if len(c) > 1: conflict.append((k, dict(c)))
        K['hun'] = c.most_common(1)[0][0]
    K['eum'] = K['hun'].split()[-1] if K['hun'] else ''

# --- 3. 등급(사이트 빈도) ---
def level(n): return 1 if n >= 20 else 2 if n >= 8 else 3 if n >= 3 else 4 if n >= 2 else 5
for K in kanji.values(): K['lv'] = level(K['n'])

io.open(os.path.join(S, 'kanji_list.txt'), 'w', encoding='utf-8').write('\n'.join(kanji) + '\n')

# --- 4. 사전 붙이기 ---
dp = os.path.join(S, 'dict.json')
DICT = json.load(io.open(dp, encoding='utf-8')) if os.path.exists(dp) else {}
if not DICT: print('!! dict.json 이 없습니다. python3 src/fetch.py 를 실행한 뒤 다시 빌드하세요 (부수·구성·획순 없이 계속)')
eum_bad, no_ko, no_part = [], [], collections.Counter()
def walk(tree):
    for n in tree:
        yield n['e']
        if 'c' in n: yield from walk(n['c'])
for k, K in kanji.items():
    d = DICT.get(k, {})
    for f in ('rad', 'radn', 'strokes', 'trad', 'ja', 'tree', 'paths'):
        if f in d: K[f] = d[f]
    if 'ko' in d:
        K['ko'] = d['ko']
        if K['eum'] and K['eum'] not in d['ko']: eum_bad.append((k, K['hun'], d['ko']))
    elif DICT: no_ko.append(k)
    if 'rad' in K: K['radname'] = PARTS.get(K['rad']) or PARTS.get(chr(ord(K['rad']) - 0x2F00 + 0x4E00), '')   # 강희부수 → 이름
    if k in HANJA and HANJA[k]: K['hj'] = HANJA[k]
    for e in walk(K.get('tree', [])):
        if e not in kanji and e not in PARTS: no_part[e] += 1

# 강희 부수 문자(U+2F00~)는 NFKC 로 통상 한자로 바꿔 표시한다 (⽈→曰)
import unicodedata
KX = lambda c: unicodedata.normalize('NFKC', c)
RADNAME = {'一':'한 일','丨':'뚫을 곤','丶':'점 주','丿':'삐침 별','乙':'새 을','亅':'갈고리 궐','二':'두 이','亠':'돼지해머리','人':'사람 인','儿':'어진사람 인','入':'들 입','八':'여덟 팔','冂':'멀 경','冖':'민갓머리','冫':'이수변','几':'안석 궤','凵':'위튼입구','刀':'칼 도','力':'힘 력','勹':'쌀포몸','匕':'비수 비','匚':'튼입구몸','匸':'감출혜몸','十':'열 십','卜':'점 복','卩':'병부 절','厂':'민엄호','厶':'마늘 모','又':'또 우','口':'입 구','囗':'큰입구몸','土':'흙 토','士':'선비 사','夂':'뒤져올 치','夊':'천천히걸을 쇠','夕':'저녁 석','大':'큰 대','女':'여자 녀','子':'아들 자','宀':'갓머리','寸':'마디 촌','小':'작을 소','尢':'절름발이 왕','尸':'주검 시','屮':'왼손 좌','山':'메 산','巛':'개미허리','工':'장인 공','己':'몸 기','巾':'수건 건','干':'방패 간','幺':'작을 요','广':'엄호','廴':'민책받침','廾':'스물입발','弋':'주살 익','弓':'활 궁','彐':'튼가로왈','彡':'터럭 삼','彳':'두인변','心':'마음 심','戈':'창 과','戶':'지게 호','手':'손 수','支':'지탱할 지','攴':'칠 복','文':'글월 문','斗':'말 두','斤':'도끼 근','方':'모 방','无':'없을 무','日':'날 일','曰':'가로 왈','月':'달 월','木':'나무 목','欠':'하품 흠','止':'그칠 지','歹':'죽을사변','殳':'갖은등글월문','毋':'말 무','比':'견줄 비','毛':'털 모','氏':'각시 씨','气':'기운 기','水':'물 수','火':'불 화','爪':'손톱 조','父':'아비 부','爻':'점괘 효','爿':'나뭇조각 장','片':'조각 편','牙':'어금니 아','牛':'소 우','犬':'개 견','玄':'검을 현','玉':'구슬 옥','瓜':'오이 과','瓦':'기와 와','甘':'달 감','生':'날 생','用':'쓸 용','田':'밭 전','疋':'짝 필','疒':'병질엄','癶':'필발머리','白':'흰 백','皮':'가죽 피','皿':'그릇 명','目':'눈 목','矛':'창 모','矢':'화살 시','石':'돌 석','示':'보일 시','禸':'짐승발자국 유','禾':'벼 화','穴':'구멍 혈','立':'설 립','竹':'대 죽','米':'쌀 미','糸':'실 사','缶':'장군 부','网':'그물 망','羊':'양 양','羽':'깃 우','老':'늙을 로','而':'말이을 이','耒':'가래 뢰','耳':'귀 이','聿':'붓 율','肉':'고기 육','臣':'신하 신','自':'스스로 자','至':'이를 지','臼':'절구 구','舌':'혀 설','舛':'어그러질 천','舟':'배 주','艮':'괘이름 간','色':'빛 색','艸':'풀 초','虍':'범호엄','虫':'벌레 충','血':'피 혈','行':'다닐 행','衣':'옷 의','襾':'덮을 아','見':'볼 견','角':'뿔 각','言':'말씀 언','谷':'골 곡','豆':'콩 두','豕':'돼지 시','豸':'갖은돼지시변','貝':'조개 패','赤':'붉을 적','走':'달릴 주','足':'발 족','身':'몸 신','車':'수레 거','辛':'매울 신','辰':'별 진','辵':'책받침','邑':'고을 읍','酉':'닭 유','釆':'분별할 변','里':'마을 리','金':'쇠 금','長':'길 장','門':'문 문','阜':'언덕 부','隶':'미칠 이','隹':'새 추','雨':'비 우','靑':'푸를 청','非':'아닐 비','面':'낯 면','革':'가죽 혁','韋':'다룸가죽 위','韭':'부추 구','音':'소리 음','頁':'머리 혈','風':'바람 풍','飛':'날 비','食':'밥 식','首':'머리 수','香':'향기 향','馬':'말 마','骨':'뼈 골','高':'높을 고','髟':'터럭발머리','鬥':'싸울 투','鬯':'울창주 창','鬲':'솥 력','鬼':'귀신 귀','魚':'물고기 어','鳥':'새 조','鹵':'소금 로','鹿':'사슴 록','麥':'보리 맥','麻':'삼 마','黃':'누를 황','黍':'기장 서','黑':'검을 흑','黹':'바느질할 치','黽':'맹꽁이 맹','鼎':'솥 정','鼓':'북 고','鼠':'쥐 서','鼻':'코 비','齊':'가지런할 제','齒':'이 치','龍':'용 룡','龜':'거북 귀','龠':'피리 약'}
for K in kanji.values():
    if 'rad' in K:
        K['rad'] = KX(K['rad']); K['radname'] = RADNAME.get(K['rad'], K.get('radname', ''))

# --- 5. 출력 데이터 ---
WOUT = [{'w': W['w'], 'rd': W['rd'], 'ko': W['ko'], 'kr': W['kr'], 'k': W['k'], 'n': W['n'],
         'apps': [a for a in APPS if a in W['apps']], 'ex': W['ex']} for W in sorted(words.values(), key=lambda W: -W['n'])]
KOUT = []
for K in sorted(kanji.values(), key=lambda K: -K['n']):
    row = {f: K[f] for f in ('k', 'hun', 'n', 'lv', 'rad', 'radname', 'strokes', 'ko', 'trad', 'tree', 'paths', 'hj') if f in K}
    if 'ja' in K: row['on'] = [x for x in K['ja'] if re.match(r'^[ァ-ヺー]+$', x)]; row['kun'] = [x for x in K['ja'] if re.match(r'^[ぁ-ゖー.-]+$', x)]
    row['words'] = [w for w, _ in K['words'].most_common()]
    row['apps'] = [a for a in APPS if a in K['apps']]
    KOUT.append(row)
# --- 5-1. 소리 가족(형성자): 같은 부품을 가진 한자들이 같은 음독을 낼 때 ---
KB = {r['k']: r for r in KOUT}
def walk_e(t):
    for n in t:
        yield n['e']
        if 'c' in n: yield from walk_e(n['c'])
has = collections.defaultdict(set)
for r in KOUT:
    for e in set(walk_e(r.get('tree', []))): has[e].add(r['k'])
    has[r['k']].add(r['k'])                                   # 부품 자신이 사이트 한자면 가족에 넣는다 (反 ハン)
cand = []
for pc, ks in has.items():
    if len(ks) < 2: continue
    byon = collections.defaultdict(set)
    for c in ks:
        for on in KB[c].get('on', [])[:2]: byon[on].add(c)    # 주 음독 2개만
    for on, ms in byon.items():
        ratio = len(ms) / len(ks)
        if len(ms) >= 2 and (ratio >= 0.4 or (len(ms) >= 3 and ratio >= 0.3)):
            cand.append((pc, on, frozenset(ms), len(ks)))
# 구성원이 같은 가족은 하나로: 부품은 더 구체적인 것(포함 한자 수가 적은 것), 음독은 모두 나열
import unicodedata
def base_on(on):   # 청탁음 통일: ボウ→ホウ, ガ→カ (탁점·반탁점 제거)
    return ''.join(ch for ch in unicodedata.normalize('NFD', on) if ch not in '\u3099\u309a')
# 1) 부품+기본음이 같으면 한 가족으로 합친다(방/보우 청탁 짝). 2) 구성원이 같은 가족은 더 구체적인 부품 하나만 남긴다
byfam = {}
for pc, on, ms, tot in cand:
    f = byfam.setdefault((pc, base_on(on)), {'p': pc, 'on': [], 'ks': set(), 'tot': tot})
    if on not in f['on']: f['on'].append(on)
    f['ks'] |= ms
merged = {}
for f in sorted(byfam.values(), key=lambda f: f['tot']):
    key = frozenset(f['ks'])
    if key in merged:
        for on in f['on']:
            if on not in merged[key]['on']: merged[key]['on'].append(on)
        continue
    merged[key] = {'p': f['p'], 'on': f['on'], 'ks': sorted(f['ks'], key=lambda c: -KB[c]['n'])}
FAM = sorted(merged.values(), key=lambda f: (-len(f['ks']), f['p']))
for i, f in enumerate(FAM):
    for c in f['ks']: KB[c].setdefault('fam', []).append(i)
FAMK = len({c for f in FAM for c in f['ks']})

N, NW = len(KOUT), len(WOUT)
tp = os.path.join(S, 'tpl.html')
if os.path.exists(tp):
    html = (io.open(tp, encoding='utf-8').read()
        .replace('/*__KANJI__*/', json.dumps(KOUT, ensure_ascii=False, separators=(',', ':')))
        .replace('/*__WORDS__*/', json.dumps(WOUT, ensure_ascii=False, separators=(',', ':')))
        .replace('/*__PARTS__*/', json.dumps(PARTS, ensure_ascii=False, separators=(',', ':')))
        .replace('/*__FAM__*/', json.dumps(FAM, ensure_ascii=False, separators=(',', ':')))
        .replace('/*__APPS__*/', json.dumps(APPS, ensure_ascii=False))
        .replace('__N__', str(N)).replace('__NW__', str(NW)))
    for old in glob.glob(os.path.join(ROOT, 'Kanji*-Cards.html')): os.remove(old)
    OUT = os.path.join(ROOT, 'Kanji%d-Cards.html' % N)
    io.open(OUT, 'w', encoding='utf-8').write(html)
    print('생성:', OUT, '(%.0f KB)' % (os.path.getsize(OUT) / 1024))
else:
    print('tpl.html 없음 → 데이터 검사만')

# --- 6. 보고 ---
lv = collections.Counter(K['lv'] for K in KOUT)
print('한자 %d · 한자어 %d · 작품 %d' % (N, NW, len(APPS)), '| 등급', dict(sorted(lv.items())))
print('부수 %d · 획수 %d · 한국음 %d · 구성 %d · 획순 %d · 정자체 %d · 한국어 한자어 %d' % tuple(sum(1 for K in KOUT if f in K) for f in ('rad', 'strokes', 'ko', 'tree', 'paths', 'trad', 'hj')))
print('소리 가족 %d · 포함 한자 %d · 3자 이상 %d' % (len(FAM), FAMK, sum(1 for f in FAM if len(f['ks']) >= 3)))
print('훈음 불일치(미통일):', conflict or '없음')
print('훈음의 음 ≠ 한국음:', eum_bad or '없음')
print('한국음 없음:', ''.join(no_ko) or '없음')
print('이름 없는 구성 요소:', ' '.join(f'{e}{n}' for e, n in no_part.most_common(40)) or '없음', ('(총 %d종)' % len(no_part) if no_part else ''))
