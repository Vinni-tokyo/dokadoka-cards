# 도카도카 한국어 공부 · 노래로 배우기 — fromis_9 「Supersonic」 (노포라이브)

YouTube 「프로미스나인 노포라이브 [SUPERSONIC] - 노래만 있는 버전」(하나냥 채널, 2025-01-03, 2분 45초)으로 만든
**노래 학습 카드 앱**(일본어 모어 학습자용). 가사 59줄 = 한글 줄 23 + 영어만 있는 줄 36. 한글 줄에 **가나 읽기**와 문법 메모.

공식 MV(HYBE LABELS, 2024-08)는 앱 안 임베드 재생이 막혀 있어(오류 150) 재생되는 라이브 영상을 씁니다.
가사·일본어 번역은 **공식 MV 의 공식 한국어·일본어 자막**(59줄 1:1)에서 가져왔습니다.

## 줄 시각 — 공식 자막을 라이브에 맞춤

라이브는 공식 MV 와 **같은 반주·같은 템포**이고 노래 시작이 5.9초 빠릅니다. 음성 인식(faster-whisper, 한국어)으로
안정적으로 대응된 10줄의 오프셋이 −5.78 ~ −6.09초로 일정해서, 공식 자막 시각 전체를 **−5.92초** 옮겨 썼습니다
(`src/subtitles.ko.srt` · `src/subtitles.ja.srt`). 후렴의 영어 부분은 음성 인식이 흐려 대조에서 뺐습니다.

박 그리드(`src/beats.json`)는 라이브 음원에서 `beats.py` 로 구했습니다(138.4 BPM · 4/4 · 95마디).
마디 시작이 어긋나게 들리면 노래방의 「미세 조정」에서 ±1박으로 맞출 수 있습니다.

## 학습 탭

**오늘 · 복습 · 목록 · 학습법** 넷. 「오늘」은 단락(1절 · 프리코러스 · 후렴 …) 단위로 4단계를 안내합니다:
들으며 읽기 → 마디 따라 부르기 → 가사 가리고 부르기 → 표현·단어(퀴즈). 한글 줄 23줄과 표현·단어 34개는
**한국어 음원(edge-tts)** 을 내장해 「읽어주기」가 오프라인에서도 됩니다.

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8102).

## 구성

```
supersonic-cards/
├─ Korean-Supersonic59-Cards.html   앱 (단일 파일, 데이터·음원 내장)
├─ start.bat / start.sh
├─ README.md
└─ src/
   ├─ subtitles.ko.srt / subtitles.ja.srt   공식 MV 자막을 −5.92초 옮긴 것
   ├─ rd.txt                       가나 읽기·문법 메모 `id|読み|注記` (한글 23줄)
   ├─ study.txt                    표현 15 · 단어 19
   ├─ beats.json / beats.py        박 그리드
   ├─ audio/                       edge-tts 음원 + index.json
   ├─ build.py                     최종 HTML 생성 (VID · SCENES · 시리즈 정보)
   └─ tpl.html                     화면 템플릿 (vitaminme-cards 와 동일 계열)
```

## 재빌드

```bash
cd src && python3 build.py
../../.venv/bin/python ../../tools/make_study_audio.py supersonic-cards --cards   # 음원(인터넷 필요) 후 build.py 재실행
```

## 출처

- 영상: YouTube `BSTM6WWqxKw` — 하나냥 채널, 2025-01-03. 팬 업로드 라이브 영상이라 삭제·비공개가 되면 재생되지 않습니다.
- 가사·번역: 공식 MV `0LiQp7y8Wwc` 의 공식 자막(HYBE LABELS). 읽기·메모·학습 항목은 직접 작성한 것이라 오류가 있을 수 있습니다.

학습용 개인 이용을 전제로 한 페이지입니다. 영상은 YouTube 공식 플레이어로 재생됩니다.
