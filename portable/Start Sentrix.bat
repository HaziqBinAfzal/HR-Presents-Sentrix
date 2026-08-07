@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Sentrix.ps1"
if errorlevel 1 (
  echo.
  echo Sentrix could not start. Review the message above.
  pause
)
