#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Claude Code Hook - Session start memory initialization"""

import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import json
import requests
from datetime import datetime

def main():
    print("[HOOK] Session start hook running...")
    try:
        # Check memory server health
        response = requests.get('http://localhost:8080/api/health', timeout=3)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                doc_count = result.get('data', {}).get('database', {}).get('document_count', 0)
                print(f"[MEMORY] Memory system active: {doc_count} memories available")
                
                # Search for recent session summaries
                search_response = requests.post(
                    'http://localhost:8080/api/search',
                    json={
                        'query': 'session warehouse inventory management recent',
                        'max_results': 3,
                        'similarity_threshold': 0.4,
                        'source_filter': 'claude_code'
                    },
                    timeout=3
                )
                
                if search_response.status_code == 200:
                    search_result = search_response.json()
                    if search_result.get('success'):
                        recent = search_result.get('data', {}).get('results', [])
                        if recent:
                            print("[FOUND] Recent work found:")
                            for i, memory in enumerate(recent[:2], 1):
                                title = memory.get('title', 'Unknown')
                                preview = memory.get('preview', '')[:100]
                                print(f"  {i}. {title}")
                                if preview:
                                    print(f"     {preview}...")
            else:
                print("[WARNING] Memory server not responding")
        else:
            print("[WARNING] Memory server not available")
    except Exception:
        # Silent fail - don't disrupt the session
        pass
    
    return 0

if __name__ == '__main__':
    sys.exit(main())