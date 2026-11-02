@echo off
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_and_run.ps1"
if errorlevel 1 (
  echo.
  echo Setup did not finish. See the error above.
  pause
)
