@echo off
echo ========================================
echo  Starting Frontend Server
echo ========================================
echo.

cd /d "%~dp0frontend"

echo Starting React development server...
echo This will take 30-60 seconds...
echo.

npm start

pause
