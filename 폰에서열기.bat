@echo off
chcp 65001 >nul
title 도카도카 - 폰에서 열기
REM 집 안 와이파이의 폰에서 이 PC 의 학습 앱을 연다.
REM 윈도우 쪽 파이썬이 WSL 폴더를 그대로 서빙하므로 관리자 권한이 필요 없다.
set ROOT=\\wsl.localhost\Ubuntu-24.04\home\kim-h\work\dokadoka-cards
set PORT=8100

echo.
echo   도카도카 어학 학습 - 폰에서 열기
echo   ----------------------------------------
for /f "tokens=2 delims=:" %%a in ('powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 ^| Where-Object {$_.IPAddress -like '192.168.*' -or $_.IPAddress -like '10.*'} ^| Select-Object -First 1).IPAddress" 2^>nul') do set IP=%%a
powershell -NoProfile -Command "$ip=(Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like '192.168.*' -or $_.IPAddress -like '10.*'} | Select-Object -First 1).IPAddress; Write-Host ('   폰 브라우저에서 열 주소:  http://' + $ip + ':%PORT%/') -ForegroundColor Green"
echo.
echo   이 창을 닫으면 서버가 꺼집니다.
echo   처음 실행 시 방화벽 허용 창이 뜨면 [개인 네트워크] 를 체크하고 허용하세요.
echo.

pushd "%ROOT%"
py -3 -m http.server %PORT% --bind 0.0.0.0
popd
