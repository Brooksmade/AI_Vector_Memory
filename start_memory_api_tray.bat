@echo off
title Claude Memory API - System Tray Launcher

echo ========================================
echo   Claude Memory API - System Tray Mode
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if PowerShell script exists
if not exist "Start-MemoryAPI-Tray.ps1" (
    echo Error: Start-MemoryAPI-Tray.ps1 not found!
    echo Please ensure all files are in the correct directory.
    pause
    exit /b 1
)

echo Starting system tray application...
echo.
echo This window will close and the server will run in the background.
echo Look for the tray icon in your notification area.
echo.

REM Wait a moment to show the message
timeout /t 3 /nobreak >nul

REM Launch PowerShell script
powershell -ExecutionPolicy Bypass -File "Start-MemoryAPI-Tray.ps1"

REM If we get here, something went wrong
echo.
echo System tray application has stopped or failed to start.
pause