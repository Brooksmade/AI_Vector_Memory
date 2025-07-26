# Claude Memory API - Startup Files Guide

This document explains the startup files for the Claude Memory API server.

## Main Startup Files

### 1. `start_memory_api.bat`
- **Purpose**: Starts the API server in console mode
- **Use when**: You want to see server logs in a console window
- **Features**: Shows all server output, easy debugging

### 2. `start_tray_silent.bat`
- **Purpose**: Starts the API server with system tray icon (silent mode)
- **Use when**: For Windows startup or background operation
- **Features**: No console window, system tray icon for control

### 3. `memory_api_tray.py`
- **Purpose**: The actual Python system tray application
- **Note**: Called by start_tray_silent.bat, not run directly

## Installation Scripts

### `install-startup-tray.bat`
- Adds the tray app to Windows startup
- Creates a launcher in the Windows Startup folder

### `remove-from-startup.bat`
- Removes the tray app from Windows startup

### `check-startup.bat`
- Shows what's currently in your Windows startup folder

## Quick Start

**For manual start with console:**
```bash
start_memory_api.bat
```

**For background operation with tray icon:**
```bash
start_tray_silent.bat
```

**To add to Windows startup:**
```bash
install-startup-tray.bat
```

## Removed Files
The following redundant files have been removed to simplify the project:
- Launch-MemoryAPI.cmd/ps1
- Start-MemoryAPI.ps1
- Start-MemoryAPI-Tray.ps1
- start_memory_api_tray.bat
- Various test and fix batch files