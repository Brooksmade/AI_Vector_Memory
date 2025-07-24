# Claude Memory API - Complete Uninstall Guide

This guide will completely remove the Claude Memory API system from your computer and restore your system to its previous state.

## ⚠️ WARNING
This will permanently delete all stored memories and cannot be undone. Make sure you have backups of any important conversation data before proceeding.

---

## Step 1: Stop All Running Services

### Stop the API Server
If the server is currently running:
1. Go to the PowerShell window running the server
2. Press **Ctrl+C** to stop it
3. Close the PowerShell window

### Stop Background Processes
```powershell
# Kill any remaining Python processes
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*memory_api_server*" } | Stop-Process -Force

# Kill any PowerShell processes running the memory API
Get-Process powershell -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*ClaudeMemory*" } | Stop-Process -Force
```

---

## Step 2: Remove Windows Startup Integration

### Remove Startup Script
```powershell
# Remove startup script if it exists
$startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\ClaudeMemoryAPI.ps1"
if (Test-Path $startupPath) {
    Remove-Item $startupPath -Force
    Write-Host "Removed startup script: $startupPath"
}
```

### Remove Scheduled Tasks (if any were created)
```powershell
# Check for any scheduled tasks
Get-ScheduledTask | Where-Object { $_.TaskName -like "*Claude*Memory*" -or $_.TaskName -like "*MemoryAPI*" } | Unregister-ScheduledTask -Confirm:$false
```

### Remove Windows Services (if any were installed)
```powershell
# Check for Windows services
$service = Get-Service -Name "ClaudeMemoryAPI" -ErrorAction SilentlyContinue
if ($service) {
    Stop-Service -Name "ClaudeMemoryAPI" -Force
    Remove-Service -Name "ClaudeMemoryAPI"
    Write-Host "Removed Windows service: ClaudeMemoryAPI"
}
```

---

## Step 3: Remove PowerShell Module Integration

### Unload PowerShell Module
```powershell
# Remove from current session
Remove-Module ClaudeMemory -ErrorAction SilentlyContinue

# Remove from PowerShell profile (if added)
$profiles = @(
    $PROFILE.AllUsersAllHosts,
    $PROFILE.AllUsersCurrentHost, 
    $PROFILE.CurrentUserAllHosts,
    $PROFILE.CurrentUserCurrentHost
)

foreach ($profile in $profiles) {
    if (Test-Path $profile) {
        $content = Get-Content $profile
        $newContent = $content | Where-Object { $_ -notlike "*ClaudeMemory*" -and $_ -notlike "*memory_api*" }
        if ($content.Count -ne $newContent.Count) {
            $newContent | Set-Content $profile
            Write-Host "Cleaned PowerShell profile: $profile"
        }
    }
}
```

---

## Step 4: Remove Environment Variables

```powershell
# Remove any environment variables that may have been set
[Environment]::SetEnvironmentVariable("CLAUDE_MEMORY_API_URL", $null, "User")
[Environment]::SetEnvironmentVariable("CLAUDE_MEMORY_PATH", $null, "User")
[Environment]::SetEnvironmentVariable("FLASK_ENV", $null, "User")
[Environment]::SetEnvironmentVariable("FLASK_DEBUG", $null, "User")

# Remove from system-wide environment if they exist
[Environment]::SetEnvironmentVariable("CLAUDE_MEMORY_API_URL", $null, "Machine")
[Environment]::SetEnvironmentVariable("CLAUDE_MEMORY_PATH", $null, "Machine")
```

---

## Step 5: Clean Up File Associations and Registry

### Remove File Associations (if any were created)
```powershell
# Clean up any file associations for .memory files or similar
$extensions = @(".memory", ".claude-memory")
foreach ($ext in $extensions) {
    $key = "HKCU:\Software\Classes\$ext"
    if (Test-Path $key) {
        Remove-Item $key -Recurse -Force
        Write-Host "Removed file association for $ext"
    }
}
```

### Remove Registry Entries
```powershell
# Remove any registry entries related to Claude Memory API
$registryPaths = @(
    "HKCU:\Software\ClaudeMemoryAPI",
    "HKLM:\Software\ClaudeMemoryAPI",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run\ClaudeMemoryAPI"
)

foreach ($path in $registryPaths) {
    if (Test-Path $path) {
        Remove-Item $path -Recurse -Force
        Write-Host "Removed registry key: $path"
    }
}
```

