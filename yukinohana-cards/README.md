# 도카도카 일본어 공부 · ドカドカ日本語 — 中島美嘉「雪の華」

YouTube 「中島美嘉「雪の華」Music Video」(中島美嘉 Official YouTube Channel, 2003년 곡, 5분 50초, 1억 뷰)로 만든
**일본어 노래 학습 카드 앱**(한국어 학습자용). 가사 46줄. 한국어 뜻·히라가나 읽기·주석·한자 풀이·표현 26·단어 26.
성시경 × 나카시마 미카 토크쇼 앱에서 화제가 된 그 곡입니다(한국에서는 박효신 「눈의 꽃」으로 알려짐).

## 가사와 시각을 만든 방법

- 이 MV 에는 자막이 없어서 가사는 같은 곡의 **THE FIRST TAKE 공식 일본어 자막**(46줄)에서 가져왔습니다. 자막에 붙은 읽기 표시 「人陰(かげ)」「瞬間(とき)」는 본문에서 떼고 읽기 줄에 반영했습니다.
- 줄 시각은 MV 음원을 faster-whisper(medium, 일본어) 로 단어 단위 인식한 뒤 가사 줄과 대조해 잡았습니다(`src/align.py`). 46줄 중 44줄이 유사도 0.73 이상으로 직접 대응됐고, 가타카나 표기 「シアワセがあふれだす」 두 줄만 앞뒤 사이를 보간했습니다.
- 박 그리드(`src/beats.json`)는 MV 음원에서 `beats.py` 로 구했습니다. 마디 머리가 어긋나면 노래방 「미세 조정」의 ±1박으로 맞추세요.
- 앱 안 임베드 재생을 착수 전에 확인했습니다(정상). 첫 34초는 연주 도입부입니다.

## 학습 탭

**오늘 · 복습 · 목록 · 학습법** 넷. 「오늘」은 단락(1절 · 후렴 1 · 2절 · 후렴 2 · 브릿지 · 마지막 후렴 · 아웃트로) 단위로
들으며 읽기 → 마디 따라 부르기 → 가사 가리고 부르기 → 표현·단어 4단계를 안내합니다. 가사·표현·단어·한자 풀이 표제어는
**일본어 음원(edge-tts)** 을 내장했고, TTS 가 잘못 읽는 표기(人陰→かげ, 瞬間→とき, 2人→ふたり, 今年→ことし)는 `src/tts_fix.txt` 로 교정했습니다.

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8105).

## 구성

```
yukinohana-cards/
├─ Japanese-YukiNoHana46-Cards.html   앱 (단일 파일, 데이터·음원 내장)
├─ start.bat / start.sh
├─ README.md
└─ src/
   ├─ lyrics.txt / subtitles.srt   가사 46줄 · 음성 인식으로 맞춘 시각 (align.py)
   ├─ ko.txt                       id|한국어 뜻|읽기|주석 — 직접 번역, 읽기는 fugashi 후 손보정
   ├─ kanji.txt / words.txt        한자 훈음(가사 한자 75자 100% 커버) · 한자어 사전 60항목
   ├─ study.txt                    표현 26 · 단어 26
   ├─ tts_fix.txt                  TTS 발음 교정표
   ├─ beats.json / beats.py / align.py
   ├─ audio/                       edge-tts 음원 + index.json
   ├─ build.py / tpl.html          최종 HTML 생성 (firstlove-cards 와 동일 계열)
```

## 재빌드

```bash
cd src && ../../.venv/bin/python gen_words.py > words.txt && python3 build.py
../../.venv/bin/python ../../tools/make_study_audio.py yukinohana-cards --cards --gloss   # 음원(인터넷 필요) 후 build.py 재실행
```

줄 시각을 다시 잡으려면 MV 음원(wav)을 받아 faster-whisper 로 단어 시각(words.json)을 만든 뒤 `python3 align.py words.json` 을 돌립니다. 어긋나는 줄은 `fixes.txt`(`id|시작|끝`)로 손보정할 수 있습니다.

## 출처

- 영상: YouTube `mF5Qq2YheTg` — 中島美嘉 Official YouTube Channel. 가사는 THE FIRST TAKE(`fcVHGZVCkDI`) 의 공식 자막.
- 번역·읽기·주석·학습 항목은 직접 작성한 것이라 오류가 있을 수 있습니다.

학습용 개인 이용을 전제로 한 페이지입니다. 영상은 YouTube 공식 플레이어로 재생됩니다.
