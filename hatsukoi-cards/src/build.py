import io, json, os, re, subprocess, sys, base64
S = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, os.path.join(S, 'seg.py')], check=True, stdout=subprocess.DEVNULL)
OUT = os.path.join(os.path.dirname(S), 'Japanese-Hatsukoi172-Cards.html')
VID = 'OUx16Z5PpII'

# 장면 = 화제 전환 기준 타임라인 (키, 시작초, 한국어, 일본어)
SCENES = [
 ('intro',  0,   '작품 첫인상',            '作品の第一印象'),
 ('cast',   12,  '배역 소개 · 야에와 하루미치', '役の紹介 · 也英と晴道'),
 ('build',  57,  '캐릭터 만들기',           'キャラクターの作り方'),
 ('duo',    125, '두 배우의 호흡',          '二人の共演'),
 ('young',  205, '젊은 시절을 연기한 배우들',   '若い時代を演じた二人'),
 ('food',   321, '워크숍과 음식',           'ワークショップと食事'),
 ('locate', 382, '로케이션 · 홋카이도와 기지',  'ロケ地 · 北海道と基地'),
 ('script', 467, '기획과 각본',             '企画と脚本'),
 ('color',  515, '대본과 색 · 감독의 고집',    '台本と色 · 監督のこだわり'),
 ('msg',    588, '시청자에게',              '見る人へ'),
]

SPEAKERS = [('', '화자 미상', '話者不明', 0)]

KANJI_RE = re.compile(r'[一-鿿々]')

