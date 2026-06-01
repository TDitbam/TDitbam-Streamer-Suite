@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   TDitbam Streamer Suite Build Script
echo ==========================================

:: 1. Build EXE
echo [1/3] Building Executable...
python -m PyInstaller --onefile --name TDitbamStreamerSuite --clean --collect-all customtkinter --noconsole --uac-admin main.py
if %errorlevel% neq 0 (
    echo [ERROR] Build failed.
    pause
    exit /b %errorlevel%
)

:: 2. Build Installer
echo.
echo [2/3] Building Installer (Inno Setup)...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_main.iss
if %errorlevel% neq 0 (
    echo [ERROR] Installer build failed.
    pause
    exit /b %errorlevel%
)

echo.
echo ==========================================
echo   BUILD SUCCESSFUL!
echo   Output: output\TDitbam-StreamerSuite-v3.1.0-Setup.exe
echo ==========================================
pause
