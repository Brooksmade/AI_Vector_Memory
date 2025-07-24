#!/usr/bin/env python3
"""
Install Claude Memory API as a Windows Service
This allows the API to start automatically with Windows and run in the background.
"""

import sys
import os
import subprocess
from pathlib import Path

def create_service_script():
    """Create a service wrapper script"""
    service_script = Path(__file__).parent / "memory_api_service.py"
    
    service_content = f'''#!/usr/bin/env python3
"""
Windows Service wrapper for Claude Memory API
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging for service  
logging.basicConfig(
    filename=r'{Path(__file__).parent / "service.log"}',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_service():
    """Main service loop"""
    try:
        logging.info("Starting Claude Memory API Service")
        
        # Change to the correct directory
        os.chdir(r'{Path(__file__).parent}')
        
        # Import and run the API server
        from memory_api_server import app, API_HOST, API_PORT, logger
        
        logging.info(f"Service starting on {{API_HOST}}:{{API_PORT}}")
        
        # Run the Flask app (use Waitress for production)
        try:
            from waitress import serve
            serve(app, host=API_HOST, port=API_PORT)
        except ImportError:
            # Fallback to Flask development server
            app.run(host=API_HOST, port=API_PORT, debug=False)
            
    except Exception as e:
        logging.error(f"Service error: {{e}}")
        import traceback
        logging.error(traceback.format_exc())
        time.sleep(5)  # Wait before potential restart

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            print("Installing Claude Memory API Service...")
            # Service installation would go here
        elif sys.argv[1] == "uninstall":
            print("Uninstalling Claude Memory API Service...")
            # Service uninstallation would go here
        elif sys.argv[1] == "start":
            print("Starting Claude Memory API Service...")
            run_service()
    else:
        run_service()
'''
    
    with open(service_script, 'w') as f:
        f.write(service_content)
        
    return service_script

def install_waitress():
    """Install Waitress WSGI server for production"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'waitress'])
        print("✅ Waitress WSGI server installed")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Could not install Waitress - will use Flask development server")
        return False

def create_startup_batch():
    """Create a batch file for manual service start"""
    batch_file = Path(__file__).parent / "start_service.bat"
    
    batch_content = f'''@echo off
echo Starting Claude Memory API Service...
cd /d "{Path(__file__).parent}"
call venv\\Scripts\\activate.bat
python memory_api_service.py start
pause
'''
    
    with open(batch_file, 'w') as f:
        f.write(batch_content)
        
    print(f"✅ Startup batch file created: {batch_file}")
    return batch_file

def create_task_scheduler_xml():
    """Create XML for Windows Task Scheduler"""
    xml_file = Path(__file__).parent / "claude_memory_api_task.xml"
    
    xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Claude Memory API Service - Starts automatically with Windows</Description>
    <Author>Claude Memory System</Author>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions>
    <Exec>
      <Command>{Path(__file__).parent / "start_service.bat"}</Command>
      <WorkingDirectory>{Path(__file__).parent}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
    
    with open(xml_file, 'w') as f:
        f.write(xml_content)
        
    print(f"✅ Task Scheduler XML created: {xml_file}")
    return xml_file

def main():
    """Main installation function"""
    print("🔧 Installing Claude Memory API as Background Service")
    print()
    
    # Step 1: Create service script
    print("1. Creating service wrapper script...")
    service_script = create_service_script()
    print(f"✅ Service script created: {service_script}")
    
    # Step 2: Install production server
    print("\\n2. Installing production WSGI server...")
    install_waitress()
    
    # Step 3: Create startup batch file
    print("\\n3. Creating startup batch file...")
    batch_file = create_startup_batch()
    
    # Step 4: Create Task Scheduler XML
    print("\\n4. Creating Task Scheduler configuration...")
    xml_file = create_task_scheduler_xml()
    
    print("\\n" + "="*60)
    print("🎉 INSTALLATION COMPLETE!")
    print("="*60)
    print()
    print("📋 NEXT STEPS:")
    print()
    print("OPTION A - Automatic Startup (Recommended):")
    print("1. Open Task Scheduler (Windows + R, type 'taskschd.msc')")
    print("2. Click 'Import Task...' in the right panel")
    print(f"3. Select: {xml_file}")
    print("4. Click 'OK' to import")
    print("5. The service will start automatically on boot")
    print()
    print("OPTION B - Manual Startup:")
    print(f"1. Double-click: {batch_file}")
    print("2. Or run in command prompt for debugging")
    print()
    print("OPTION C - Test Now:")
    print(f"1. cd {Path(__file__).parent}")
    print("2. python memory_api_service.py start")
    print()
    print("📊 VERIFY INSTALLATION:")
    print("- Wait 10 seconds after starting")
    print("- Open browser to: http://localhost:8080/api/health")
    print("- Should see: {'success': true, 'data': {'status': 'healthy'}}")
    print()
    print("🔗 The Memory API will now be available from ANY project!")

if __name__ == "__main__":
    main()