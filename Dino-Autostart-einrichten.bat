@echo off
chcp 65001 >nul
title Dino Autostart einrichten
cd /d "%~dp0"

echo.
echo  ============================================
echo    Dino startet ab jetzt automatisch mit Windows
echo  ============================================
echo.

rem --- Dino-Starter in diesem Ordner finden ---
set "TARGET="
if exist "%~dp0Dino-Starten.bat" set "TARGET=%~dp0Dino-Starten.bat"
if not defined TARGET if exist "%~dp0Dino-Start.bat" set "TARGET=%~dp0Dino-Start.bat"
if not defined TARGET if exist "%~dp0Dino-Fenster-Start.bat" set "TARGET=%~dp0Dino-Fenster-Start.bat"

if not defined TARGET (
  echo  [X] Keine Dino-Starter-Datei gefunden.
  echo      Leg diese Datei in den gleichen Ordner wie Dino-Starten.bat.
  echo.
  pause
  exit /b
)

echo  Gefunden: %TARGET%
echo  Lege Autostart-Verknuepfung an...
echo.

powershell -NoProfile -Command "$ws=New-Object -ComObject WScript.Shell; $lnk=$ws.CreateShortcut([Environment]::GetFolderPath('Startup')+'\Dino.lnk'); $lnk.TargetPath='%TARGET%'; $lnk.WorkingDirectory='%~dp0'; $lnk.WindowStyle=7; $lnk.Description='Dino KI Autostart'; $lnk.Save()"

if %errorlevel%==0 (
  echo  [OK] Fertig! Dino startet jetzt bei jedem Hochfahren automatisch.
  echo.
  echo  Rueckgaengig machen: Win+R druecken, "shell:startup" eingeben,
  echo  dann die Datei "Dino.lnk" dort loeschen.
) else (
  echo  [!] Hat nicht geklappt. Du kannst es auch von Hand machen:
  echo      1) Win+R druecken, "shell:startup" eingeben, Enter
  echo      2) Eine Verknuepfung von Dino-Starten.bat in diesen Ordner ziehen.
)

echo.
pause
