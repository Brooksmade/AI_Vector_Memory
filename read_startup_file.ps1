$startupFolder = [Environment]::GetFolderPath('Startup')
$startupFile = Join-Path $startupFolder "ClaudeMemoryAPI-Startup.bat"

if (Test-Path $startupFile) {
    Write-Host "Content of ClaudeMemoryAPI-Startup.bat:"
    Write-Host "====================================="
    Get-Content $startupFile
} else {
    Write-Host "Startup file not found at: $startupFile"
}