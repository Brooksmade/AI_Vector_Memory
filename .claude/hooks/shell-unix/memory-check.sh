#!/bin/bash
# Claude Code Hook - Check memory before file operations

# Get the JSON payload from stdin
JSON_PAYLOAD=$(cat)

# Extract tool name and file path from JSON
TOOL_NAME=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('tool_name', ''))")
FILE_PATH=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); inputs=data.get('tool_input', {}); print(inputs.get('file_path', ''))")

# If it's a file operation, check memory
if [[ "$TOOL_NAME" == "Edit" ]] || [[ "$TOOL_NAME" == "Write" ]] || [[ "$TOOL_NAME" == "MultiEdit" ]]; then
    if [[ -n "$FILE_PATH" ]]; then
        # Call memory API to check for past issues
        MEMORY_RESPONSE=$(curl -s -X POST http://localhost:8080/api/search \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"$FILE_PATH error bug fix\", \"max_results\": 3, \"similarity_threshold\": 0.5}")
        
        # Check if there are high-similarity warnings
        echo "$MEMORY_RESPONSE" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        results = data.get('data', {}).get('results', [])
        warnings = [r for r in results if r.get('similarity', 0) > 0.6 and 'error' in r.get('preview', '').lower()]
        if warnings:
            titles = [w.get('title', 'Unknown')[:30] for w in warnings[:2]]
            print(f\"⚠ Memory: {len(warnings)} past issues - {', '.join(titles)}\")
        else:
            if results:
                print(f\"● Memory check: {len(results)} related memories found\")
            else:
                print(\"● Memory check: clear\")
except:
    print(\"● Memory: offline\")
"
    fi
fi

# Exit 0 to allow the operation to proceed
# Exit 2 to block the operation
exit 0