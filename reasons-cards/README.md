# 도카도카 영어 공부 · 노래로 배우기 — Matt Redman 「10,000 Reasons (Bless the Lord)」

YouTube 영상 「10,000 Reasons (Bless the Lord) - Matt Redman (with Lyrics)」(GloryToFatherGod, 2011-11-25, 5분 42초)로 만든
**영어 노래 학습 카드 앱**(한국어 모어 학습자용). 가사 51줄, 한국어 뜻·문법 메모 병기.

이 영상에는 자막이 전혀 없어서(수동·자동 모두), 줄별 타이밍을 **음성 인식(faster-whisper)** 으로 만들었습니다.
가사 원문은 영상 설명란에서 가져오되, 실제로 불리는 순서(후렴 5번, 3절 뒤 "Forevermore" 반복, 애드리브 "Bless You, Lord")에 맞게 고쳤습니다.
느리고 발음이 또렷한 찬송이라 **영어 초·중급 듣기·따라 부르기**에 맞습니다.

같은 폴더의 `english-cards/`(인터뷰) 템플릿에 노래 기능을 더했습니다.

- **노래방 탭** — 지금 부르는 줄을 크게, 줄의 시작·끝 시각에 맞춰 왼쪽부터 노란색으로 채움. 이전 줄·다음 두 줄, 카운트인 점, 「처음부터 / 이 줄부터 / 일시정지」
- **마디 반복** — BPM 72 · 4/4 박 그리드로 1·2·4·8마디 DJ 식 루프, 「이 줄의 마디」, ◀ ▶(설정 마디 수만큼 이동), ±1마디 조절, 속도 0.5×·0.75×, 마디 시작 ±1박 보정. 루프 구간의 가사가 아래 나열되고 재생에 맞춰 하이라이트
- **구간 = 장면** — 후렴 1 · 1절 · 후렴 2 · 2절 · 후렴 3 · 3절 · 후렴 4 · 후렴 5 · 브릿지 · 아웃트로

---

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8092). `file://` 로 열면 YouTube 임베드가 거부되어(Error 153) 재생 버튼이 YouTube 새 탭을 엽니다.

## 구성

```
reasons-cards/
├─ English-Reasons51-Cards.html   앱 (단일 파일, 데이터 내장)
├─ start.bat / start.sh           실행기
├─ README.md
└─ src/
   ├─ lyrics.txt                  가사 원문 (불리는 순서, 빈 줄 = 구간 경계)
   ├─ align.py                    가사 줄 ↔ 음성 인식 단어 시각 정렬 → subtitles.srt
   ├─ subtitles.srt               줄별 시각 (align.py 출력)
   ├─ beats.py / beats.json       BPM·박 그리드 (템포 추적 모드 --track 72: 끝부분 리타르단도 반영)
   ├─ ko.txt                      한국어 뜻·주석 51건 `id|뜻|주석`
   ├─ study.txt                   학습 표현·단어 38건 `종류|영어|뜻|메모`
   ├─ build.py                    최종 HTML 생성
   └─ tpl.html                    화면 템플릿 (english-cards + 노래방·마디 반복)
```

## 재빌드 · 타이밍 다시 만들기

```bash
python3 src/build.py                       # 자막·읽기·학습 데이터로 HTML 생성
```

음성 파일과 인식 결과는 리포에 넣지 않습니다. 타이밍을 다시 만들려면:

```bash
../.venv/bin/yt-dlp -x --audio-format wav -o /tmp/song.wav -- https://www.youtube.com/watch?v=DXDGE_lRI0E
../.venv/bin/pip install faster-whisper librosa soundfile        # 최초 1회
../.venv/bin/python - <<'EOF'
from faster_whisper import WhisperModel; import json
m = WhisperModel('medium', device='cpu', compute_type='int8')
segs, _ = m.transcribe('/tmp/song.wav', language='en', word_timestamps=True, condition_on_previous_text=False,
                       initial_prompt='Worship song lyrics: Bless the Lord, O my soul. Worship His holy name.')
json.dump([{'w': w.word.strip(), 's': round(w.start,2), 'e': round(w.end,2)} for s in segs for w in (s.words or [])], open('/tmp/words.json','w'))
EOF
python3 src/align.py /tmp/words.json       # → src/subtitles.srt (매칭 실패 줄은 보간, fixes.txt 로 손 보정 가능)
../.venv/bin/python src/beats.py /tmp/song.wav src/subtitles.srt --track 72   # → src/beats.json
python3 src/build.py
```

`small` 모델은 3절과 브릿지를 놓쳤고 `medium` 은 51줄 전부 잡았습니다(CPU 63초). 줄 시각은 음성 인식 기준이라 0.2~0.5초 어긋날 수 있고, 앱의 편집으로는 고칠 수 없으니 `fixes.txt`(`id|시작|끝`)에 적고 다시 정렬합니다.

## 출처

- 영상: YouTube `DXDGE_lRI0E` — 10,000 Reasons (Bless the Lord) - Matt Redman (with Lyrics), GloryToFatherGod 채널(공식 아님)
- 곡: Matt Redman · Jonas Myrin, 「10,000 Reasons」(2011). 가사의 권리는 원저작권자에게 있습니다.
- 줄 시각·번역·주석·학습 항목은 직접 만든 것이라 오류가 있을 수 있습니다.

학습용 개인 이용을 전제로 한 페이지입니다. 영상은 YouTube 공식 플레이어로 재생됩니다.
