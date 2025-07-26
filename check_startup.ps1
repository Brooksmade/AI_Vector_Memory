$startupFolder = [Environment]::GetFolderPath('Startup')
Write-Host "Startup folder: $startupFolder"
Write-Host ""

if (Test-Path $startupFolder) {
    $files = Get-ChildItem $startupFolder -ErrorAction SilentlyContinue
    if ($files.Count -eq 0) {
        Write-Host "No files in startup folder"
    } else {
        Write-Host "Files in startup folder:"
        foreach ($file in $files) {
            Write-Host "  - $($file.Name)"
        }
    }
    
    Write-Host ""
    Write-Host "Claude-related files:"
    $claudeFiles = Get-ChildItem $startupFolder -Filter "*Claude*" -ErrorAction SilentlyContinue
    if ($claudeFiles.Count -eq 0) {
        Write-Host "  None found"
    } else {
        foreach ($file in $claudeFiles) {
            Write-Host "  - $($file.Name)"
        }
    }
} else {
    Write-Host "Startup folder not found!"
}