---

## Step 6: Remove the Entire Directory

### Full Directory Removal
```powershell
# Navigate out of the directory first
cd C:\

# Remove the entire Claude Memory API directory
$memoryDir = "E:\tools\claude-code-vector-memory"
if (Test-Path $memoryDir) {
    # Force remove all files and subdirectories
    Remove-Item $memoryDir -Recurse -Force -ErrorAction Stop
    Write-Host "Successfully removed directory: $memoryDir"
} else {
    Write-Host "Directory not found: $memoryDir"
}
```

**Alternative manual method:**
1. Open File Explorer
2. Navigate to `E:\tools\`
3. Right-click on `claude-code-vector-memory` folder
4. Select "Delete" 
5. Confirm deletion
6. Empty Recycle Bin if desired

---

## Step 7: Clean Up Python Environment References

### Remove Python Virtual Environment References
```powershell
# Remove any pip cache references
pip cache purge

# Remove any global Python packages that were installed for this project
pip uninstall flask flask-cors flask-limiter chromadb pydantic sentence-transformers -y
```

---

## Step 8: Restore CLAUDE.md Files (IMPORTANT)

If you modified any CLAUDE.md files to integrate with this system, you need to restore them:

### For Claude Code CLI Projects
```powershell
# Check each project where you added memory integration
$projects = @(
    "E:\github\subframe-warehouse-inventory-management",
    # Add other project paths here
)

foreach ($project in $projects) {
    $claudeFile = "$project\CLAUDE.md"
    if (Test-Path $claudeFile) {
        Write-Host "MANUAL ACTION REQUIRED: Review and restore $claudeFile"
        Write-Host "Remove any lines referring to:"
        Write-Host "  - HTTP memory API"
        Write-Host "  - localhost:8080"
        Write-Host "  - memory_search.py API calls"
        Write-Host ""
    }
}
```

**Manual Steps Required:**
1. Go to each project that used this memory system
2. Open the `CLAUDE.md` file
3. Remove or restore the memory integration sections
4. Replace with your original memory approach or remove entirely

---

## Step 9: Verify Complete Removal

### Verification Checklist
Run these commands to verify everything is removed:

```powershell
# 1. Check if directory exists
Test-Path "E:\tools\claude-code-vector-memory"  # Should return False

# 2. Check for running processes
Get-Process | Where-Object { $_.ProcessName -like "*python*" -and $_.MainWindowTitle -like "*memory*" }  # Should return nothing

# 3. Check startup folder
Test-Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\ClaudeMemoryAPI.ps1"  # Should return False

# 4. Check for PowerShell module
Get-Module ClaudeMemory -ListAvailable  # Should return nothing

# 5. Check environment variables
[Environment]::GetEnvironmentVariable("CLAUDE_MEMORY_API_URL", "User")  # Should return nothing

# 6. Check if port 8080 is free
Test-NetConnection -ComputerName localhost -Port 8080  # Should fail or timeout
```

---

## Step 10: Restart Computer

**Recommended:** Restart your computer to ensure all changes take effect and no lingering processes remain.

```powershell
Restart-Computer -Confirm
```

---

## Complete Removal Verification

After restart, your system should be completely clean:
- ✅ No Claude Memory API directory
- ✅ No background processes
- ✅ No startup scripts
- ✅ No PowerShell modules
- ✅ No environment variables
- ✅ No registry entries
- ✅ No Windows services
- ✅ Port 8080 available
- ✅ No file associations

---

## If You Need Help

If you encounter any issues during uninstallation:

1. **Permission Errors**: Run PowerShell as Administrator
2. **File in Use Errors**: Restart computer and try again
3. **Registry Access Denied**: Use `regedit` as Administrator to manually remove entries
4. **Persistent Processes**: Use Task Manager to force-kill any remaining processes

---

## Note

This uninstall process removes all traces of the Claude Memory API system. If you want to use a memory system in the future, you'll need to implement a different approach or reinstall this system from scratch.

The original script-based memory approach from your previous setup was not affected by this installation and can still be used if you have those files backed up.