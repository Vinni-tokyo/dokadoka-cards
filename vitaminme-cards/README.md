# 도카도카 한국어 공부 · 노래로 배우기 — fromis_9 「Vitamin ME」

YouTube 공식 MV 「fromis_9 (프로미스나인) 'Vitamin ME' MV」(fromis_9 공식 채널, 2026-07-21, 3분 33초)에 붙은
**공식 한국어·일본어 가사 자막**(84줄, 1:1 대응·타이밍 포함)으로 만든 **노래 학습 카드 앱**(일본어 모어 학습자용).
가사 84줄 = 한글 줄 33 + 영어만 있는 줄 51. 한글 줄에는 **가나 읽기**와 문법 메모를 붙였습니다.

같은 폴더의 `korean-cards/`(예능·브이로그) 템플릿을 그대로 쓰되, 노래에 맞게 세 가지를 더했습니다.

- **읽기(カナ) 줄** — 카드와 대본에 가타카나 읽기 표시(토글 `R`). 연음을 반영한 근사치이며 음원이 정답
- **영어만 있는 줄 옵션** — 「Not A,B,C」 「Vitamin ME」 같은 훅은 기본 포함, 학습에 집중할 땐 끄면 한글 33줄만
- **곡 구성 = 장면** — 인트로 · 1절 · 프리코러스 · 후렴 · 훅 · 2절 · … · 브릿지 · 마지막 후렴 · 아웃트로 12구간

대본 탭 각 줄의 ↻ 로 **한 줄만 반복**해 따라 부를 수 있고, 반복 중 다음을 누르면 다음 줄로 반복이 옮겨 갑니다.

---

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저를 엽니다(포트 8093). Python 3 가 필요합니다. `file://` 로 열면 YouTube 임베드가 거부되어(Error 153) 재생 버튼이 YouTube 새 탭을 엽니다.

## 구성

```
vitaminme-cards/
├─ Korean-VitaminME84-Cards.html   앱 (단일 파일, 데이터 내장)
├─ start.bat / start.sh            실행기
├─ README.md
└─ src/
   ├─ subtitles.ko.srt             공식 MV 한국어 가사 자막 (yt-dlp `--sub-langs ko`)
   ├─ subtitles.ja.srt             공식 MV 일본어 가사 자막 (행이 한국어와 1:1)
   ├─ subtitles.en.srt             영어 자막 (참고용, 26행부터 한 줄 어긋나 있어 미사용)
   ├─ rd.txt                       가나 읽기·문법 메모 `id|読み|注記` (한글 33줄)
   ├─ study.txt                    학습 표현·단어 40건 `종류|한국어|일본어|메모`
   ├─ build.py                     최종 HTML 생성 (자막 행 대응·읽기 누락을 assert 로 검사)
   └─ tpl.html                     화면 템플릿 (korean-cards 템플릿 + 읽기 줄·영어 줄 옵션)
```

## 재빌드

```bash
python3 src/build.py
```

## 다른 노래로 바꾸려면

1. 공식 MV 에 **수동 한국어·일본어 자막**이 있는지 `yt-dlp --list-subs` 로 확인합니다(fromis_9 공식 MV 는 ko·ja·en·zh 가 붙어 있었습니다). 자동 자막은 노래에서 쓸 수 없습니다.
2. `--sub-langs ko,ja --convert-subs srt` 로 받아 `src/subtitles.ko.srt`·`src/subtitles.ja.srt` 에 둡니다. 행 수와 시각이 1:1 인지 빌드가 검사합니다.
3. `rd.txt` 에 한글 줄의 읽기·메모를, `study.txt` 에 어휘를 쓰고, `build.py` 의 `VID`·`NICK`·`SCENES`·시리즈 제목을 바꿉니다.
4. `start.*` 의 파일명·포트, `tpl.html` 의 `LS` 키·내보내기 파일명을 바꿉니다.

## 출처

- 영상·가사 자막: YouTube `sLk8zWUuYTA` — fromis_9 (프로미스나인) 'Vitamin ME' MV (fromis_9 공식 채널, 2026-07-21). 한국어·일본어 가사 자막은 채널이 붙인 공식 자막입니다.
- 읽기·문법 메모·학습 항목은 직접 작성한 것이라 오류가 있을 수 있습니다. 앱 안의 「편집」으로 고칠 수 있습니다.

가사의 권리는 원저작권자에게 있습니다. 영상은 YouTube 공식 플레이어로 재생되며, 학습용 개인 이용을 전제로 한 페이지입니다.
