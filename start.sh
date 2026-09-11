#!/usr/bin/env bash
# === 도카도카 어학 학습 관문(일본어·한국어·영어) — 이 폴더 전체를 간이 서버로 열기 ===
# YouTube 는 file:// 재생을 거부하므로(Error 153) 서버를 띄워 http:// 로 연다. 각 앱 폴더는 하위 경로로 열린다.
set -u
cd "$(dirname "$0")"
PORT="${PORT:-8100}"
PAGE="index.html"
command -v python3 >/dev/null || { echo "[!] python3 가 필요합니다."; exit 1; }
while command -v ss >/dev/null && ss -ltn 2>/dev/null | grep -q ":$PORT "; do PORT=$((PORT+1)); done
URL="http://localhost:$PORT/$PAGE"
python3 -m http.server "$PORT" >/dev/null 2>&1 &
SRV=$!
trap 'kill "$SRV" 2>/dev/null' INT TERM EXIT
sleep 1
echo "열기: $URL"
( xdg-open "$URL" || open "$URL" ) >/dev/null 2>&1 || echo "브라우저에서 위 주소를 직접 여세요."
echo "종료하려면 Ctrl+C."
wait "$SRV"
