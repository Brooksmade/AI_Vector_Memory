#!/bin/bash
# Claude Code Hook - Save session summary to memory

# Get the JSON payload from stdin
JSON_PAYLOAD=$(cat)

# Extract session info
SESSION_ID=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('session_id', ''))")
TRANSCRIPT_PATH=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('transcript_path', ''))")

# Generate session summary
SUMMARY=$(python -c "
import json
import sys
from datetime import datetime

# Read transcript if available
transcript_content = ''
try:
    with open('$TRANSCRIPT_PATH', 'r') as f:
        transcript_content = f.read()
except:
    pass

# Extract key information
files_modified = []
errors_encountered = []
technologies = set()

# Basic parsing (you can enhance this)
for line in transcript_content.split('\\n'):
    if 'Edit' in line or 'Write' in line:
        # Try to extract file path
        if '.tsx' in line or '.ts' in line:
            technologies.add('typescript')
        if '.py' in line:
            technologies.add('python')
    if 'error' in line.lower() or 'failed' in line.lower():
        errors_encountered.append(line[:100])

# Create summary
summary = {
    'title': f'Session: Warehouse Inventory Development',
    'content': f'Session ID: $SESSION_ID\\nWork completed in warehouse inventory management project.\\nTechnologies: {list(technologies)}\\nErrors: {len(errors_encountered)}',
    'source': 'claude_code',
    'technologies': list(technologies),
    'complexity': 'medium',
    'project': 'warehouse-inventory-management'
}

print(json.dumps(summary))
")

# Store session summary in memory
if [[ -n "$SUMMARY" ]]; then
    RESPONSE=$(curl -s -X POST http://localhost:8080/api/add_memory \
        -H "Content-Type: application/json" \
        -d "$SUMMARY" 2>/dev/null)
    
    if [[ $? -eq 0 ]]; then
        echo "● Session saved to memory"
    else
        echo "● Session save failed"
    fi
fi

exit 0