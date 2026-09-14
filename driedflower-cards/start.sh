#!/usr/bin/env bash
# === 도카도카 일본어 공부 / ドカドカ日本語 — 로컬 서버로 열기 ===
# YouTube 는 file:// 재생을 거부하므로(Error 153) 간이 서버를 띄워 http:// 로 연다.
set -u
cd "$(dirname "$0")"
PORT="${PORT:-8107}"
PAGE="Japanese-DriedFlower49-Cards.html"
command -v python3 >/dev/null || { echo "[!] python3 가 필요합니다."; exit 1; }

# 그 포트가 "이 폴더"를 서빙하는지 응답으로 확인한다.
# (폴더를 옮기면 옛 서버가 살아 있어도 404 만 낸다 — 포트가 열렸는지만 보면 속는다)
code=$(curl -s -o /dev/null -m 3 -w '%{http_code}' "http://localhost:$PORT/$PAGE" 2>/dev/null || true)
if [ "$code" = "200" ]; then
  echo "이미 서버가 실행 중입니다: http://localhost:$PORT/$PAGE"
  ( xdg-open "http://localhost:$PORT/$PAGE" || open "http://localhost:$PORT/$PAGE" ) >/dev/null 2>&1 || true
  exit 0
fi

# 200 이 아닌데 포트가 막혀 있으면 낡은 서버나 다른 앱이다. 빈 포트로 물러난다.
while command -v ss >/dev/null && ss -ltn 2>/dev/null | grep -q ":$PORT "; do
  PORT=$((PORT+1))
done

URL="http://localhost:$PORT/$PAGE"
python3 -m http.server "$PORT" >/dev/null 2>&1 &
SRV=$!
trap 'kill "$SRV" 2>/dev/null' INT TERM EXIT
sleep 1
echo "열기: $URL"
( xdg-open "$URL" || open "$URL" ) >/dev/null 2>&1 || echo "브라우저에서 위 주소를 직접 여세요."
echo "종료하려면 Ctrl+C."
wait "$SRV"
