#!/usr/bin/env python3
"""Claude Code Hook - Check memory before git operations"""

import sys
import json
import requests

def main():
    try:
        # Read JSON payload from stdin
        json_payload = sys.stdin.read()
        data = json.loads(json_payload)
        
        # Extract command
        tool_name = data.get('tool_name', '')
        command = data.get('tool_input', {}).get('command', '')
        
        # Check if this is a git command
        if tool_name == 'Bash' and 'git ' in command:
            # For git commits
            if 'git commit' in command:
                print("[GIT] Checking memory for commit best practices...")
                
                # Search for commit-related memories
                response = requests.post(
                    'http://localhost:8080/api/search',
                    json={
                        'query': 'git commit message convention style',
                        'max_results': 2,
                        'similarity_threshold': 0.4
                    },
                    timeout=3
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        for r in result.get('data', {}).get('results', []):
                            if 'commit' in r.get('preview', '').lower():
                                print('[REMINDER] Include clear commit messages and co-author attribution')
                                break
            
            # For git merge
            elif 'git merge' in command or 'git rebase' in command:
                print("[WARNING] Checking memory for past merge conflicts...")
                
                # Search for merge issues
                response = requests.post(
                    'http://localhost:8080/api/search',
                    json={
                        'query': 'git merge conflict rebase error',
                        'max_results': 3,
                        'similarity_threshold': 0.5
                    },
                    timeout=3
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        conflicts = [
                            r for r in result.get('data', {}).get('results', [])
                            if 'conflict' in r.get('preview', '').lower() or 'merge' in r.get('preview', '').lower()
                        ]
                        
                        if conflicts:
                            print('[WARNING] Past merge issues detected:')
                            for c in conflicts[:2]:
                                print(f"  - {c.get('title', 'Unknown')}")
                            print('[ACTION] Consider checking branch status before merging')
    except Exception:
        # Silent fail
        pass
    
    return 0

if __name__ == '__main__':
    sys.exit(main())