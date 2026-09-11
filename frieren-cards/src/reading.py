"""히라가나 읽기 자동 생성. fugashi(unidic-lite) 토큰의 품사를 보고
자립어+뒤에 붙는 조사/조동사를 한 덩이로 묶어(어절 단위 근사) 띄어쓰기."""
import fugashi
import jaconv

_tagger = fugashi.Tagger()

# 이 품사로 시작하면 새 어절
_START_POS = {'名詞', '動詞', '形容詞', '形状詞', '副詞', '連体詞', '接続詞', '感動詞', '代名詞', '接頭辞'}
_CONTINUE_POS = {'助詞', '助動詞', '接尾辞', '記号', '補助記号'}


def _kana(word):
    k = word.feature.kana or word.feature.pron or word.surface
    return jaconv.kata2hira(k)


def reading(text):
    words = list(_tagger(text))
    groups = []
    cur = ''
    for w in words:
        pos1 = w.feature.pos1
        surf = w.surface
        if not surf.strip():
            continue
        kana = _kana(w) if surf not in '。、！？…～「」『』・（）()' else ''
        if pos1 in _START_POS and cur:
            groups.append(cur)
            cur = kana
        else:
            cur += kana
    if cur:
        groups.append(cur)
    return ' '.join(g for g in groups if g)


if __name__ == '__main__':
    for t in ['ちょちょちょちょっと、ごめん', '全然話についていけてないんだけど',
              'これってこの３日の間に起きた事件の内容のこと話してるんだよね？']:
        print(t, '->', reading(t))
