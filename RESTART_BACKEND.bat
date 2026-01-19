@echo off
REM ========================================
REM  Backend Server Restart Script
REM ========================================

echo.
echo ========================================
echo  Restarting Backend Server
echo ========================================
echo.

REM Kill any existing Python processes running app.py
echo [1/3] Stopping existing backend processes...
taskkill /F /FI "WINDOWTITLE eq *app.py*" 2>nul
timeout /t 2 /nobreak > nul

REM Navigate to backend directory
cd /d "%~dp0backend"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [2/3] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [2/3] No virtual environment found, using system Python...
)

REM Start the backend server
echo [3/3] Starting backend server...
echo.
echo ========================================
echo  Backend Server Starting...
echo ========================================
echo.
echo Backend will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
