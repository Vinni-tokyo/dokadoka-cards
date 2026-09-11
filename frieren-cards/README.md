# 도카도카 일본어 공부 · ドカドカ日本語 — 葬送のフリーレン ミニアニメ「●●の魔法」(3편)

TOHO animation 공식 채널이 올리는 『葬送のフリーレン(장송의 프리렌)』공식 미니 애니 3편(제20~22회, 화당 1~2분)으로 만든
**일본어 학습 카드 앱**(한국어 학습자용). 2023년 화제작 본편의 등장인물(프리렌·페른 등)이 짧은 마법 개그를 펼치는 보너스 영상입니다.

- **입구**: `index.html` — 3편 목록. 각 화는 `Japanese-Frieren<회차번호>-Cards.html` 단일 파일.
- 등장인물이 2~3명뿐이고 대사가 짧아, 자동생성 자막(수동 자막 없음)치고는 인식이 또렷한 편입니다.
- 이전에 만들려던 『銀河特急 ミルキー☆サブウェイ』와 달리 **영상 삽입 재생(embed)이 정상 작동**하는 것을 헤드리스 브라우저로 직접 확인한 뒤에 만들었습니다.

## 실행

| 환경 | 방법 |
|---|---|
| Windows | `start.bat` **더블클릭** |
| Linux / mac | `./start.sh` |

간이 서버를 띄우고 브라우저로 `index.html`(3편 목록)을 엽니다(포트 8088).

## 구성

```
frieren-cards/
├─ index.html                       3편 목록(입구)
├─ Japanese-Frieren20/21/22-Cards.html   화별 앱(단일 파일, 데이터·음원 내장)
├─ start.bat / start.sh
├─ README.md
└─ src/
   ├─ seg.py           ASR 롤링 캡션을 문장 단위로 손 재분할 → epN/segs.json
   │                    (한 큐가 여러 문장을 담고 종료 시각이 다음 큐와 겹치는 형식.
   │                     실제 발화 구간 = 이 큐 시작 → 다음 큐 시작. 여러 문장은 글자수 비례로 시간 분배)
   ├─ reading.py       fugashi(unidic-lite)로 히라가나 읽기 자동 생성
   ├─ kanji.txt        한자 훈음 사전(3편 공용, 129자)
   ├─ words.txt        한자어 사전(3편 공용, 104항목) — gen_words.py + lemma_meanings.py 로 자동 생성
   ├─ gen_words.py / lemma_meanings.py
   ├─ check_cov.py     화별 한자 커버리지 검사
   ├─ make_audio.py    화별 학습 음원 생성(edge-tts, ja-JP-Nanami / ko-KR-SunHi)
   ├─ build.py         최종 HTML 생성(화 번호 인자로 선택, 기본 전체)
   ├─ tpl.html         화면 템플릿(yubisaki-cards·milky-cards 계열과 동일 기반)
   ├─ raw/epN/         원본 자동생성 자막(YouTube ASR)
   └─ epN/
      ├─ segs.json      분할 결과(자동)
      ├─ ko.txt         id|한국어 뜻|읽기(히라가나)|주석 — 직접 번역
      ├─ words.txt / kanji.txt   (공용 사전의 사본, build.py 가 읽음)
      ├─ study.txt      표현(E)·단어(V) 큐레이션
      └─ audio/         학습 음원(mp3) + index.json
```

## 재빌드

```bash
cd src
python3 seg.py            # raw/epN/*.srt → epN/segs.json (seg.py 안의 손 분할표를 고치면 재생성)
python3 gen_words.py > words.txt && cp words.txt kanji.txt ep20/ ep21/ ep22/   # 사전 갱신 시
python3 check_cov.py ep20  # 한자 커버리지 확인(20/21/22 반복)
python3 build.py           # 전체 화 빌드
python3 make_audio.py      # 학습 음원 생성(edge-tts, 인터넷 필요) 후 build.py 재실행
```

## 번역·자막에 대해

- **자막**: 세 편 모두 수동 자막이 없어 YouTube 자동생성 자막(ASR)을 받았습니다. 롤링 캡션 형식이라 한 줄에 여러 문장이
  섞이고 종료 시각이 다음 줄과 겹칩니다 — 문장 단위로 손으로 다시 나누고(`seg.py`), 오인식 일부(예: 제목이 매번
  "早々のフリーレン"으로 잘못 인식되는 것 등)를 교정했습니다. 다만 등장인물 목소리를 직접 대조하며 만든 것이 아니라,
  빠르거나 겹치는 대사·불분명한 고유명사(주문 이름 등)는 원문에 가깝게 남기고 무리하게 지어내지 않았습니다.
- **한국어 뜻**: 직접 번역. 원작(만화·애니 본편)을 참고했지만 오류가 있을 수 있습니다.
- **화자 표시**: 자동자막에 화자 이름이 없어 전부 "화자 미상"으로 처리했습니다. 대신 카드 본문에 "フリーレン様"처럼
  호칭이 그대로 남아 있어 문맥으로 화자를 짐작할 수 있습니다.
- **한자 풀이**: 3편에 나오는 한자 129자·한자어 104항목에 훈음·뜻·한국 한자음을 달았습니다.

## 출처

- 영상: YouTube 공식 채널 TOHO animation 「葬送のフリーレン ミニアニメ「●●の魔法」」 제20~22회.
- 원작: 山田鐘人・アベツカサ 『葬送のフリーレン』(小学館) / TVアニメ(マッドハウス制作).
- 자막·번역·읽기·주석·학습 항목은 위 영상을 바탕으로 직접 작성한 것이라 오류가 있을 수 있습니다.

학습용 개인 이용을 전제로 한 페이지입니다. 영상은 YouTube 공식 플레이어로 재생됩니다.
