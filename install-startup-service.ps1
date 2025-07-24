# Install Claude Memory API Server as Windows Service (Alternative method)
# This provides more robust startup handling

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Status
)

$ServiceName = "ClaudeMemoryAPI"
$ServiceDisplayName = "Claude Memory API Server"
$ScriptPath = $PSScriptRoot
$BatFile = Join-Path $ScriptPath "start_memory_api.bat"

function Install-Service {
    Write-Host "🔧 Installing Claude Memory API as Windows Service..." -ForegroundColor Cyan
    
    if (-not (Test-Path $BatFile)) {
        Write-Host "❌ Error: start_memory_api.bat not found!" -ForegroundColor Red
        return $false
    }
    
    # Create service wrapper script
    $ServiceScript = Join-Path $ScriptPath "service_wrapper.bat"
    @"
@echo off
cd /d "$ScriptPath"
call "$BatFile"
"@ | Out-File -FilePath $ServiceScript -Encoding ASCII
    
    try {
        # Create service using sc command
        $result = & sc.exe create $ServiceName binPath= $ServiceScript start= auto displayName= $ServiceDisplayName
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Service installed successfully!" -ForegroundColor Green
            Write-Host "🚀 Starting service..." -ForegroundColor Cyan
            & sc.exe start $ServiceName
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
    Write-Host "🗑️ Removing Claude Memory API Service..." -ForegroundColor Cyan
    
    try {
        # Stop service if running
        & sc.exe stop $ServiceName | Out-Null
        Start-Sleep -Seconds 2
        
        # Delete service
        $result = & sc.exe delete $ServiceName
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Service removed successfully!" -ForegroundColor Green
            
            # Clean up service wrapper
            $ServiceScript = Join-Path $ScriptPath "service_wrapper.bat"
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
    Write-Host "📊 Claude Memory API Service Status:" -ForegroundColor Cyan
    
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        
        if ($service) {
            Write-Host "   Status: $($service.Status)" -ForegroundColor Yellow
            Write-Host "   Start Type: $($service.StartType)" -ForegroundColor Yellow
        } else {
            Write-Host "   Status: Not Installed" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "   Status: Not Installed" -ForegroundColor Red
    }
}

# Main execution
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
    Write-Host "Claude Memory API Service Manager" -ForegroundColor Green
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\install-startup-service.ps1 -Install    # Install as Windows service" -ForegroundColor Cyan
    Write-Host "  .\install-startup-service.ps1 -Uninstall  # Remove service" -ForegroundColor Cyan
    Write-Host "  .\install-startup-service.ps1 -Status     # Check service status" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Note: Must run as Administrator for service installation" -ForegroundColor Red
}