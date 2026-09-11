#!/usr/bin/env bash
# === 은하특급 밀키☆서브웨이 학습 카드 — 로컬 서버로 열기 ===
set -u
cd "$(dirname "$0")"
PORT="${PORT:-8090}"
PAGE="index.html"
command -v python3 >/dev/null || { echo "[!] python3 가 필요합니다."; exit 1; }

code=$(curl -s -o /dev/null -m 3 -w '%{http_code}' "http://localhost:$PORT/$PAGE" 2>/dev/null || true)
if [ "$code" = "200" ]; then
  echo "이미 서버가 실행 중입니다: http://localhost:$PORT/$PAGE"
  ( xdg-open "http://localhost:$PORT/$PAGE" || open "http://localhost:$PORT/$PAGE" ) >/dev/null 2>&1 || true
  exit 0
fi

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
