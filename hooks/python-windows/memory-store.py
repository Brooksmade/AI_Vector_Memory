#!/usr/bin/env python3
"""Claude Code Hook - Store errors and outcomes after operations"""

import sys
import json
import requests
from datetime import datetime
import os

def main():
    try:
        # Read JSON payload from stdin
        json_payload = sys.stdin.read()
        data = json.loads(json_payload)
        
        # Extract tool name and response
        tool_name = data.get('tool_name', '')
        tool_response = data.get('tool_response', {})
        
        # Check if there was an error
        has_error = False
        if isinstance(tool_response, dict) and tool_response.get('error'):
            has_error = True
        elif isinstance(tool_response, str) and ('error' in tool_response.lower() or 'failed' in tool_response.lower()):
            has_error = True
        
        # If there was an error, store it in memory
        if has_error:
            file_path = data.get('tool_input', {}).get('file_path', 'unknown')
            
            # Store error in memory for future learning
            memory_data = {
                'title': f'Error: {tool_name} on {os.path.basename(file_path)}',
                'content': f'Tool: {tool_name}\nFile: {file_path}\nError: {str(tool_response)[:500]}\nDate: {datetime.now().isoformat()}',
                'source': 'claude_code',
                'technologies': ['error-tracking'],
                'complexity': 'high',
                'project': os.path.basename(os.getcwd())
            }
            
            requests.post(
                'http://localhost:8080/api/add_memory',
                json=memory_data,
                timeout=3
            )
    except Exception:
        # Silent fail
        pass
    
    return 0

if __name__ == '__main__':
    sys.exit(main())