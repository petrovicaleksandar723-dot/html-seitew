@echo off
title Dino KI
cd /d "%~dp0"

set "PYTHONHOME="
set "PYTHONPATH="

echo.
echo  ============================================
echo    Dino wird gestartet...
echo  ============================================
echo.

rem --- ECHTEN Python ueber vollen Pfad finden (umgeht den Windows-Fake) ---
set "PYCMD="
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do if exist "%%D\python.exe" set "PYCMD=%%D\python.exe"
if defined PYCMD goto python_ok
for /d %%D in ("%ProgramFiles%\Python3*") do if exist "%%D\python.exe" set "PYCMD=%%D\python.exe"
if defined PYCMD goto python_ok
for /d %%D in ("%ProgramFiles(x86)%\Python3*") do if exist "%%D\python.exe" set "PYCMD=%%D\python.exe"
if defined PYCMD goto python_ok

rem --- Fallback: py / python ---
where py >nul 2>&1
if %errorlevel%==0 set "PYCMD=py"
if defined PYCMD goto python_ok
where python >nul 2>&1
if %errorlevel%==0 set "PYCMD=python"
if defined PYCMD goto python_ok

echo  [!] Kein Python gefunden.
echo      Gratis: https://www.python.org/downloads/  (Haken "Add Python to PATH")
start https://www.python.org/downloads/
pause
exit /b

:python_ok
echo  Python: %PYCMD%

rem --- Dino-Datei finden ---
set "PYFILE="
if exist "Dino-Fenster.py" set "PYFILE=Dino-Fenster.py"
if not defined PYFILE if exist "DinoFenster.py" set "PYFILE=DinoFenster.py"
if not defined PYFILE for %%F in (*.py) do if not defined PYFILE set "PYFILE=%%F"
if not defined PYFILE goto no_pyfile

echo  Starte: %PYFILE%
echo  (Ein Dino-Fenster geht gleich auf. Dieses Fenster offen lassen.)
echo.
"%PYCMD%" -E "%PYFILE%" 2> "Dino-Fehler.txt"

echo.
echo  --- Dino wurde beendet ---
echo  Falls KEIN Fenster kam: oeffne Dino-Fehler.txt und schick mir den Inhalt.
echo.
pause
exit /b

:no_pyfile
echo  [X] Keine Dino-Fenster.py in diesem Ordner gefunden.
echo      Leg Dino-Fenster.py in DENSELBEN Ordner wie diese .bat.
echo.
pause
exit /b
