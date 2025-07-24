@echo off
REM Install Claude Memory API Server to Windows Startup
REM This script adds the API server to Windows startup

echo.
echo ========================================
echo   Installing to Windows Startup
echo ========================================
echo.

REM Get current directory
set "SCRIPT_DIR=%~dp0"
set "BAT_FILE=%SCRIPT_DIR%start_memory_api.bat"

REM Check if the batch file exists
if not exist "%BAT_FILE%" (
    echo ❌ Error: start_memory_api.bat not found!
    echo Please ensure the file exists in this directory.
    pause
    exit /b 1
)

REM Get Windows startup folder
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM Create a batch file in startup folder that calls our main script
set "STARTUP_BAT=%STARTUP_FOLDER%\ClaudeMemoryAPI.bat"

echo 🔧 Creating startup script...
echo @echo off > "%STARTUP_BAT%"
echo REM Auto-start Claude Memory API Server >> "%STARTUP_BAT%"
echo cd /d "%SCRIPT_DIR%" >> "%STARTUP_BAT%"
echo start "Claude Memory API" "%BAT_FILE%" >> "%STARTUP_BAT%"

if exist "%STARTUP_BAT%" (
    echo ✅ Successfully installed to Windows startup!
    echo.
    echo 📍 Startup file location: %STARTUP_BAT%
    echo 🚀 The API server will now start automatically when Windows boots.
    echo.
    echo 💡 To remove from startup, delete the file:
    echo    %STARTUP_BAT%
    echo.
) else (
    echo ❌ Failed to create startup file!
    echo Please check permissions and try running as administrator.
)

pause