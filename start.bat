@echo off
rem === 도카도카 어학 학습 관문(일본어·한국어·영어) — 이 폴더 전체를 간이 서버로 열기 ===
rem YouTube 는 file:// 재생을 거부하므로(Error 153) 서버를 띄워 http:// 로 연다. 각 앱 폴더는 하위 경로로 열린다.
setlocal
cd /d "%~dp0"
if /i "%CD:~0,2%"=="\\" goto :unc
if not exist "%~dp0index.html" goto :nofile
set PORT=8100
set PAGE=index.html
set URL=http://localhost:%PORT%/%PAGE%
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
start "dokadoka-hub-server" /min %PY% -m http.server %PORT%
timeout /t 2 >nul
start "" "%URL%"
echo.
echo 최소화된 "dokadoka-hub-server" 창을 닫으면 서버가 종료됩니다.
timeout /t 3 >nul
exit /b 0
:unc
echo [!] 네트워크 경로(\\wsl.localhost\... 등)에서는 실행할 수 없습니다.
echo     이 폴더를 Windows 디스크(예: 바탕화면)로 복사한 뒤 실행하세요.
pause
exit /b 1
:nofile
echo [!] index.html 을 찾을 수 없습니다. start.bat 과 같은 폴더에 두세요.
pause
exit /b 1
:nopython
echo [!] Python 이 필요합니다. https://www.python.org/downloads/windows/
echo     설치 시 "Add Python to PATH" 를 체크하세요.
pause
exit /b 1
