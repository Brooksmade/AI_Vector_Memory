@echo off
REM Fix Windows Startup - Remove old version and install tray version
REM This ensures only the system tray version runs at startup

echo.
echo ========================================
echo   Fixing Startup Configuration
echo ========================================
echo.

REM Get Windows startup folder
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo 🔍 Checking for existing startup files...

REM Remove any existing Claude Memory API startup files
if exist "%STARTUP_FOLDER%\ClaudeMemoryAPI.bat" (
    echo 🗑️  Removing old startup file: ClaudeMemoryAPI.bat
    del "%STARTUP_FOLDER%\ClaudeMemoryAPI.bat"
)

if exist "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.bat" (
    echo 🗑️  Removing existing tray startup file...
    del "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.bat"
)

if exist "%STARTUP_FOLDER%\start_memory_api.bat" (
    echo 🗑️  Removing direct startup file...
    del "%STARTUP_FOLDER%\start_memory_api.bat"
)

echo.
echo ✅ Cleaned up old startup files
echo.
echo 🔧 Now installing system tray version...
echo.

REM Run the install-startup-tray.bat to add the tray version
call "%~dp0install-startup-tray.bat"