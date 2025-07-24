# Claude Memory API - System Tray Mode

The Claude Memory API now supports running in **System Tray Mode**, which allows the server to run in the background without showing a console window. This is the recommended way to run the API server for daily use.

## 🚀 Quick Start

### Option 1: Desktop Shortcut (Recommended)
1. Run `create-desktop-shortcut.ps1` to create desktop shortcuts
2. Double-click **"Claude Memory API (System Tray)"** shortcut on your desktop
3. The server will start in the background with a system tray icon

### Option 2: Manual Launch
```batch
# Run the batch file
start_memory_api_tray.bat

# Or run PowerShell script directly
powershell -ExecutionPolicy Bypass -File "Start-MemoryAPI-Tray.ps1"

# Or run Python directly
.\venv\Scripts\python.exe memory_api_tray.py
```

## 📋 System Tray Features

### 🔔 System Tray Icon
- **Green Icon**: Server is running and healthy
- **Red Icon**: Server is stopped or has errors
- **Yellow Icon**: Server is starting up
- **Gray Icon**: Status unknown

### 📱 Right-Click Menu Options
- **Status** (Double-click): View detailed server status
- **Open Health Check**: Opens browser to `/api/health` endpoint
- **Start Server**: Start the API server (if stopped)
- **Stop Server**: Stop the API server gracefully
- **View Logs**: Open the log file in your default text editor
- **Quit**: Exit the tray application

### 🔔 Windows Notifications
The system tray app shows notifications for:
- Server startup success/failure
- Server stop events
- Health check warnings
- Error conditions

## 🆚 Console vs System Tray Mode

| Feature | Console Mode | System Tray Mode |
|---------|--------------|------------------|
| **Visibility** | Visible PowerShell window | Hidden, tray icon only |
| **Background Operation** | Window must stay open | Runs completely in background |
| **Status Monitoring** | Manual health checks | Automatic health monitoring |
| **Startup Notifications** | Console output only | Windows notifications |
| **Control Interface** | Ctrl+C to stop | Right-click tray menu |
| **Best For** | Development, debugging | Daily use, production |

## 📁 Files Created

### New System Tray Files
- `memory_api_tray.py` - Main system tray application
- `Start-MemoryAPI-Tray.ps1` - PowerShell launcher for tray mode
- `start_memory_api_tray.bat` - Batch file launcher for tray mode

### Updated Files
- `requirements_api.txt` - Added system tray dependencies
- `create-desktop-shortcut.ps1` - Updated to create both shortcuts

### Dependencies Added
- `pystray==0.19.5` - System tray functionality
- `pillow==11.2.1` - Icon image generation
- `plyer==2.1.0` - Cross-platform notifications

## 🔧 Configuration

The system tray application uses the same configuration as the console version:
- **Host**: localhost (default)
- **Port**: 8080 (default)
- **Database**: `./chroma_db/`
- **Logs**: `./logs/tray_app.log`

## 🐛 Troubleshooting

### Tray Icon Not Appearing
- Check if the application is running in Task Manager
- Look for error messages in `logs/tray_app.log`
- Try running in console mode first to check for errors

### Server Not Starting
- Verify virtual environment is set up correctly
- Check `logs/tray_app.log` for detailed error messages
- Ensure port 8080 is not already in use

### Dependencies Missing
```bash
# Reinstall tray dependencies
.\venv\Scripts\pip.exe install -r requirements_api.txt
```

### Notifications Not Working
- Check Windows notification settings
- Ensure the application has notification permissions
- Try running as administrator if needed

## 💡 Usage Tips

1. **First Time Setup**: Use the console mode first to verify everything works, then switch to tray mode
2. **Health Monitoring**: The tray icon color indicates server health - green means everything is working
3. **Log Access**: Right-click the tray icon and select "View Logs" to see detailed information
4. **Status Check**: Double-click the tray icon to see current server status
5. **Clean Shutdown**: Always use "Quit" from the tray menu rather than ending the process

## 🔒 Security Notes

- The system tray application runs with the same permissions as the console version
- All API endpoints remain the same and maintain their security features
- Log files contain the same information as console mode
- The hidden console window is a display feature only - no security changes

This system tray mode provides a professional, unobtrusive way to run the Claude Memory API server while maintaining full functionality and providing easy access to status and controls.