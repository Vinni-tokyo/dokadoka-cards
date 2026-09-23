@echo off
rem === 도카도카 일본어 공부 / ドカドカ日本語 — 로컬 서버로 열기 ===
rem YouTube 는 file:// 재생을 거부하므로(Error 153) 간이 서버를 띄워 http:// 로 연다.
setlocal enabledelayedexpansion
cd /d "%~dp0"
if /i "%CD:~0,2%"=="\\" goto :unc
if not exist "%~dp0Japanese-Eien52-Cards.html" goto :nofile
set PORT=8118
set PAGE=Japanese-Eien52-Cards.html

where py >nul 2>nul && (set PY=py) || (set PY=python)
%PY% --version >nul 2>nul || goto :nopython

rem 그 포트가 "이 폴더"를 서빙하는지 응답으로 확인한다.
rem (폴더를 옮기면 옛 서버가 살아 있어도 404 만 낸다 — 포트가 열렸는지만 보면 속는다)
set URL=http://localhost:!PORT!/!PAGE!
set CODE=
for /f %%c in ('curl.exe -s -o NUL -m 3 -w "%%{http_code}" "!URL!" 2^>NUL') do set CODE=%%c
if "!CODE!"=="200" (
  echo 이미 서버가 실행 중입니다. 브라우저만 엽니다.
  start "" "!URL!"
  timeout /t 2 >nul
  exit /b 0
)

rem 응답이 200 이 아닌데 포트가 막혀 있으면, 낡은 서버나 다른 앱이다. 빈 포트로 물러난다.
:PORTLOOP
netstat -ano | findstr /r /c:"LISTENING" | findstr /c:":!PORT! " >nul
if not errorlevel 1 (
  set /a PORT+=1
  goto PORTLOOP
)
set URL=http://localhost:!PORT!/!PAGE!

echo 서버를 시작합니다 ... !URL!
start "dokadoka-server-!PORT!" /min %PY% -m http.server !PORT!
timeout /t 2 >nul
start "" "!URL!"
echo.
echo 최소화된 "dokadoka-server-!PORT!" 창을 닫으면 서버가 종료됩니다.
timeout /t 3 >nul
exit /b 0

:unc
echo [!] 네트워크 경로(\\wsl.localhost\... 등)에서는 실행할 수 없습니다.
echo     이 폴더를 Windows 디스크로 복사한 뒤 실행하세요.
pause
exit /b 1

:nofile
echo [!] Japanese-Eien52-Cards.html 을 찾을 수 없습니다.
echo     start.bat 과 같은 폴더에 두세요.
pause
exit /b 1

:nopython
echo [!] Python 이 필요합니다. https://www.python.org/downloads/windows/
echo     설치 시 "Add Python to PATH" 를 체크하세요.
pause
exit /b 1
