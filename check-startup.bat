@echo off
REM Check Windows Startup folder for Claude Memory API entries

echo.
echo ========================================
echo   Checking Windows Startup Folder
echo ========================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo 📁 Startup folder location:
echo    %STARTUP_FOLDER%
echo.

echo 📋 All files in startup folder:
echo --------------------------------
dir /b "%STARTUP_FOLDER%" 2>nul || echo    [Empty - no files found]
echo.

echo 🔍 Claude Memory API related files:
echo --------------------------------
dir /b "%STARTUP_FOLDER%\*Claude*.bat" 2>nul || echo    [None found]
dir /b "%STARTUP_FOLDER%\*memory*.bat" 2>nul || echo    [None found]
echo.

pause