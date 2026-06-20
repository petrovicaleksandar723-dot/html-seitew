@echo off
chcp 65001 >nul
title Dino KI
cd /d "%~dp0"

echo.
echo  ============================================
echo    Dino wird gestartet...
echo  ============================================
echo.

rem --- 1) Python suchen ---
set "PYCMD="
where python >nul 2>&1
if %errorlevel%==0 set "PYCMD=python"
if defined PYCMD goto python_ok
where py >nul 2>&1
if %errorlevel%==0 set "PYCMD=py"
if defined PYCMD goto python_ok
where python3 >nul 2>&1
if %errorlevel%==0 set "PYCMD=python3"
if defined PYCMD goto python_ok

echo  [!] Python wurde nicht gefunden.
echo.
where winget >nul 2>&1
if %errorlevel%==0 goto python_winget
goto python_manual

:python_winget
echo  Installiere Python automatisch (winget)...
echo.
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
echo.
echo  Python installiert. Bitte dieses Fenster schliessen und
echo  Dino-Start.bat NOCHMAL doppelklicken.
echo.
pause
exit /b

:python_manual
echo  Ich oeffne die Download-Seite fuer Python...
start https://www.python.org/downloads/
echo.
echo  WICHTIG: bei der Installation Haken bei "Add Python to PATH" setzen!
echo  Danach Dino-Start.bat nochmal starten.
echo.
pause
exit /b

:python_ok
echo  Python gefunden: %PYCMD%
echo.

rem --- 2) Ollama suchen ---
where ollama >nul 2>&1
if %errorlevel%==0 goto ollama_ok

echo  [!] Ollama wurde nicht gefunden.
echo.
where winget >nul 2>&1
if %errorlevel%==0 goto ollama_winget
goto ollama_manual

:ollama_winget
echo  Installiere Ollama automatisch (winget)...
echo.
winget install -e --id Ollama.Ollama --accept-source-agreements --accept-package-agreements
echo.
echo  Ollama installiert. Warte kurz, bis der Dienst startet...
timeout /t 5 >nul
where ollama >nul 2>&1
if %errorlevel%==0 goto start_dino
echo.
echo  Hinweis: Ollama ist installiert, aber in diesem Fenster noch nicht aktiv.
echo  Bitte Dino-Start.bat einmal neu starten - dann laeuft alles durch.
echo.
pause
exit /b

:ollama_manual
echo  Ich oeffne die Download-Seite fuer Ollama...
start https://ollama.com/download
echo.
echo  Installier Ollama, dann Dino-Start.bat nochmal starten.
echo.
pause
exit /b

:ollama_ok
echo  Ollama gefunden.
echo.

rem --- 3) Dino-Datei finden ---
:start_dino
set "PYFILE="
if exist "Dino-KI.py" set "PYFILE=Dino-KI.py"
if defined PYFILE goto pyfile_ok
if exist "DinoKI.py" set "PYFILE=DinoKI.py"
if defined PYFILE goto pyfile_ok
for %%F in (*.py) do if not defined PYFILE set "PYFILE=%%F"
if not defined PYFILE goto no_pyfile
goto pyfile_ok

:no_pyfile
echo  [X] Keine Dino-Datei gefunden.
echo      Leg Dino-KI.py in denselben Ordner wie diese .bat.
echo.
pause
exit /b

:pyfile_ok
echo  Starte Dino: %PYFILE%
echo  (Das Chat-Fenster oeffnet sich gleich von selbst im Browser.)
echo.
%PYCMD% "%PYFILE%"

echo.
echo  Dino wurde beendet.
echo.
pause
