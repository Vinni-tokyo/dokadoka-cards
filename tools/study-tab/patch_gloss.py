#!/usr/bin/env python3
"""한자 풀이·표현 풀이를 토크 계열 앱에 옮겨 붙인다.

뜻 영역에 ① 문장을 단어로 쪼갠 한자 풀이(읽기·한국 한자음·뜻·글자별 훈음, 단어마다 소리 버튼)와
② 이 카드에 걸린 학습 표현 풀이를 더한다. 노래 앱(yubisaki·driedflower 계열)에는 이미 있던 것을
japanese-cards 처럼 그 기능이 생기기 전에 만들어진 앱으로 옮기기 위한 스크립트다.

사용: python3 patch_gloss.py <앱폴더>/src
  - tpl.html 에 CSS·마크업·렌더 함수를 넣고
  - build.py 가 kanji.txt·words.txt 를 읽어 카드마다 kj 를 만들게 고친다
이미 적용된 파일은 건너뛴다.
"""
import io
import os
import sys


def rep(h, old, new, cnt=1):
    n = h.count(old)
    assert n == cnt, f'앵커 {n}개 (기대 {cnt}): {old[:70]!r}'
    return h.replace(old, new)


CSS = '''.gloss{margin:14px 0 0;padding-top:12px;border-top:1px solid var(--line)}
.gloss .cap{display:flex;align-items:center;gap:8px;font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin-bottom:7px}
.gloss .cap .sub{display:inline;font-size:10px;letter-spacing:0;text-transform:none;font-weight:500;margin:0}
.kjrow{display:grid;grid-template-columns:minmax(96px,auto) minmax(0,1fr);gap:4px 12px;padding:6px 0;border-bottom:1px dashed var(--line);font-size:12.5px;line-height:1.55;align-items:baseline}
.kjrow:last-child{border-bottom:0}
.kjrow .w{font-size:15px;font-weight:650;white-space:nowrap}
.kjrow .w small{display:block;font-size:11px;font-weight:400;color:var(--ink-3);white-space:normal}
.kjrow .m{min-width:0;word-break:keep-all}
.kjrow .hj{display:inline-block;margin-right:6px;padding:0 6px;border-radius:5px;background:var(--brand-soft);color:var(--brand);font-weight:700;font-size:11.5px}
.kjrow .ch{display:block;margin-top:2px;font-size:11.5px;color:var(--ink-3)}
.exrow{padding:6px 0;border-bottom:1px dashed var(--line);font-size:12.5px;line-height:1.6;word-break:keep-all}
.exrow:last-child{border-bottom:0}
.exrow b{font-weight:650;color:var(--brand)}
.exrow small{color:var(--ink-3);font-size:11px;margin-left:5px}
.exrow .n{display:block;color:var(--ink-3);font-size:11.5px;margin-top:1px}
.tts-mini{display:inline-grid;place-items:center;width:24px;height:24px;padding:0;margin-left:6px;border-radius:50%;border:1px solid var(--line-2);background:var(--surface);color:var(--ink-2);vertical-align:middle;flex:none}
.tts-mini .ic{width:13px;height:13px}
.tts-mini:hover,.tts-mini[aria-pressed=true]{background:var(--brand-soft);border-color:var(--brand-line);color:var(--brand)}
'''

BOX = '''      <div class="gloss" id="kanjiBox" hidden>
       <div class="cap">한자 풀이 <span class="sub" lang="ja">漢字の読みと意味</span> <span class="sub">· 일본어 독음 · 한국 한자음 · 뜻 · 훈음</span></div>
       <div id="kanjiList"></div>
      </div>
      <div class="gloss" id="explBox" hidden>
       <div class="cap">표현 풀이 <span class="sub" lang="ja">表現の解説</span></div>
       <div id="explList"></div>
      </div>
'''

JS = '''
/* 한자 풀이(빌드가 사전으로 만든 d.kj) + 표현 풀이(이 카드에 나오는 학습 표현) */
function ttsPause(){ if(!OFFLINE && player && ready){ try{ if(player.getPlayerState() === 1) player.pauseVideo(); }catch(e){} } }
function ttsBtn(text){
  const b = document.createElement('button'); b.type = 'button'; b.className = 'tts-mini'; b.title = '읽어주기 / 読み上げ';
  b.innerHTML = '<svg class="ic"><use href="#i-sound"/></svg>'; b.dataset.t = text;
  b.onclick = e => { e.stopPropagation(); ttsMark(b); ttsPause(); aPlay(text, 1, 0, () => b.setAttribute('aria-pressed', 'false'), 2, 1); };
  return b;
}
function paintGloss(d){
  const kb = $('kanjiList'); kb.textContent = '';
  (d.kj || []).forEach(([head, rd, mean, hj, chars]) => {
    const row = document.createElement('div'); row.className = 'kjrow';
    const w = document.createElement('div'); w.className = 'w'; w.lang = 'ja'; w.textContent = head;
    w.appendChild(ttsBtn(rd || head));   /* 읽어주기는 훈독(사전 읽기)으로 */
    const r = document.createElement('small'); r.textContent = rd; w.appendChild(r);
    const m = document.createElement('div'); m.className = 'm';
    const h = document.createElement('span'); h.className = 'hj'; h.textContent = hj;
    m.append(h, document.createTextNode(mean));
    if(chars && chars.length){
      const c = document.createElement('span'); c.className = 'ch';
      chars.forEach(([ch, hun], i) => {
        if(i) c.appendChild(document.createTextNode(' · '));
        const b = document.createElement('b'); b.lang = 'ja'; b.textContent = ch;
        c.append(b, document.createTextNode(' ' + hun));
      });
      m.appendChild(c);
    }
    row.append(w, m); kb.appendChild(row);
  });
  $('kanjiBox').hidden = !kb.childElementCount;
  const eb = $('explList'); eb.textContent = '';
  STUDY.filter(r => r.t === 'E' && (r.cids || []).includes(d.id)).forEach(r => {
    const row = document.createElement('div'); row.className = 'exrow';
    const b = document.createElement('b'); b.lang = 'ja'; b.textContent = r.ja;
    row.append(b, ttsBtn(r.rd || r.ja));
    if(r.rd){ const s = document.createElement('small'); s.lang = 'ja'; s.textContent = r.rd; row.appendChild(s); }
    row.appendChild(document.createTextNode(' ' + r.ko));
    if(r.note){ const n = document.createElement('span'); n.className = 'n'; n.textContent = r.note; row.appendChild(n); }
    eb.appendChild(row);
  });
  $('explBox').hidden = !eb.childElementCount;
}
'''

