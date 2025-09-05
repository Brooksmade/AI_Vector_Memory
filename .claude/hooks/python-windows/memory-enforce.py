#!/usr/bin/env python3
"""Memory enforcement hook - ensures memory is checked before operations"""
import sys
import json
import os

def main():
    try:
        # Read stdin
        stdin_data = sys.stdin.read()
        data = json.loads(stdin_data)
        
        tool_name = data.get('tool_name', '')
        tool_input = data.get('tool_input', {})
        
        # Tools that should always check memory
        memory_critical_tools = ['Edit', 'Write', 'MultiEdit', 'Bash']
        
        if tool_name in memory_critical_tools:
            # Build enforcement message based on tool
            enforcement_msg = None
            
            if tool_name in ['Edit', 'Write', 'MultiEdit']:
                file_path = tool_input.get('file_path', '')
                if file_path:
                    basename = os.path.basename(file_path)
                    enforcement_msg = f"MEMORY CHECK REQUIRED for {basename}: Search memory for past issues with this file before proceeding."
            
            elif tool_name == 'Bash':
                command = tool_input.get('command', '')
                if command and any(word in command.lower() for word in ['install', 'migrate', 'build', 'test']):
                    enforcement_msg = "MEMORY CHECK: Review past command executions and errors before running this command."
            
            if enforcement_msg:
                # Return a response that adds context but still allows the operation
                response = {
                    "permissionDecision": "allow",
                    "permissionDecisionReason": "Auto-approved with memory reminder",
                    "systemMessage": enforcement_msg
                }
            else:
                # Default allow
                response = {
                    "permissionDecision": "allow",
                    "permissionDecisionReason": "Operation approved"
                }
        else:
            # Non-critical tools - just allow
            response = {
                "permissionDecision": "allow",
                "permissionDecisionReason": "Non-critical operation"
            }
        
        # Output JSON response
        print(json.dumps(response))
        
    except Exception as e:
        # On error, allow but note the issue
        fallback = {
            "permissionDecision": "allow",
            "permissionDecisionReason": f"Enforcement check error: {str(e)[:50]}"
        }
        print(json.dumps(fallback))
    
    return 0

if __name__ == '__main__':
    sys.exit(main())