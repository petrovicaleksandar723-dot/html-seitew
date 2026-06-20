@echo off
chcp 65001 >nul
title Dino KI
cd /d "%~dp0"

echo.
echo   Starte Dino KI...  (das Chat-Fenster oeffnet sich gleich im Browser)
echo.

REM Python finden und die App (Server + Jarvis-Chatfenster) starten
where python  >nul 2>nul && (python  dino_server.py & goto ende)
where py      >nul 2>nul && (py      dino_server.py & goto ende)
where python3 >nul 2>nul && (python3 dino_server.py & goto ende)

echo.
echo   [!] Python wurde nicht gefunden.
echo       Lade es hier (kostenlos): https://www.python.org/downloads/
echo       WICHTIG bei der Installation: Haken bei "Add Python to PATH" setzen!
echo.

:ende
echo.
pause
