@echo off
title Ofrenda AI - Ghost in the Machine
echo ========================================================
echo   OFRENDA AI - SACRED DIGITAL ALTAR & SÉANCE
echo   Powered by Google Gemma 2B Open-Weight Intelligence
echo ========================================================
echo.
echo Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

echo.
echo [1/2] Starting local HTTP Server on http://localhost:8080...
start "" "http://localhost:8080"
python backend/app.py 8080
pause
