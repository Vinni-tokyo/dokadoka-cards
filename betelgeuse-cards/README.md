# 도카도카 일본어 공부 · ドカドカ日本語 — 優里「ベテルギウス」

YouTube 「優里『ベテルギウス』Official Music Video」(優里 Official YouTube Channel, 2021-11, 4분 52초)로 만든
**일본어 노래 학습 카드 앱**(한국어 학습자용). 가사 52줄. 한국어 뜻·히라가나 읽기·주석·한자 풀이·표현 27·단어 25.

## 왜 이 곡인가

- 공식 MV 에 **공식 일본어·한국어 가사 자막**(52줄)이 있어 가사와 시각을 그대로 믿을 수 있습니다. 음성 인식·손보정이 필요 없었습니다.
- 초당 2.7자의 느린 발라드라 마디 따라 부르기·가사 가리기 단계에 맞고, 「〜てくれた」「〜たり〜たり」「〜たび(に)」「〜だろう」 같은 기본 문형이 반복됩니다.
- 앱 안 임베드 재생을 착수 전에 확인했습니다(정상). 첫 56초는 연주만 있는 도입부입니다.

## 줄 시각

시작은 공식 한국어 자막의 시각(0.01초 단위), 끝은 일본어 자막의 시각(초 단위)을 쓰되 다음 줄 시작을 넘지 않게 잘랐습니다.
박 그리드(`src/beats.json`)는 MV 음원에서 `beats.py` 로 구했습니다(119.8 BPM · 4/4). 마디 머리가 어긋나면 노래방 「미세 조정」의 ±1박으로 맞추세요.

## 학습 탭

**오늘 · 복습 · 목록 · 학습법** 넷. 「오늘」은 단락(1절 · 후렴 1 · 2절 · 후렴 2 · 브릿지 · 마지막 후렴 · 아웃트로) 단위로
들으며 읽기 → 마디 따라 부르기 → 가사 가리고 부르기 → 표현·단어 4단계를 안내합니다. 가사 52줄·표현·단어·한자 풀이 표제어는
**일본어 음원(edge-tts)** 을 내장해 「읽어주기」가 오프라인에서도 됩니다.

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8103).

## 구성

```
betelgeuse-cards/
├─ Japanese-Betelgeuse52-Cards.html   앱 (단일 파일, 데이터·음원 내장)
├─ start.bat / start.sh
├─ README.md
└─ src/
   ├─ lyrics.txt        가사 52줄 (빈 줄 = 구간 경계)
   ├─ subtitles.srt     줄별 시각 (공식 자막)
   ├─ ko.txt            id|한국어 뜻|읽기|주석 — 뜻은 공식 한국어 자막을 바탕으로 다듬음, 읽기는 fugashi 후 손보정
   ├─ kanji.txt         한자 훈음 63자 (가사 한자 61자 100% 커버, 빌드가 검사)
   ├─ words.txt         한자어 사전 52항목 (gen_words.py 로 생성)
   ├─ gen_words.py / lemma_meanings.py / lemma_base.py / check_cov.py
   ├─ study.txt         표현 27 · 단어 25
   ├─ beats.json / beats.py
   ├─ audio/            edge-tts 음원 + index.json
   ├─ build.py          최종 HTML 생성
   └─ tpl.html          화면 템플릿 (firstlove-cards 와 동일 계열)
```

## 재빌드

```bash
cd src && ../../.venv/bin/python gen_words.py > words.txt && python3 build.py
../../.venv/bin/python ../../tools/make_study_audio.py betelgeuse-cards --cards --gloss   # 음원(인터넷 필요) 후 build.py 재실행
```

## 출처

- 영상: YouTube `cbqvxDTLMps` — 優里 Official YouTube Channel. 가사·한국어 자막은 채널이 올린 공식 자막.
- 읽기·주석·한자 풀이·학습 항목은 직접 작성한 것이라 오류가 있을 수 있습니다.

학습용 개인 이용을 전제로 한 페이지입니다. 영상은 YouTube 공식 플레이어로 재생됩니다.
