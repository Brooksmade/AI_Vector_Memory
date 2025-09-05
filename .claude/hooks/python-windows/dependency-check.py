#!/usr/bin/env python3
"""Claude Code Hook - Check memory before installing dependencies"""

import sys
import json
import requests
import re

def main():
    try:
        # Read JSON payload from stdin
        json_payload = sys.stdin.read()
        data = json.loads(json_payload)
        
        # Extract command
        tool_name = data.get('tool_name', '')
        command = data.get('tool_input', {}).get('command', '')
        
        # Check if this is a dependency installation command
        if tool_name == 'Bash' and any(cmd in command for cmd in ['npm install', 'pip install', 'yarn add']):
            print("[DEPENDENCY] Checking memory for dependency issues...")
            
            # Try to extract package name
            package = None
            match = re.search(r'install\s+([a-z0-9\-_@/]+)', command, re.IGNORECASE)
            if match:
                package = match.group(1)
            
            # Build search query
            search_query = 'dependency install error'
            if package:
                search_query = f'{package} dependency install error version conflict'
            
            # Search for past issues
            response = requests.post(
                'http://localhost:8080/api/search',
                json={
                    'query': search_query,
                    'max_results': 3,
                    'similarity_threshold': 0.4
                },
                timeout=3
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    dep_issues = []
                    for r in result.get('data', {}).get('results', []):
                        preview = r.get('preview', '').lower()
                        if 'version' in preview or 'conflict' in preview or 'peer' in preview:
                            dep_issues.append(r)
                    
                    if dep_issues:
                        print('[WARNING] Found past dependency issues:')
                        for issue in dep_issues[:2]:
                            print(f"  - {issue.get('title', 'Unknown')}")
                            preview = issue.get('preview', '')
                            if 'version' in preview.lower():
                                print('    [ACTION] Check package.json for version conflicts')
                            if 'peer' in preview.lower():
                                print('    [ACTION] Check peer dependency requirements')
                        print('\n[ACTION] Consider checking package versions before installing')
    except Exception:
        # Silent fail
        pass
    
    return 0

if __name__ == '__main__':
    sys.exit(main())