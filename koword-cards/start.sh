#!/usr/bin/env bash
# === 도카도카 한국어 단어·표현 카드 — 로컬 서버로 열기 ===
# 이 앱은 유튜브를 쓰지 않으므로 HTML 을 그냥 열어도 됩니다.
# 「▶ 장면」이 옆 폴더의 영상 앱을 열기 때문에 상대 경로가 살아 있는 서버 실행을 권합니다.
set -u
cd "$(dirname "$0")"
PORT="${PORT:-8106}"
PAGE="$(ls Korean-Words*-Cards.html 2>/dev/null | head -1)"
[ -n "$PAGE" ] || { echo "[!] Korean-Words*-Cards.html 이 없습니다. python3 src/build.py 를 먼저 실행하세요."; exit 1; }
command -v python3 >/dev/null || { echo "[!] python3 가 필요합니다."; exit 1; }

# 그 포트가 "이 폴더"를 서빙하는지 응답으로 확인한다(옛 서버가 살아 404 만 내는 경우를 거른다)
code=$(curl -s -o /dev/null -m 3 -w '%{http_code}' "http://localhost:$PORT/$PAGE" 2>/dev/null || true)
if [ "$code" = "200" ]; then
  echo "이미 서버가 실행 중입니다: http://localhost:$PORT/$PAGE"
  ( xdg-open "http://localhost:$PORT/$PAGE" || open "http://localhost:$PORT/$PAGE" ) >/dev/null 2>&1 || true
  exit 0
fi
while command -v ss >/dev/null && ss -ltn 2>/dev/null | grep -q ":$PORT "; do PORT=$((PORT+1)); done

# 「▶ 장면」이 ../ 로 옆 앱을 열 수 있게 상위 폴더를 서빙한다
URL="http://localhost:$PORT/koword-cards/$PAGE"
(cd .. && python3 -m http.server "$PORT" >/dev/null 2>&1) &
SRV=$!
trap 'kill "$SRV" 2>/dev/null' INT TERM EXIT
sleep 1
echo "열기: $URL"
( xdg-open "$URL" || open "$URL" ) >/dev/null 2>&1 || echo "브라우저에서 위 주소를 직접 여세요."
echo "종료하려면 Ctrl+C."
wait "$SRV"
