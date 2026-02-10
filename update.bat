@echo off
echo.
echo ======================================
echo 🏏 Updating SwarnSports Links...
echo ======================================
echo.

REM Change to the script's directory
cd /d "%~dp0"

cd backend
python telegram_fetcher.py
if errorlevel 1 (
    echo ❌ Error fetching links!
    pause
    exit /b 1
)
cd ..

git add data.json
git commit -m "Update links - %date% %time%" || echo No changes to commit
git push

echo.
echo ✅ Done! Website will update in 1-2 minutes.
echo.
pause
