#!/bin/bash
# Claude Code Hook - Store errors and outcomes after operations

# Get the JSON payload from stdin
JSON_PAYLOAD=$(cat)

# Extract tool name, response, and details
TOOL_NAME=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); print(data.get('tool_name', ''))")
TOOL_RESPONSE=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); print(str(data.get('tool_response', {}))[:500])")

# Check if there was an error in the response
HAS_ERROR=$(echo "$JSON_PAYLOAD" | python -c "
import sys, json
data = json.load(sys.stdin)
response = data.get('tool_response', {})
# Check for error indicators
if isinstance(response, dict) and response.get('error'):
    print('true')
elif isinstance(response, str) and ('error' in response.lower() or 'failed' in response.lower()):
    print('true')
else:
    print('false')
")

# If there was an error, store it in memory
if [[ "$HAS_ERROR" == "true" ]]; then
    FILE_PATH=$(echo "$JSON_PAYLOAD" | python -c "import sys, json; data=json.load(sys.stdin); inputs=data.get('tool_input', {}); print(inputs.get('file_path', 'unknown'))")
    
    # Store error in memory for future learning
    curl -s -X POST http://localhost:8080/api/add_memory \
        -H "Content-Type: application/json" \
        -d "{
            \"title\": \"Error: $TOOL_NAME on $(basename $FILE_PATH)\",
            \"content\": \"Tool: $TOOL_NAME\\nFile: $FILE_PATH\\nError: $TOOL_RESPONSE\\nDate: $(date -Iseconds)\",
            \"source\": \"claude_code\",
            \"technologies\": [\"error-tracking\"],
            \"complexity\": \"high\",
            \"project\": \"$(basename $(pwd))\"
        }" > /dev/null 2>&1
fi

# Always exit 0 to not interfere with normal operation
exit 0