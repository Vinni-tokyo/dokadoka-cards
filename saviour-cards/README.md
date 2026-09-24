# 도카도카 일본어 공부 · ドカドカ日本語 — Live Church Worship「Beautiful Saviour」

YouTube 「Beautiful Saviour - Planetshakers (Official Japanese) / Live Church Worship」(Live Church Worship, 2017-04, 6분 38초)로 만든
**일본어 찬양 학습 카드 앱**(한국어 학습자용). 34줄. 한국어 뜻·히라가나 읽기·주석·한자 풀이·표현 10·단어 7.

## 이 곡을 고른 이유

- 앱 안 재생을 착수 전에 확인했습니다(`tools/embed_check.py` → OK).
- Planetshakers 곡의 **공인 일본어 번역**(豊口由起子·榊山純)입니다. 가사는 채널 설명란에 올린 공식 가사를 썼습니다.
- 〜に勝る·上げられ·ひれ伏しあがめる 같은 예배 어휘와 聖い(きよい)·救い主(ぬし) 읽기가 나오고, 브릿지 두 줄이 네 번 돕니다.

## 줄 시각

자막 트랙이 없어 **음성 인식(faster-whisper medium, 단어 시각)** 으로 맞췄습니다.
`tools/asr_words.py` → `tools/align_dp.py` 로 34줄을 순서 정렬했습니다(31줄 직접 대응, 유사도 평균 0.70).
인식이 뭉개진 3줄(11·31·33번)은 받아쓰기의 구간 시각에 맞춰 손으로 넣었습니다.
잘린 끝 시각은 `tools/fix_cue_ends.py` 로 보정했습니다. 박 그리드는 `beats.py` 로 구했습니다(BPM 104.0).

## 읽어주기 보정

| 본문 | 합성기가 읽던 소리 | 이 곡의 읽기 |
|---|---|---|
| 名に勝って | **かっ**て | **まさっ**て |
| 主 | (자리에 따라 ぬし) | しゅ |

`救い主` 는 すくいぬし 가 맞으므로 `主|しゅ` 보다 먼저 `救い主|すくいぬし` 를 적었습니다(치환은 위에서부터).
聖い方(かた)·大海 등 같이 짚힌 곳은 재어 보니 제대로 읽고 있었습니다.

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8120).

## 재빌드

```bash
cd src && ../../.venv/bin/python gen_words.py > words.txt && python3 build.py
../../.venv/bin/python ../../tools/make_study_audio.py saviour-cards --cards --gloss
```

## 출처

- 영상 · 음원 · 가사: YouTube Live Church Worship 「Beautiful Saviour (Official Japanese)」 (NUVdDXGGlVE) 와 그 설명란의 공식 가사
- 한국어 뜻 · 히라가나 읽기 · 문법 주석 · 표현/단어 풀이 · 한자 훈음: 학습용으로 직접 작성

학습용 개인 이용을 전제로 한 페이지입니다.
