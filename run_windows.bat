@echo off
title CyberRecon Launcher
color 0a
cls

echo ==================================================
echo      CYBER RECON TOOLKIT - INITIALIZING...
echo ==================================================
echo.

cd /d "%~dp0"

IF EXIST "venv" (
    echo [OK] Virtual Environment found.
) ELSE (
    echo [INFO] Creating Virtual Environment (First Run)...
    python -m venv venv
)

echo [INFO] Activating Environment...
call venv\Scripts\activate

echo [INFO] Installing Dependencies...
if exist requirements.txt (
    pip install -r requirements.txt >nul 2>&1
) else (
    echo [ERROR] requirements.txt not found at repo root.
    pause
    exit /b 1
)

echo [INFO] Starting Backend Server...
echo [INFO] Opening Browser...
start http://127.0.0.1:5000

python backend/app.py
pause