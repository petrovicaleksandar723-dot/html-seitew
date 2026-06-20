@echo off
chcp 65001 >nul
title Dino KI
cd /d "%~dp0"

REM Python-Datei automatisch finden (egal ob Dino-KI.py oder DinoKI.py)
set "PYFILE="
if exist "Dino-KI.py" set "PYFILE=Dino-KI.py"
if not defined PYFILE if exist "DinoKI.py" set "PYFILE=DinoKI.py"
if not defined PYFILE for %%F in (*.py) do set "PYFILE=%%F"

if not defined PYFILE (
  echo.
  echo   [!] Keine Dino-Datei in diesem Ordner gefunden.
  echo       Leg die Datei Dino-KI.py in DENSELBEN Ordner wie diese .bat.
  echo.
  pause
  exit /b
)

echo.
echo   Starte Dino...  dein Chat-Fenster oeffnet sich gleich im Browser.
echo   Datei: %PYFILE%
echo.

where python  >nul 2>nul && (python  "%PYFILE%" & goto ende)
where py      >nul 2>nul && (py      "%PYFILE%" & goto ende)
where python3 >nul 2>nul && (python3 "%PYFILE%" & goto ende)

echo   [!] Python wurde nicht gefunden.
echo       Gratis laden: https://www.python.org/downloads/
echo       WICHTIG bei der Installation: Haken bei "Add Python to PATH" setzen!
echo.

:ende
echo.
pause
