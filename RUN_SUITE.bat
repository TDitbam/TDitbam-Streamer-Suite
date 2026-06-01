@echo off
title TDitbam Streamer Suite Pro
echo [*] Starting TDitbam Streamer Suite...
cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo [!] Program crashed or Python is not installed correctly.
    echo [!] Make sure you have installed requirements via: pip install -r requirements.txt
    pause
)
