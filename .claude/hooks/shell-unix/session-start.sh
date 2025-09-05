#!/bin/bash
# Claude Code Hook - Initialize memory context at session start

# Get the JSON payload from stdin
JSON_PAYLOAD=$(cat)

# Extract session info
SESSION_ID=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('session_id', ''))")
PROJECT_DIR=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('cwd', ''))")

# Search for relevant past work in this project
MEMORY_RESPONSE=$(curl -s -X POST http://localhost:8080/api/search \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$(basename $PROJECT_DIR) recent work session\", \"max_results\": 5, \"similarity_threshold\": 0.4}")

# Check if there are relevant memories
echo "$MEMORY_RESPONSE" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        results = data.get('data', {}).get('results', [])
        relevant = [r for r in results if r.get('similarity', 0) > 0.5]
        if relevant:
            print(f'● Memory: {len(relevant)} relevant memories found')
        else:
            print('● Memory: initialized')
except:
    print('● Memory: offline')
"

# Update memory context with current session
curl -s -X POST http://localhost:8080/api/active/context \
    -H "Content-Type: application/json" \
    -d "{
        \"session_id\": \"$SESSION_ID\",
        \"project\": \"$(basename $PROJECT_DIR)\",
        \"start_time\": \"$(date -Iseconds)\"
    }" > /dev/null 2>&1

exit 0