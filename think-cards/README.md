# 도카도카 영어 공부 · How to Stop AI from Killing Your Critical Thinking

YouTube TED 강연 「How to Stop AI from Killing Your Critical Thinking」(Advait Sarkar, TED, 2025-12-28, 14분 55초, 조회 69만)로 만든
**영어 학습 카드 앱**(한국어 모어 학습자용). 카드 127장.

AI 에 일을 맡길수록 우리가 무엇을 잃는지, 그리고 어떻게 쓰면 오히려 생각이 깊어지는지를 사례로 풀어냅니다. 업무 문서·보고서를 소재로 해서 비즈니스 영어와 학술 토론 어휘가 함께 나옵니다.

**자막 출처와 라이선스** · 영어·한국어 자막 모두 **TED 가 공개한 공식 자막**이고, TED 강연과 자막은
[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) 으로 배포됩니다.
이 앱은 그 자막을 출처 표기와 함께 비영리 학습 목적으로 그대로 싣습니다. 한국어 뜻은 TED 한국어 자막을
시각으로 맞춰 붙인 것이고(번역을 새로 만들지 않았습니다), 학습 표현·단어와 문법 메모만 직접 작성했습니다.

---

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8088). `file://` 로 열면 YouTube 임베드가 거부되어(Error 153)
재생 버튼이 YouTube 새 탭을 엽니다.

## 기능

- **카드** — 영어 문장 + 한국어 뜻(가리기/보기), 장면별 필터, 체크 진도
- **대본** — 127줄 목록, 줄 클릭 시 그 위치부터 재생, 줄별 구간 반복
- **감상** — 영상을 끊김 없이 재생하며 현재 문장과 앞뒤 문장을 크게 표시
- **학습** — 드릴(간격 반복) · 표현 20 · 단어 20 · 퀴즈 · 오늘 분량 · 학습법
- **장면** — 도입(계산기의 교훈) · 자동화가 앗아가는 것 · 메타인지 · AI 를 제대로 쓰는 법 · 맺음

## 구성

```
think-cards/
├─ English-Thinking127-Cards.html   앱 (단일 파일, 데이터 내장)
├─ start.bat / start.sh
├─ README.md
└─ src/
   ├─ subtitles.srt   TED 공식 영어 자막 (yt-dlp --sub-langs en)
   ├─ ko.srt          TED 공식 한국어 자막 (yt-dlp --sub-langs ko)
   ├─ seg.py          영어 자막 → 카드 분할 (문장 끝 기준)
   ├─ build.py        최종 HTML 생성 (한국어 자막을 시각으로 맞춰 붙임)
   ├─ tpl.html        화면 템플릿
   └─ study.txt       학습 표현·단어 40건 `종류|영어|뜻|메모`
```

## 재빌드

```bash
python3 src/build.py
```

자막을 다시 받으려면:

```bash
../.venv/bin/yt-dlp --skip-download --write-subs --sub-langs en,ko \
  --sub-format srt --convert-subs srt -o 'src/%(id)s.%(ext)s' \
  -- https://www.youtube.com/watch?v=3lPnN8omdPA
# 받은 파일을 src/subtitles.srt (en), src/ko.srt (ko) 로 둔다
```

## 출처

- 영상·자막: YouTube `3lPnN8omdPA` — How to Stop AI from Killing Your Critical Thinking (Advait Sarkar, TED, 2025-12-28)
- 라이선스: TED 강연 및 자막 CC BY-NC-ND 4.0. 비영리 학습 목적으로 출처를 밝혀 사용합니다.
- 학습 표현·단어와 문법 메모는 직접 작성한 것이라 오류가 있을 수 있습니다. 앱 안의 「편집」으로 고칠 수 있습니다.

영상은 YouTube 공식 플레이어로 재생됩니다.
