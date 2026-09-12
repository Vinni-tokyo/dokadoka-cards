import io, json, os, re, sys, base64
S = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(S)

VIDS = {
    2: 'Cq18ngJQ3sU', 3: 'lx4CQ-4hEVM', 4: 'UKOSnxWUOd0', 5: 'S6jjcVNzcdM', 6: 'kbe4I_Jd8NY',
    7: 'venWKTSh3cs', 8: 'xGkekMDEY8s', 9: 'VT7mZComrzw', 10: 'bWCkSOafQNc', 11: 'gCM9WYAJC38',
    12: 'VNGnINmsrF8', 13: 'WKwc-judGQo', 14: 'r5m1bfVUfSQ', 15: 'Cr_8koqGgTA', 16: 'rD_T-TLBR9I',
    17: 'p5X1q7ipaic', 18: 'WTUkzIG8ZeE', 19: '1_gk3UwnugY',
    20: 'DddirskV5Vo', 21: 'dBafvwMBbGk', 22: 'xvGmhEz0WHc'}
TITLES = {
    2: 'お酒からアルコールだけを抜く魔法', 3: '朝決まった時間に起きれるようになる魔法',
    4: '体から良いにおいが出る魔法', 5: '運がよくなる魔法', 6: 'しつこい油汚れを落とす魔法',
    7: 'ものすごく早口に澱みなく喋れる魔法', 8: '魚の気持ちがわかる魔法', 9: '運が良くなる魔法その2',
    10: '語尾が変なふうになる魔法', 11: '服の汚れをきれいさっぱり落とす魔法', 12: '身長が伸びる魔法',
    13: 'おなかいっぱいになる魔法', 14: '大体なんでも切る魔法', 15: '高速で移動する魔法',
    16: '体のまわりを涼しくする魔法', 17: '得意技を封じる魔法', 18: '見た者を拘束する魔法',
    19: '童心に還る魔法',
    20: '心と体が入れ替わる魔法', 21: 'お洗濯の魔法', 22: '考えていることを言ってしまう魔法その2'}
TITLES_KO = {
    2: '술에서 알코올만 빼는 마법', 3: '아침에 정해진 시간에 일어나게 되는 마법',
    4: '몸에서 좋은 냄새가 나는 마법', 5: '운이 좋아지는 마법', 6: '찌든 기름때를 지우는 마법',
    7: '엄청 빠르게 막힘없이 말할 수 있는 마법', 8: '물고기의 마음을 알 수 있는 마법',
    9: '운이 좋아지는 마법 그 두 번째', 10: '말끝이 이상해지는 마법',
    11: '옷의 얼룩을 깨끗하게 빼는 마법', 12: '키가 자라는 마법', 13: '배가 불러지는 마법',
    14: '대체로 뭐든 자르는 마법', 15: '고속으로 이동하는 마법', 16: '몸 주위를 시원하게 하는 마법',
    17: '특기를 봉인하는 마법', 18: '본 사람을 구속하는 마법', 19: '동심으로 돌아가는 마법',
    20: '몸과 마음이 바뀌는 마법', 21: '빨래 마법', 22: '생각을 말해버리는 마법 그 두 번째'}

SPEAKERS = [('', '화자 미상', '話者不明', 0)]

KANJI_RE = re.compile(r'[一-鿿々]')


