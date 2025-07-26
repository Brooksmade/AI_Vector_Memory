@echo off
REM Remove Claude Memory API from Windows Startup
title Removing Claude Memory API from Startup

echo.
echo ========================================
echo   Removing from Windows Startup
echo ========================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

echo Startup folder: %STARTUP_FOLDER%
echo.
echo Removing Claude Memory API startup files...
echo.

set "REMOVED_COUNT=0"

REM Remove all possible startup variations - BAT files
if exist "%STARTUP_FOLDER%\ClaudeMemoryAPI-Startup.bat" (
    echo Removing: ClaudeMemoryAPI-Startup.bat
    del /f /q "%STARTUP_FOLDER%\ClaudeMemoryAPI-Startup.bat" 2>nul
    if not exist "%STARTUP_FOLDER%\ClaudeMemoryAPI-Startup.bat" (
        echo    [OK] Removed successfully
        set /a REMOVED_COUNT+=1
    ) else (
        echo    [RETRY] Clearing attributes and trying again...
        attrib -r -s -h "%STARTUP_FOLDER%\ClaudeMemoryAPI-Startup.bat" 2>nul
        del /f /q "%STARTUP_FOLDER%\ClaudeMemoryAPI-Startup.bat" 2>nul
        if not exist "%STARTUP_FOLDER%\ClaudeMemoryAPI-Startup.bat" (
            echo    [OK] Removed after clearing attributes
            set /a REMOVED_COUNT+=1
        ) else (
            echo    [ERROR] Failed to remove file
        )
    )
    echo.
)

if exist "%STARTUP_FOLDER%\ClaudeMemoryAPI.bat" (
    echo Removing: ClaudeMemoryAPI.bat
    del /f /q "%STARTUP_FOLDER%\ClaudeMemoryAPI.bat" 2>nul
    if not exist "%STARTUP_FOLDER%\ClaudeMemoryAPI.bat" (
        echo    [OK] Removed successfully
        set /a REMOVED_COUNT+=1
    ) else (
        echo    [RETRY] Clearing attributes and trying again...
        attrib -r -s -h "%STARTUP_FOLDER%\ClaudeMemoryAPI.bat" 2>nul
        del /f /q "%STARTUP_FOLDER%\ClaudeMemoryAPI.bat" 2>nul
        if not exist "%STARTUP_FOLDER%\ClaudeMemoryAPI.bat" (
            echo    [OK] Removed after clearing attributes
            set /a REMOVED_COUNT+=1
        ) else (
            echo    [ERROR] Failed to remove file
        )
    )
    echo.
)

if exist "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.bat" (
    echo Removing: ClaudeMemoryAPI-Tray.bat
    del /f /q "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.bat" 2>nul
    if not exist "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.bat" (
        echo    [OK] Removed successfully
        set /a REMOVED_COUNT+=1
    ) else (
        echo    [RETRY] Clearing attributes and trying again...
        attrib -r -s -h "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.bat" 2>nul
        del /f /q "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.bat" 2>nul
        if not exist "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.bat" (
            echo    [OK] Removed after clearing attributes
            set /a REMOVED_COUNT+=1
        ) else (
            echo    [ERROR] Failed to remove file
        )
    )
    echo.
)

if exist "%STARTUP_FOLDER%\start_memory_api.bat" (
    echo Removing: start_memory_api.bat
    del /f /q "%STARTUP_FOLDER%\start_memory_api.bat" 2>nul
    if not exist "%STARTUP_FOLDER%\start_memory_api.bat" (
        echo    [OK] Removed successfully
        set /a REMOVED_COUNT+=1
    ) else (
        echo    [ERROR] Failed to remove file
    )
    echo.
)

REM Remove PowerShell scripts
if exist "%STARTUP_FOLDER%\ClaudeMemoryAPI.ps1" (
    echo Removing: ClaudeMemoryAPI.ps1
    del /f /q "%STARTUP_FOLDER%\ClaudeMemoryAPI.ps1" 2>nul
    if not exist "%STARTUP_FOLDER%\ClaudeMemoryAPI.ps1" (
        echo    [OK] Removed successfully
        set /a REMOVED_COUNT+=1
    )
    echo.
)

if exist "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.ps1" (
    echo Removing: ClaudeMemoryAPI-Tray.ps1
    del /f /q "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.ps1" 2>nul
    if not exist "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.ps1" (
        echo    [OK] Removed successfully
        set /a REMOVED_COUNT+=1
    )
    echo.
)

REM Remove any shortcuts
if exist "%STARTUP_FOLDER%\ClaudeMemoryAPI.lnk" (
    echo Removing: ClaudeMemoryAPI.lnk
    del /f /q "%STARTUP_FOLDER%\ClaudeMemoryAPI.lnk" 2>nul
    if not exist "%STARTUP_FOLDER%\ClaudeMemoryAPI.lnk" (
        echo    [OK] Removed successfully
        set /a REMOVED_COUNT+=1
    )
    echo.
)

if exist "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.lnk" (
    echo Removing: ClaudeMemoryAPI-Tray.lnk
    del /f /q "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.lnk" 2>nul
    if not exist "%STARTUP_FOLDER%\ClaudeMemoryAPI-Tray.lnk" (
        echo    [OK] Removed successfully
        set /a REMOVED_COUNT+=1
    )
    echo.
)

echo ========================================
if %REMOVED_COUNT% GTR 0 (
    echo SUCCESS: Removed %REMOVED_COUNT% startup file(s)
) else (
    echo INFO: No Claude Memory API startup files found
)
echo ========================================
echo.
echo Press any key to exit...
pause >nul