#!/usr/bin/env python3
"""Claude Code Hook - Check memory before running tests"""

import sys
import json
import requests

def main():
    try:
        # Read JSON payload from stdin
        json_payload = sys.stdin.read()
        data = json.loads(json_payload)
        
        # Extract tool name and command
        tool_name = data.get('tool_name', '')
        command = data.get('tool_input', {}).get('command', '')
        
        # Check if this is a test command
        if tool_name == 'Bash' and any(test_cmd in command for test_cmd in ['npm test', 'npm run test', 'jest', 'pytest']):
            print("🧪 Checking memory for past test failures...")
            
            # Search for test-related issues
            response = requests.post(
                'http://localhost:8080/api/search',
                json={
                    'query': 'test failed error jest pytest npm',
                    'max_results': 3,
                    'similarity_threshold': 0.5
                },
                timeout=3
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # Check for past test failures
                    test_issues = [
                        r for r in result.get('data', {}).get('results', [])
                        if 'test' in r.get('preview', '').lower() and 'fail' in r.get('preview', '').lower()
                    ]
                    
                    if test_issues:
                        print('⚠️ Found past test issues:')
                        for issue in test_issues[:2]:
                            print(f"  • {issue.get('title', 'Unknown')} ({issue.get('date', 'Unknown')})")
                            preview = issue.get('preview', '')
                            if 'FAIL' in preview or 'failed' in preview:
                                print(f"    Issue: {preview[:150]}...")
                        print('\n💡 Consider checking these specific test areas before running.')
    except Exception:
        # Silent fail
        pass
    
    return 0

if __name__ == '__main__':
    sys.exit(main())