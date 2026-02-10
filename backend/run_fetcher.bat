@echo off
setlocal enabledelayedexpansion

for /f "delims=" %%e in ('echo prompt $E ^| cmd') do set "ESC=%%e"
set "GREEN=%ESC%[92m"
set "YELLOW=%ESC%[93m"
set "RED=%ESC%[91m"
set "RESET=%ESC%[0m"

cd /d "%~dp0"

echo %YELLOW%Running telegram_fetcher.py...%RESET%
python telegram_fetcher.py
if errorlevel 1 (
  echo %RED%Error: fetch failed. Check logs above.%RESET%
  pause
  exit /b 1
)

echo %GREEN%Fetch completed at %date% %time%%RESET%
pause
