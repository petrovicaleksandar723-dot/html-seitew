@echo off
title Dino KI
cd /d "%~dp0"

echo.
echo  ============================================
echo    Dino wird gestartet...
echo  ============================================
echo.

rem --- Echten Python ueber vollen Pfad finden (umgeht den Windows-Fake) ---
set "PYCMD="
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do if exist "%%D\python.exe" set "PYCMD=%%D\python.exe"
if defined PYCMD goto python_ok
for /d %%D in ("%ProgramFiles%\Python3*") do if exist "%%D\python.exe" set "PYCMD=%%D\python.exe"
if defined PYCMD goto python_ok
where py >nul 2>&1
if %errorlevel%==0 set "PYCMD=py"
if defined PYCMD goto python_ok
where python >nul 2>&1
if %errorlevel%==0 set "PYCMD=python"
if defined PYCMD goto python_ok

echo  [!] Kein Python gefunden. https://www.python.org/downloads/
start https://www.python.org/downloads/
pause
exit /b

:python_ok
echo  Python: %PYCMD%

set "PYFILE="
if exist "Dino-Fenster.py" set "PYFILE=Dino-Fenster.py"
if not defined PYFILE if exist "DinoFenster.py" set "PYFILE=DinoFenster.py"
if not defined PYFILE for %%F in (*.py) do if not defined PYFILE set "PYFILE=%%F"
if not defined PYFILE goto no_pyfile

echo  Starte: %PYFILE%
echo  (Ein Dino-Fenster geht gleich auf. Dieses Fenster offen lassen.)
echo.

rem Genau wie dein funktionierender Test: voller Pfad, keine Extra-Schalter
"%PYCMD%" "%PYFILE%" 2> "Dino-Fehler.txt"

echo.
echo  --- Dino wurde beendet ---
echo  Falls KEIN Fenster kam: oeffne Dino-Fehler.txt und schick mir den Inhalt.
echo.
pause
exit /b

:no_pyfile
echo  [X] Keine Dino-Fenster.py in diesem Ordner gefunden.
pause
exit /b
