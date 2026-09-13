# 도카도카 어학 학습 · Dokadoka Cards

YouTube 영상 한 편의 자막을 **대사 카드 · 대본 · 구간 재생 · 표현/단어 · 퀴즈 · 일일 분량**이 든 **단일 HTML 학습 앱**으로 만드는 프로젝트입니다.
현재 일본어 2편 · 한국어 3편 · 영어 1편이 있고, 루트의 `index.html` 이 언어별 관문입니다.

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** → 관문 페이지(포트 8100) |
| Linux / mac | `./start.sh` |

각 앱 폴더에도 자기만의 `start.bat`/`start.sh` 가 있어 폴더째 복사해도 단독으로 동작합니다.
YouTube 는 `file://` 에서의 임베드 재생을 거부하므로(Error 153) 간이 서버로 여는 것이 기본입니다. Python 3 만 있으면 됩니다.

## 구성

```
dokadoka-cards/
├─ index.html                 관문 — 언어(ja/ko/en)별로 앱 카드를 나열. APPS 배열이 목록
├─ start.sh / start.bat       관문 실행기 (포트 8100)
├─ japanese-cards/            🇯🇵 Snow Man 인터뷰 · 105장 · 포트 8099 · WORKFLOW_PROMPT.md(정본 작업 지시서)
├─ kanji-cards/               🇯🇵 한자 카드 · 일본어 7작품의 한자 963자·한자어 1,433개 · 유튜브 없음 · 포트 8084
├─ yubisaki-cards/            🇯🇵 ゆびさきと恋々 1화 · 185장 · 포트 8097
├─ bokuyaba-cards/            🇯🇵 僕の心のヤバイやつ 1화 · 184장 · 포트 8093 (자동자막 교정 106건·한자 풀이)
├─ firstlove-cards/           🇯🇵 宇多田ヒカル 「First Love」 노래 · 28줄 · 포트 8091 (노래방·마디 반복·음성 인식 타이밍)
├─ saranghagi-cards/          🇰🇷 유재하 「사랑하기 때문에」 cover by 지원 노래 · 33줄 · 포트 8089 (일본어 모어 학습자용, 노래방·마디 반복)
├─ korean-cards/              🇰🇷 프로미스나인 예능·브이로그 2시리즈 · 383+306장 · 포트 8098 (일본어 모어 학습자용)
├─ vitaminme-cards/           🇰🇷 fromis_9 「Vitamin ME」 노래 가사 · 84줄(가나 읽기) · 포트 8093 (일본어 모어 학습자용)
├─ english-cards/             🇺🇸 73 Questions With Zendaya · 248장 · 포트 8096
├─ social-cards/              🇺🇸 TED · 사회적 건강 · 78장 · 포트 8087 (TED 공식 자막 CC)
├─ think-cards/               🇺🇸 TED · AI 와 비판적 사고 · 127장 · 포트 8088 (TED 공식 자막 CC)
├─ harris-cards/              🇺🇸 TED · AI 는 우리의 시험 · 130장 · 포트 8086 (TED 공식 자막 CC)
├─ tipping-cards/             🇺🇸 TED · 기후 티핑포인트 · 157장 · 포트 8085 (TED 공식 자막 CC)
├─ reasons-cards/             🇺🇸 Matt Redman 「10,000 Reasons」 노래 가사 · 51줄(음성 인식 타이밍) · 포트 8092
├─ altman-cards/              🇺🇸 Sam Altman · Bloomberg TV 인터뷰(고급) · 123장 · 포트 8095
├─ feifei-cards/              🇺🇸 Fei-Fei Li · The Circuit 다큐 인터뷰(고급) · 250장 · 포트 8094
└─ .venv/                     (gitignore) yt-dlp — 자막 내려받기용
```

앱 폴더 하나의 구조는 공통입니다: `src/subtitles.srt`(원본 자막) → `src/seg.py`(카드 분할) → `src/<l1>.txt`(번역·주석) + `src/study.txt`(표현·단어) → `python3 src/build.py` → `<Lang>-<Nick><N>-Cards.html`.
자세한 절차·판단 기준·재발 방지 목록은 [japanese-cards/WORKFLOW_PROMPT.md](japanese-cards/WORKFLOW_PROMPT.md) 에 있습니다.

## 새 영상 추가

1. `python3 -m venv .venv && .venv/bin/pip install yt-dlp` (최초 1회)
2. `WORKFLOW_PROMPT.md` 절차대로 자막이 좋은 영상을 고르고, 자막 형식이 같은 앱 폴더를 복사해 시작합니다.
3. 파일명 · 포트 · LocalStorage 키(`LS`) · 내보내기 파일명 4곳을 바꿉니다(안 바꾸면 앱 간 진도가 섞입니다).
4. `index.html` 의 `APPS` 에 한 줄(`learn: 'ja'|'ko'|'en'`)을 더하면 관문에 실립니다.

## 학습 음원 (표현·단어)

각 앱의 표현·단어에는 원문과 뜻 두 가지 로컬 mp3 음원이 심겨 있습니다(앱당 3~5MB, 한국어 앱 11MB). 항목을 고치거나 새 앱을 만들면 다시 생성합니다(인터넷 필요, 증분).

```bash
.venv/bin/pip install edge-tts                       # 최초 1회
.venv/bin/python tools/make_study_audio.py yubisaki-cards   # 또는 --all
python3 yubisaki-cards/src/build.py                  # 생성한 음원을 HTML 에 심는다
```

음성은 `tools/make_study_audio.py` 의 `FAMILY` 표에서 앱별로 정합니다(일본어 Nanami, 영어 Ava/Andrew, 한국어 SunHi). 노래 앱 중 First Love 는 대상이고, 10,000 Reasons·Vitamin ME 는 대상이 아닙니다.

## 재빌드

```bash
python3 japanese-cards/src/build.py
python3 yubisaki-cards/src/build.py
python3 bokuyaba-cards/src/build.py
python3 firstlove-cards/src/build.py
python3 saranghagi-cards/src/build.py
python3 korean-cards/src/build.py
python3 english-cards/src/build.py
python3 altman-cards/src/build.py
python3 feifei-cards/src/build.py
```

각 빌드는 번역 id ↔ 카드 id 전수 대응, 학습 항목의 자막 내 존재(`0개: 없음`)를 assert 로 검사합니다.

## 출처·이용

영상은 재배포하지 않습니다. 모든 재생은 **YouTube 공식 플레이어**를 통해 이뤄지며, 조회수·광고는 원저작자에게 돌아갑니다.
자막은 각 채널이 붙인 것으로 출처는 각 앱 README에 적어 두었습니다. 번역·주석·학습 항목은 직접 작성한 것이라
오류가 있을 수 있고, 앱 안 「편집」으로 고칠 수 있습니다.

비영리 어학 학습 목적의 개인 프로젝트입니다. 검색 노출은 `noindex` 로 막아 두었습니다.
자막·영상의 권리자께서 게시 중단을 원하시면 저장소 Issue 로 알려 주시면 바로 내리겠습니다.
