#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Claude Code Hook - Session start (context injection only, no operations)"""

import sys
import json
import os
from datetime import datetime

def main():
    # Read stdin - SessionStart hooks receive session data
    try:
        stdin_data = sys.stdin.read()
        if stdin_data:
            session_data = json.loads(stdin_data)
    except:
        session_data = {}
    
    # Build context to inject into the session
    project_name = os.path.basename(os.getcwd())
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Create the context message
    context_lines = [
        f"● Memory system ready for {project_name} at {current_time}"
    ]
    
    # Output the additionalContext for SessionStart
    response = {
        "additionalContext": "\n".join(context_lines)
    }
    
    # Output as JSON
    print(json.dumps(response))
    
    return 0

if __name__ == '__main__':
    sys.exit(main())