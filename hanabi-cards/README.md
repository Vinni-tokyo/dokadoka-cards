# 도카도카 일본어 공부 · ドカドカ日本語 — DAOKO × 米津玄師「打上花火」

YouTube 「DAOKO × 米津玄師『打上花火』MUSIC VIDEO」(Daoko 공식 채널, 2017-08, 4분 53초)로 만든
**일본어 노래 학습 카드 앱**(한국어 학습자용). 가사 44줄. 한국어 뜻·히라가나 읽기·주석·한자 풀이·표현 24·단어 28.

## 왜 이 곡인가

- 공식 MV 에 **공식 일본어·한국어 가사 자막**(44줄, 1:1, 0.01초 단위 시각)이 있어 가사와 시각을 그대로 씁니다. 음성 인식·손보정이 필요 없었습니다.
- 초당 2.7자의 미드템포. 「〜んだ」「〜て欲しかった」「〜かな」「二度と〜ない」「〜ずに」「〜ちゃいそう」 같은 회화 문형이 촘촘합니다.
- 앱 안 임베드 재생을 착수 전에 확인했습니다(정상). 첫 23초는 연주 도입부입니다.

## 줄 시각·박 그리드

공식 일본어 자막의 시각을 그대로 쓰되 다음 줄 시작을 넘지 않게 잘랐습니다. 박 그리드(`src/beats.json`)는 MV 음원에서 `beats.py` 로 구했습니다.
마디 머리가 어긋나면 노래방 「미세 조정」의 ±1박으로 맞추세요.

## 학습 탭

**오늘 · 복습 · 목록 · 학습법** 넷. 「오늘」은 단락(1절 · 후렴 1 · 2절 · 브릿지 · 후렴 2 · 마지막) 단위로
들으며 읽기 → 마디 따라 부르기 → 가사 가리고 부르기 → 표현·단어 4단계를 안내합니다. 가사 44줄·표현·단어·한자 풀이 표제어는
**일본어 음원(edge-tts)** 을 내장했습니다. TTS 가 잘못 읽는 한자(君の→きみの, 何度→なんど, 夕凪→ゆうなぎ 등)는 `src/tts_fix.txt` 로 교정했습니다.

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8104).

## 구성

```
hanabi-cards/
├─ Japanese-Hanabi44-Cards.html   앱 (단일 파일, 데이터·음원 내장)
├─ start.bat / start.sh
├─ README.md
└─ src/
   ├─ lyrics.txt / subtitles.srt   가사 44줄 · 공식 자막 시각
   ├─ ko.txt                       id|한국어 뜻|읽기|주석 — 뜻은 공식 한국어 자막을 바탕으로 다듬음, 읽기는 fugashi 후 손보정
   ├─ kanji.txt / words.txt        한자 훈음(가사 한자 79자 100% 커버) · 한자어 사전 70항목 (gen_words.py)
   ├─ study.txt                    표현 24 · 단어 28
   ├─ tts_fix.txt                  TTS 발음 교정표
   ├─ beats.json / beats.py
   ├─ audio/                       edge-tts 음원 + index.json
   ├─ build.py / tpl.html          최종 HTML 생성 (firstlove-cards 와 동일 계열)
```

## 재빌드

```bash
cd src && ../../.venv/bin/python gen_words.py > words.txt && python3 build.py
../../.venv/bin/python ../../tools/make_study_audio.py hanabi-cards --cards --gloss   # 음원(인터넷 필요) 후 build.py 재실행
```

## 출처

- 영상: YouTube `-tKVN2mAKRI` — Daoko 공식 채널. 가사·한국어 자막은 채널이 올린 공식 자막.
- 읽기·주석·한자 풀이·학습 항목은 직접 작성한 것이라 오류가 있을 수 있습니다.

학습용 개인 이용을 전제로 한 페이지입니다. 영상은 YouTube 공식 플레이어로 재생됩니다.