BUILD_DICT = '''
# --- 한자 풀이 사전 (yubisaki-cards 와 같은 규칙) ---------------------------------
KJ = {}
for _ln in io.open(os.path.join(S, 'kanji.txt'), encoding='utf-8'):
    _ln = _ln.strip()
    if not _ln or _ln.startswith('#'): continue
    _ch, _hun = _ln.split('|', 1); KJ[_ch.strip()] = _hun.strip()
WORDS = []
for _ln in io.open(os.path.join(S, 'words.txt'), encoding='utf-8'):
    _ln = _ln.rstrip('\\n')
    if not _ln.strip() or _ln.lstrip().startswith('#'): continue
    _p = [x.strip() for x in _ln.split('|')]
    assert len(_p) == 5, _ln
    for _stem in _p[0].split(','): WORDS.append((_stem.strip(), _p[1], _p[2], _p[3], _p[4]))
WORDS.sort(key=lambda w: -len(w[0]))
STEM_RE = re.compile('|'.join(re.escape(w[0]) for w in WORDS)) if WORDS else None
BY_STEM = {w[0]: w for w in WORDS}
KANJI_RE = re.compile(r'[一-鿿々]')
def kanji_notes(text):
    out, seen, covered = [], set(), set()
    if STEM_RE:
        for m in STEM_RE.finditer(text):
            stem, head, rd, mean, hj = BY_STEM[m.group()]
            covered.update(range(m.start(), m.end()))
            if head in seen: continue
            seen.add(head); out.append([head, rd, mean, hj, [[c, KJ[c]] for c in head if KANJI_RE.match(c)]])
    left = [text[i] for i in range(len(text)) if KANJI_RE.match(text[i]) and i not in covered]
    return out, left

'''


def patch_tpl(path):
    h = io.open(path, encoding='utf-8').read()
    if 'id="kanjiBox"' in h:
        print(f'skip (이미 적용) {path}')
        return False
    h = rep(h, '.ttsrow{', CSS + '.ttsrow{')
    h = rep(h, '      <p class="note" id="note" hidden></p>\n',
            '      <p class="note" id="note" hidden></p>\n' + BOX)
    h = rep(h, 'function setReveal(', JS + 'function setReveal(')
    h = rep(h, "  $('note').hidden = !d.note; $('note').textContent = d.note || '';\n",
            "  $('note').hidden = !d.note; $('note').textContent = d.note || '';\n  paintGloss(d);\n")
    # 소리 버튼도 한 번에 하나만 눌린 상태가 되도록
    h = rep(h, "function ttsMark(el){ document.querySelectorAll('.ttsrow .btn[aria-pressed=true]')",
            "function ttsMark(el){ document.querySelectorAll('.tts-mini[aria-pressed=true],.ttsrow .btn[aria-pressed=true]')")
    io.open(path, 'w', encoding='utf-8').write(h)
    print(f'ok   {path}')
    return True


def patch_build(path):
    h = io.open(path, encoding='utf-8').read()
    if 'def kanji_notes(' in h:
        print(f'skip (이미 적용) {path}')
        return False
    h = rep(h, '\ndata = []\n', BUILD_DICT + '\ndata = []\n')
    h = rep(h, "    if note: row['note'] = note\n    data.append(row)\n",
            "    if note: row['note'] = note\n"
            "    _kj, _left = kanji_notes(s['ja'])\n"
            "    if _kj: row['kj'] = _kj\n"
            "    if _left: uncovered.append((s['id'], ''.join(_left)))\n"
            "    data.append(row)\n")
    h = rep(h, '\ndata = []\n', '\ndata, uncovered = [], []\n')
    h = rep(h, "    data.append(row)\n", "    data.append(row)\n", 1)
    # 루프 뒤 검사 — 카드 만들기가 끝난 직후
    h = rep(h, "\n# --- 학습 탭", "\nassert not uncovered, f'사전에 없는 한자: {uncovered}'\n"
            "_missing_kj = sorted({c for w in WORDS for c in w[1] if KANJI_RE.match(c) and c not in KJ})\n"
            "assert not _missing_kj, f'kanji.txt 에 없는 한자: {_missing_kj}'\n"
            "\n# --- 학습 탭")
    h = rep(h, "print('카드:', len(data),",
            "print('한자 풀이:', sum(len(d.get('kj', [])) for d in data), '건')\nprint('카드:', len(data),")
    io.open(path, 'w', encoding='utf-8').write(h)
    print(f'ok   {path}')
    return True


if __name__ == '__main__':
    for d in sys.argv[1:]:
        patch_tpl(os.path.join(d, 'tpl.html'))
        patch_build(os.path.join(d, 'build.py'))
