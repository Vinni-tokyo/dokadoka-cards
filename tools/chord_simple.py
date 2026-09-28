#!/usr/bin/env python3
"""반주 트랙에서 간이 코드를 딴다(자동 채보). 결과는 박 단위 코드 구간 json.

코드 후보를 그 조의 기본 3화음 + 자주 빌려 쓰는 코드로 좁히고(경과 코드는 뺀다 — 넓게 열면
dim·m7-5 가 엉뚱하게 튀어나왔다), 바꿀 때 벌점을 줘 반 마디 안팎으로는 흔들리지 않게 한다.
반주 트랙은 demucs 로 목소리를 뗀 no_vocals.wav 를 쓴다.

사용: .venv/bin/python tools/chord_simple.py <no_vocals.wav> <출력 json>
      (지금은 D 장조 후보표가 들어 있다 — 다른 조면 VOC·prior 를 바꾼다)
"""
import sys
import librosa, numpy as np, json
y,sr=librosa.load(sys.argv[1],sr=22050,mono=True)
tun=librosa.estimate_tuning(y=y,sr=sr); _, beats = librosa.beat.beat_track(y=y, sr=sr, units='time', start_bpm=75)
H=librosa.effects.harmonic(y,margin=3); hop=512
C=librosa.feature.chroma_cqt(y=H,sr=sr,tuning=tun,hop_length=hop,bins_per_octave=36)
B=librosa.feature.chroma_cqt(y=H,sr=sr,tuning=tun,hop_length=hop,fmin=librosa.note_to_hz('E1'),n_octaves=2,bins_per_octave=36)
t=librosa.frames_to_time(np.arange(C.shape[1]),sr=sr,hop_length=hop)
N='C C# D D# E F F# G G# A A# B'.split()
# D 장조 기본 3화음 + 빌린 코드. (근음, 3음 간격)
VOC={'D':(2,4),'Em':(4,3),'F#m':(6,3),'G':(7,4),'A':(9,4),'Bm':(11,3),'F#':(6,4),'B':(11,4),'E':(4,4),'Gm':(7,3),'C':(0,4),'A#':(10,4)}
labels=list(VOC); T=[]
for k,(r,th) in VOC.items():
    v=np.zeros(12); v[r]=1.5; v[(r+th)%12]=1; v[(r+7)%12]=1; T.append(v/np.linalg.norm(v))
T=np.array(T)
prior={'D':.06,'Em':.03,'F#m':.02,'G':.06,'A':.06,'Bm':.04,'F#':0,'B':0,'E':0,'Gm':0,'C':0,'A#':0}
edges=list(beats)+[t[-1]]; X=[];Bx=[];span=[]
for a,b in zip(edges[:-1],edges[1:]):
    m=(t>=a)&(t<b)
    X.append(C[:,m].mean(1)); Bx.append(B[:,m].mean(1)); span.append((a,b))
X=np.array(X); Bx=np.array(Bx)
S=(X/(np.linalg.norm(X,axis=1,keepdims=True)+1e-9))@T.T
bass=Bx/(Bx.max(1,keepdims=True)+1e-9)
for j,k in enumerate(labels): S[:,j]+=0.3*bass[:,VOC[k][0]]+prior[k]
# 비터비 — 최소 2박 유지를 위해 바꿀 때 벌점
K=len(labels); sw=0.55
D=S[0].copy(); P=[]
for i in range(1,len(S)):
    bj=int(D.argmax()); keep=D; change=D[bj]-sw
    choose=np.where(keep>=change, np.arange(K), bj); P.append(choose)
    D=np.maximum(keep,change)+S[i]
path=[int(D.argmax())]
for ch in reversed(P): path.append(int(ch[path[-1]]))
path=path[::-1]
seq=[]
for i,j in enumerate(path):
    n=labels[j]
    if seq and seq[-1][2]==n: seq[-1][1]=span[i][1]
    else: seq.append([float(span[i][0]),float(span[i][1]),n])
json.dump([[round(a,2),round(b,2),n] for a,b,n in seq],open(sys.argv[2],'w'))
print(f'{sys.argv[1]}: 코드 구간 {len(seq)} → {sys.argv[2]}')
