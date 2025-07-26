#!/usr/bin/env python3
"""
Claude Memory API System Tray Application

This application runs the Claude Memory API server in the background with a system tray icon.
It provides a discreet way to run the server without showing a console window, while still
allowing easy access to status and controls through the system tray.

Features:
- System tray icon with status indicator
- Right-click context menu for controls
- Background Flask server execution
- Health monitoring and status updates
- Graceful shutdown handling
- Windows notification support
"""

import sys
import os
import threading
import time
import subprocess
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from datetime import datetime

try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
    from plyer import notification
except ImportError as e:
    print(f"Required dependencies not installed: {e}")
    print("Please install with: pip install pystray pillow plyer")
    sys.exit(1)

# Windows-specific imports for hiding console
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes


class MemoryAPITrayApp:
    """System tray application for Claude Memory API Server"""
    
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
        self.server_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.health_status = "Unknown"
        self.last_health_check = None
        self.tray_icon = None
        
        # Configuration
        self.host = "localhost"
        self.port = 8080
        self.api_url = f"http://{self.host}:{self.port}"
        
        # Setup logging
        self.setup_logging()
        
        # Hide console window on Windows
        if sys.platform == "win32":
            self.hide_console()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "tray_app.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def hide_console(self):
        """Hide the console window on Windows"""
        try:
            # Get console window handle
            console_window = ctypes.windll.kernel32.GetConsoleWindow()
            if console_window:
                # Hide the window
                ctypes.windll.user32.ShowWindow(console_window, 0)  # SW_HIDE
                self.logger.info("Console window hidden")
            else:
                self.logger.info("No console window to hide (running without console)")
        except Exception as e:
            self.logger.warning(f"Could not hide console window: {e}")
    
    def create_icon_image(self, color: str = "green") -> Image.Image:
        """Create system tray icon image"""
        # Create a 64x64 image
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Color mapping
        colors = {
            "green": "#00ff00",    # Running
            "red": "#ff0000",      # Stopped/Error
            "yellow": "#ffff00",   # Starting/Warning
            "gray": "#808080"      # Unknown
        }
        
        fill_color = colors.get(color, colors["gray"])
        
        # Draw a circle
        draw.ellipse([8, 8, 56, 56], fill=fill_color, outline="#ffffff", width=2)
        
        # Add "M" for Memory
        draw.text((24, 20), "M", fill="#ffffff", anchor="mm")
        
        return image
    
    def update_icon_status(self, status: str):
        """Update tray icon based on server status"""
        if not self.tray_icon:
            return
            
        color_map = {
            "running": "green",
            "stopped": "red", 
            "starting": "yellow",
            "error": "red",
            "unknown": "gray"
        }
        
        color = color_map.get(status.lower(), "gray")
        new_icon = self.create_icon_image(color)
        self.tray_icon.icon = new_icon
        
        # Update tooltip
        tooltip_text = f"Claude Memory API - {status.title()}"
        if self.last_health_check:
            tooltip_text += f"\nLast check: {self.last_health_check.strftime('%H:%M:%S')}"
        
        self.tray_icon.title = tooltip_text
    
    def show_notification(self, title: str, message: str, timeout: int = 5):
        """Show system notification"""
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=timeout,
                app_name="Claude Memory API"
            )
        except Exception as e:
            self.logger.warning(f"Could not show notification: {e}")
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        # Check if we're in the right directory
        if not Path("memory_api_server.py").exists():
            self.show_notification(
                "Setup Error", 
                "memory_api_server.py not found in current directory"
            )
            return False
        
        # Check virtual environment
        if not Path("venv/Scripts/python.exe").exists():
            self.show_notification(
                "Setup Error",
                "Virtual environment not found. Please run setup first."
            )
            return False
        
        return True
    
    def start_server(self):
        """Start the Flask API server in background"""
        if self.is_running:
            self.logger.info("Server already running")
            return
        
        if not self.check_prerequisites():
            return
        
        self.logger.info("Starting Claude Memory API server...")
        self.update_icon_status("starting")
        
        try:
            # Prepare environment
            env = os.environ.copy()
            env['FLASK_ENV'] = 'production'
            env['FLASK_DEBUG'] = '0'
            env['PYTHONPATH'] = str(Path.cwd())
            
            # Start server process (hidden)
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            # Use the virtual environment's Python directly
            venv_python = Path.cwd() / "venv" / "Scripts" / "python.exe"
            if not venv_python.exists():
                self.logger.error(f"Virtual environment Python not found: {venv_python}")
                self.show_notification("Error", "Virtual environment Python not found")
                return
            
            # Start server using venv Python directly
            cmd = [str(venv_python), "memory_api_server.py"]
            
            self.server_process = subprocess.Popen(
                cmd,
                env=env,
                startupinfo=startupinfo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                cwd=str(Path.cwd()),  # Ensure correct working directory
                encoding='utf-8',  # Handle Unicode output
                errors='replace'  # Replace undecodable characters
            )
            
            self.is_running = True
            
            # Start health monitoring
            self.start_health_monitoring()
            
            # Monitor server output in background
            def monitor_output():
                try:
                    for line in iter(self.server_process.stdout.readline, ''):
                        if line:
                            self.logger.info(f"Server output: {line.strip()}")
                except Exception as e:
                    self.logger.error(f"Error monitoring server output: {e}")
            
            output_thread = threading.Thread(target=monitor_output, daemon=True)
            output_thread.start()
            
            # Monitor server errors in background
            def monitor_errors():
                try:
                    for line in iter(self.server_process.stderr.readline, ''):
                        if line:
                            self.logger.error(f"Server error: {line.strip()}")
                except Exception as e:
                    self.logger.error(f"Error monitoring server errors: {e}")
            
            error_thread = threading.Thread(target=monitor_errors, daemon=True)
            error_thread.start()
            
            # Wait a moment then check if server started
            time.sleep(5)  # Give more time to start
            if self.check_server_health():
                self.update_icon_status("running")
                self.show_notification(
                    "Server Started", 
                    f"Claude Memory API running on {self.api_url}"
                )
                self.logger.info("Server started successfully")
            else:
                # Check if process is still running
                if self.server_process and self.server_process.poll() is not None:
                    self.logger.error(f"Server process exited with code: {self.server_process.returncode}")
                    self.is_running = False
                    self.update_icon_status("error")
                    self.show_notification(
                        "Server Crashed",
                        "Server process terminated unexpectedly. Check logs."
                    )
                else:
                    self.update_icon_status("error")
                    self.show_notification(
                        "Server Error",
                        "Server started but health check failed"
                    )
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            self.update_icon_status("error")
            self.show_notification("Startup Error", f"Failed to start server: {str(e)}")
            self.is_running = False
    
    def stop_server(self):
        """Stop the Flask API server"""
        if not self.is_running:
            return
        
        self.logger.info("Stopping Claude Memory API server...")
        self.update_icon_status("stopping")
        
        try:
            if self.server_process:
                self.server_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.server_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.logger.warning("Server didn't stop gracefully, killing...")
                    self.server_process.kill()
                
                self.server_process = None
            
            self.is_running = False
            self.update_icon_status("stopped")
            self.show_notification("Server Stopped", "Claude Memory API has been stopped")
            self.logger.info("Server stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping server: {e}")
            self.show_notification("Stop Error", f"Error stopping server: {str(e)}")
    
    def check_server_health(self) -> bool:
        """Check if server is healthy"""
        try:
            response = requests.get(f"{self.api_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.health_status = "Healthy"
                    self.last_health_check = datetime.now()
                    return True
            
            self.health_status = "Unhealthy"
            return False
            
        except requests.exceptions.RequestException:
            self.health_status = "Unreachable"
            return False
        except Exception as e:
            self.health_status = f"Error: {str(e)}"
            return False
    
    def start_health_monitoring(self):
        """Start background health monitoring"""
        def monitor():
            while self.is_running:
                if self.check_server_health():
                    self.update_icon_status("running")
                else:
                    self.update_icon_status("error")
                time.sleep(30)  # Check every 30 seconds
        
        if not self.server_thread or not self.server_thread.is_alive():
            self.server_thread = threading.Thread(target=monitor, daemon=True)
            self.server_thread.start()
    
    def open_browser(self):
        """Open browser to API documentation or health endpoint"""
        import webbrowser
        webbrowser.open(f"{self.api_url}/api/health")
    
    def show_status(self):
        """Show detailed status information"""
        status_info = f"""Claude Memory API Status

Server: {'Running' if self.is_running else 'Stopped'}
URL: {self.api_url}
Health: {self.health_status}
Last Check: {self.last_health_check.strftime('%Y-%m-%d %H:%M:%S') if self.last_health_check else 'Never'}

Process ID: {self.server_process.pid if self.server_process else 'None'}
"""
        
        self.show_notification("Status", status_info, timeout=10)
        self.logger.info(f"Status requested: {status_info.replace(chr(10), ' | ')}")
    
    def view_logs(self):
        """Open log file in default text editor"""
        try:
            log_file = Path("logs/tray_app.log")
            if log_file.exists():
                if sys.platform == "win32":
                    os.startfile(log_file)
                else:
                    subprocess.run(["xdg-open", str(log_file)])
            else:
                self.show_notification("No Logs", "Log file not found")
        except Exception as e:
            self.show_notification("Error", f"Could not open logs: {e}")
    
    def create_menu(self):
        """Create system tray context menu"""
        return pystray.Menu(
            item(
                "Status", 
                self.show_status,
                default=True  # Double-click action
            ),
            item(
                "Open Health Check",
                self.open_browser,
                enabled=lambda item: self.is_running
            ),
            pystray.Menu.SEPARATOR,
            item(
                "Start Server",
                lambda: threading.Thread(target=self.start_server, daemon=True).start(),
                enabled=lambda item: not self.is_running
            ),
            item(
                "Stop Server",
                self.stop_server,
                enabled=lambda item: self.is_running
            ),
            pystray.Menu.SEPARATOR,
            item("View Logs", self.view_logs),
            pystray.Menu.SEPARATOR,
            item("Quit", self.quit_application)
        )
    
    def quit_application(self):
        """Quit the tray application"""
        self.logger.info("Shutting down tray application...")
        
        # Stop server if running
        if self.is_running:
            self.stop_server()
        
        # Stop tray icon
        if self.tray_icon:
            self.tray_icon.stop()
        
        self.logger.info("Tray application stopped")
    
    def run(self):
        """Run the system tray application"""
        self.logger.info("Starting Claude Memory API Tray Application...")
        
        # Create system tray icon
        icon_image = self.create_icon_image("gray")
        self.tray_icon = pystray.Icon(
            "claude_memory_api",
            icon_image,
            "Claude Memory API - Stopped",
            self.create_menu()
        )
        
        # Show startup notification
        self.show_notification(
            "Claude Memory API",
            "System tray application started. Right-click icon for options."
        )
        
        # Auto-start server
        threading.Thread(target=self.start_server, daemon=True).start()
        
        # Run tray icon (blocking)
        self.tray_icon.run()


def main():
    """Main entry point"""
    try:
        # Add a small delay if running on startup to ensure Windows is ready
        if "--startup" in sys.argv:
            time.sleep(5)  # Wait 5 seconds for Windows to fully load
            
        app = MemoryAPITrayApp()
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()