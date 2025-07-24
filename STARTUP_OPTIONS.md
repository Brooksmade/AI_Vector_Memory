# Claude Memory API - Auto-Startup Options

The Claude Memory API can be configured to automatically start when Windows boots. You have several options, each with different benefits:

## 🚀 Quick Start Options

### Option 1: Startup Folder (Recommended) 
**✅ No admin rights required | ✅ Simple setup | ✅ User-specific**

```batch
# Install system tray to startup folder
install-startup-tray.bat

# Remove from startup folder  
remove-startup-tray.bat
```

### Option 2: Windows Service (Advanced)
**⚠️ Requires admin rights | ✅ Robust | ✅ Runs without login**

```powershell
# Install as Windows service (run as Administrator)
.\install-startup-tray-service.ps1 -Install

# Remove service
.\install-startup-tray-service.ps1 -Uninstall

# Check service status
.\install-startup-tray-service.ps1 -Status
```

## 📊 Comparison of Methods

| Method | Admin Required | Starts Without Login | Robustness | Setup Difficulty |
|--------|----------------|---------------------|------------|------------------|
| **Startup Folder** | ❌ No | ❌ No | ⭐⭐⭐ Good | ⭐ Easy |
| **Windows Service** | ✅ Yes | ✅ Yes | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Medium |

## 🔧 Detailed Setup Instructions

### Method 1: Startup Folder Setup

This method adds the system tray application to your Windows startup folder, so it starts when you log in.

**Advantages:**
- No administrator privileges needed
- Easy to install and remove
- User-specific (doesn't affect other users)
- System tray icon appears when you log in

**Disadvantages:**
- Only starts when you log in to Windows
- User must be logged in for the API to be available

**Setup Steps:**
1. Double-click `install-startup-tray.bat`
2. The script will automatically:
   - Create a startup script in your Windows startup folder
   - Configure it to launch the system tray version
   - Show confirmation of successful installation

**Files Created:**
- `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\ClaudeMemoryAPI-Tray.bat`

**To Remove:**
- Double-click `remove-startup-tray.bat`, or
- Manually delete the file from the startup folder

### Method 2: Windows Service Setup

This method installs the API server as a proper Windows service for maximum reliability.

**Advantages:**
- Starts automatically with Windows (before login)
- Automatic restart if the process crashes
- Runs in background even without user login
- Most robust and reliable method
- Still shows system tray icon when user logs in

**Disadvantages:**
- Requires administrator privileges to install
- More complex setup and troubleshooting
- System-wide installation

**Setup Steps:**
1. **Right-click** on PowerShell or Command Prompt and **"Run as Administrator"**
2. Navigate to the project directory
3. Run: `.\install-startup-tray-service.ps1 -Install`
4. The service will be installed and started automatically

**Service Management:**
```powershell
# Check service status
.\install-startup-tray-service.ps1 -Status

# Start service manually
Start-Service ClaudeMemoryAPITray

# Stop service manually  
Stop-Service ClaudeMemoryAPITray

# Remove service completely
.\install-startup-tray-service.ps1 -Uninstall
```

## 🔍 Verification

After installation, verify the setup is working:

### For Startup Folder Method:
1. **Restart Windows** or **log out and back in**
2. Look for the **green system tray icon** in your notification area
3. **Right-click** the icon and select **"Status"** to verify it's running

### For Windows Service Method:
1. **Restart Windows** (full restart, not just logout)
2. Before logging in, the service should already be running
3. After logging in, look for the **system tray icon**
4. Check service status: `.\install-startup-tray-service.ps1 -Status`

### General Verification:
- Test API health: Open browser to `http://localhost:8080/api/health`
- Check system tray: Green icon = running, Red icon = stopped
- View logs: Right-click tray icon → "View Logs"

## 🛠️ Troubleshooting

### Startup Folder Method Issues:

**Tray icon doesn't appear:**
- Check if the startup file exists: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\ClaudeMemoryAPI-Tray.bat`
- Try running the batch file manually to see error messages
- Check `logs/tray_app.log` for error details

**Server doesn't start:**
- Ensure virtual environment is set up correctly
- Verify all dependencies are installed: `.\venv\Scripts\pip install -r requirements_api.txt`
- Check if port 8080 is already in use

### Windows Service Method Issues:

**Service won't install:**
- Ensure you're running PowerShell as Administrator
- Check Windows Event Viewer for service installation errors
- Verify Python virtual environment exists

**Service starts but no tray icon:**
- The service runs in the background; tray icon only appears when user logs in
- Check service status: `Get-Service ClaudeMemoryAPITray`
- Check service logs in Windows Event Viewer

**Service won't start:**
- Check service status: `.\install-startup-tray-service.ps1 -Status`
- Look for errors in Windows Event Viewer (Windows Logs → System)
- Ensure Python virtual environment is set up correctly

## 📝 Files Overview

### Auto-Startup Files:
- `install-startup-tray.bat` - Install to startup folder
- `remove-startup-tray.bat` - Remove from startup folder  
- `install-startup-tray-service.ps1` - Windows service installer
- `STARTUP_OPTIONS.md` - This documentation

### Legacy Console Auto-Startup (still available):
- `install-startup.bat` - Install console version to startup folder
- `remove-startup.bat` - Remove console version from startup folder
- `install-startup-service.ps1` - Console version Windows service

## 🎯 Recommendations

**For most users:** Use the **Startup Folder method** (`install-startup-tray.bat`)
- Simple, safe, and effective
- No admin rights needed
- Easy to remove if needed

**For servers or always-on systems:** Use the **Windows Service method**
- Most reliable for 24/7 operation
- Starts before user login
- Automatic restart on failure

**For development:** Don't use auto-startup
- Manually start when needed using desktop shortcuts
- Easier to stop/restart during development

The system tray mode provides the best user experience while keeping the server running discreetly in the background with easy access to status and controls.