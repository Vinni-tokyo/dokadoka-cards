# 도카도카 일본어 공부 · ドカドカ日本語 — 尾崎豊「I LOVE YOU」

YouTube 「尾崎 豊 - I LOVE YOU (Official Music Video)」(Yutaka Ozaki Official YouTube Channel, 4분 15초)로 만든
**일본어 노래 학습 카드 앱**(한국어 학습자용). 22줄. 한국어 뜻·히라가나 읽기·주석·한자 풀이·표현 23·단어 16.

## 이 곡을 고른 이유

- 앱 안 재생을 착수 전에 확인했습니다(`tools/embed_check.py` → OK).
- **공식 채널에 공식 일본어·한국어 자막이 둘 다 붙어 있고 22줄이 그대로 맞물립니다.** 작업 문서의 최상 등급(A)입니다.
  음성 인식을 쓰지 않았습니다.
- **한 줄이 13초씩 갑니다.** 말이 느려 발음을 붙잡기 좋습니다.
- 같은 꼴이 자리를 옮겨 가며 되풀이됩니다. 「まるで〜みたい」가 두 줄 잇따르다 7번 줄에서 「〜の様な」로 바뀌고,
  2번 줄 辿り着いた 가 14번 줄에서 辿り着けない 로 뒤집힙니다. 방에는 닿았지만 삶에는 닿지 못한다는 말입니다.
- **恋와 愛를 갈라 씁니다.** 두 말의 차이를 한 노래 안에서 볼 수 있습니다.
- 〜ぬ(触れられぬ·しまわぬ)·〜すぎる·〜さえ〜ない 같은 문어투가 나옵니다.
- 躰(体)·小猫(子猫)·暮し(暮らし)처럼 옛 표기가 섞여 있어, 사전형과 본문 표기를 함께 익히게 됩니다.

## 줄 시각

공식 자막 두 벌에서 만들었습니다. 일본어 22큐와 한국어 22큐가 줄 수·시각 모두 그대로 맞아
**시각을 손대지 않고 썼습니다.** 한국어 뜻은 공식 번역을 기준으로 학습용으로 다듬었습니다
(`src/_ko_official.txt` 가 그 기준입니다).
박 그리드(`src/beats.json`)는 `beats.py` 로 구했습니다(BPM 149.3 · 4/4).

## 학습 탭

**오늘 · 복습 · 목록 · 학습법** 넷. 「오늘」은 단락(1절 앞·1절 뒤·2절 앞·2절 뒤) 단위로
들으며 읽기 → 마디 따라 부르기 → 가사 가리고 부르기 → 표현·단어 4단계를 안내합니다.
가사 22줄·표현·단어·한자 풀이 표제어는 **일본어 음원(edge-tts)** 130개를 내장해
「읽어주기」가 오프라인에서도 됩니다. 음원은 −22 LUFS 로 정규화돼 있고 🔈 버튼으로 음량을 바꿉니다.

## 노래방·화면 잠금

가사 중심 화면입니다. 늘 고정되는 것은 아래 이동 바 한 줄뿐이고, 마디·미세 조정은
오른쪽 끝 버튼으로 여는 서랍에 있습니다. 탭 줄 오른쪽 끝 자물쇠를 누르면 화면이 잠기고
**2초간 꾹 누르면** 풀립니다(PC 는 Esc). 잠긴 동안에도 영상과 읽어주기는 계속 재생됩니다.

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8111).

## 구성

```
iloveyou-cards/
├─ Japanese-ILoveYou22-Cards.html   앱 (단일 파일, 데이터·음원 내장)
├─ start.bat / start.sh
├─ README.md
└─ src/
   ├─ lyrics.txt        가사 22줄 (빈 줄 = 구간 경계) — 공식 일본어 자막에서
   ├─ subtitles.srt     줄별 시각 (공식 자막 그대로, 손대지 않음)
   ├─ _ko_official.txt  공식 한국어 자막 22줄 (뜻을 다듬을 때의 기준)
   ├─ ko.txt            id|한국어 뜻|읽기|주석 — 학습용으로 직접 작성
   ├─ kanji.txt         한자 훈음 50자 (가사 한자 44자 100% 커버, 빌드가 검사)
   ├─ words.txt         한자어 사전 37항목 (gen_words.py 로 생성)
   ├─ gen_words.py / lemma_meanings.py / lemma_base.py / check_cov.py
   ├─ study.txt         표현 23 · 단어 16
   ├─ segs.json         가사 줄 목록 (gen_words·check_cov 용)
   ├─ beats.json / beats.py / align.py
   ├─ audio/            edge-tts 음원 130개 + index.json
   ├─ build.py          최종 HTML 생성
   └─ tpl.html          화면 템플릿 (mahou-cards 와 동일 계열)
```

## 재빌드

```bash
cd src && ../../.venv/bin/python gen_words.py > words.txt && python3 build.py
../../.venv/bin/python ../../tools/make_study_audio.py iloveyou-cards --cards --gloss   # 음원(인터넷 필요) 후 build.py 재실행
```

줄 시각을 다시 만들려면 공식 자막을 받습니다(리포에 넣지 않습니다).

```bash
.venv/bin/yt-dlp --skip-download --write-subs --sub-langs "ja,ko" --sub-format srt \
  --convert-subs srt -o "%(id)s.%(ext)s" "https://youtu.be/EsOsc-sajMk"
.venv/bin/python src/beats.py il.wav                 # → beats.json
```

## 출처

- 영상 · 음원 · 가사 · 한국어 번역: YouTube Yutaka Ozaki Official YouTube Channel 「I LOVE YOU」 (EsOsc-sajMk) 의 공식 자막
- 히라가나 읽기 · 문법 주석 · 표현/단어 풀이 · 한자 훈음: 학습용으로 직접 작성

학습용 개인 이용을 전제로 한 페이지입니다.
