# Install Claude Memory API Server (System Tray) as Windows Service
# This provides the most robust startup handling for system tray mode

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Status
)

$ServiceName = "ClaudeMemoryAPITray"
$ServiceDisplayName = "Claude Memory API Server (System Tray)"
$ScriptPath = $PSScriptRoot
$TrayScript = Join-Path $ScriptPath "memory_api_tray.py"
$PythonExe = Join-Path $ScriptPath "venv\Scripts\python.exe"

function Install-Service {
    Write-Host "🔧 Installing Claude Memory API (System Tray) as Windows Service..." -ForegroundColor Cyan
    
    if (-not (Test-Path $TrayScript)) {
        Write-Host "❌ Error: memory_api_tray.py not found!" -ForegroundColor Red
        return $false
    }
    
    if (-not (Test-Path $PythonExe)) {
        Write-Host "❌ Error: Python virtual environment not found!" -ForegroundColor Red
        return $false
    }
    
    # Create service wrapper script
    $ServiceScript = Join-Path $ScriptPath "service_tray_wrapper.bat"
    @"
@echo off
cd /d "$ScriptPath"
"$PythonExe" "$TrayScript"
"@ | Out-File -FilePath $ServiceScript -Encoding ASCII
    
    try {
        # Create service using sc command
        $binPath = "`"$ServiceScript`""
        $result = & sc.exe create $ServiceName binPath= $binPath start= auto displayName= "`"$ServiceDisplayName`""
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Service installed successfully!" -ForegroundColor Green
            Write-Host "🚀 Starting service..." -ForegroundColor Cyan
            & sc.exe start $ServiceName
            
            Write-Host ""
            Write-Host "🔔 System Tray Service Features:" -ForegroundColor Cyan
            Write-Host "   - Starts automatically with Windows" -ForegroundColor White
            Write-Host "   - Runs in background with system tray icon" -ForegroundColor White
            Write-Host "   - Automatic restart if crashed" -ForegroundColor White
            Write-Host "   - No user login required" -ForegroundColor White
            
            return $true
        } else {
            Write-Host "❌ Failed to install service: $result" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Error installing service: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Uninstall-Service {
    Write-Host "🗑️ Removing Claude Memory API Tray Service..." -ForegroundColor Cyan
    
    try {
        # Stop service if running
        & sc.exe stop $ServiceName | Out-Null
        Start-Sleep -Seconds 3
        
        # Delete service
        $result = & sc.exe delete $ServiceName
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Service removed successfully!" -ForegroundColor Green
            
            # Clean up service wrapper
            $ServiceScript = Join-Path $ScriptPath "service_tray_wrapper.bat"
            if (Test-Path $ServiceScript) {
                Remove-Item $ServiceScript -Force
            }
            return $true
        } else {
            Write-Host "❌ Failed to remove service: $result" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Error removing service: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Get-ServiceStatus {
    Write-Host "📊 Claude Memory API Tray Service Status:" -ForegroundColor Cyan
    
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        
        if ($service) {
            Write-Host "   Status: $($service.Status)" -ForegroundColor Yellow
            Write-Host "   Start Type: $($service.StartType)" -ForegroundColor Yellow
            Write-Host "   Display Name: $($service.DisplayName)" -ForegroundColor Yellow
        } else {
            Write-Host "   Status: Not Installed" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "   Status: Not Installed" -ForegroundColor Red
    }
}

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Main execution
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Claude Memory API Tray Service Manager" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($Install -or $Uninstall) {
    if (-not (Test-Administrator)) {
        Write-Host "❌ Error: Administrator privileges required for service installation!" -ForegroundColor Red
        Write-Host "Please run this script as Administrator." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "💡 Alternative: Use install-startup-tray.bat for startup folder method" -ForegroundColor Cyan
        exit 1
    }
}

if ($Install) {
    $success = Install-Service
    if (-not $success) { exit 1 }
}
elseif ($Uninstall) {
    $success = Uninstall-Service
    if (-not $success) { exit 1 }
}
elseif ($Status) {
    Get-ServiceStatus
}
else {
    Write-Host "Claude Memory API Tray Service Manager" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\install-startup-tray-service.ps1 -Install    # Install as Windows service" -ForegroundColor Cyan
    Write-Host "  .\install-startup-tray-service.ps1 -Uninstall  # Remove service" -ForegroundColor Cyan
    Write-Host "  .\install-startup-tray-service.ps1 -Status     # Check service status" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🔔 System Tray Service Benefits:" -ForegroundColor Green
    Write-Host "   - Automatic startup with Windows" -ForegroundColor White
    Write-Host "   - Runs without user login" -ForegroundColor White
    Write-Host "   - Automatic restart if crashed" -ForegroundColor White
    Write-Host "   - System tray icon when user logs in" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  Note: Requires Administrator privileges" -ForegroundColor Red
    Write-Host "💡 Alternative: Use install-startup-tray.bat (no admin required)" -ForegroundColor Cyan
}