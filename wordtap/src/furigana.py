"""예문 줄의 한자 위에 붙일 읽기(후리가나).

줄 원문(가사·자막)과 그 줄의 읽기(앱의 ko.txt — 사람이 고친 읽기)를 맞춘다.
가나 부분은 그대로 맞물려야 하고, 한자 덩어리에 읽기를 몇 글자씩 줄지는 가능한 경우를 전부 따져
형태소 분석(fugashi)의 읽기에 가장 가까운 것을 고른다. 실제로 붙는 글자는 언제나 ko.txt 의 읽기다
(主=しゅ, 人陰=かげ 같은 노래의 읽기를 지킨다). 맞출 수 없으면 None — 화면은 줄 아래 읽기 한 줄로 대신한다.
"""
import re, json, io, sys
KAN = r'一-鿿々〆ヶ'
HIRA = lambda s: ''.join(chr(ord(c) - 0x60) if 'ァ' <= c <= 'ヶ' else c for c in s)
_tagger = None
def hints(text):
    """形態素解析で漢字の塊ごとの読み候補 {開始位置: 読み} — 位置合わせの「先に試す候補」"""
    global _tagger
    if _tagger is None:
        import fugashi; _tagger = fugashi.Tagger()
    out, pos = {}, 0
    for t in _tagger(text):
        s = t.surface; i = text.find(s, pos)
        if i < 0: continue
        pos = i + len(s)
        r = HIRA(t.feature.kana or '') if t.feature.kana not in (None, '*') else ''
        if not r or not re.search(f'[{KAN}]', s): continue
        a, b = 0, len(s)                                   # 앞뒤 가나(送り仮名)를 읽기에서도 뗀다
        while b > a and not re.match(f'[{KAN}]', s[b - 1]) and r.endswith(HIRA(s[b - 1])): r = r[:-1]; b -= 1
        while a < b and not re.match(f'[{KAN}]', s[a]) and r.startswith(HIRA(s[a])): r = r[1:]; a += 1
        core = s[a:b]
        if r and re.fullmatch(f'[{KAN}]+', core): out[i + a] = (core, r)
    # 何十年 = 何 + 十 + 年 처럼 이어진 후보는 이어 붙인다
    for k in sorted(out):
        c, r = out[k]; j = k + len(c)
        while j in out: c += out[j][0]; r += out[j][1]; j += len(out[j][0])
        out[k] = (c, r)
    return out
KANA = re.compile(r'[ぁ-ゖァ-ヺー]+')
def ruby(text, rd):
    """text の漢字の塊ごとに読みを付ける → [[字, 読み], ...]（読み '' = 付けない）。合わなければ None
    読み(rd)を塊に割り振るやり方を全部試し、形態素解析の読みに一番近いものを選ぶ。"""
    H = hints(text)
    segs = []                                              # (文字列, 種類, 解析の読み)
    for mm in re.finditer(rf'[{KAN}]+|[ぁ-ゖァ-ヺー]+|[A-Za-z0-9０-９Ａ-Ｚａ-ｚ\'’.]+|.', text):
        s = mm.group()
        if re.match(rf'[{KAN}]', s):
            h = H.get(mm.start()); segs.append((s, 'k', h[1] if h and h[0] == s else ''))
        elif re.match(r'[ぁ-ゖァ-ヺー]', s): segs.append((s, 'n', ''))
        elif re.match(r'[A-Za-z0-9０-９Ａ-Ｚａ-ｚ]', s): segs.append((s, 'l', ''))
        else: segs.append((s, 'p', ''))
    R = re.sub(r'[\s　、。,.!?！？「」『』…・~〜～―“”"()（）]', '', rd)
    eq = lambda a, b: HIRA(a) == HIRA(b)
    import functools
    @functools.lru_cache(None)
    def best(i, p):                                        # (벌점, 읽기 목록) — 못 맞추면 None
        if i == len(segs): return (0, ()) if p == len(R) else None
        s, k, h = segs[i]
        if k == 'p': r = best(i + 1, p); return r and (r[0], ('',) + r[1])
        if k == 'n':
            if not eq(R[p:p + len(s)], s) and not (s == 'ー' and p < len(R)): return None
            r = best(i + 1, p + len(s)); return r and (r[0], ('',) + r[1])
        out = None
        if k == 'l':                                       # 영문·숫자: 읽기에 그대로 있으면 그대로, 아니면 아무 길이(벌점 1)
            lit = s.replace("'", '').replace('’', '').replace('.', '')
            opts = [(len(lit), 0)] if R[p:p + len(lit)].lower() == lit.lower() else []
            opts += [(n, 1) for n in range(0, len(R) - p + 1)]
        else:
            opts = []
            for n in range(len(s), min(len(R) - p, 3 * len(s) + 1) + 1):
                v = R[p:p + n]
                if not KANA.fullmatch(v): break
                opts.append((n, 0 if h and eq(v, h) else (2 + abs(n - len(h)) if h else abs(n - 2 * len(s)) * .5)))
        for n, pen in opts:
            r = best(i + 1, p + n)
            if r and (out is None or r[0] + pen < out[0]): out = (r[0] + pen, (R[p:p + n] if k == 'k' else '',) + r[1])
        return out
    r = best(0, 0)
    if not r: return None
    return [[s, HIRA(v)] for (s, k, h), v in zip(segs, r[1])]


def encode(text, rd):
    """「{君|きみ}が{泣|な}くの」 꼴 — 페이지에 싣는 모양. 못 맞추면 ''"""
    r = ruby(text, rd)
    return ''.join('{%s|%s}' % (s, v) if v else s for s, v in r) if r else ''
