#!/usr/bin/env python3
"""First action check - initializes memory on first tool use and auto-approves"""
import sys
import json
import os
from datetime import datetime

# Track if we've already initialized this session
SESSION_MARKER = os.path.join(os.environ.get('TEMP', '/tmp'), f'claude_session_{os.getpid()}.marker')

def main():
    try:
        # Read stdin - REQUIRED for PreToolUse hooks
        stdin_data = sys.stdin.read()
        data = json.loads(stdin_data)
        
        tool_name = data.get('tool_name', '')
        
        # Check if this is the first action of the session
        first_action = not os.path.exists(SESSION_MARKER)
        
        # Default response - allow the operation
        response = {
            "permissionDecision": "allow",
            "permissionDecisionReason": "Operation approved"
        }
        
        if first_action:
            # Mark that we've initialized
            try:
                with open(SESSION_MARKER, 'w') as f:
                    f.write(str(datetime.now()))
            except:
                pass
            
            # Initialize memory context
            project_name = os.path.basename(os.getcwd())
            memory_context = []
            
            try:
                import requests
                
                # Check memory server health
                health_response = requests.get('http://localhost:8080/api/health', timeout=1)
                
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    if health_data.get('success'):
                        doc_count = health_data.get('data', {}).get('database', {}).get('document_count', 0)
                        memory_context.append(f"Memory system active: {doc_count} memories available")
                        
                        # Search for relevant memories
                        search_response = requests.post(
                            'http://localhost:8080/api/search',
                            json={
                                'query': f'{project_name} recent work session important',
                                'max_results': 5,
                                'similarity_threshold': 0.4
                            },
                            timeout=1
                        )
                        
                        if search_response.status_code == 200:
                            search_data = search_response.json()
                            memories = search_data.get('data', {}).get('results', [])
                            
                            if memories:
                                memory_context.append(f"Found {len(memories)} relevant memories from past sessions")
                                
                                # Add memory titles to context
                                for mem in memories[:3]:
                                    memory_context.append(f"- {mem.get('title', 'Unknown')}")
                        
                        # Log session start
                        requests.post(
                            'http://localhost:8080/api/add_memory',
                            json={
                                'title': f'Session: {project_name}',
                                'content': f'New session started at {datetime.now().isoformat()} in {project_name}',
                                'source': 'claude_code',
                                'project': project_name
                            },
                            timeout=1
                        )
                        
            except Exception as e:
                memory_context.append(f"Memory system unavailable: {str(e)[:30]}")
            
            # Build the context message
            if memory_context and doc_count > 0:
                context_msg = f"● Memory initialized: {doc_count} memories ready"
            else:
                context_msg = "● Memory system offline"
            
            # Add context to the response
            response["permissionDecisionReason"] = context_msg
        
        # Output the JSON response
        print(json.dumps(response))
        
    except Exception as e:
        # On any error, allow the operation
        fallback = {
            "permissionDecision": "allow",
            "permissionDecisionReason": f"Initialization error: {str(e)[:50]}"
        }
        print(json.dumps(fallback))
    
    return 0

if __name__ == '__main__':
    sys.exit(main())