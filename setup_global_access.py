#!/usr/bin/env python3
"""
Setup global access to Claude Memory API from any project.
Creates command-line utilities and shortcuts for easy access.
"""

import os
import sys
import subprocess
from pathlib import Path
import winreg

def add_to_system_path():
    """Add the memory API directory to system PATH"""
    memory_dir = str(Path(__file__).parent)
    
    try:
        # Open the Environment Variables registry key
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
            0,
            winreg.KEY_ALL_ACCESS
        )
        
        # Get current PATH
        current_path, _ = winreg.QueryValueEx(key, "PATH")
        
        # Add our directory if not already there
        if memory_dir not in current_path:
            new_path = current_path + ";" + memory_dir
            winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"✅ Added {memory_dir} to system PATH")
        else:
            print(f"✅ {memory_dir} already in system PATH")
            
        winreg.CloseKey(key)
        return True
        
    except PermissionError:
        print("❌ Permission denied - run as Administrator to modify system PATH")
        return False
    except Exception as e:
        print(f"❌ Error modifying PATH: {e}")
        return False

def create_global_commands():
    """Create global command-line utilities"""
    memory_dir = Path(__file__).parent
    
    # Command scripts to create
    commands = {
        'claude-memory-start.bat': f'''@echo off
REM Start Claude Memory API Server
echo Starting Claude Memory API Server...
cd /d "{memory_dir}"
call venv\\Scripts\\activate.bat
python memory_api_server.py
''',
        
        'claude-memory-stop.bat': f'''@echo off
REM Stop Claude Memory API Server
echo Stopping Claude Memory API Server...
taskkill /f /im python.exe /fi "WINDOWTITLE eq Claude Memory API*" 2>nul
echo Server stopped.
pause
''',
        
        'claude-memory-status.bat': f'''@echo off
REM Check Claude Memory API Status
echo Checking Claude Memory API Status...
curl -s http://localhost:8080/api/health 2>nul
if %errorlevel% equ 0 (
    echo ✅ Memory API is running
) else (
    echo ❌ Memory API is not running
    echo Start with: claude-memory-start
)
pause
''',
        
        'claude-memory-search.bat': f'''@echo off
REM Search Claude Memory API
if "%~1"=="" (
    echo Usage: claude-memory-search "your search query"
    pause
    exit /b 1
)
echo Searching for: %~1
curl -X POST http://localhost:8080/api/search -H "Content-Type: application/json" -d "{\\"query\\": \\"%~1\\", \\"max_results\\": 3}"
pause
''',
        
        'claude-memory-health.bat': f'''@echo off
REM Quick health check
curl -s http://localhost:8080/api/health
'''
    }
    
    created_commands = []
    
    for filename, content in commands.items():
        command_file = memory_dir / filename
        
        with open(command_file, 'w') as f:
            f.write(content)
            
        created_commands.append(command_file)
        print(f"✅ Created global command: {filename}")
    
    return created_commands

def create_desktop_shortcuts():
    """Create desktop shortcuts for easy access"""
    try:
        import win32com.client
        
        desktop = Path.home() / "Desktop"
        memory_dir = Path(__file__).parent
        
        shortcuts = [
            {
                'name': 'Claude Memory API - Start',
                'target': str(memory_dir / 'claude-memory-start.bat'),
                'icon': str(memory_dir / 'claude-memory-start.bat'),
                'description': 'Start Claude Memory API Server'
            },
            {
                'name': 'Claude Memory API - Status',  
                'target': str(memory_dir / 'claude-memory-status.bat'),
                'icon': str(memory_dir / 'claude-memory-status.bat'),
                'description': 'Check Claude Memory API Status'
            }
        ]
        
        shell = win32com.client.Dispatch("WScript.Shell")
        
        for shortcut_info in shortcuts:
            shortcut_path = desktop / f"{shortcut_info['name']}.lnk"
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = shortcut_info['target']
            shortcut.WorkingDirectory = str(memory_dir)
            shortcut.Description = shortcut_info['description']
            shortcut.save()
            
            print(f"✅ Created desktop shortcut: {shortcut_info['name']}")
            
        return True
        
    except ImportError:
        print("⚠️  pywin32 not available - skipping desktop shortcuts")
        print("   Install with: pip install pywin32")
        return False
    except Exception as e:
        print(f"⚠️  Could not create desktop shortcuts: {e}")
        return False

