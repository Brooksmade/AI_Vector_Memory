#!/usr/bin/env python3
"""Claude Code Hook - Learn from errors and suggest recovery"""

import sys
import json
import requests
import re

def main():
    try:
        # Read JSON payload from stdin
        json_payload = sys.stdin.read()
        data = json.loads(json_payload)
        
        # Extract tool response to check for errors
        tool_name = data.get('tool_name', '')
        tool_response = str(data.get('tool_response', {}))[:1000]
        
        # Check if there was an error
        if 'error' in tool_response.lower() or 'failed' in tool_response.lower():
            print("🔍 Analyzing error and searching for solutions...")
            
            # Extract error type
            error_type = 'GenericError'
            if 'TypeError' in tool_response:
                error_type = 'TypeError'
            elif 'SyntaxError' in tool_response:
                error_type = 'SyntaxError'
            elif 'Cannot find module' in tool_response or 'Module not found' in tool_response:
                error_type = 'ModuleNotFound'
            elif 'ENOENT' in tool_response or 'no such file' in tool_response.lower():
                error_type = 'FileNotFound'
            elif 'Permission denied' in tool_response:
                error_type = 'PermissionError'
            elif 'null' in tool_response.lower() or 'undefined' in tool_response.lower():
                error_type = 'NullReference'
            
            # Search for similar errors and their solutions
            response = requests.post(
                'http://localhost:8080/api/search',
                json={
                    'query': f'{error_type} error fixed solution resolved',
                    'max_results': 3,
                    'similarity_threshold': 0.5
                },
                timeout=3
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    solutions = []
                    for r in result.get('data', {}).get('results', []):
                        preview = r.get('preview', '').lower()
                        if 'fixed' in preview or 'resolved' in preview or 'solution' in preview:
                            # Try to extract the fix
                            fix_match = re.search(r'fixed by (.+?)[\.\n]', preview, re.IGNORECASE)
                            if fix_match:
                                solutions.append(fix_match.group(1))
                            elif 'add' in preview:
                                solutions.append('Check if dependencies or imports are missing')
                            elif 'null' in preview or 'undefined' in preview:
                                solutions.append('Add null checks or optional chaining')
                    
                    if solutions:
                        print('💡 Potential solutions from memory:')
                        for i, sol in enumerate(solutions[:3], 1):
                            print(f'  {i}. {sol}')
                        print('\n🔧 Try these solutions or search memory for more details.')
                    else:
                        # Store this new error for future learning
                        memory_data = {
                            'title': f'Error: {error_type} in {tool_name}',
                            'content': f'Error Type: {error_type}\nTool: {tool_name}\nResponse: {tool_response}\nStatus: Unresolved - needs solution',
                            'source': 'claude_code',
                            'technologies': ['error-tracking'],
                            'complexity': 'high',
                            'project': 'warehouse-inventory-management'
                        }
                        
                        requests.post(
                            'http://localhost:8080/api/add_memory',
                            json=memory_data,
                            timeout=3
                        )
                        
                        print("📝 New error pattern stored for future learning")
    except Exception:
        # Silent fail
        pass
    
    return 0

if __name__ == '__main__':
    sys.exit(main())