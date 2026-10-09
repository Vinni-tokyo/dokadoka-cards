"""words.txt 커버리지 검사. 사용: python3 check_cov.py <ep_dir>
모든 ja 텍스트의 한자가 words.txt 의 어간으로 전부 커버되는지 확인하고
안 되는 부분을 보여준다."""
import json, re, sys, os
S = os.path.dirname(os.path.abspath(__file__))
KANJI_RE = re.compile(r'[一-鿿々]')


def load_words(path):
    WORDS = []
    for ln in open(path, encoding='utf-8'):
        ln = ln.rstrip('\n')
        if not ln.strip() or ln.lstrip().startswith('#'):
            continue
        p = [x.strip() for x in ln.split('|')]
        if len(p) != 5:
            print('형식 오류:', ln); continue
        for stem in p[0].split(','):
            WORDS.append((stem.strip(), p[1], p[2], p[3], p[4]))
    WORDS.sort(key=lambda w: -len(w[0]))
    return WORDS


def check(ep_dir):
    words_path = os.path.join(ep_dir, 'words.txt')
    if not os.path.exists(words_path):
        print('없음:', words_path); return None
    WORDS = load_words(words_path)
    STEM_RE = re.compile('|'.join(re.escape(w[0]) for w in WORDS)) if WORDS else None
    segs = json.load(open(os.path.join(ep_dir, 'segs.json'), encoding='utf-8'))
    total_uncovered = {}
    for s in segs:
        text = s['ja']
        covered = set()
        if STEM_RE:
            for m in STEM_RE.finditer(text):
                covered.update(range(m.start(), m.end()))
        for i, c in enumerate(text):
            if KANJI_RE.match(c) and i not in covered:
                total_uncovered.setdefault(c, []).append((s['id'], text))
    return total_uncovered


if __name__ == '__main__':
    ep_dir = sys.argv[1]
    unc = check(ep_dir)
    if unc is None:
        sys.exit(1)
    if not unc:
        print('전부 커버됨!')
    else:
        print(f'미커버 한자 {len(unc)}종:')
        for c, hits in sorted(unc.items()):
            ids = sorted(set(h[0] for h in hits))
            sample = hits[0][1]
            print(f'  {c}  (id {ids[:5]}{"..." if len(ids)>5 else ""})  예: {sample}')
