@echo off
REM Install Claude Memory API Server (System Tray) to Windows Startup
REM This script adds the system tray API server to Windows startup

echo.
echo ========================================
echo   Installing System Tray Mode to Startup
echo ========================================
echo.

REM Get current directory
set "SCRIPT_DIR=%~dp0"
set "TRAY_BAT=%SCRIPT_DIR%start_memory_api_tray.bat"

REM Check if the tray batch file exists
if not exist "%TRAY_BAT%" (
    echo ❌ Error: start_memory_api_tray.bat not found!
    echo Please ensure the file exists in this directory.
    pause
    exit /b 1
)

REM Get Windows startup folder
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM Create a batch file in startup folder that calls our tray script
set "STARTUP_BAT=%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.bat"

echo 🔧 Creating system tray startup script...
echo @echo off > "%STARTUP_BAT%"
echo REM Auto-start Claude Memory API Server in System Tray >> "%STARTUP_BAT%"
echo cd /d "%SCRIPT_DIR%" >> "%STARTUP_BAT%"
echo start "Claude Memory API Tray" /min "%TRAY_BAT%" >> "%STARTUP_BAT%"

if exist "%STARTUP_BAT%" (
    echo ✅ Successfully installed system tray mode to Windows startup!
    echo.
    echo 📍 Startup file location: %STARTUP_BAT%
    echo 🔔 The API server will now start in system tray when Windows boots.
    echo.
    echo 🎯 System Tray Features:
    echo    - Runs completely in background
    echo    - System tray icon for status and control
    echo    - No visible console windows
    echo    - Right-click menu for controls
    echo.
    echo 💡 To remove from startup, run: remove-startup-tray.bat
    echo    Or manually delete: %STARTUP_BAT%
    echo.
) else (
    echo ❌ Failed to create startup file!
    echo Please check permissions and try running as administrator.
)

pause