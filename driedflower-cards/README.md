# 도카도카 일본어 공부 · ドカドカ日本語 — 優里「ドライフラワー」

YouTube 「優里『ドライフラワー』Official Music Video -ディレクターズカットver.-」(優里 Official YouTube Channel, 2021-03, 4분 48초)로 만든
**일본어 노래 학습 카드 앱**(한국어 학습자용). 가사 49줄. 한국어 뜻·히라가나 읽기·주석·한자 풀이·표현 31·단어 31.

## 이 곡을 고른 이유와 제약

- 앱 안 임베드 재생을 착수 전에 확인했습니다(정상).
- 76 BPM 대의 느린 발라드라 마디 따라 부르기·가사 가리기 단계에 맞고, 「〜てくれる」「〜ずに」「〜てほしい」「〜たら」 같은 일상 문형이 반복됩니다.
- 1절과 2절이 같은 자리에서 말을 뒤집습니다(「私じゃなくていい」↔「君じゃなくてよかった」, 「嫌いじゃないの」↔「大嫌いだよ」). 짝을 이루는 줄은 주석에 표시했습니다.
- **이 MV 에는 공식 일본어 가사 자막이 없습니다.** 공식 자막은 한국어·영어·중국어뿐입니다.
  그래서 **가사 원문은 앱 사용자가 제공한 가사지를 그대로 쓰고**, 줄별 시각만 음원에서 구했습니다.

## 줄 시각

음원을 faster-whisper(medium, 단어 시각)로 인식하고 `align.py` 로 가사 49줄과 순서 정렬했습니다.
**49줄 전부 직접 대응**했고 보간·손보정은 0줄입니다(유사도 최저 0.78, 대부분 1.00).
박 그리드(`src/beats.json`)는 `beats.py` 로 구했습니다(BPM 152.9 · 4/4). 이 곡처럼 느린 발라드는 실제 템포의 두 배로 잡히고
위상 일관성이 낮게 나옵니다(눈의 꽃 앱과 같음). 마디 머리가 어긋나면 노래방 「미세 조정」의 ±1박으로 맞추세요.

## 학습 탭

**오늘 · 복습 · 목록 · 학습법** 넷. 「오늘」은 단락(1절 · 후렴 1 · 2절 · 후렴 2 · 브릿지 · 브릿지 2 · 마지막 후렴) 단위로
들으며 읽기 → 마디 따라 부르기 → 가사 가리고 부르기 → 표현·단어 4단계를 안내합니다. 가사 49줄·표현·단어·한자 풀이 표제어는
**일본어 음원(edge-tts)** 235개를 내장해 「읽어주기」가 오프라인에서도 됩니다. 음원은 −22 LUFS 로 정규화돼 있고 🔈 버튼으로 음량을 바꿉니다.

## 화면 잠금

탭 줄 오른쪽 끝 자물쇠를 누르면 화면이 잠깁니다. **2초간 꾹 누르면** 풀립니다(손을 떼면 처음부터). PC 는 Esc 로도 풀립니다.
잠긴 동안에도 영상과 읽어주기는 계속 재생됩니다. 들으면서 화면을 건드려 카드가 넘어가는 것을 막습니다.

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8107).

## 구성

```
driedflower-cards/
├─ Japanese-DriedFlower49-Cards.html   앱 (단일 파일, 데이터·음원 내장)
├─ start.bat / start.sh
├─ README.md
└─ src/
   ├─ lyrics.txt        가사 49줄 (빈 줄 = 구간 경계) — 사용자 제공
   ├─ subtitles.srt     줄별 시각 (align.py 가 음성 인식 단어 시각에서 만든 것)
   ├─ ko.txt            id|한국어 뜻|읽기|주석 — 학습용으로 직접 작성
   ├─ kanji.txt         한자 훈음 85자 (가사 한자 84자 100% 커버, 빌드가 검사)
   ├─ words.txt         한자어 사전 70항목 (gen_words.py 로 생성)
   ├─ gen_words.py / lemma_meanings.py / lemma_base.py / check_cov.py
   ├─ study.txt         표현 31 · 단어 31
   ├─ segs.json         가사 줄 목록 (gen_words·check_cov 용)
   ├─ beats.json / beats.py / align.py
   ├─ audio/            edge-tts 음원 235개 + index.json
   ├─ build.py          최종 HTML 생성
   └─ tpl.html          화면 템플릿 (yukinohana-cards 와 동일 계열)
```

## 재빌드

```bash
cd src && ../../.venv/bin/python gen_words.py > words.txt && python3 build.py
../../.venv/bin/python ../../tools/make_study_audio.py driedflower-cards --cards --gloss   # 음원(인터넷 필요) 후 build.py 재실행
```

줄 시각을 다시 만들려면 음원과 인식 결과가 필요합니다(둘 다 리포에 넣지 않습니다).

```bash
.venv/bin/yt-dlp -x --audio-format wav -o dry.wav "https://youtu.be/kzZ6KXDM1RI"
# faster-whisper(medium, language=ja, word_timestamps=True) → words.json
python3 src/align.py words.json          # → subtitles.srt
.venv/bin/python src/beats.py dry.wav    # → beats.json
```

## 출처

- 영상 · 음원: YouTube 優里 Official YouTube Channel, 「優里『ドライフラワー』Official Music Video -ディレクターズカットver.-」 (kzZ6KXDM1RI)
- 가사 원문: 앱 사용자가 제공
- 한국어 뜻 · 읽기 · 주석 · 표현/단어 풀이: 학습용으로 직접 작성

학습용 개인 이용을 전제로 한 페이지입니다.
