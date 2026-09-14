# -*- coding: utf-8 -*-
"""한글 철자 → 표준 발음. 규칙만으로 구현하고, 기존 앱의 가타카나 읽기로 검증한다."""
CHO="ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
JUNG="ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
JONG=["","ㄱ","ㄲ","ㄳ","ㄴ","ㄵ","ㄶ","ㄷ","ㄹ","ㄺ","ㄻ","ㄼ","ㄽ","ㄾ","ㄿ","ㅀ","ㅁ","ㅂ","ㅄ","ㅅ","ㅆ","ㅇ","ㅈ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]
def dec(ch):
    if not ('가'<=ch<='힣'): return None
    i=ord(ch)-0xAC00
    return [CHO[i//588], JUNG[(i%588)//28], JONG[i%28]]
def com(c,v,t):
    return chr(0xAC00 + CHO.index(c)*588 + JUNG.index(v)*28 + JONG.index(t))
# 겹받침 → (남는 받침, 넘어가는 자음)
# 연음될 때: (앞에 남는 받침, 뒤로 넘어가는 자음)
DOUBLE={"ㄳ":("ㄱ","ㅅ"),"ㄵ":("ㄴ","ㅈ"),"ㄶ":("ㄴ","ㅎ"),"ㄺ":("ㄹ","ㄱ"),"ㄻ":("ㄹ","ㅁ"),
        "ㄼ":("ㄹ","ㅂ"),"ㄽ":("ㄹ","ㅅ"),"ㄾ":("ㄹ","ㅌ"),"ㄿ":("ㄹ","ㅍ"),"ㅀ":("ㄹ","ㅎ"),"ㅄ":("ㅂ","ㅅ")}
# 자음 앞에서 남는 대표음 (연음과 다르다: 읽어[일거] vs 읽다[익따])
REP={"ㄳ":"ㄱ","ㄵ":"ㄴ","ㄶ":"ㄴ","ㄺ":"ㄱ","ㄻ":"ㅁ","ㄼ":"ㄹ","ㄽ":"ㄹ","ㄾ":"ㄹ","ㄿ":"ㅂ","ㅀ":"ㄹ","ㅄ":"ㅂ"}
NEUT={"ㄲ":"ㄱ","ㅋ":"ㄱ","ㅅ":"ㄷ","ㅆ":"ㄷ","ㅈ":"ㄷ","ㅊ":"ㄷ","ㅌ":"ㄷ","ㅎ":"ㄷ","ㅍ":"ㅂ"}
TENSE={"ㄱ":"ㄲ","ㄷ":"ㄸ","ㅂ":"ㅃ","ㅅ":"ㅆ","ㅈ":"ㅉ"}
ASP={"ㄱ":"ㅋ","ㄷ":"ㅌ","ㅂ":"ㅍ","ㅈ":"ㅊ"}
NASAL={"ㄱ":"ㅇ","ㄷ":"ㄴ","ㅂ":"ㅁ"}
def pron(word):
    S=[dec(c) for c in word]
    if any(s is None for s in S): return word
    for i in range(len(S)):
        c,v,t=S[i]; nxt=S[i+1] if i+1<len(S) else None
        if not nxt:
            if t in DOUBLE: t=REP[t]
            S[i][2]=NEUT.get(t,t); continue
        nc=nxt[0]
        # ① ㅎ 축약 (놓고→노코)
        if t in ("ㅎ","ㄶ","ㅀ") and nc in ASP:
            nxt[0]=ASP[nc]; S[i][2]="" if t=="ㅎ" else DOUBLE[t][0]; continue
        if nc=="ㅎ" and t in ASP and t not in ("",):
            base=DOUBLE[t][0] if t in DOUBLE else t
            if base in ASP: nxt[0]=ASP[base]; S[i][2]=""; continue
        # ② ㅎ 탈락 (좋아→조아)
        if t in ("ㅎ","ㄶ","ㅀ") and nc=="ㅇ":
            if t=="ㅎ": S[i][2]=""
            else: S[i][2]=""; nxt[0]=DOUBLE[t][0]
            continue
        # ③ 연음 (모음 앞)
        if nc=="ㅇ":
            if t in DOUBLE:
                keep,mv=DOUBLE[t]; S[i][2]=keep
                nxt[0]="ㅆ" if mv=="ㅅ" else mv        # 없어[업써]·몫이[목씨]
            elif t: 
                # 구개음화 (굳이→구지)
                if t in ("ㄷ","ㅌ") and nxt[1]=="ㅣ": nxt[0]={"ㄷ":"ㅈ","ㅌ":"ㅊ"}[t]; S[i][2]=""
                else: nxt[0]=t; S[i][2]=""
            continue
        was_double = t in DOUBLE
        if was_double: t=REP[t]; S[i][2]=t
        t=NEUT.get(t,t); S[i][2]=t
        # ④ 비음화
        if nc in ("ㄴ","ㅁ") and t in NASAL: S[i][2]=NASAL[t]
        elif nc=="ㄹ" and t in ("ㄱ","ㅇ","ㅁ","ㅂ"):
            nxt[0]="ㄴ"
            if t in NASAL: S[i][2]=NASAL[t]
        # ⑤ 유음화
        elif t=="ㄴ" and nc=="ㄹ": S[i][2]="ㄹ"
        elif t=="ㄹ" and nc=="ㄴ": nxt[0]="ㄹ"
        # ⑥ 경음화
        elif t in ("ㄱ","ㄷ","ㅂ") and nc in TENSE: nxt[0]=TENSE[nc]
        elif was_double and t=="ㄹ" and nc in TENSE: nxt[0]=TENSE[nc]
    return "".join(com(*s) for s in S)
if __name__=="__main__":
    T=[("좋아요","조아요"),("학교","학꾜"),("눈빛은","눈비츤"),("맛있어","마시써"),("굳이","구지"),
       ("신라","실라"),("국물","궁물"),("낳고","나코"),("앉아","안자"),("읽어","일거"),("같이","가치"),
       ("입학","이팍"),("먹는다","멍는다"),("설날","설랄"),("꽃","꼳"),("있다","읻따"),("없어","업써"),
       ("읽다","익따"),("젊어","절머"),("넓다","널따"),("몫이","목씨"),("싫어","시러"),("많아","마나"),
       ("옷이","오시"),("밥먹어","밤머거"),("한국말","한궁말"),("좋다","조타"),("싸워","싸워"),
       ("첫인상","처딘상"),("꽃이","꼬치"),("값","갑"),("닭","닥"),("핥아","할타"),("잡히다","자피다"),
       ("역할","여칼"),("연습","연습"),("심장","심장"),("활동","활똥"),("숙제","숙쩨")]
    bad=0
    for a,b in T:
        g=pron(a); ok = g==b
        if not ok: bad+=1
        print(("  OK  " if ok else "  ✗   ")+f"{a} → {g}"+("" if ok else f"   (기대 {b})"))
    print(f"\n  표준 예제 {len(T)}개 중 {len(T)-bad}개 일치")
