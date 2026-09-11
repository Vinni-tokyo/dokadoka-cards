@echo off
rem === 도카도카 일본어 공부 / ドカドカ日本語 — 로컬 서버로 열기 ===
rem YouTube 는 file:// 재생을 거부하므로(Error 153) 간이 서버를 띄워 http:// 로 연다.
setlocal
cd /d "%~dp0"
if /i "%CD:~0,2%"=="\\" goto :unc
if not exist "%~dp0Japanese-Yubisaki185-Cards.html" goto :nofile
set PORT=8097
set PAGE=Japanese-Yubisaki185-Cards.html
set URL=http://localhost:%PORT%/%PAGE%

rem 이미 서버가 떠 있으면 새로 띄우지 않고 브라우저만 연다 (중복 실행 방지)
netstat -ano | findstr /r /c:"LISTENING" | findstr /c:":%PORT% " >nul
if not errorlevel 1 (
  echo 이미 서버가 실행 중입니다. 브라우저만 엽니다.
  start "" "%URL%"
  timeout /t 2 >nul
  exit /b 0
)

where py >nul 2>nul && (set PY=py) || (set PY=python)
%PY% --version >nul 2>nul || goto :nopython

echo 서버를 시작합니다 ... %URL%
start "yubisaki-cards-server" /min %PY% -m http.server %PORT%
timeout /t 2 >nul
start "" "%URL%"
echo.
echo 최소화된 "yubisaki-cards-server" 창을 닫으면 서버가 종료됩니다.
timeout /t 3 >nul
exit /b 0

:unc
echo [!] 네트워크 경로(\\wsl.localhost\... 등)에서는 실행할 수 없습니다.
echo     이 폴더를 Windows 디스크(예: 바탕화면)로 복사한 뒤 실행하세요.
pause
exit /b 1

:nofile
echo [!] Japanese-Yubisaki185-Cards.html 을 찾을 수 없습니다.
echo     start.bat 과 같은 폴더에 두세요.
pause
exit /b 1

:nopython
echo [!] Python 이 필요합니다. https://www.python.org/downloads/windows/
echo     설치 시 "Add Python to PATH" 를 체크하세요.
pause
exit /b 1