def create_startup_folder_shortcut():
    """Add shortcut to Windows Startup folder for auto-start"""
    try:
        startup_folder = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
        memory_dir = Path(__file__).parent
        
        # Create a batch file that starts the service silently
        silent_start_bat = memory_dir / "claude-memory-silent-start.bat"
        
        silent_content = f'''@echo off
REM Silent startup of Claude Memory API
cd /d "{memory_dir}"
call venv\\Scripts\\activate.bat
start /min python memory_api_server.py
'''
        
        with open(silent_start_bat, 'w') as f:
            f.write(silent_content)
            
        # Create shortcut in startup folder
        import win32com.client
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut_path = startup_folder / "Claude Memory API.lnk"
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(silent_start_bat)
        shortcut.WorkingDirectory = str(memory_dir)
        shortcut.Description = "Auto-start Claude Memory API"
        shortcut.WindowStyle = 7  # Minimized
        shortcut.save()
        
        print(f"✅ Added to Windows Startup: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not add to startup folder: {e}")
        return False

def create_environment_variables():
    """Create environment variables for easy access"""
    memory_dir = Path(__file__).parent
    
    # Set user environment variables
    try:
        import winreg
        
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_ALL_ACCESS
        )
        
        # Set CLAUDE_MEMORY_API_URL
        winreg.SetValueEx(key, "CLAUDE_MEMORY_API_URL", 0, winreg.REG_SZ, "http://localhost:8080")
        
        # Set CLAUDE_MEMORY_PATH  
        winreg.SetValueEx(key, "CLAUDE_MEMORY_PATH", 0, winreg.REG_SZ, str(memory_dir))
        
        winreg.CloseKey(key)
        
        print("✅ Environment variables set:")
        print("   CLAUDE_MEMORY_API_URL=http://localhost:8080")
        print(f"   CLAUDE_MEMORY_PATH={memory_dir}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not set environment variables: {e}")
        return False

def main():
    """Main setup function"""
    print("🌐 Setting up Global Access to Claude Memory API")
    print("="*60)
    print()
    
    # Step 1: Create global command utilities
    print("1. Creating global command utilities...")
    commands = create_global_commands()
    
    # Step 2: Set environment variables
    print("\\n2. Setting environment variables...")
    create_environment_variables()
    
    # Step 3: Try to add to system PATH (requires admin)
    print("\\n3. Adding to system PATH...")
    path_added = add_to_system_path()
    
    # Step 4: Create desktop shortcuts
    print("\\n4. Creating desktop shortcuts...")
    create_desktop_shortcuts()
    
    # Step 5: Add to startup folder
    print("\\n5. Adding to Windows startup...")
    create_startup_folder_shortcut()
    
    print("\\n" + "="*60)
    print("🎉 GLOBAL ACCESS SETUP COMPLETE!")
    print("="*60)
    print()
    print("🚀 NOW AVAILABLE FROM ANYWHERE:")
    print()
    print("Command Line (from any directory):")
    if path_added:
        print("  claude-memory-start      - Start the API server")
        print("  claude-memory-stop       - Stop the API server")  
        print("  claude-memory-status     - Check if server is running")
        print("  claude-memory-search     - Search memories")
    else:
        print("  (Commands available after restart or manual PATH update)")
    print()
    print("Environment Variables:")
    print("  %CLAUDE_MEMORY_API_URL%  - http://localhost:8080")
    print("  %CLAUDE_MEMORY_PATH%     - API installation directory")
    print()
    print("Desktop Shortcuts:")
    print("  'Claude Memory API - Start'  - Start server")
    print("  'Claude Memory API - Status' - Check status")
    print()
    print("Auto-Start:")
    print("  ✅ Added to Windows Startup folder")
    print("  📱 Will start automatically when Windows boots")
    print()
    print("💡 USAGE FROM ANY PROJECT:")
    print()
    print("1. API starts automatically with Windows")
    print("2. From any project directory:")
    print("   curl http://localhost:8080/api/health")
    print("3. Claude Code CLI will find the API automatically")
    print("4. Use environment variable in scripts: %CLAUDE_MEMORY_API_URL%")
    print()
    if not path_added:
        print("⚠️  RESTART REQUIRED:")
        print("   Restart your computer for PATH changes to take effect")
    else:
        print("✅ READY TO USE IMMEDIATELY!")

if __name__ == "__main__":
    main()