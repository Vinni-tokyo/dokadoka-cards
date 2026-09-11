# 도카도카 한국어 공부 · 노래로 배우기 — 유재하 「사랑하기 때문에」 cover by 지원 (fromis_9)

YouTube 영상 「[fl▶ylist] ‘유재하 - 사랑하기 때문에’ cover by 지원」(Official fromis_9, 2023-12-14, 5분 18초)로 만든
**한국어 노래 학습 카드 앱**(일본어 모어 학습자용). 가사 33줄, 가타카나 읽기·일본어 뜻·문법 메모 병기.

이 영상에는 자막이 없어서(수동·자동 모두), 줄별 타이밍을 **음성 인식(faster-whisper, 한국어)** 으로 만들었습니다.
두 번 인식(기본·빔 서치)한 결과를 대조해 33줄 전부 맞췄고, 어긋난 15줄은 `src/fixes.txt` 로 손보정했습니다.
느린 발라드라 **한국어 초·중급 듣기·따라 부르기**에 맞고, 노래에만 나오는 문어체(〜소, 〜리오, 〜리, 〜기에)를 배울 수 있습니다.

같은 폴더의 `korean-cards/`(예능) 템플릿에 노래 기능을 더했습니다(`Vitamin ME` 앱과 같은 구성이지만 드릴·로컬 음원·한자 없음 대신 읽기 등 최신 기능 포함).

- **カラオケ 탭** — 지금 부르는 줄을 크게, 줄의 시작·끝 시각에 맞춰 왼쪽부터 노란색으로 채움. 읽기(가타카나)·뜻 표시, 이전 줄·다음 두 줄, 카운트인 점
- **小節リピート** — BPM 130(발라드의 2배 박) · 4/4 박 그리드로 1·2·4·8마디 루프, 「この行の小節」, ◀ ▶, ±1마디, 속도 0.5×·0.75×, 마디 시작 ±1박 보정
- **구간 = 장면** — 1절 · 후렴 1 · 2절 · 후렴 2 · 마지막 후렴(아웃트로)
- 그 외(드릴·로컬 음원(원문·뜻)·이어 듣기·재생 구간 보정 등)는 다른 한국어 앱과 동일

---

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8089). `file://` 로 열면 YouTube 임베드가 거부되어(Error 153) 재생 버튼이 YouTube 새 탭을 엽니다.

## 구성

```
saranghagi-cards/
├─ Korean-Saranghagi33-Cards.html   앱 (단일 파일, 데이터·음원 내장)
├─ start.bat / start.sh             실행기
├─ README.md
└─ src/
   ├─ lyrics.txt                    가사 원문 (불리는 순서, 빈 줄 = 구간 경계)
   ├─ align.py                      가사 줄 ↔ 음성 인식 단어 시각 정렬(한글·가나·한자·영숫자) → subtitles.srt
   ├─ fixes.txt                     줄별 시각 손보정 15건 `id|시작|끝`
   ├─ subtitles.srt                 줄별 시각 (align.py 출력)
   ├─ beats.py / beats.json         BPM·박 그리드
   ├─ ja.txt                        일본어 뜻·주석 33건 `id|訳|注記`
   ├─ rd.txt                        가타카나 읽기 33건 `id|読み`
   ├─ study.txt                     학습 표현·단어 47건 `種類|韓国語|日本語|メモ`
   ├─ audio/                        학습 음원 (원문 한국어·뜻 일본어 mp3)
   ├─ build.py                      최종 HTML 생성 (korean-cards 와 같은 SERIES 1개 구조)
   └─ tpl.html                      화면 템플릿 (korean-cards + カラオケ·小節リピート)
```

## 재빌드 · 타이밍 다시 만들기

```bash
python3 src/build.py
```

음성 파일과 인식 결과는 리포에 넣지 않습니다. 타이밍을 다시 만들려면:

```bash
../.venv/bin/yt-dlp --js-runtimes node -x --audio-format wav -o /tmp/song.wav -- https://www.youtube.com/watch?v=MzKzs5DnQT8
../.venv/bin/python - <<'EOF'
from faster_whisper import WhisperModel; import json
m = WhisperModel('medium', device='cpu', compute_type='int8')
segs, _ = m.transcribe('/tmp/song.wav', language='ko', beam_size=5, word_timestamps=True, condition_on_previous_text=False,
                       initial_prompt='유재하 「사랑하기 때문에」. 처음 느낀 그대 눈빛은 혼자만의 오해였던가요. 커다란 그대를 향해 작아져 가는 나이기에.')
json.dump([{'w': w.word, 's': round(w.start, 2), 'e': round(w.end, 2)} for s in segs for w in (s.words or [])],
          open('/tmp/words.json', 'w', encoding='utf-8'), ensure_ascii=False)
EOF
python3 src/align.py /tmp/words.json        # → src/subtitles.srt (fixes.txt 가 마지막에 덮어씀)
../.venv/bin/python src/beats.py /tmp/song.wav
python3 src/build.py
```

빔 서치(`beam_size=5`)와 가사 힌트(`initial_prompt`)가 없으면 2절을 잘못 알아듣습니다(실제로 「커다란 그대를 향해」가 환청으로 나왔음).

## 출처

- 영상: YouTube `MzKzs5DnQT8` — Official fromis_9 「fl▶ylist」, 2023-12-14. 원곡 유재하 「사랑하기 때문에」(1987)
- 가사: 원곡 가사(커버도 동일). 줄별 시각은 음성 인식으로 맞춘 것이라 오차가 있을 수 있습니다.
- 번역·읽기·주석·학습 항목은 직접 작성한 것이라 오류가 있을 수 있습니다.

학습용 개인 이용을 전제로 한 페이지입니다. 영상은 YouTube 공식 플레이어로 재생됩니다.
