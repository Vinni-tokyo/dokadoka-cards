# 도카도카 일본어 공부 · ドカドカ日本語 — 「First Love 初恋」 메이킹

YouTube 「The Making of First Love | Hikari Mitsushima, Takeru Satoh, Dir. Yuri Kanchiku & more」
(Netflix Malaysia 채널, 2022-12, 10분 39초)로 만든 **일본어 학습 카드 앱**(한국어 학습자용). 172장.

넷플릭스 드라마 「First Love 하츠코이」의 제작 비하인드 영상입니다. 배우 미츠시마 히카리·사토 타케루와
칸치쿠 유리 감독 등이 배역 만들기, 상대 배우와의 호흡, 홋카이도 로케이션, 각본과 색 설계까지
카메라 앞에서 직접 이야기합니다.

## 자막이 없는 영상이라 음성 인식으로 만들었습니다

이 영상은 **수동 자막도 자동 자막도 전혀 없습니다.** 그래서 faster-whisper(medium, 일본어)로 받아쓴 뒤
문장 단위로 카드를 만들었습니다. 인식 자체는 꽤 정확했지만 **사람 이름과 전문 용어를 자주 틀렸습니다.**

| 인식 결과 | 교정 |
|---|---|
| 野口**あえ** | 野口**也英** (주인공 이름) |
| **波木春**道 / ハルウィッチ | **並木晴**道 |
| 佐藤**タケル** / 竹内くん | 佐藤**健** / 健くん |
| **三島**ひかり / 道島さん | **満島**ひかり / 満島さん |
| **矢木莉佳子** | **八木莉可子** |
| **国**自衛隊 | **航空**自衛隊 |
| **カッパ**印刷 | **活版**印刷 |
| **うんかい** | **雲海** |
| 初作 | 所作 |
| 心差しの高さ | 志の高さ |

이런 식으로 **32곳**을 고쳤고, 고친 카드는 앱에서 **교정문 아래에 인식 원문을 함께** 보여 줍니다.
「어떻게 들렸는지」와 「실제로 무엇을 말했는지」를 비교할 수 있어 듣기 훈련에 쓸 만합니다.

문맥으로도 확신이 서지 않는 4곳(旧話, 説明でした, 手伝うみたいな…, 職人の視野思い 등)은
**고치지 않고 그대로 두고** 주석에 「음성 인식이 불명확한 곳」이라고 표시했습니다.

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8086).

## 구성

```
hatsukoi-cards/
├─ Japanese-Hatsukoi172-Cards.html   앱 (단일 파일, 데이터·음원 내장)
├─ start.bat / start.sh
├─ README.md
└─ src/
   ├─ raw/asr.json      faster-whisper 인식 결과(원본)
   ├─ fixes.txt         오인식 교정 32건 `id|교정문`
   ├─ seg.py            인식 구간 + 교정 → segs.json (40자 넘는 줄만 문장 끝에서 분할)
   ├─ ko.txt            id|한국어 뜻|읽기(히라가나)|주석 — 직접 작성
   ├─ reading.py        fugashi(unidic-lite) 히라가나 읽기 자동 생성
   ├─ kanji.txt         한자 훈음 사전 320자
   ├─ words.txt         한자어 사전 315항목 (gen_words.py 로 생성)
   ├─ gen_words.py / lemma_meanings.py / lemma_base.py
   │                    lemma_base = mika·frieren·milky 앱 사전에서 재사용한 120건
   ├─ study.txt         표현 42 · 단어 46
   ├─ make_audio.py     학습 음원(edge-tts, ja-JP-Nanami / ko-KR-SunHi)
   ├─ audio/            mp3 176개 + index.json
   ├─ build.py          최종 HTML 생성
   └─ tpl.html          화면 템플릿(mika-cards 계열 + 인식 원문 병기 기능 추가)
```

## 재빌드

```bash
cd src
python3 gen_words.py > words.txt    # 사전 갱신 시
python3 build.py                    # seg.py 를 먼저 돌리고 HTML 생성
python3 make_audio.py               # 학습 음원(인터넷 필요) 후 build.py 재실행
```

대본을 처음부터 다시 만들려면 음원을 받아 인식을 돌립니다(음원과 인식 원본은 리포에 넣지 않습니다).

```bash
../.venv/bin/yt-dlp --js-runtimes node -x --audio-format wav -o /tmp/mk.wav -- https://www.youtube.com/watch?v=OUx16Z5PpII
../.venv/bin/python - <<'EOF'
from faster_whisper import WhisperModel; import json
m = WhisperModel('medium', device='cpu', compute_type='int8')
segs, _ = m.transcribe('/tmp/mk.wav', language='ja', beam_size=5, vad_filter=True,
                       vad_parameters={'min_silence_duration_ms': 400}, condition_on_previous_text=False,
                       initial_prompt='ドラマ「First Love 初恋」のメイキング映像。満島ひかり、佐藤健、監督の寒竹ゆりへのインタビュー。')
json.dump([{'s': round(s.start,2), 'e': round(s.end,2), 'ja': s.text.strip()} for s in segs],
          open('src/raw/asr.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
EOF
```

`initial_prompt` 에 작품·인명을 넣어야 고유명사 인식이 그나마 나아집니다. 그래도 이름은 대부분 틀리므로 `fixes.txt` 가 필요합니다.

## 장면 · 화자

10개 장면으로 나눴습니다(작품 첫인상 / 배역 소개 / 캐릭터 만들기 / 두 배우의 호흡 / 젊은 시절 배우들 /
워크숍과 음식 / 로케이션 / 기획과 각본 / 대본과 색 / 시청자에게).

화자는 **전부 "화자 미상"** 입니다. 음성 인식은 누가 말했는지 구분하지 못하고, 영상의 화면 이름표도
읽어들이지 않았습니다. 배우 다섯 명과 감독이 번갈아 말하므로 억지로 배정하지 않았습니다.

## 번역·읽기에 대해

- **한국어 뜻**: 직접 번역했습니다.
- **히라가나 읽기**: fugashi 자동 생성 후 인명·지명(野口也英→のぐちやえ, 羽田→はねだ),
  숫자(300、400人→さんびゃく よんひゃくにん), 문맥 독음(方→かた/ほう)을 손으로 고쳤습니다.
- **한자 풀이**: 본문 한자 313자 전부를 사전으로 커버했습니다(빌드가 누락을 검사).
- 준비된 원고가 아니라 **생각하며 말하는 화법**이라 말이 끊기고 다시 시작되는 곳이 그대로 있습니다.
  교과서 문장과 다른 실제 발화를 익히기에 좋고, 그만큼 처음에는 어렵게 들립니다.

## 출처

- 영상: YouTube `OUx16Z5PpII` — Netflix Malaysia 채널, 2022-12-19, 10분 39초.
- 대본은 이 영상의 음성을 인식해 만든 것이고, 번역·읽기·주석·학습 항목도 직접 작성한 것이라 오류가 있을 수 있습니다.

학습용 개인 이용을 전제로 한 페이지입니다. 영상은 YouTube 공식 플레이어로 재생됩니다.
