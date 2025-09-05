#!/usr/bin/env python3
"""Memory check hook - checks for past issues and auto-approves safe operations"""
import sys
import json
import os
from datetime import datetime

def main():
    
    try:
        # Read stdin - REQUIRED for PreToolUse hooks
        stdin_data = sys.stdin.read()
        data = json.loads(stdin_data)
        
        tool_name = data.get('tool_name', '')
        tool_input = data.get('tool_input', {})
        file_path = tool_input.get('file_path', '')
        
        # Default response - allow the operation
        response = {
            "permissionDecision": "allow",
            "permissionDecisionReason": "Memory check completed"
        }
        
        # Check memory for past issues with this file
        if file_path and tool_name in ['Edit', 'Write', 'MultiEdit']:
            try:
                import requests
                
                # Search for past issues with this file
                search_response = requests.post(
                    'http://localhost:8080/api/search',
                    json={
                        'query': f'{os.path.basename(file_path)} error issue problem bug freeze',
                        'max_results': 5,
                        'similarity_threshold': 0.5
                    },
                    timeout=1
                )
                
                if search_response.status_code == 200:
                    result = search_response.json()
                    memories = result.get('data', {}).get('results', [])
                    
                    # Check if we found high-relevance issues
                    critical_issues = [m for m in memories if m.get('similarity', 0) > 0.7]
                    
                    if critical_issues:
                        # Found critical issues - ask for confirmation
                        issue_titles = [issue.get('title', 'Unknown')[:30] for issue in critical_issues[:2]]
                        warning_msg = f"⚠ Memory: {len(critical_issues)} past issues with {os.path.basename(file_path)}: {', '.join(issue_titles)}"
                        
                        response = {
                            "permissionDecision": "ask",
                            "permissionDecisionReason": warning_msg
                        }
                    else:
                        # No critical issues - auto-approve with context
                        if memories:
                            response["permissionDecisionReason"] = f"● Memory check: {len(memories)} related memories found"
                        else:
                            response["permissionDecisionReason"] = "● Memory check: clear"
                
            except Exception as e:
                # If memory check fails, still allow but note the error
                response["permissionDecisionReason"] = "● Memory: offline"
        
        # Output the JSON response
        print(json.dumps(response))
        
    except Exception as e:
        # On any error, allow the operation but log the issue
        fallback = {
            "permissionDecision": "allow",
            "permissionDecisionReason": f"Hook error: {str(e)[:50]}"
        }
        print(json.dumps(fallback))
    
    return 0

if __name__ == '__main__':
    sys.exit(main())