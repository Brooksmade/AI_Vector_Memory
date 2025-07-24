# Create Desktop Shortcuts for Claude Memory API Server
# This script creates desktop shortcuts for both console and system tray modes

param(
    [switch]$TrayOnly,  # Create only the system tray shortcut
    [switch]$ConsoleOnly  # Create only the console shortcut
)

$ScriptPath = $PSScriptRoot
$DesktopPath = [Environment]::GetFolderPath("Desktop")

function Create-Shortcut {
    param(
        [string]$Name,
        [string]$TargetFile,
        [string]$Description,
        [string]$IconPath = "cmd.exe,0"
    )
    
    $ShortcutPath = Join-Path $DesktopPath "$Name.lnk"
    $TargetPath = Join-Path $ScriptPath $TargetFile
    
    if (-not (Test-Path $TargetPath)) {
        Write-Host "Warning: $TargetFile not found, skipping shortcut creation" -ForegroundColor Yellow
        return
    }
    
    # Create shortcut object
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
    
    # Set shortcut properties
    $Shortcut.TargetPath = $TargetPath
    $Shortcut.WorkingDirectory = $ScriptPath
    $Shortcut.Description = $Description
    $Shortcut.IconLocation = $IconPath
    
    # Save the shortcut
    $Shortcut.Save()
    
    Write-Host "Created: $Name" -ForegroundColor Green
    Write-Host "   Location: $ShortcutPath" -ForegroundColor Cyan
}

Write-Host "" 
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Creating Claude Memory API Shortcuts" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create System Tray shortcut (default and recommended)
if (-not $ConsoleOnly) {
    Write-Host "Creating System Tray shortcut (recommended)..." -ForegroundColor Green
    Create-Shortcut -Name "Claude Memory API (System Tray)" -TargetFile "start_memory_api_tray.bat" -Description "Launch Claude Memory API Server in System Tray" -IconPath "shell32.dll,25"
}

# Create Console shortcut (traditional)
if (-not $TrayOnly) {
    Write-Host "Creating Console shortcut (traditional)..." -ForegroundColor Yellow
    Create-Shortcut -Name "Claude Memory API (Console)" -TargetFile "start_memory_api.bat" -Description "Launch Claude Memory API Server in Console" -IconPath "cmd.exe,0"
}

Write-Host ""
Write-Host "Shortcut Recommendations:" -ForegroundColor Cyan
Write-Host "   - Use 'System Tray' version for background operation" -ForegroundColor Green
Write-Host "   - Use 'Console' version for debugging or development" -ForegroundColor Yellow
Write-Host ""
Write-Host "System Tray Features:" -ForegroundColor Cyan
Write-Host "   - Runs in background without visible window" -ForegroundColor White
Write-Host "   - System tray icon with status indicator" -ForegroundColor White
Write-Host "   - Right-click menu for controls and status" -ForegroundColor White
Write-Host "   - Windows notifications for important events" -ForegroundColor White
Write-Host ""
Write-Host "Desktop shortcuts created successfully!" -ForegroundColor Green