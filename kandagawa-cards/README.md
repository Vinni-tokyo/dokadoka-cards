# 도카도카 일본어 공부 · ドカドカ日本語 — かぐや姫「神田川」

YouTube 「かぐや姫 - 神田川」(3분 4초)로 만든 **일본어 노래 학습 카드 앱**(한국어 학습자용).
가사 22줄. 한국어 뜻·히라가나 읽기·주석·한자 풀이·표현 21·단어 22.

## 이 곡을 고른 이유와 제약

- 앱 안 재생을 착수 전에 확인했습니다(`tools/embed_check.py` → OK).
- 1973년 포크송. 느리고(91 BPM) 가사가 평이한 구어체라 따라 부르기에 맞습니다.
- 1절과 2절이 같은 자리에서 말을 바꿉니다(「忘れたかしら」↔「捨てたのかしら」, 「言ったのに」가 두 번).
  후렴은 「何も恐くなかった」를 「やさしさが恐かった」로 뒤집습니다. 짝을 이루는 줄은 주석에 표시했습니다.
- **자막이 전혀 없습니다**(수동·자동 모두). 그래서 **가사 원문은 앱 사용자가 제공한 가사지를 그대로 쓰고**,
  줄별 시각만 음원에서 구했습니다.
- ⚠ **이 영상은 공식 채널이 아닙니다**(2012년 개인 업로드). 내려가면 앱이 재생되지 않습니다.
  원 음반사 PANAM 의 공식 업로드(싱글 `egtVKrL4NYE` · 앨범 `ur7dz3FWMnk` · 라이브 `bQazmGAHUVo`)도
  재생 검사를 통과했으니, 옮기려면 `src/build.py` 의 `VID` 를 바꾸고 **줄 시각을 다시 맞춰야** 합니다
  (버전마다 길이가 3~7초 다릅니다).

## 줄 시각

음원을 faster-whisper(medium, 단어 시각)로 인식하고 `align.py` 로 가사 22줄과 순서 정렬했습니다.
**22줄 전부 직접 대응**했고 보간은 0줄입니다(유사도 최저 0.67, 대부분 1.00).
인식이 줄 앞부분만 잡아 끝이 일찍 찍힌 2줄(13·18번)은 `tools/fix_cue_ends.py` 로 이 곡의 실제
노래 속도에 맞춰 늘렸습니다. 박 그리드(`src/beats.json`)는 `beats.py` 로 구했습니다(BPM 91.3 · 4/4 · 70마디).

## 학습 탭

**오늘 · 복습 · 목록 · 학습법** 넷. 「오늘」은 단락(1절 · 후렴 1 · 2절 · 후렴 2) 단위로
들으며 읽기 → 마디 따라 부르기 → 가사 가리고 부르기 → 표현·단어 4단계를 안내합니다.
가사 22줄·표현·단어·한자 풀이 표제어는 **일본어 음원(edge-tts)** 151개를 내장해
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

간이 서버를 띄우고 브라우저를 엽니다(포트 8108).

## 구성

```
kandagawa-cards/
├─ Japanese-Kandagawa22-Cards.html   앱 (단일 파일, 데이터·음원 내장)
├─ start.bat / start.sh
├─ README.md
└─ src/
   ├─ lyrics.txt        가사 22줄 (빈 줄 = 구간 경계) — 사용자 제공
   ├─ subtitles.srt     줄별 시각 (align.py + fix_cue_ends.py)
   ├─ ko.txt            id|한국어 뜻|읽기|주석 — 학습용으로 직접 작성
   ├─ kanji.txt         한자 훈음 55자 (가사 한자 53자 100% 커버, 빌드가 검사)
   ├─ words.txt         한자어 사전 45항목 (gen_words.py 로 생성)
   ├─ gen_words.py / lemma_meanings.py / lemma_base.py / check_cov.py
   ├─ study.txt         표현 21 · 단어 22
   ├─ segs.json         가사 줄 목록 (gen_words·check_cov 용)
   ├─ beats.json / beats.py / align.py
   ├─ audio/            edge-tts 음원 151개 + index.json
   ├─ build.py          최종 HTML 생성
   └─ tpl.html          화면 템플릿 (driedflower-cards 와 동일 계열)
```

## 재빌드

```bash
cd src && ../../.venv/bin/python gen_words.py > words.txt && python3 build.py
../../.venv/bin/python ../../tools/make_study_audio.py kandagawa-cards --cards --gloss   # 음원(인터넷 필요) 후 build.py 재실행
```

줄 시각을 다시 만들려면 음원과 인식 결과가 필요합니다(둘 다 리포에 넣지 않습니다).

```bash
.venv/bin/yt-dlp -x --audio-format wav -o kd.wav "https://youtu.be/JSgyHiKESGw"
# faster-whisper(medium, language=ja, word_timestamps=True) → words.json
python3 src/align.py words.json                    # → subtitles.srt
python3 ../tools/fix_cue_ends.py src/subtitles.srt # 잘린 끝 시각 보정
.venv/bin/python src/beats.py kd.wav               # → beats.json
```

## 출처

- 영상 · 음원: YouTube 「かぐや姫 - 神田川」 (JSgyHiKESGw) — 공식 채널 아님
- 가사 원문: 앱 사용자가 제공
- 한국어 뜻 · 읽기 · 주석 · 표현/단어 풀이: 학습용으로 직접 작성

학습용 개인 이용을 전제로 한 페이지입니다.
