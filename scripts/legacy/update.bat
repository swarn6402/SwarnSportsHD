@echo off
setlocal
rem Legacy manual publisher. Normal updates use Actions > Fetch Links.
cd /d "%~dp0..\.."
if errorlevel 1 exit /b 1

set "publish_branch="
for /f "delims=" %%b in ('git branch --show-current') do set "publish_branch=%%b"
if not "%publish_branch%"=="main" (
  echo Legacy publishing requires main. Switch branches before fetching.
  exit /b 1
)

rem Never include previously staged files in the automatic commit.
git diff --cached --quiet
if errorlevel 1 (
  echo Staged changes exist. Unstage them before using this legacy publisher.
  exit /b 1
)
echo.
echo ======================================
echo Updating SwarnSports Links...
echo ======================================
echo.
cd backend
if errorlevel 1 exit /b 1
python telegram_fetcher.py
if errorlevel 1 exit /b 1
cd ..
git diff --quiet -- data.json
if not errorlevel 1 (
  echo No changes to data.json.
  exit /b 0
)
git add -- data.json
if errorlevel 1 exit /b 1
git commit -m "Update links"
if errorlevel 1 exit /b 1
git push
if errorlevel 1 exit /b 1
echo.
echo Done! Website will update in 1-2 minutes.
echo.
pause