def load_words_kanji(ep_dir):
    KJ = {}
    for ln in open(os.path.join(ep_dir, 'kanji.txt'), encoding='utf-8'):
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        ch, hun = ln.split('|', 1)
        KJ[ch.strip()] = hun.strip()
    WORDS = []
    for ln in open(os.path.join(ep_dir, 'words.txt'), encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln.strip() or ln.lstrip().startswith('#'):
            continue
        p = [x.strip() for x in ln.split('|')]
        assert len(p) == 5, ln
        for stem in p[0].split(','):
            WORDS.append((stem.strip(), p[1], p[2], p[3], p[4]))
    WORDS.sort(key=lambda w: -len(w[0]))
    return KJ, WORDS


def kanji_notes(text, KJ, STEM_RE, BY_STEM):
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


def keys_of(term):
    t = term.split('〜')[0].strip() or term.replace('〜', '').strip()
    ks = []
    for n in range(len(t), max(len(t) - 3, 0), -1):
        k = t[:n]
        if len(k) >= 2 or KANJI_RE.match(k):
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


def build(ep):
    ep_dir = os.path.join(S, f'ep{ep}')
    VID = VIDS[ep]
    OUT = os.path.join(ROOT, f'Japanese-Frieren{ep}-Cards.html')

    ko = {}
    for ln in open(os.path.join(ep_dir, 'ko.txt'), encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln.strip() or ln.lstrip().startswith('#'):
            continue
        p = ln.split('|')
        ko[int(p[0])] = (p[1].strip(), p[2].strip() if len(p) > 2 else '', p[3].strip() if len(p) > 3 else '')

    segs = json.load(open(os.path.join(ep_dir, 'segs.json'), encoding='utf-8'))
    missing = [s['id'] for s in segs if s['id'] not in ko]
    assert not missing, f'ep{ep} 번역 없음: {missing}'
    extra = sorted(set(ko) - {s['id'] for s in segs})
    assert not extra, f'ep{ep} 카드에 없는 id: {extra}'

    KJ, WORDS = load_words_kanji(ep_dir)
    STEM_RE = re.compile('|'.join(re.escape(w[0]) for w in WORDS))
    BY_STEM = {w[0]: w for w in WORDS}

    data, uncovered = [], []
    for s in segs:
        k, rd, note = ko[s['id']]
        row = {'id': s['id'], 's': s['s'], 'e': s['e'], 'ja': s['ja'], 'rd': rd, 'ko': k,
               'spk': '', 'scene': 'main'}
        if note:
            row['note'] = note
        kj, left = kanji_notes(s['ja'], KJ, STEM_RE, BY_STEM)
        if kj:
            row['kj'] = kj
        if left:
            uncovered.append((s['id'], ''.join(left)))
        data.append(row)
    assert not uncovered, f'ep{ep} 사전에 없는 한자: {uncovered}'
    missing_kj = sorted({c for w in WORDS for c in w[1] if KANJI_RE.match(c) and c not in KJ})
    assert not missing_kj, f'ep{ep} kanji.txt 에 없는 한자: {missing_kj}'

    STUDY = []
    by_id = {c['id']: c for c in data}
    for ln in io.open(os.path.join(ep_dir, 'study.txt'), encoding='utf-8'):
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
    assert not dup, f'ep{ep} 중복: {dup}'

    tpl = open(os.path.join(S, 'tpl.html'), encoding='utf-8').read()
    tpl = tpl.replace(
        'ゆびさきと恋々 1화 · <span class="n">—</span>문장<br><span lang="ja">ゆびさきと恋々 第1話 · <span class="n">—</span>フレーズ',
        f'프리렌 미니 애니 제{ep}회 · <span class="n">—</span>문장<br><span lang="ja">葬送のフリーレン ミニアニメ「●●の魔法」第{ep}回：「{TITLES[ep]}」 · <span class="n">—</span>フレーズ')
    tpl = tpl.replace('japanese-yubisaki-edits.json', f'japanese-frieren{ep}-edits.json')
    tpl = tpl.replace(
        '<title>도카도카 일본어 공부 · ドカドカ日本語</title>',
        f'<title>도카도카 일본어 공부 · 프리렌 미니 애니 제{ep}회</title>')

    html = (tpl
        .replace('/*__DATA__*/', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
        .replace('/*__SCENES__*/', json.dumps([{'key': 'main', 'ko': TITLES_KO[ep], 'ja': f'第{ep}回', 'at': 0}], ensure_ascii=False))
        .replace('/*__SPEAKERS__*/', json.dumps([{'key': k, 'ja': ja_, 'ko': ko_, 'member': bool(m)} for k, ko_, ja_, m in SPEAKERS], ensure_ascii=False))
        .replace('/*__STUDY__*/', json.dumps(STUDY, ensure_ascii=False, separators=(',', ':')))
        .replace('/*__VID__*/', VID))

    _adir = os.path.join(ep_dir, 'audio')
    _amap = {}
    if os.path.exists(os.path.join(_adir, 'index.json')):
        for _k, _fn in json.load(open(os.path.join(_adir, 'index.json'), encoding='utf-8')).items():
            _fp = os.path.join(_adir, _fn)
            if os.path.exists(_fp):
                _amap[_k] = 'data:audio/mpeg;base64,' + base64.b64encode(open(_fp, 'rb').read()).decode()
    html = html.replace('/*__AUDIO__*/', json.dumps(_amap, ensure_ascii=False))

    open(OUT, 'w', encoding='utf-8').write(html)

    print(f'--- ep{ep} 생성:', OUT)
    print('  학습 음원:', len(_amap), '건')
    print('  한자 풀이:', sum(len(d.get('kj', [])) for d in data), '건 / 카드', sum(1 for d in data if 'kj' in d), '장 · 한자어', len({w[1] for w in WORDS}), '· 한자', len(KJ))
    print('  카드:', len(data), '| 읽기 있음:', sum(1 for d in data if d['rd']))
    print('  학습:', len(STUDY), '건 (표현', sum(1 for r in STUDY if r['t'] == 'E'), '/ 단어', sum(1 for r in STUDY if r['t'] == 'V'), ')',
          '· 연결됨', sum(1 for r in STUDY if r['cids']), '건')
    zero = [r['ja'] for r in STUDY if not r['cids']]
    if zero:
        print('  0개:', ', '.join(zero))
    print('  크기: %.1f KB' % (os.path.getsize(OUT) / 1024))
    return len(data)


if __name__ == '__main__':
    eps = [int(a) for a in sys.argv[1:]] or sorted(VIDS)
    for ep in eps:
        build(ep)
