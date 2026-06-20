@echo off
chcp 65001 >nul
title Dino KI
cd /d "%~dp0"
setlocal enabledelayedexpansion

echo.
echo  ============================================
echo   🦖 Dino wird gestartet...
echo  ============================================
echo.

rem ----------------------------------------------------------------
rem 1) Python suchen (python -> py -> python3)
rem ----------------------------------------------------------------
set "PYCMD="

where python >nul 2>&1
if %errorlevel%==0 (
    set "PYCMD=python"
    goto :python_ok
)

where py >nul 2>&1
if %errorlevel%==0 (
    set "PYCMD=py"
    goto :python_ok
)

where python3 >nul 2>&1
if %errorlevel%==0 (
    set "PYCMD=python3"
    goto :python_ok
)

rem --- Kein Python gefunden ---
echo  ⚠️  Python wurde nicht gefunden.
echo.

where winget >nul 2>&1
if %errorlevel%==0 goto :python_install_winget
goto :python_install_manual

:python_install_winget
echo  📥 Ich installiere Python jetzt automatisch (winget)...
echo.
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
echo.
echo  ✅ Python installiert.
echo.
echo  Bitte schließe dieses Fenster und starte Dino-Start.bat NOCHMAL.
echo  (Python ist erst in einem neuen Fenster aktiv.)
echo.
pause
exit /b

:python_install_manual
echo  Ich öffne jetzt die Download-Seite für Python...
start https://www.python.org/downloads/
echo.
echo  WICHTIG: bei der Installation Haken bei 'Add Python to PATH' setzen!
echo  Danach starte Dino-Start.bat nochmal.
echo.
pause
exit /b

:python_ok
echo  ✅ Python da (!PYCMD!).
echo.

rem ----------------------------------------------------------------
rem 2) Ollama suchen
rem ----------------------------------------------------------------
where ollama >nul 2>&1
if %errorlevel%==0 goto :ollama_ok

echo  ⚠️  Ollama wurde nicht gefunden.
echo.

where winget >nul 2>&1
if %errorlevel%==0 goto :ollama_install_winget
goto :ollama_install_manual

:ollama_install_winget
echo  📥 Ich installiere Ollama jetzt automatisch (winget)...
echo.
winget install -e --id Ollama.Ollama --accept-source-agreements --accept-package-agreements
echo.
echo  ✅ Ollama installiert.
echo  ⏳ Kurz warten, damit der Ollama-Dienst startet...
timeout /t 5 >nul

where ollama >nul 2>&1
if %errorlevel%==0 (
    echo  ✅ Ollama bereit.
    echo.
    goto :start_dino
)

echo.
echo  Hinweis: Ollama ist installiert, aber in diesem Fenster noch nicht aktiv.
echo  Bitte starte Dino-Start.bat einmal neu - dann läuft alles durch.
echo.
pause
exit /b

:ollama_install_manual
echo  Ich öffne jetzt die Download-Seite für Ollama...
start https://ollama.com/download
echo.
echo  Installier Ollama, dann starte Dino-Start.bat nochmal.
echo.
pause
exit /b

:ollama_ok
echo  ✅ Ollama da.
echo.

rem ----------------------------------------------------------------
rem 3) Dino-Python-Datei finden
rem ----------------------------------------------------------------
:start_dino
set "PYFILE="

if exist "Dino-KI.py" (
    set "PYFILE=Dino-KI.py"
    goto :pyfile_ok
)

if exist "DinoKI.py" (
    set "PYFILE=DinoKI.py"
    goto :pyfile_ok
)

for %%F in (*.py) do (
    if not defined PYFILE set "PYFILE=%%F"
)

if not defined PYFILE goto :no_pyfile
goto :pyfile_ok

:no_pyfile
echo  ❌ Keine Dino-Datei gefunden - leg Dino-KI.py in denselben Ordner.
echo.
pause
exit /b

:pyfile_ok
echo  🚀 Starte Dino: !PYFILE!
echo  (Das Browser-Fenster öffnet sich gleich von selbst.)
echo.

rem ----------------------------------------------------------------
rem 4) App starten
rem ----------------------------------------------------------------
%PYCMD% "!PYFILE!"

echo.
echo  ============================================
echo   Dino wurde beendet.
echo  ============================================
echo.
pause
endlocal
