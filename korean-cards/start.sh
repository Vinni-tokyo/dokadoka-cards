#!/usr/bin/env bash
# === 도카도카 한국어 공부 / ドカドカ韓国語 — 로컬 서버로 열기 ===
# YouTube 는 file:// 재생을 거부하므로(Error 153) 간이 서버를 띄워 http:// 로 연다.
set -u
cd "$(dirname "$0")"
PORT="${PORT:-8099}"
PAGE="Korean-Cliff389-Cards.html"

command -v python3 >/dev/null || { echo "[!] python3 가 필요합니다."; exit 1; }
# 포트가 이미 쓰이면 다음 포트로 물러난다
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
