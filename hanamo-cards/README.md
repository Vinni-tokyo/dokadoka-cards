# 도카도카 일본어 공부 · ドカドカ日本語 — MEBIG「花も」

YouTube 「花も : 日本語 賛美 Music Video」(ワーシップルーム, 2020-05, 3분 42초)로 만든
**일본어 찬양 학습 카드 앱**(한국어 학습자용). 20줄. 한국어 뜻·히라가나 읽기·주석·한자 풀이·표현 10·단어 7.
한국 CCM 「꽃들도」의 일본어판입니다.

## 이 곡을 고른 이유

- 앱 안 재생을 착수 전에 확인했습니다(`tools/embed_check.py` → OK).
- 가사는 채널 설명란에 올린 것을 썼습니다(작곡 MEBIG).
- **명령형이 줄줄이 나옵니다** — 奏でよ·響け·歌え·仰げ. 「花も雲も風も大海も」로 조사 も 를 익힙니다.
- 3분 42초로 짧아 첫 곡으로 좋습니다.

## 줄 시각

자막 트랙이 없어 **음성 인식(faster-whisper medium, 단어 시각)** 으로 맞췄습니다.
`tools/asr_words.py` → `tools/align_dp.py` 로 20줄을 순서 정렬했습니다(**20줄 전부 직접 대응**, 유사도 평균 0.88).
잘린 끝 시각은 `tools/fix_cue_ends.py` 로 보정했습니다. 박 그리드는 `beats.py` 로 구했습니다(BPM 130.0).

## 읽어주기 보정

`主` 가 자리에 따라 ぬし 로 읽혀 `src/tts_fix.txt` 에 `主|しゅ` 를 넣었습니다.
같이 짚힌 大海(おおうみ)·実(み)는 재어 보니 제대로 읽고 있었습니다.

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8123).

## 재빌드

```bash
cd src && ../../.venv/bin/python gen_words.py > words.txt && python3 build.py
../../.venv/bin/python ../../tools/make_study_audio.py hanamo-cards --cards --gloss
```

## 출처

- 영상 · 음원 · 가사: YouTube ワーシップルーム 「花も」 (HNinJx29zlY) 와 그 설명란의 가사 (작곡 MEBIG)
- 한국어 뜻 · 히라가나 읽기 · 문법 주석 · 표현/단어 풀이 · 한자 훈음: 학습용으로 직접 작성

학습용 개인 이용을 전제로 한 페이지입니다.
