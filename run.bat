@echo off
setlocal
cd /d "%~dp0"

:: 1. Try to run the application first
python main.py

:: 2. If it fails, identify the cause and fix it
if %errorlevel% neq 0 (
    echo.
    echo [!] Application failed or Python is missing. Diagnosing...
    
    :: Check if Python is installed
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] Python not found. Installing via winget...
        winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
        if %errorlevel% equ 0 (
            echo [*] Python installed. Please restart this script.
        ) else (
            echo [!] winget failed. Please install Python manually from python.org
        )
    ) else (
        :: Python exists, so the error was likely missing libraries
        if exist "requirements.txt" (
            echo [!] Missing libraries detected. Installing requirements...
            python -m pip install -r requirements.txt
            
            echo [*] Retrying application...
            python main.py
        ) else (
            echo [!] requirements.txt not found. Cannot auto-install libraries.
        )
    )
    pause
)
