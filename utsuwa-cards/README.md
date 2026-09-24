# 도카도카 일본어 공부 · ドカドカ日本語 — JPCC Worship「主の器」

YouTube 「主の器 / Shu No Utsuwa (Official Lyric Video) - JPCC Worship x Live Church Worship」(JPCC Worship, 2019-06, 5분 30초)로 만든
**일본어 찬양 학습 카드 앱**(한국어 학습자용). 38줄. 한국어 뜻·히라가나 읽기·주석·한자 풀이·표현 14·단어 6.

## 이 곡을 고른 이유

- 앱 안 재생을 착수 전에 확인했습니다(`tools/embed_check.py` → OK).
- 인도네시아 JPCC Worship 의 곡 「Bejana-Mu」를 Live Church Worship 이 일본어로 옮긴 **공식 가사 영상**입니다.
  가사는 채널 설명란에 권리자가 직접 올린 것을 썼습니다.
- 한 줄이 짧고 느려 따라 부르기 좋고, 후렴 여덟 줄이 세 번 돌아 〜に従う·御手·〜のため 가 몸에 붙습니다.

## 줄 시각

자막 트랙이 없어 **음성 인식(faster-whisper medium, 단어 시각)** 으로 맞췄습니다.
`tools/asr_words.py` 로 단어 시각을 뽑고 `tools/align_dp.py` 로 가사 38줄을 순서 정렬했습니다
(38줄 중 36줄 직접 대응, 유사도 평균 0.84). 인식이 뭉개진 2절 앞 두 줄(5·6번)은 2절이 다시 나오는
자리(17·18번)의 길이에 맞춰 손으로 넣었습니다. 잘린 끝 시각은 `tools/fix_cue_ends.py` 로 보정했습니다.
박 그리드는 `beats.py` 로 구했습니다(BPM 145.8).

## 읽어주기 보정

`主` 가 자리에 따라 ぬし 로 읽혀 `src/tts_fix.txt` 에 `主|しゅ` 를 넣었습니다(`tools/hear_tts.py` 로 재어 확인).

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8119). 학습 탭·노래방·화면 잠금은 다른 노래 앱과 같습니다.

## 재빌드

```bash
cd src && ../../.venv/bin/python gen_words.py > words.txt && python3 build.py
../../.venv/bin/python ../../tools/make_study_audio.py utsuwa-cards --cards --gloss   # 음원(인터넷 필요) 후 build.py 재실행
```

## 출처

- 영상 · 음원 · 가사: YouTube JPCC Worship 「主の器」 (WM9Yek6yqc0) 와 그 설명란의 공식 가사 (번역 榊山純)
- 한국어 뜻 · 히라가나 읽기 · 문법 주석 · 표현/단어 풀이 · 한자 훈음: 학습용으로 직접 작성

학습용 개인 이용을 전제로 한 페이지입니다.
