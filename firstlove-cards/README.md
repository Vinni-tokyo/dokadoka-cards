# 도카도카 일본어 공부 · 노래로 배우기 — 宇多田ヒカル 「First Love」

YouTube 영상 「Hikaru Utada(우타다 히카루) - First Love [가사/해석/번역/lyrics]」(Sople soso playlist · with 유니버설뮤직코리아, 2023-01-16, 4분 18초)로 만든
**일본어 노래 학습 카드 앱**(한국어 모어 학습자용). 가사 28줄, 히라가나 읽기·한국어 뜻·한자 풀이 병기.

이 영상에는 자막이 없어서(수동·자동 모두), 줄별 타이밍을 **음성 인식(faster-whisper, 일본어)** 으로 만들었습니다.
28줄 모두 인식 결과와 맞았고(보간 0), 어긋남은 대체로 0.2~0.5초 안입니다.
느린 발라드라 **일본어 초·중급 듣기·따라 부르기**에 맞고, 문형(〜んだろう·〜ても·〜まで·〜ばかり)이 반복되어 외우기 좋습니다.

같은 폴더의 `yubisaki-cards/`(애니) 템플릿에 노래 기능을 더했습니다.

- **노래방 탭** — 지금 부르는 줄을 크게, 줄의 시작·끝 시각에 맞춰 왼쪽부터 노란색으로 채움. 읽기·뜻 표시, 이전 줄·다음 두 줄, 카운트인 점, 「처음부터 / 이 줄부터 / 일시정지」
- **마디 반복** — BPM 90 · 4/4 박 그리드로 1·2·4·8마디 루프, 「이 줄의 마디」, ◀ ▶, ±1마디, 속도 0.5×·0.75×, 마디 시작 ±1박 보정(발라드라 템포가 조금 흔들리므로 어긋나면 보정)
- **구간 = 장면** — 1절 · 후렴 1 · 2절 · 후렴 2 · 후렴 3(아웃트로)
- 그 외(드릴·로컬 음원·이어 듣기·한자 풀이·재생 구간 보정 등)는 다른 일본어 앱과 동일

---

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8091). `file://` 로 열면 YouTube 임베드가 거부되어(Error 153) 재생 버튼이 YouTube 새 탭을 엽니다.
상위 폴더의 `start.bat`/`start.sh`(포트 8100)로 열면 관문 페이지에서 다른 앱과 함께 고를 수 있습니다.

## 구성

```
firstlove-cards/
├─ Japanese-FirstLove28-Cards.html   앱 (단일 파일, 데이터·음원 내장)
├─ start.bat / start.sh              실행기
├─ README.md
└─ src/
   ├─ lyrics.txt                     가사 원문 (불리는 순서, 빈 줄 = 구간 경계)
   ├─ align.py                       가사 줄 ↔ 음성 인식 단어 시각 정렬(일본어·영어 혼용) → subtitles.srt
   ├─ subtitles.srt                  줄별 시각 (align.py 출력)
   ├─ beats.py / beats.json          BPM·박 그리드 (reasons-cards 와 같은 도구)
   ├─ ko.txt                         한국어 뜻·읽기·주석 28건 `id|뜻|읽기|주석`
   ├─ study.txt                      학습 표현·단어 45건 `종류|일본어|읽기|뜻|메모`
   ├─ words.txt / kanji.txt          한자 풀이 사전 (한자어 21 · 한자 27)
   ├─ audio/                         학습 음원 (원문·뜻 mp3, tools/make_study_audio.py)
   ├─ build.py                       최종 HTML 생성
   └─ tpl.html                       화면 템플릿 (yubisaki-cards + 노래방·마디 반복)
```

## 재빌드 · 타이밍 다시 만들기

```bash
python3 src/build.py                       # 가사·시각·번역·학습 데이터·음원으로 HTML 생성
```

음성 파일과 인식 결과는 리포에 넣지 않습니다. 타이밍을 다시 만들려면:

```bash
../.venv/bin/yt-dlp --js-runtimes node -x --audio-format wav -o /tmp/song.wav -- https://www.youtube.com/watch?v=lLz9_XdyJGo
../.venv/bin/python - <<'EOF'
from faster_whisper import WhisperModel; import json
m = WhisperModel('medium', device='cpu', compute_type='int8')
segs, _ = m.transcribe('/tmp/song.wav', language='ja', word_timestamps=True, condition_on_previous_text=False,
                       initial_prompt='宇多田ヒカル「First Love」の歌詞。最後のキスはタバコのflavorがした。')
json.dump([{'w': w.word, 's': round(w.start, 2), 'e': round(w.end, 2)} for s in segs for w in (s.words or [])],
          open('/tmp/words.json', 'w', encoding='utf-8'), ensure_ascii=False)
EOF
python3 src/align.py /tmp/words.json        # → src/subtitles.srt (매칭 실패 줄은 보간 + REPORT)
../.venv/bin/python src/beats.py /tmp/song.wav   # → src/beats.json
python3 src/build.py
```

특정 줄의 시각이 틀리면 `src/fixes.txt` 에 `id|시작초|끝초` 를 적고 `align.py` 를 다시 돌리거나, 앱 안 편집 박스의 「재생 구간 조정」으로 그 자리에서 맞출 수 있습니다.

## 출처

- 영상: YouTube `lLz9_XdyJGo` — Sople soso playlist(유니버설뮤직코리아 협력), 2023-01-16. 원곡 宇多田ヒカル 「First Love」(1999)
- 가사: 공식 가사. 줄별 시각은 음성 인식(faster-whisper medium)으로 맞춘 것이라 오차가 있을 수 있습니다.
- 번역·읽기·주석·학습 항목은 직접 작성한 것이라 오류가 있을 수 있습니다.

학습용 개인 이용을 전제로 한 페이지입니다. 영상은 YouTube 공식 플레이어로 재생됩니다.
