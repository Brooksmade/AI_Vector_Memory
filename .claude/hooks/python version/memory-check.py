#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Claude Code Hook - Check memory before file operations"""

import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import json
import requests

def main():
    print("[HOOK] Memory check hook running...")
    try:
        # Read JSON payload from stdin
        json_payload = sys.stdin.read()
        data = json.loads(json_payload)
        
        # Extract tool name and file path
        tool_name = data.get('tool_name', '')
        file_path = data.get('tool_input', {}).get('file_path', '')
        
        print(f"   Tool: {tool_name}, File: {file_path or 'N/A'}")
        
        # Check if it's a file operation
        if tool_name in ['Edit', 'Write', 'MultiEdit'] and file_path:
            # Call memory API to check for past issues
            response = requests.post(
                'http://localhost:8080/api/search',
                json={
                    'query': f'{file_path} error bug fix',
                    'max_results': 3,
                    'similarity_threshold': 0.5
                },
                timeout=3
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # Check for high-similarity warnings
                    warnings = [
                        r for r in result.get('data', {}).get('results', [])
                        if r.get('similarity', 0) > 0.6 and 'error' in r.get('preview', '').lower()
                    ]
                    
                    if warnings:
                        for warning in warnings:
                            print(f"[WARNING] Memory Warning: {warning.get('title', 'Unknown')} ({warning.get('date', 'Unknown')})")
                            preview = warning.get('preview', '')[:150]
                            if preview:
                                print(f"   Preview: {preview}...")
                        print("\n[TIP] Consider checking the memory for past solutions before proceeding.")
                    else:
                        print("   [OK] No warnings found in memory")
                else:
                    print("   [INFO] Memory check skipped (not a file operation)")
    except Exception as e:
        # Print error but don't block operation
        try:
            print(f"   [ERROR] Hook error: {str(e)[:50]}")
        except:
            print("   [ERROR] Hook encountered an error")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())