# 학습 탭 개편 패치 (2026-09-13)

`docs/UX_STUDY_FLOW_PLAN_2026-09-13.md` 의 P1·P2·P3 를 템플릿에 적용하는 스크립트.
원본 템플릿(개편 전 mika-cards 계열 `src/tpl.html`)에 한 번만 적용한다. 각 치환은 정확히 1회 일치해야 하며 아니면 멈춘다.

```bash
python3 tools/study-tab/patch_study.py <앱>/src/tpl.html          # 토크쇼·애니 계열 (P1+P2)
python3 tools/study-tab/patch_song.py  <노래앱>/src/tpl.html      # 노래 계열은 위를 먼저 적용한 뒤 (P3)
cd <앱>/src && python3 build.py
```

적용 완료: mika-cards, firstlove-cards (2026-09-13). 이 둘은 patch_*.py 를 순서대로(study → song → foot → cue → tts → tts2 → layout → tts3 → layout2 → layout3 → karafill) 적용한 것.

다른 계열의 노래 템플릿(reasons·vitaminme·saranghagi)은 라벨 언어·필드명·드릴 유무가 달라 **port_song.py** 로 한 번에 옮긴다(앱별 CFG).
```bash
python3 tools/study-tab/port_song.py saranghagi-cards      # src/tpl.html 제자리 수정, 한 번만
.venv/bin/python tools/make_study_audio.py saranghagi-cards --cards   # 가사 줄 음원(읽어주기)
```
적용 완료: reasons-cards, vitaminme-cards, saranghagi-cards (2026-09-13).

바뀌는 것
- 하위 탭 6 → 4 (오늘 · 복습 · 목록 · 학습법). 드릴·퀴즈는 단계·버튼에서 열리고 「돌아가기」로 복귀
- 「오늘」 = 4단계 스테퍼. 진행은 localStorage `stages[day][n]={done,total}`, 4단계 완료 시 Day 자동 완료, 연속 학습일
- 1·3단계는 카드 뷰 안의 세션(상단 진행 바 + 하단 「들었다·다음」), 노래 앱은 노래방 뷰 세션
- 복습 탭 = SRS 기한 + 퀴즈 오답 + 체크한 대사
- 모바일: 학습 탭에서 플레이어를 미니 바로, 드릴 채점·세션 버튼은 하단 고정
- 노래 앱: 단락(절·후렴)=Day, 마디 반복 패널을 노래방 하단 한 줄로, 지금 줄 탭 = 그 줄의 마디 반복, 가사 가리기 3단

## 토크쇼·인터뷰 앱 (2026-09-13)

mika 계열(bokuyaba·frieren·hatsukoi·milky·yubisaki)은 patch_*.py 체인(study → foot → cue → tts → tts2 → layout → tts3 → layout2)을 그대로 적용.
라벨 언어·필드가 다른 계열(영어 7종 · korean-cards · japanese-cards)은 **port_talk.py** 로 한 번에 옮긴다(앱별 CFG).
```bash
python3 tools/study-tab/port_talk.py english-cards
```
적용 완료: 전체 (2026-09-13). 남은 앱: kanji-cards(구조가 다른 별도 앱, 대상 아님).
