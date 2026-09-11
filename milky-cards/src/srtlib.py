"""공용 srt 파싱/정렬 도구. 銀河特急 ミルキー☆サブウェイ 전 7화 공통.

일본어 자막: 큐 하나에 '-' 로 시작하는 줄이 여럿이면 화자가 다른 여러 발화.
줄바꿈만 있고 '-' 없는 줄은 한 발화가 두 줄로 나뉜 것(합친다).
"""
import re


def parse_srt(path):
    raw = open(path, encoding='utf-8-sig').read()
    cues = []
    for block in re.split(r'\n\s*\n', raw.strip()):
        lines = block.split('\n')
        if len(lines) < 3:
            continue
        m = re.match(r'(\d{2}):(\d{2}):(\d{2})[,.](\d{3}) --> (\d{2}):(\d{2}):(\d{2})[,.](\d{3})', lines[1])
        if not m:
            continue
        h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, m.groups())
        st = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000
        en = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000
        text = '\n'.join(lines[2:]).strip()
        cues.append({'s': st, 'e': en, 'text': text})
    return cues


def split_dash(text):
    """큐 텍스트를 발화 단위로 쪼갠다. '-' 로 시작하는 줄 = 새 발화, 아니면 이어붙임."""
    parts = []
    for ln in text.split('\n'):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith('-') or ln.startswith('−') or ln.startswith('―'):
            parts.append(ln.lstrip('-−― ').strip())
        elif parts:
            parts[-1] = parts[-1] + ' ' + ln
        else:
            parts.append(ln)
    return parts


SFX_ONLY = re.compile(r'^[\(（\[][^)\)\]）]*[\)）\]]$')
TITLE_ONLY = re.compile(r'^[“"”].*[”"“]$', re.S)


def split_cue(cue):
    """큐 하나 -> [{'s','e','text'}...] 발화 리스트. 글자수 비례로 시간 분배."""
    parts = [p for p in split_dash(cue['text']) if p and not SFX_ONLY.match(p) and not TITLE_ONLY.match(p)]
    if not parts:
        return []
    total = sum(len(p) for p in parts) or 1
    out = []
    t = cue['s']
    span = cue['e'] - cue['s']
    for i, p in enumerate(parts):
        dur = span * len(p) / total
        st = t
        en = cue['e'] if i == len(parts) - 1 else t + dur
        out.append({'s': round(st, 2), 'e': round(en, 2), 'text': p})
        t = en
    return out


def build_lines(srt_path):
    """srt 파일 -> 발화 리스트(전체), 큐 분할 포함"""
    out = []
    for cue in parse_srt(srt_path):
        out.extend(split_cue(cue))
    return out


def overlap(a, b):
    return max(0.0, min(a['e'], b['e']) - max(a['s'], b['s']))


def align_ko(ja_lines, ko_lines):
    """각 ja 발화에 시간이 가장 많이 겹치는 ko 발화 하나를 붙인다(단일 최선 매치).
    ko 한 줄이 여러 ja 줄에 걸쳐 재사용될 수 있다(빠른 대사 교환에서 자연스러움)."""
    result = []
    for j in ja_lines:
        best, best_ov = None, 0.0
        for k in ko_lines:
            ov = overlap(j, k)
            if ov > best_ov:
                best, best_ov = k, ov
        if best is None:
            # 겹치는 게 없으면 시간상 가장 가까운 것
            best = min(ko_lines, key=lambda k: min(abs(k['s'] - j['s']), abs(k['e'] - j['e'])))
        result.append(best['text'].replace('\n', ' '))
    return result
