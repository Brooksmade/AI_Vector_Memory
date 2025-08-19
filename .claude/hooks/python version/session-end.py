#!/usr/bin/env python3
"""Claude Code Hook - Save session summary at end"""

import sys
import json
import requests
from datetime import datetime
import os

def main():
    try:
        # Read JSON payload from stdin if available
        json_payload = ""
        if not sys.stdin.isatty():
            json_payload = sys.stdin.read()
        
        session_data = {}
        if json_payload:
            try:
                session_data = json.loads(json_payload)
            except:
                pass
        
        # Prepare session summary
        current_time = datetime.now().isoformat()
        project_name = os.path.basename(os.getcwd())
        
        # Create a basic session summary
        summary = f"Session ended at {current_time} for project {project_name}"
        
        # If we have session data, enhance the summary
        if session_data:
            tools_used = session_data.get('tools_used', [])
            files_modified = session_data.get('files_modified', [])
            
            if tools_used:
                summary += f"\nTools used: {', '.join(set(tools_used[:5]))}"
            if files_modified:
                summary += f"\nFiles modified: {', '.join(files_modified[:5])}"
        
        # Store session summary
        memory_data = {
            'title': f'Session: {project_name} - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'content': summary,
            'source': 'claude_code',
            'technologies': ['session-tracking'],
            'complexity': 'low',
            'project': project_name
        }
        
        response = requests.post(
            'http://localhost:8080/api/add_memory',
            json=memory_data,
            timeout=3
        )
        
        if response.status_code == 200:
            print("💾 Session summary saved to memory")
        
    except Exception:
        # Silent fail
        pass
    
    return 0

if __name__ == '__main__':
    sys.exit(main())