ko = {}
for ln in open(os.path.join(S, 'ko.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'):
        continue
    p = ln.split('|')
    ko[int(p[0])] = (p[1].strip(), p[2].strip() if len(p) > 2 else '', p[3].strip() if len(p) > 3 else '')

segs = json.load(open(os.path.join(S, 'segs.json'), encoding='utf-8'))
missing = [s['id'] for s in segs if s['id'] not in ko]
assert not missing, f'번역 없음: {missing}'
extra = sorted(set(ko) - {s['id'] for s in segs})
assert not extra, f'카드에 없는 id: {extra}'

KJ = {}
for ln in open(os.path.join(S, 'kanji.txt'), encoding='utf-8'):
    ln = ln.strip()
    if not ln or ln.startswith('#'):
        continue
    ch, hun = ln.split('|', 1)
    KJ[ch.strip()] = hun.strip()
WORDS = []
for ln in open(os.path.join(S, 'words.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'):
        continue
    p = [x.strip() for x in ln.split('|')]
    assert len(p) == 5, ln
    for stem in p[0].split(','):
        WORDS.append((stem.strip(), p[1], p[2], p[3], p[4]))
WORDS.sort(key=lambda w: -len(w[0]))
STEM_RE = re.compile('|'.join(re.escape(w[0]) for w in WORDS))
BY_STEM = {w[0]: w for w in WORDS}


def scene_of(t):
    key = SCENES[0][0]
    for k, at, _ko, _ja in SCENES:
        if t >= at:
            key = k
    return key


def kanji_notes(text):
    out, seen, covered = [], set(), set()
    for m in STEM_RE.finditer(text):
        stem, head, rd, mean, hj = BY_STEM[m.group()]
        covered.update(range(m.start(), m.end()))
        if head in seen:
            continue
        seen.add(head)
        chars = [[c, KJ[c]] for c in head if KANJI_RE.match(c)]
        out.append([head, rd, mean, hj, chars])
    left = [text[i] for i in range(len(text)) if KANJI_RE.match(text[i]) and i not in covered]
    return out, left


data, uncovered = [], []
for s in segs:
    k, rd, note = ko[s['id']]
    row = {'id': s['id'], 's': s['s'], 'e': s['e'], 'ja': s['ja'], 'rd': rd, 'ko': k,
           'spk': '', 'scene': scene_of(s['s'])}
    if note:
        row['note'] = note
    if s.get('raw'):
        row['raw'] = s['raw']          # 교정 전 음성 인식 원문
    kj, left = kanji_notes(s['ja'])
    if kj:
        row['kj'] = kj
    if left:
        uncovered.append((s['id'], ''.join(left)))
    data.append(row)
assert not uncovered, f'사전에 없는 한자: {uncovered}'
missing_kj = sorted({c for w in WORDS for c in w[1] if KANJI_RE.match(c) and c not in KJ})
assert not missing_kj, f'kanji.txt 에 없는 한자: {missing_kj}'

KANJI1 = re.compile(r'^[一-鿿]$')


def keys_of(term):
    t = term.split('〜')[0].strip() or term.replace('〜', '').strip()
    ks = []
    for n in range(len(t), max(len(t) - 3, 0), -1):
        k = t[:n]
        if len(k) >= 2 or KANJI1.match(k):
            ks.append(k)
    return ks


def find_hits(term, cards):
    for k in keys_of(term):
        ids = [c['id'] for c in cards if k in c['ja']]
        if ids:
            return ids, k
    return [], ''


def pick_example(ids, by_id):
    best, best_score = None, None
    for i in ids:
        c = by_id[i]
        n = len(c['ja'])
        sc = 10 if 6 <= n <= 26 else (n - 6 if n < 6 else -(n - 26) * 0.3)
        if best_score is None or sc > best_score:
            best, best_score = i, sc
    return best


STUDY = []
by_id = {c['id']: c for c in data}
for ln in io.open(os.path.join(S, 'study.txt'), encoding='utf-8'):
    ln = ln.rstrip('\n')
    if not ln.strip() or ln.lstrip().startswith('#'):
        continue
    p = [x.strip() for x in ln.split('|')]
    if len(p) < 4 or p[0] not in ('E', 'V') or not p[1] or not p[3]:
        continue
    row = {'t': p[0], 'ja': p[1], 'rd': p[2], 'ko': p[3]}
    if len(p) > 4 and p[4]:
        row['note'] = p[4]
    row['cids'], row['hit'] = find_hits(p[1], data)
    ex = pick_example(row['cids'], by_id)
    if ex is not None:
        row['ex'] = ex
    STUDY.append(row)
seen = set()
dup = [r['ja'] for r in STUDY if (r['t'], r['ja']) in seen or seen.add((r['t'], r['ja']))]
assert not dup, f'중복: {dup}'

tpl = open(os.path.join(S, 'tpl.html'), encoding='utf-8').read()
REPL = [
 ('ゆびさきと恋々 1화 · <span class="n">—</span>문장<br><span lang="ja">ゆびさきと恋々 第1話 · <span class="n">—</span>フレーズ',
  'First Love 하츠코이 메이킹 · <span class="n">—</span>문장<br><span lang="ja">「First Love 初恋」メイキング · <span class="n">—</span>フレーズ'),
 ('<title>도카도카 일본어 공부 · ドカドカ日本語</title>',
  '<title>도카도카 일본어 공부 · First Love 하츠코이 메이킹</title>'),
 ('japanese-yubisaki-edits.json', 'japanese-hatsukoi-edits.json'),
 ('화면 자막도 카드에 포함', '인식이 불명확한 줄도 포함'),
 ('心の声もカードに含める', '不明瞭な行も含める'),
 # 학습법 탭을 이 영상에 맞게
 ('<h3>토크쇼 한 편을 「쓸 수 있는 일본어」로 바꾸는 4단계</h3>',
  '<h3>메이킹 영상 한 편을 「쓸 수 있는 일본어」로 바꾸는 4단계</h3>'),
 ('<p lang="ja">トーク番組1本を「使える日本語」に変える4ステップ</p>',
  '<p lang="ja">メイキング映像1本を「使える日本語」に変える4ステップ</p>'),
 ('이 교재는 교과서가 아니라 <b>실제 인터뷰 대화</b>입니다. 지어낸 예문에 없는 맞장구·줄임말·말 끊김이 그대로 들어 있습니다.',
  '이 교재는 교과서가 아니라 <b>배우·감독이 카메라 앞에서 실제로 한 말</b>입니다. 준비된 문장이 아니라 생각하며 말하는 화법이라, 말이 끊기고 다시 시작되는 곳이 그대로 있습니다.'),
 ('この教材は教科書ではなく<b>実際のインタビューの会話</b>です。作られた例文にはない相づち・略し方・言いよどみが詰まっています。',
  'この教材は教科書ではなく<b>俳優・監督がカメラの前で実際に話した言葉</b>です。用意された文章ではないので、言い直しや言いよどみがそのまま入っています。'),
 ('640개 카드를 한 번에 들어도 남지 않습니다', '172개 카드를 한 번에 들어도 남지 않습니다'),
 ('640枚を一度に浴びても定着しません', '172枚を一度に浴びても定着しません'),
]
GUIDE_OLD_KO = '둘 다 <b>정중어</b>가 기본이지만 결이 다릅니다. 성시경은 또박또박한 <b>학습자형 일본어</b>(〜んですが·〜ですよね), 나카시마 미카는 자연스러운 <b>네이티브 구어</b>(〜んですよ·〜かな·줄임말). 같은 주제를 두 사람이 어떻게 다르게 말하는지 비교하면 좋습니다.'
GUIDE_NEW_KO = '이 영상은 자막이 없어 <b>음성 인식으로 받아쓴 대본</b>입니다. 사람 이름과 전문 용어를 기계가 자주 틀리기 때문에 32곳을 손으로 고쳤고, 고친 카드에는 <b>원문</b>을 함께 보여 줍니다. 원문과 교정문을 비교하면 「어떻게 들렸는지」와 「실제로 무엇을 말했는지」의 차이가 보여 듣기 훈련에 도움이 됩니다.'
GUIDE_OLD_JA = 'どちらも<b>敬語</b>が基本ですが質が違います。ソン・シギョンははっきりした<b>学習者の日本語</b>(〜んですが・〜ですよね)、中島美嘉は自然な<b>ネイティブの口語</b>(〜んですよ・〜かな・略し方)。同じ話題を二人がどう言い分けるか比べてみてください。'
GUIDE_NEW_JA = 'この動画は字幕がないため<b>音声認識で書き起こした台本</b>です。人名や固有名詞を機械がよく間違えるので32か所を手で直し、直したカードには<b>原文</b>を並べて表示しています。原文と修正文を見比べると「どう聞こえたか」と「実際に何と言ったか」の差が分かります。'
REPL += [('<h5>두 사람의 말투 차이 · 二人の話し方</h5>', '<h5>원문과 교정문 · 原文と修正文</h5>'),
         (GUIDE_OLD_KO, GUIDE_NEW_KO), (GUIDE_OLD_JA, GUIDE_NEW_JA)]
for a, b in REPL:
    if a not in tpl:
        print('  (교체 대상 없음):', a[:42])
    tpl = tpl.replace(a, b)
tpl = tpl.replace('자막은 채널이 올린 공식 수동 일본어 자막입니다. 화자 표기가 없어 문맥으로 추정했고, 읽기·번역은 직접 작성한 것이라 오류가 있을 수 있습니다.',
                  '이 영상은 자막이 없어 음성 인식(faster-whisper)으로 대본을 만들고 32곳을 손으로 교정했습니다. 교정한 카드는 원문을 함께 보여 줍니다. 읽기·번역은 직접 작성한 것이라 오류가 있을 수 있습니다.')
tpl = tpl.replace('字幕はチャンネル公式の日本語字幕。話者表記がないため文脈から推定、読み・訳は手作業のため誤りがあり得ます。',
                  'この動画は字幕がないため音声認識で書き起こし、32か所を手で修正しました。読み・訳は手作業のため誤りがあり得ます。')

html = (tpl
    .replace('/*__DATA__*/', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__SCENES__*/', json.dumps([{'key': k, 'ko': ko_, 'ja': ja_, 'at': at} for k, at, ko_, ja_ in SCENES], ensure_ascii=False))
    .replace('/*__SPEAKERS__*/', json.dumps([{'key': k, 'ja': ja_, 'ko': ko_, 'member': bool(m)} for k, ko_, ja_, m in SPEAKERS], ensure_ascii=False))
    .replace('/*__STUDY__*/', json.dumps(STUDY, ensure_ascii=False, separators=(',', ':')))
    .replace('/*__VID__*/', VID))

_adir = os.path.join(S, 'audio')
_amap = {}
if os.path.exists(os.path.join(_adir, 'index.json')):
    for _k, _fn in json.load(open(os.path.join(_adir, 'index.json'), encoding='utf-8')).items():
        _fp = os.path.join(_adir, _fn)
        if os.path.exists(_fp):
            _amap[_k] = 'data:audio/mpeg;base64,' + base64.b64encode(open(_fp, 'rb').read()).decode()
html = html.replace('/*__AUDIO__*/', json.dumps(_amap, ensure_ascii=False))
open(OUT, 'w', encoding='utf-8').write(html)

print('생성:', OUT)
print('학습 음원:', len(_amap), '건')
print('한자 풀이:', sum(len(d.get('kj', [])) for d in data), '건 / 카드', sum(1 for d in data if 'kj' in d),
      '장 · 한자어', len({w[1] for w in WORDS}), '· 한자', len(KJ))
print('카드:', len(data), '| 교정 원문 병기:', sum(1 for d in data if d.get('raw')), '| 읽기 있음:', sum(1 for d in data if d['rd']))
print('학습:', len(STUDY), '건 (표현', sum(1 for r in STUDY if r['t'] == 'E'), '/ 단어', sum(1 for r in STUDY if r['t'] == 'V'), ')',
      '· 연결됨', sum(1 for r in STUDY if r['cids']), '건')
zero = [r['ja'] for r in STUDY if not r['cids']]
if zero:
    print('  0개:', ', '.join(zero))
print('크기: %.1f KB' % (os.path.getsize(OUT) / 1024))
for k, at, ko_, ja_ in SCENES:
    print('  %-7s %02d:%02d %-26s %3d장' % (k, at // 60, at % 60, ko_, sum(1 for d in data if d['scene'] == k)))
