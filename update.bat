@echo off
echo.
echo ======================================
echo Updating SwarnSports Links...
echo ======================================
echo.
cd backend
python telegram_fetcher.py
cd ..
git add data.json
git commit -m "Update links" || echo No changes to commit
git push
echo.
echo Done! Website will update in 1-2 minutes.
echo.
pause
