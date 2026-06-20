@echo off
title Dino KI
cd /d "%~dp0"

echo.
echo  ============================================
echo    Dino wird gestartet...
echo  ============================================
echo.

rem --- Python suchen ---
set "PYCMD="
where py >nul 2>&1
if %errorlevel%==0 set "PYCMD=py"
if defined PYCMD goto python_ok
where python >nul 2>&1
if %errorlevel%==0 set "PYCMD=python"
if defined PYCMD goto python_ok
where python3 >nul 2>&1
if %errorlevel%==0 set "PYCMD=python3"
if defined PYCMD goto python_ok

echo  [!] Python wurde nicht gefunden.
echo      Gratis laden: https://www.python.org/downloads/
echo      WICHTIG: Haken bei "Add Python to PATH" setzen, dann PC neu starten.
echo.
start https://www.python.org/downloads/
pause
exit /b

:python_ok
echo  Python gefunden: %PYCMD%

rem --- Dino-Fenster-Datei suchen ---
set "PYFILE="
if exist "Dino-Fenster.py" set "PYFILE=Dino-Fenster.py"
if not defined PYFILE if exist "DinoFenster.py" set "PYFILE=DinoFenster.py"
if not defined PYFILE for %%F in (*.py) do if not defined PYFILE set "PYFILE=%%F"

if not defined PYFILE goto no_pyfile
echo  Starte: %PYFILE%
echo  (Ein Programm-Fenster geht gleich auf. Dieses schwarze Fenster offen lassen.)
echo.
%PYCMD% "%PYFILE%"
echo.
echo  Dino wurde beendet.
echo.
pause
exit /b

:no_pyfile
echo  [X] Keine Dino-Fenster.py in diesem Ordner gefunden.
echo      Leg Dino-Fenster.py in DENSELBEN Ordner wie diese .bat.
echo.
pause
exit /b
