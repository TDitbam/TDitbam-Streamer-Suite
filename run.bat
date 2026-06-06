@echo off
cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo [!] Program crashed or failed to start.
    pause
)
