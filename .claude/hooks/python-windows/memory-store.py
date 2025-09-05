#!/usr/bin/env python3
"""Memory store hook - captures and stores tool results to memory"""
import sys
import json
import os
from datetime import datetime

def main():
    try:
        # Read stdin - REQUIRED for PostToolUse hooks
        stdin_data = sys.stdin.read()
        data = json.loads(stdin_data)
        
        tool_name = data.get('tool_name', '')
        tool_input = data.get('tool_input', {})
        tool_response = data.get('tool_response', {})
        
        # Extract key information
        file_path = tool_input.get('file_path', '')
        command = tool_input.get('command', '')
        
        # Only process if we have something to store
        if not (file_path or command):
            return 0
        
        try:
            import requests
            
            # Store errors for learning
            if 'error' in str(tool_response).lower():
                title = f'Error: {tool_name}'
                if file_path:
                    title += f' on {os.path.basename(file_path)}'
                elif command:
                    title += f' - {command[:30]}'
                
                memory_data = {
                    'title': title,
                    'content': f'Tool: {tool_name}\nInput: {str(tool_input)[:200]}\nError: {str(tool_response)[:500]}',
                    'source': 'claude_code',
                    'technologies': ['error', tool_name.lower()],
                    'complexity': 'high',
                    'project': os.path.basename(os.getcwd()),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Fire and forget
                requests.post(
                    'http://localhost:8080/api/add_memory',
                    json=memory_data,
                    timeout=0.5
                )
            
            # Store significant successful operations
            elif tool_name in ['Write', 'MultiEdit'] and file_path:
                memory_data = {
                    'title': f'Modified: {os.path.basename(file_path)}',
                    'content': f'File: {file_path}\nOperation: {tool_name}\nTimestamp: {datetime.now().isoformat()}',
                    'source': 'claude_code',
                    'technologies': ['file_operation'],
                    'complexity': 'low',
                    'project': os.path.basename(os.getcwd())
                }
                
                requests.post(
                    'http://localhost:8080/api/add_memory',
                    json=memory_data,
                    timeout=0.5
                )
            
            # Store significant bash operations
            elif tool_name == 'Bash' and command:
                significant_keywords = ['migrate', 'install', 'build', 'deploy', 'test', 'create', 'init', 'git']
                if any(keyword in command.lower() for keyword in significant_keywords):
                    memory_data = {
                        'title': f'Command: {command[:50]}',
                        'content': f'Command: {command}\nResult: Success\nTimestamp: {datetime.now().isoformat()}',
                        'source': 'claude_code',
                        'technologies': ['bash', 'command'],
                        'complexity': 'medium',
                        'project': os.path.basename(os.getcwd())
                    }
                    
                    requests.post(
                        'http://localhost:8080/api/add_memory',
                        json=memory_data,
                        timeout=0.5
                    )
                    
        except:
            # Silent fail - PostToolUse shouldn't block operations
            pass
            
    except:
        # Silent fail on any error
        pass
    
    # PostToolUse hooks just return 0
    return 0

if __name__ == '__main__':
    sys.exit(main())