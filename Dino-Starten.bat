@echo off
chcp 65001 >nul
title Dino KI
cd /d "%~dp0"

echo.
echo   Starte Dino...  (dein Chat-Fenster oeffnet sich gleich im Browser)
echo.

where python  >nul 2>nul && (python  Dino-KI.py & goto ende)
where py      >nul 2>nul && (py      Dino-KI.py & goto ende)
where python3 >nul 2>nul && (python3 Dino-KI.py & goto ende)

echo   [!] Python wurde nicht gefunden.
echo       Gratis laden: https://www.python.org/downloads/
echo       WICHTIG: Haken bei "Add Python to PATH" setzen!
echo.

:ende
echo.
pause
