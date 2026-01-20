@echo off
echo ========================================
echo  Starting Biometric Verification System
echo ========================================
echo.

echo [1/3] Starting Backend Server...
cd backend
start cmd /k "python app.py"
timeout /t 3 /nobreak > nul

echo [2/3] Starting Frontend Server...
cd ..\frontend
start cmd /k "npm start"

echo [3/3] Opening Browser...
timeout /t 10 /nobreak > nul
start http://localhost:3000

echo.
echo ========================================
echo  System Started Successfully!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit this window...
pause > nul
